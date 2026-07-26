#!/usr/bin/env python3
"""Mechanical half of the pretty-hyper-docs visual audit.

Scans markdown docs for pd:viz marker pairs and reports one verdict per
visual: OK / MISSING / UNCENTERED / STALE / DRIFT / BUDGET, plus doc-level
findings (unbalanced markers, budget overruns, any marker in LICENSE/NOTICE).

The CONTRADICTS verdict needs the evidence pass and is judged by Claude;
this script surfaces each visual's stored facts list for that judgment.

Usage:
    audit_visuals.py [--root REPO_ROOT] DOC.md [DOC.md ...]

Writes nothing. Exit 0 = all OK, exit 1 = findings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

# `m?pd:` accepts both the current `pd:` prefix and the legacy `mpd:` one. Repos
# processed before the rename carry `mpd:` markers and an `mpd.json` manifest; the
# skill reads them and rewrites them to the current form the next time it touches
# that block, so no third-party repo needs a migration pass to keep auditing clean.
MARKER_OPEN = re.compile(
    r'<!--\s*m?pd:viz\s+name="(?P<name>[^"]+)"\s+src="(?P<src>[^"]+)"'
    r'\s+facts-hash="(?P<facts_hash>[^"]*)"\s+src-hash="(?P<src_hash>[^"]*)"\s*-->'
)
MARKER_CLOSE = re.compile(r"<!--\s*m?pd:viz\s+end\s*-->")
MANIFEST_NAME = "viz.json"
MANIFEST_LEGACY = "mpd.json"
# Matches markdown images and HTML <img> embeds (the README spec uses <img> for width control)
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)|<img\s[^>]*?src=\"([^\"]+)\"")
# An embed is centered by a block wrapper carrying align="center" — GitHub's sanitizer
# strips style=, so that attribute is the only mechanism. align on the <img> itself is
# inline vertical alignment and does not center, so it deliberately does not match here.
# DOTALL because alt text routinely wraps across lines, and the <img> arm skips over
# quoted attribute values rather than stopping at the first ">" — alt text says things
# like "client -> server", and a naive [^>]* would read that as the end of the tag.
CENTERED = re.compile(
    r'<(?P<tag>div|p)\s+align=["\']center["\']\s*>\s*'
    r'(?:!\[[^\]]*\]\([^)\s]+\)'
    r'|<img\b(?:[^>"\']|"[^"]*"|\'[^\']*\')*/?>)\s*'
    r'</(?P=tag)\s*>',
    re.IGNORECASE | re.DOTALL,
)

# Per-doc visual budgets: max marker pairs. None = unlimited (not used today).
BUDGETS = {
    "README": 4,          # hero + up to 3 body diagrams
    "ARCHITECTURE": 2,
    "DEVELOPMENT": 2,
    "CONTRIBUTING": 2,
    "SECURITY": 1,
    "CODE_OF_CONDUCT": 1,
    "SUPPORT": 1,
}
FORBIDDEN = {"LICENSE", "NOTICE"}  # zero visuals, zero markers, ever


CONTRACT = ".prettydocs/prettydocs.md"       # current location
LEGACY_CONTRACT = "docs/assets/src/DESIGN.md"  # pre-.prettydocs location


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def doc_key(path: Path) -> str:
    return path.name.upper().removesuffix(".MD").removesuffix(".TXT")


def project_chain(root: Path) -> list[Path]:
    """The project dir, then each ancestor up to and including the repo root.

    Bounded by the directory holding `.git` so the walk can never wander above the
    repo into unrelated parts of the filesystem. A repo with no `.git` (a tarball,
    a fixture) yields the project dir alone.
    """
    top = next((d for d in [root, *root.parents] if (d / ".git").exists()), None)
    chain = [root]
    if top is not None and top != root:
        for parent in root.parents:
            chain.append(parent)
            if parent == top:
                break
    return chain


def resolve_contract(root: Path) -> tuple[Path | None, str]:
    """Locate this project's frozen design contract.

    Nearest wins, then inheritance: a project without its own `prettydocs.md` uses
    the closest ancestor's, which is what keeps a monorepo visually coherent, and
    dropping one into the project overrides that. Falls back to the legacy path so
    a repo written before the move keeps auditing until its migration is accepted.

    Returns (path, how) where how is own / inherited / legacy / missing.
    """
    for depth, directory in enumerate(project_chain(root)):
        candidate = directory / CONTRACT
        if candidate.exists():
            return candidate, "own" if depth == 0 else "inherited"
    legacy = root / LEGACY_CONTRACT
    if legacy.exists():
        return legacy, "legacy"
    return None, "missing"


def audit_doc(doc: Path, root: Path, design_hash: str | None, rows: list, problems: list) -> None:
    text = doc.read_text(encoding="utf-8")
    opens = list(MARKER_OPEN.finditer(text))
    closes = list(MARKER_CLOSE.finditer(text))
    key = doc_key(doc)

    if key in FORBIDDEN and (opens or closes or IMAGE.search(text)):
        problems.append(f"{doc}: BUDGET — {key} must contain zero visuals/markers (hard violation)")
        return

    if len(opens) != len(closes):
        problems.append(f"{doc}: unbalanced pd:viz markers ({len(opens)} open / {len(closes)} close)")

    budget = BUDGETS.get(key)
    if budget is not None and len(opens) > budget:
        problems.append(f"{doc}: BUDGET — {len(opens)} visuals, budget is {budget}")

    for i, m in enumerate(opens):
        name, src = m.group("name"), m.group("src")
        block_end = closes[i].start() if i < len(closes) else len(text)
        block = text[m.end():block_end]
        verdicts = []

        img = IMAGE.search(block)
        img_path = (img.group(1) or img.group(2)) if img else None
        asset = root / img_path if img_path else None
        if asset is None:
            verdicts.append("MISSING (no image in block)")
        elif not asset.exists():
            verdicts.append(f"MISSING ({img_path})")

        if img and not CENTERED.search(block):
            verdicts.append("UNCENTERED (image not wrapped in a centering element)")

        src_dir = root / src
        meta_path = src_dir / MANIFEST_NAME
        if not meta_path.exists() and (src_dir / MANIFEST_LEGACY).exists():
            meta_path = src_dir / MANIFEST_LEGACY
        facts: list[str] = []
        if not meta_path.exists():
            verdicts.append(f"STALE ({MANIFEST_NAME} absent)")
        else:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            facts = meta.get("facts", [])
            if (m.group("facts_hash") != meta.get("facts_hash", "")
                    or m.group("src_hash") != meta.get("src_hash", "")):
                verdicts.append("STALE (marker/manifest hash mismatch)")
            comp = src_dir / "index.html"
            if not comp.exists():
                svgs = sorted(src_dir.glob("*.svg"))
                comp = svgs[0] if svgs else None
            if comp is None:
                verdicts.append("STALE (no composition source)")
            elif sha256_file(comp) != meta.get("src_hash", ""):
                verdicts.append("STALE (source edited since render)")
            if design_hash and meta.get("design_hash") and meta["design_hash"] != design_hash:
                verdicts.append("DRIFT (design system changed)")

        rows.append({
            "doc": doc.name,
            "name": name,
            "verdict": "; ".join(verdicts) if verdicts else "OK",
            "facts": facts,
        })


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="project root (asset paths resolve against this)")
    ap.add_argument("docs", nargs="+")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    design, how = resolve_contract(root)
    design_hash = sha256_file(design) if design is not None else None

    rows: list = []
    problems: list = []
    for d in args.docs:
        p = Path(d)
        if not p.exists():
            problems.append(f"{d}: file not found")
            continue
        audit_doc(p, root, design_hash, rows, problems)

    # A project that embeds visuals but has no design contract is a hard finding, not
    # a skipped check. Reporting it as a note and exiting 0 (the old behaviour) meant
    # every DRIFT comparison silently became unreachable while the run still looked
    # clean — the one failure mode that hides all the others.
    if rows and design is None:
        problems.append(
            f"{root}: no design contract for this project — looked for {CONTRACT} here "
            f"and in every ancestor up to the repo root, then {LEGACY_CONTRACT}. "
            f"DRIFT is unenforceable for all {len(rows)} visual(s) until one exists."
        )
    elif how == "legacy":
        print(f"note: reading the pre-.prettydocs contract at {LEGACY_CONTRACT} — offer to "
              f"migrate it to {CONTRACT}. Every hash is taken over file bytes, so the move "
              f"changes no hash and re-renders nothing.", file=sys.stderr)
    elif how == "inherited":
        print(f"note: no {CONTRACT} in this project — inheriting {design}", file=sys.stderr)

    w = max([len(r["name"]) for r in rows] + [6])
    print(f"{'DOC':<22} {'VISUAL':<{w}} VERDICT")
    for r in rows:
        print(f"{r['doc']:<22} {r['name']:<{w}} {r['verdict']}")
        for f in r["facts"]:
            print(f"{'':<22} {'':<{w}}   fact: {f}")
    for p in problems:
        print(f"PROBLEM  {p}")

    bad = problems or any(r["verdict"] != "OK" for r in rows)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
