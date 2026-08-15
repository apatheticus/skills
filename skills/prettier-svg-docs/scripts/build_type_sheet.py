#!/usr/bin/env python3
"""Compose the type contact sheet from the 27 type specimens.

Each tile is that type's OWN specimen scaled down, never a redrawing. That is the
same rule the style contact sheet follows, and it is what makes the sheet unable to
drift from the catalog it indexes: there is one drawing of each type in the repo.

The one hard problem is collision. Twenty-seven files, each with its own `<style>`
block, class names, ids and `url(#...)` references, land in one document; without
namespacing, tile 3's `.name` silently restyles tile 19. So every class and id is
rewritten with a per-tile prefix, in the CSS and in the markup, and every reference
form that can point at an id is rewritten with it.

Tokens are NOT namespaced: all 27 specimens resolve to `flat-material` against one
palette, so their `:root` blocks are identical by construction. The script asserts
that rather than assuming it.

    python3 scripts/build_type_sheet.py            # writes docs/assets/types.svg
    python3 scripts/build_type_sheet.py --check     # report only, write nothing

No dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
SPECIMENS = PROJECT / "docs/samples/types"
OUT = PROJECT / "docs/assets/types.svg"

COL_X = (40, 610)          # left edge of each column, matching the style sheet
TILE_W = 550
SCALE = TILE_W / 1200
HEAD_H = 172               # title block above the first row
SLUG_H = 44                # room under a tile for its slug
ROW_GAP = 24
LOOP_S = 12

# Every attribute whose value can name an id, and the shape of that reference.
ID_REF_ATTRS = ("clip-path", "filter", "mask", "fill", "stroke",
                "marker-start", "marker-mid", "marker-end")


def read_specimen(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    m = re.search(r'viewBox\s*=\s*"([^"]+)"', raw)
    if not m:
        raise SystemExit(f"{path}: no viewBox")
    vb = [float(v) for v in m.group(1).split()]
    styles = re.findall(r"<style[^>]*>(.*?)</style>", raw, re.S)
    # Body = everything inside the root, minus title/desc/style.
    body = raw[raw.index(">", raw.index("<svg")) + 1: raw.rindex("</svg>")]
    for tag in ("title", "desc", "style"):
        body = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", "", body, flags=re.S)
    return {"slug": path.stem, "vb": vb, "css": "\n".join(styles), "body": body}


def namespace(spec: dict, prefix: str) -> dict:
    """Rewrite every class and id in one specimen so it cannot touch another."""
    css, body = spec["css"], spec["body"]

    ids = set(re.findall(r'\bid="([^"]+)"', body)) | set(re.findall(r'\bid="([^"]+)"', css))
    classes = set()
    for attr in re.findall(r'\bclass="([^"]+)"', body):
        classes.update(attr.split())
    classes.update(re.findall(r"\.([A-Za-z_][\w-]*)", css))

    def sub_classes(text: str, in_css: bool) -> str:
        for c in sorted(classes, key=len, reverse=True):
            if in_css:
                text = re.sub(rf"\.{re.escape(c)}\b", f".{prefix}{c}", text)
            else:
                text = re.sub(rf'(\bclass="[^"]*?)\b{re.escape(c)}\b',
                              rf"\1{prefix}{c}", text)
        return text

    def sub_ids(text: str) -> str:
        for i in sorted(ids, key=len, reverse=True):
            text = re.sub(rf'(\bid=")({re.escape(i)})(")', rf"\1{prefix}\2\3", text)
            text = re.sub(rf"url\(#{re.escape(i)}\)", f"url(#{prefix}{i})", text)
            text = re.sub(rf'((?:xlink:)?href=")#{re.escape(i)}(")',
                          rf"\1#{prefix}{i}\2", text)
            text = re.sub(rf"(#{re.escape(i)})\b(?=[\"'\)])", f"#{prefix}{i}", text)
        return text

    # Keyframe names are global too.
    kf = set(re.findall(r"@keyframes\s+([\w-]+)", css))
    for name in sorted(kf, key=len, reverse=True):
        css = re.sub(rf"(@keyframes\s+){re.escape(name)}\b", rf"\1{prefix}{name}", css)
        css = re.sub(rf"(animation(?:-name)?\s*:[^;}}]*?)\b{re.escape(name)}\b",
                     rf"\1{prefix}{name}", css)

    spec = dict(spec)
    spec["css"] = sub_ids(sub_classes(css, in_css=True))
    spec["body"] = sub_ids(sub_classes(body, in_css=False))
    return spec


def root_block(css: str) -> str:
    m = re.search(r":root\s*\{(.*?)\}", css, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    args = ap.parse_args()

    catalog = json.loads((HERE / "diagrams.json").read_text())
    slugs = sorted(catalog["types"])
    paths = [SPECIMENS / f"{s}.svg" for s in slugs]
    missing = [p.name for p in paths if not p.exists()]
    if missing:
        print(f"ERROR  {len(missing)} specimen(s) missing: {', '.join(missing)}",
              file=sys.stderr)
        return 2

    specs = [read_specimen(p) for p in paths]

    # The palettes must be identical, or one tile silently restyles the sheet.
    roots = {root_block(s["css"]) for s in specs}
    if len(roots) > 1:
        print(f"ERROR  the {len(specs)} specimens declare {len(roots)} different "
              ":root blocks — they are supposed to share one palette. Tokens are "
              "not namespaced, so this would cross-contaminate.", file=sys.stderr)
        return 2
    shared_root = roots.pop()

    specs = [namespace(s, f"t{i}-") for i, s in enumerate(specs)]

    # Lay out two to a row; row height is the taller of the pair.
    rows, y = [], HEAD_H
    for i in range(0, len(specs), 2):
        pair = specs[i:i + 2]
        h = max(s["vb"][3] * SCALE for s in pair)
        rows.append((y, pair, h))
        y += h + SLUG_H + ROW_GAP
    total_h = int(y + 24)

    defs, cells = [], []
    for row_y, pair, row_h in rows:
        for col, s in enumerate(pair):
            x = COL_X[col]
            w = s["vb"][2] * SCALE
            h = s["vb"][3] * SCALE
            defs.append(
                f'<clipPath id="clip-{s["slug"]}">'
                f'<rect x="{x}" y="{row_y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="10"/>'
                f"</clipPath>")
            cells.append(
                f'<g clip-path="url(#clip-{s["slug"]})" style="isolation:isolate">\n'
                f'  <g transform="translate({x},{row_y:.0f}) scale({SCALE:.5f})">\n'
                f'{s["body"].strip()}\n'
                f"  </g>\n"
                f"</g>\n"
                f'<rect x="{x}" y="{row_y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="10" '
                f'fill="none" stroke="var(--dim)" stroke-opacity="0.35" stroke-width="1"/>\n'
                f'<text class="sh-slug" x="{x}" y="{row_y + h + 28:.0f}" '
                f'data-role="metadata" data-bg="background">{s["slug"]}</text>')

    css = "\n".join(s["css"] for s in specs)
    out = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" \
viewBox="0 0 1200 {total_h}" width="1200" height="{total_h}" role="img" \
data-loop-s="{LOOP_S}" data-bg="background" data-specimen="true">
<title>The prettier-svg-docs diagram-type catalog — {len(specs)} types</title>
<desc>A contact sheet of {len(specs)} animated diagram-type specimens in alphabetical \
order, two to a row. Every cell is that type's own full-width specimen scaled down, so \
each carries its real layout, connector routing and label geometry rather than a \
flattened imitation. All are drawn in the flat-material style, so the variable across \
the sheet is the type and nothing else.</desc>
<defs>
{chr(10).join(defs)}
</defs>
<style>
:root {{ {shared_root} }}
.sh-title  {{ font: 600 40px ui-sans-serif, -apple-system, "Segoe UI", Helvetica, sans-serif; fill: var(--ink); }}
.sh-sub    {{ font: 400 20px ui-sans-serif, -apple-system, "Segoe UI", Helvetica, sans-serif; fill: var(--dim); }}
.sh-slug   {{ font: 600 19px ui-monospace, Menlo, monospace; fill: var(--accent-primary); letter-spacing: 1px; }}
{css}
</style>
<rect width="1200" height="{total_h}" fill="var(--background)"/>
<text class="sh-title" x="40" y="76" data-role="title" data-bg="background">Diagram types</text>
<text class="sh-sub" x="40" y="116" data-role="essential" data-bg="background">\
{len(specs)} layout grammars, one style — the type is the variable</text>
{chr(10).join(cells)}
</svg>
'''

    print(f"{len(specs)} tiles, {len(rows)} rows, {total_h} units tall, "
          f"{len(out):,} bytes")
    if args.check:
        return 0
    OUT.write_text(out, encoding="utf-8")
    print(f"wrote {OUT.relative_to(PROJECT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
