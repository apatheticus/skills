#!/usr/bin/env python3
"""Mechanical half of the pretty-svg-docs visual audit.

Scans markdown docs for mpd:viz marker pairs and reports one verdict per visual:
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

MARKER_OPEN = re.compile(
    r'<!--\s*mpd:viz\s+name="(?P<name>[^"]+)"\s+src="(?P<src>[^"]+)"'
    r'\s+facts-hash="(?P<facts_hash>[^"]*)"\s+src-hash="(?P<src_hash>[^"]*)"\s*-->'
)
MARKER_CLOSE = re.compile(r"<!--\s*mpd:viz\s+end\s*-->")
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

PRODUCER = "more-pretty-docs"

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


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        problems.append(f"{doc}: unbalanced mpd:viz markers ({len(opens)} open / {len(closes)} close)")

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
        meta_path = src_dir / "mpd.json"
        facts: list[str] = []
        style = relaxed = None
        if not meta_path.exists():
            verdicts.append("STALE (mpd.json absent)")
        else:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            facts = meta.get("facts", [])
            style = meta.get("style")
            relaxed = meta.get("relaxed") or []

            producer = meta.get("producer")
            if producer != PRODUCER:
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
    ap.add_argument("--root", default=".", help="repo root (asset paths resolve against this)")
    ap.add_argument("docs", nargs="+")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    design = root / "docs/assets/src/DESIGN.md"
    design_hash = sha256_file(design) if design.exists() else None
    if design_hash is None:
        print("note: docs/assets/src/DESIGN.md not found — DRIFT checks skipped", file=sys.stderr)

    rows: list = []
    problems: list = []
    for d in args.docs:
        p = Path(d)
        if not p.exists():
            problems.append(f"{d}: file not found")
            continue
        audit_doc(p, root, design_hash, rows, problems)

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
