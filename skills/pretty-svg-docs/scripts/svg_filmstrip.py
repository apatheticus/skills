#!/usr/bin/env python3
"""Build a scrub harness for an animated SVG so one screenshot shows every phase.

Writes .prettydocs/src/<name>/_qa/filmstrip.html: N inline copies of the SVG, each
frozen at a different point in the loop via `animation-play-state: paused` plus a
negative `animation-delay`, labelled with its timestamp. The wrap-around copy
repeats phase 0 so the seam is visible side by side.

The harness is gitignored and never committed, which is why it may use the
<script> a committed asset may not — SMIL copies can only be posed by calling
setCurrentTime() on the document.

Usage:
    svg_filmstrip.py FILE.svg [--phases 6] [--out DIR] [--width 560]

Then serve it over HTTP and screenshot it — never open it as a file:// URL:
    python3 -m http.server 8765 --directory <out-dir>
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"


def default_out(src: Path, name: Path | str) -> Path:
    """Where the harness goes when --out is not given.

    The asset lives at <project>/docs/assets/<name>.svg, so the project root is two
    levels up and the harness belongs in <project>/.prettydocs/src/<name>/_qa — the
    one path <project>/.prettydocs/.gitignore's `src/**/_qa/` rule covers. This used
    to default to <project>/docs/assets/src/<name>/_qa, the pre-0.10.0 layout, which
    no .gitignore anywhere matches: every run silently produced a 50 KB harness
    staged for commit, in a directory the migration had already retired.

    A project still carrying the old layout keeps it, so a run there stays gitignored
    by whatever rule it already has.
    """
    project = src.parent.parent.parent
    legacy = src.parent / "src"
    if legacy.is_dir() and not (project / ".prettydocs").is_dir():
        return legacy / name / "_qa"
    return project / ".prettydocs" / "src" / name / "_qa"

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>filmstrip — {name}</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ margin: 0; padding: 24px; background: #7a7a7a;
         font: 14px/1.4 ui-monospace, SFMono-Regular, Menlo, monospace; }}
  h1 {{ font-size: 15px; font-weight: 700; color: #fff; margin: 0 0 4px; }}
  p.meta {{ color: #eee; margin: 0 0 20px; }}
  .strip {{ display: grid; grid-template-columns: repeat(auto-fill, minmax({width}px, 1fr));
            gap: 20px; }}
  figure {{ margin: 0; background: #fff; border: 1px solid #444; }}
  figcaption {{ padding: 6px 10px; background: #1c1c1c; color: #fff;
                display: flex; justify-content: space-between; }}
  figcaption b {{ font-weight: 700; }}
  .frame svg {{ display: block; width: 100%; height: auto; }}
  /* freeze every copy; each copy's own rule sets its phase */
  .frame svg * {{ animation-play-state: paused !important; }}
{phase_css}
</style>
</head>
<body>
<h1>{name} — {phases} phases of a {loop:g}s loop</h1>
<p class="meta">phase 0 and the wrap-around copy must be identical; that is the seam.
Scan every copy for clipped text, collisions, occlusion and fallback fonts.</p>
<div class="strip">
{figures}
</div>
<script>
// SMIL cannot be posed with CSS. Pause each copy's own timeline and seek it.
document.querySelectorAll('.frame > svg').forEach(function (svg) {{
  var t = parseFloat(svg.getAttribute('data-phase-t') || '0');
  if (typeof svg.pauseAnimations === 'function') {{
    svg.setCurrentTime(t);
    svg.pauseAnimations();
  }}
}});
</script>
</body>
</html>
"""


def inner_svg(raw: str) -> tuple[str, float, str]:
    """Return (svg-with-scoped-ids, loop seconds, root attribute string).

    Stdlib xml.etree is vulnerable to entity-expansion attacks, and this harness
    also inlines the file straight into an HTML page. A committed SVG asset has no
    legitimate DTD, so refuse one outright rather than parse it (svg_check.py makes
    the same refusal an explicit gate).
    """
    if re.search(r"<!(DOCTYPE|ENTITY)\b", raw, re.I):
        sys.exit("error: the SVG declares a DOCTYPE or ENTITY — strip it "
                 "(see svg_check.py; a committed asset needs no DTD)")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        sys.exit(f"error: {e}")
    loop = root.get("data-loop-s", "0")
    try:
        loop_s = float(re.sub(r"[^\d.]", "", loop) or 0)
    except ValueError:
        loop_s = 0.0
    return raw, loop_s, ""


def scope_ids(svg: str, suffix: str) -> str:
    """Make ids unique per copy so N inlined SVGs don't collide on url(#…)."""
    ids = set(re.findall(r'\bid="([^"]+)"', svg))
    for name in sorted(ids, key=len, reverse=True):
        new = f"{name}__{suffix}"
        svg = re.sub(rf'\bid="{re.escape(name)}"', f'id="{new}"', svg)
        svg = svg.replace(f"url(#{name})", f"url(#{new})")
        svg = re.sub(rf'href="#{re.escape(name)}"', f'href="#{new}"', svg)
    return svg


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file")
    ap.add_argument("--phases", type=int, default=6, help="phases to pose (default 6)")
    ap.add_argument("--out", help="output dir (default .prettydocs/src/<name>/_qa)")
    ap.add_argument("--width", type=int, default=560, help="min tile width in px")
    args = ap.parse_args()

    src = Path(args.file)
    if not src.exists():
        sys.exit(f"error: {src} not found")
    name = src.stem
    raw = src.read_text(encoding="utf-8")
    _, loop, _ = inner_svg(raw)

    if loop <= 0:
        print(f"note: {src} declares data-loop-s=0 (static) — one copy, no phases")
        phases = 1
    else:
        phases = max(2, args.phases)

    out_dir = Path(args.out) if args.out else default_out(src, name)
    out_dir.mkdir(parents=True, exist_ok=True)

    figures: list[str] = []
    phase_css: list[str] = []
    # one extra copy at t=D, which must look identical to t=0
    count = phases + 1 if loop > 0 else 1
    for i in range(count):
        t = 0.0 if loop <= 0 else (loop * i / phases)
        cid = f"p{i}"
        copy = scope_ids(raw, cid)
        # inject the seek target the inline script reads
        copy = re.sub(r"<svg\b", f'<svg data-phase-t="{t:g}"', copy, count=1)
        phase_css.append(
            f"  #{cid} svg * {{ animation-delay: -{t:g}s !important; }}"
        )
        seam = " · wrap-around, must equal phase 0" if loop > 0 and i == phases else ""
        figures.append(
            f'<figure><div class="frame" id="{cid}">{copy}</div>'
            f"<figcaption><b>phase {i}</b>"
            f"<span>t = {t:g}s{html.escape(seam)}</span></figcaption></figure>"
        )

    page = PAGE.format(
        name=html.escape(name),
        phases=phases,
        loop=loop,
        width=args.width,
        phase_css="\n".join(phase_css),
        figures="\n".join(figures),
    )
    target = out_dir / "filmstrip.html"
    target.write_text(page, encoding="utf-8")

    print(f"wrote {target}")
    print(f"serve it:  python3 -m http.server 8765 --directory {out_dir}")
    print("then open: http://localhost:8765/filmstrip.html   (never a file:// URL)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
