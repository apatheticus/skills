#!/usr/bin/env python3
"""Mechanical half of the pretty-plain-docs visual audit.

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

# The whole <img> tag, then its alt out of that tag. Two steps rather than one
# regex reaching for alt= directly, because the tag body has to be walked with the
# same quote-stepping CENTERED uses — alt text says things like "client -> server",
# and a naive [^>]* reads that as the end of the tag.
IMG_TAG = re.compile(r'<img\b(?:[^>"\']|"[^"]*"|\'[^\']*\')*/?>',
                     re.IGNORECASE | re.DOTALL)
ALT_ATTR = re.compile(r'\balt="([^"]*)"', re.IGNORECASE | re.DOTALL)
MD_IMAGE_ALT = re.compile(r"!\[([^\]]*)\]\([^)\s]+\)")


def embed_alt(block: str) -> str:
    """The alt text of the embed in this marker block, '' if there is none."""
    tag = IMG_TAG.search(block)
    if tag:
        m = ALT_ATTR.search(tag.group(0))
        return m.group(1) if m else ""
    md = MD_IMAGE_ALT.search(block)
    return md.group(1) if md else ""

PRODUCER = "pretty-plain-docs"
# No legacy alias, deliberately: this skill has never shipped under another name, so
# it has no prior work to own. The siblings' producers are therefore FOREIGN here, and
# that is the intended migration path in both directions — running this skill on a
# repo whose visuals animate offers to re-author them as statics, and running
# prettier-svg-docs on a repo this skill has processed offers to animate them. Neither
# silently claims the other's work.
PRODUCER_OWNED = {PRODUCER}

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


# --- Description parity ------------------------------------------------------
#
# A visual's alt text and its <desc> ARE the document for a reader with images off,
# and nothing covered them: src_hash covers the SVG's bytes, facts_hash covers the
# manifest, and embed markup is covered by no hash at all. Two consecutive re-authors
# in this repo shipped a board whose descriptions still described the previous
# drawing — nine steps described as ten cells, then nine gate classes described as
# eight — and both passed every gate that existed.
#
# The obvious check does not work, and it was measured rather than assumed. Requiring
# every drawn numeral to appear in the description gives 146 findings over this repo's
# own 16 embeds, nearly all of them contact-sheet chrome and chart axis ticks.
# Requiring the reverse — every number in the description to appear on the board —
# produces the IDENTICAL verdict on the buggy file and the fixed one, because the
# description's other number ("a board of eight cells") survives both; it would have
# nagged forever without once distinguishing the defect.
#
# What works is two narrow clauses, measured at 0 findings across the same corpus
# while still failing the real defect on both of them. See describe_parity.

_UNITS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
          "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
          "sixteen", "seventeen", "eighteen", "nineteen"]
_TENS = {20: "twenty", 30: "thirty", 40: "forty", 50: "fifty",
         60: "sixty", 70: "seventy", 80: "eighty", 90: "ninety"}
CARDINAL_WORDS: dict[int, str] = {n: w for n, w in enumerate(_UNITS)}
CARDINAL_WORDS.update(_TENS)
for _t, _tw in _TENS.items():
    for _u in range(1, 10):
        CARDINAL_WORDS.setdefault(_t + _u, f"{_tw}-{_UNITS[_u]}")
ORDINAL_WORDS = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth",
                 6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth",
                 11: "eleventh", 12: "twelfth"}

ORDINAL_SUFFIX = re.compile(r"\b(\d+)(?:st|nd|rd|th)\b", re.IGNORECASE)
SPECIMEN_ATTR = re.compile(r'\bdata-specimen\s*=\s*["\']true["\']', re.IGNORECASE)
DESC_BLOCK = re.compile(r"<desc\b[^>]*>(.*?)</desc\s*>", re.IGNORECASE | re.DOTALL)
# title/desc/style hold text that is never painted. Strip them before reading the
# drawing, or the <desc> would satisfy the very check it is the subject of.
NOT_DRAWN = re.compile(r"<(title|desc|style)\b[^>]*>.*?</\1\s*>",
                       re.IGNORECASE | re.DOTALL)
# One text node's own character data. The attribute list steps over quoted values
# rather than stopping at the first ">", the same idiom CENTERED uses and for the
# same reason. `[^<]*` then stops at the first child element, so a <tspan> inside a
# <text> is read as its own node — which is what makes "a node that is exactly a
# number" a meaningful question.
TEXT_NODE = re.compile(r"<(?:text|tspan)\b(?:[^>\"']|\"[^\"]*\"|'[^']*')*>([^<]*)",
                       re.IGNORECASE)
# A node that IS a number, not a node that merely contains one. "9" and "1,200"
# qualify; "§14 em dash budget" and "SHEET 3 OF 7" do not, and that distinction is
# what separates a headline value from chrome.
VALUE_ONLY = re.compile(r"^(?:\d{1,3}(?:,\d{3})+|\d+)$")


def number_forms(n: int) -> set[str]:
    """Every spelling a description may legitimately use for n.

    The ordinal counts as a form of the cardinal on purpose: a board drawing `9`
    under GATE CLASSES is fairly described as "the ninth is diagram".
    """
    out = {str(n)}
    if n >= 1000:
        out.add(f"{n:,}")
    word = CARDINAL_WORDS.get(n)
    if word:
        out.add(word)
        out.add(word.replace("-", " "))
    if n in ORDINAL_WORDS:
        out.add(ORDINAL_WORDS[n])
    return out


def ordinals_in(text: str) -> set[int]:
    low = text.lower()
    found = {n for n, w in ORDINAL_WORDS.items() if re.search(rf"\b{w}\b", low)}
    return found | {int(m.group(1)) for m in ORDINAL_SUFFIX.finditer(low)}


def describe_parity(svg_text: str, alt: str, facts: str) -> list[str]:
    """Do this visual's descriptions still match what it draws?

    Pure on strings so it is testable without a project tree on disk —
    scripts/test_alt_parity.py drives it directly. Two clauses:

    A. A text node whose whole content is a plain integer must appear in the alt or
       the <desc>, as a numeral or as a number word. Zero-padded numerals (01, 02)
       are step markers rather than claims and are skipped.

    B. An ordinal in the alt or <desc> must appear as an ordinal in the drawing or in
       viz.json's facts[] — but only when the drawing uses ordinal language at all.
       Without that gate, ordinary positional prose ("the first card, the second…")
       fires on every board that happens not to number itself.

    Skipped entirely on a `data-specimen="true"` root. A contact sheet's numbers
    belong to the tiles it indexes, not to the sheet, and gating them here produced
    146 of the 146 measured false positives.

    Known gap, deliberately not built: a range is not expanded, so a description
    reading "sections 1 to 3" does not literally contain 2. No measured case drives
    it; if one appears, expand ranges here rather than loosening a clause.
    """
    # Anchored on "<svg" rather than the first ">" in the file: a leading
    # <?xml ... ?> prolog or an XML comment would otherwise end the slice before the
    # root tag, the specimen opt-out would silently stop matching, and a contact
    # sheet would start reporting every tile's chrome. No committed file here carries
    # a prolog; a third-party one easily could, and the failure is silent.
    root = svg_text.find("<svg")
    end = svg_text.find(">", root) if root != -1 else -1
    if root != -1 and SPECIMEN_ATTR.search(svg_text[root:end if end != -1 else None]):
        return []

    desc = DESC_BLOCK.search(svg_text)
    described = f"{alt} {desc.group(1) if desc else ''}".lower()
    nodes = [n.strip() for n in TEXT_NODE.findall(NOT_DRAWN.sub(" ", svg_text))]

    findings, seen = [], set()
    for node in nodes:
        if not VALUE_ONLY.match(node) or (node.startswith("0") and len(node) > 1):
            continue
        n = int(node.replace(",", ""))
        if n in seen:
            continue
        seen.add(n)
        if not any(re.search(rf"\b{re.escape(f)}\b", described)
                   for f in number_forms(n)):
            findings.append(f"the board draws {node} and neither the alt text nor "
                            "the <desc> mentions it")

    drawn_ordinals = ordinals_in(" ".join(nodes)) | ordinals_in(facts)
    if drawn_ordinals:
        spelled = sorted(ORDINAL_WORDS.get(n, str(n)) for n in drawn_ordinals)
        for n in sorted(ordinals_in(described) - drawn_ordinals):
            findings.append(
                f"a description says {ORDINAL_WORDS.get(n, n)}, but the only "
                f"ordinal(s) the board and facts[] carry are {', '.join(spelled)}")
    return findings


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


            # The descriptions must still describe the drawing. Nothing else covers
            # this: every hash is over bytes, and a re-author that updates the board
            # and forgets the alt moves src_hash without moving the falsehood.
            if asset is not None and asset.exists() \
                    and asset.suffix.lower() == ".svg":
                for finding in describe_parity(
                        asset.read_text(encoding="utf-8", errors="replace"),
                        embed_alt(block), "\n".join(facts)):
                    verdicts.append(f"MISDESCRIBED ({finding})")

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
