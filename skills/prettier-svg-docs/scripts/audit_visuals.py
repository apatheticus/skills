#!/usr/bin/env python3
"""Mechanical half of the pretty-svg-docs visual audit.

Scans markdown docs for pd:viz marker pairs and reports one verdict per visual:
OK / MISSING / UNCENTERED / STALE / DRIFT / BUDGET / FOREIGN, plus doc-level
findings (unbalanced markers, budget overruns, any marker in LICENSE/NOTICE).

The CONTRADICTS verdict needs the evidence pass and is judged by Claude; this
script surfaces each visual's stored facts list for that judgment, along with the
style it was authored in and any gate relaxations that were applied.

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

PRODUCER = "prettier-svg-docs"
# All three values mean "this skill authored it". `pretty-svg-docs` and
# `more-pretty-docs` are what every visual written before each rename carries,
# including in third-party repos this project cannot migrate. Without the aliases the
# renamed skill would report all of its own prior work FOREIGN and offer to adopt it.
# Written as PRODUCER on the next touch.
PRODUCER_OWNED = {PRODUCER, "pretty-svg-docs", "more-pretty-docs"}

# Per-doc visual budgets: max marker pairs. None = unlimited (not used today).
BUDGETS = {
    "README": 4,          # hero + up to 3 body diagrams
    "ARCHITECTURE": 2,
    "DEVELOPMENT": 2,
    "DEPLOYMENT": 2,
    "CONTRIBUTING": 2,
    "SECURITY": 1,
    "CODE_OF_CONDUCT": 1,
    "SUPPORT": 1,
}
FORBIDDEN = {"LICENSE", "NOTICE"}  # zero visuals, zero markers, ever

BYTES_FAIL_DEFAULT = 153600  # 150 KB; a style may raise this to its declared floor


def load_byte_floors() -> tuple[int, dict[str, int]]:
    """Read the byte caps out of styles.json rather than restating them here.

    Two copies of the same numbers drift, and this script is the copy nobody
    updates. styles.json is the checker's own half of the catalog, so it wins.
    """
    catalog_path = Path(__file__).resolve().parent / "styles.json"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return BYTES_FAIL_DEFAULT, {}
    default = int(catalog.get("defaults", {}).get("bytes_fail", BYTES_FAIL_DEFAULT))
    floors = {slug: int(spec["relax"]["bytes_fail"])
              for slug, spec in catalog.get("styles", {}).items()
              if "bytes_fail" in spec.get("relax", {})}
    return default, floors


BYTES_FAIL_DEFAULT, STYLE_BYTE_FLOORS = load_byte_floors()

CONTRACT = ".prettydocs/prettydocs.md"       # current location
LEGACY_CONTRACT = "docs/assets/src/DESIGN.md"  # pre-.prettydocs location


# Docs whose visuals are structural by nature, so a missing diagram_type there is a
# finding rather than a preference. A README's hero is not structural; its body
# diagrams are, which is why the tier check below carries the other half.
STRUCTURAL_DOCS = {"ARCHITECTURE", "DEVELOPMENT", "DEPLOYMENT", "CONTRIBUTING",
                   "SECURITY", "README"}
# Tiers that legitimately have no diagram type: nothing about them is a diagram.
UNTYPED_TIERS = {"animated-hero", "banner"}

DIAGRAM_ATTR = re.compile(r'\bdata-diagram\s*=\s*["\']([^"\']+)["\']')


def svg_diagram_type(asset: Path | None) -> str | None:
    """The data-diagram on the root <svg>, or None.

    Read from the first 4 KB rather than parsed: the attribute is on the root
    element by contract, this script has no XML dependency, and a 250 KB contact
    sheet should not be parsed to answer one question.
    """
    if asset is None or not asset.exists() or asset.suffix.lower() != ".svg":
        return None
    head = asset.read_text(encoding="utf-8", errors="replace")[:4096]
    root = head.find("<svg")
    if root == -1:
        return None
    end = head.find(">", root)
    m = DIAGRAM_ATTR.search(head[root:end if end != -1 else None])
    return m.group(1).strip().lower() if m else None


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def doc_key(path: Path) -> str:
    return path.name.upper().removesuffix(".MD").removesuffix(".TXT")


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
        elif img_path and not img_path.lower().endswith(".svg"):
            verdicts.append(f"FOREIGN (embed is {Path(img_path).suffix}, not .svg)")

        if img and not CENTERED.search(block):
            verdicts.append("UNCENTERED (image not wrapped in a centering element)")

        src_dir = root / src
        meta_path = src_dir / MANIFEST_NAME
        if not meta_path.exists() and (src_dir / MANIFEST_LEGACY).exists():
            meta_path = src_dir / MANIFEST_LEGACY
        facts: list[str] = []
        style = relaxed = None
        if not meta_path.exists():
            verdicts.append(f"STALE ({MANIFEST_NAME} absent)")
        else:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            facts = meta.get("facts", [])
            style = meta.get("style")
            relaxed = meta.get("relaxed") or []
            tier = meta.get("tier")

            producer = meta.get("producer")
            if producer not in PRODUCER_OWNED:
                verdicts.append(
                    f"FOREIGN (producer={producer or 'absent'} — adopt it: see embedding.md)"
                )

            if (m.group("facts_hash") != meta.get("facts_hash", "")
                    or m.group("src_hash") != meta.get("src_hash", "")):
                verdicts.append("STALE (marker/manifest hash mismatch)")

            # For SVG the committed asset IS the source, so src_hash covers it directly.
            if asset is not None and asset.exists():
                if sha256_file(asset) != meta.get("src_hash", ""):
                    verdicts.append("STALE (asset edited since it was written)")

                cap = STYLE_BYTE_FLOORS.get(style or "", BYTES_FAIL_DEFAULT)
                size = asset.stat().st_size
                if size > cap:
                    verdicts.append(f"BUDGET ({size / 1024:.1f} KB over the {cap / 1024:.0f} KB cap)")

                recorded = (meta.get("svg") or {}).get("bytes")
                if recorded is not None and recorded != size:
                    verdicts.append(f"STALE (svg.bytes says {recorded}, file is {size})")

            if design_hash and meta.get("design_hash") and meta["design_hash"] != design_hash:
                verdicts.append("DRIFT (design system changed)")

            # The manifest and the asset must agree about the diagram type. The
            # manifest is what the plan phase decided; the attribute is what the
            # checker's diagram class actually measured. A disagreement means one of
            # them was edited alone, and the gate silently stopped covering the
            # drawing that shipped.
            declared = meta.get("diagram_type")
            drawn = svg_diagram_type(asset)
            if declared and drawn is None:
                verdicts.append(
                    f"UNTYPED (viz.json says diagram_type={declared}, but the asset "
                    "carries no data-diagram — the diagram gate never fired on it)")
            elif drawn and not declared:
                verdicts.append(
                    f"UNTYPED (asset declares data-diagram={drawn}, absent from viz.json)")
            elif declared and drawn and declared != drawn:
                verdicts.append(
                    f"UNTYPED (viz.json says {declared}, the asset says {drawn})")
            elif not declared and not drawn and doc_key(doc) in STRUCTURAL_DOCS \
                    and tier not in UNTYPED_TIERS and "diagram_type" not in meta:
                # An explicit `"diagram_type": null` means the type question was asked
                # and the honest answer was "none" — a contact sheet, a swatch board, a
                # motif. That is a decision, and recording it is what stops this
                # verdict nagging forever. An ABSENT key means nobody asked.
                verdicts.append(
                    "UNTYPED (a structural visual in a technical doc, and nothing "
                    "records whether it has a type — choose one in "
                    'reference/diagrams.md, or write "diagram_type": null to say it '
                    "genuinely has none)")

        rows.append({
            "doc": doc.name,
            "name": name,
            "verdict": "; ".join(verdicts) if verdicts else "OK",
            "facts": facts,
            "style": style,
            "relaxed": relaxed,
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
        # exists() is true for a directory, so the guard above does not catch
        # `audit_visuals.py .` — the natural way to reach for "audit this project",
        # since --root takes a directory. Without this the run dies on an
        # IsADirectoryError traceback out of read_text() instead of saying what to do.
        if p.is_dir():
            problems.append(
                f"{d}: is a directory — pass the doc files themselves, with the "
                f"project root in --root (e.g. --root {d} {d}/README.md)"
            )
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
        if r["style"]:
            note = f"style: {r['style']}"
            if r["relaxed"]:
                note += f"   relaxed: {', '.join(r['relaxed'])}"
            print(f"{'':<22} {'':<{w}}   {note}")
        for f in r["facts"]:
            print(f"{'':<22} {'':<{w}}   fact: {f}")
    for p in problems:
        print(f"PROBLEM  {p}")

    bad = problems or any(r["verdict"] != "OK" for r in rows)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
