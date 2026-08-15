#!/usr/bin/env python3
"""Both-polarity fixtures for svg_check.py's `diagram` class.

Every check is exercised twice: once with a violation that must be reported, and
once with the legal case that must NOT be. A gate that only ever sees red input
is a gate nobody has proved is reachable, and a gate that only ever sees green
input is a gate nobody has proved fires.

    python3 scripts/test_diagram_check.py

No dependencies, no network, no fixture files on disk — every case is a string.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from svg_check import Findings, check_file  # noqa: E402

DIAGRAMS = json.loads((Path(__file__).with_name("diagrams.json")).read_text())
STYLES = json.loads((Path(__file__).with_name("styles.json")).read_text())


def svg(body: str, kind: str = "architecture", extra: str = "", css: str = "") -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 700"
     data-loop-s="12" data-diagram="{kind}" {extra}>
<title>fixture</title>
<desc>a diagram fixture</desc>
<style>
  :root {{ --paper: #ffffff; --ink: #14181d; --muted: #4f5d75; }}
  {css}
  @media (prefers-reduced-motion: reduce) {{
    * {{ animation: none !important; }}
    .box, .tok {{ animation: none !important; }}
  }}
</style>
<rect width="1200" height="700" fill="var(--paper)"/>
{body}
</svg>'''


def node(x, y, w=152, h=80, tag="") -> str:
    return (f'<g data-node="" {tag}><rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'rx="8" fill="var(--paper)" stroke="var(--ink)"/></g>')


def run(source: str, diagrams: dict | None = DIAGRAMS) -> list[tuple[str, str, str]]:
    """Gate a fixture string and return only the diagram-class findings."""
    tmp = Path(__file__).with_name("._fixture.svg")
    tmp.write_text(source, encoding="utf-8")
    f = Findings()
    try:
        check_file(tmp, STYLES, None, {}, f, diagrams)
    finally:
        tmp.unlink(missing_ok=True)
    return [r for r in f.rows if r[0] == "ERROR"]


def no_catalog() -> None:
    """A tagged file with no catalog must fail loudly, not pass vacuously."""
    tagged = run(svg(node(40, 40)), diagrams=None)
    untagged = run(UNTAGGED, diagrams=None)
    problems = []
    if not any("not one diagram check ran" in m for _, _, m in tagged):
        problems.append("no-catalog: a data-diagram file passed with no catalog — "
                        "that is a vacuous pass")
    if untagged:
        problems.append(f"no-catalog: an untagged file errored with no catalog — "
                        f"{' | '.join(m for _, _, m in untagged)}")
    return problems


CASES: list[tuple[str, str, bool, str]] = []


def case(name: str, source: str, should_fail: bool, needle: str = "") -> None:
    CASES.append((name, source, should_fail, needle))


# --- 1. type declared --------------------------------------------------------
case("unknown type", svg(node(40, 40), kind="sankey"), True, "not a type")
case("known type", svg(node(40, 40)), False)
case("type via alias", svg(node(40, 40), kind="arch"), False)

# --- 2. budget ---------------------------------------------------------------
case("over node budget",
     svg("".join(node(40 + 160 * i, 40) for i in range(10))), True, "budget is 9")
case("at node budget",
     svg("".join(node(40 + 160 * (i % 6), 40 + 120 * (i // 6)) for i in range(9))), False)
case("over focal budget",
     svg(node(40, 40, tag='data-focal=""') + node(240, 40, tag='data-focal=""')
         + node(440, 40, tag='data-focal=""')), True, "focal")
case("at focal budget",
     svg(node(40, 40, tag='data-focal=""') + node(240, 40, tag='data-focal=""')), False)
case("per-type override — venn caps at 3",
     svg(node(40, 40) + node(240, 40) + node(440, 40) + node(640, 40), kind="venn"),
     True, "budget is 3")

# --- 3. orthogonal connectors ------------------------------------------------
case("diagonal path",
     svg(node(40, 40) + '<path data-edge="" d="M 192,80 L 400,300" fill="none"/>'),
     True, "diagonal")
case("diagonal line element",
     svg(node(40, 40) + '<line data-edge="" x1="192" y1="80" x2="400" y2="300"/>'),
     True, "diagonal")
case("orthogonal elbow",
     svg(node(40, 40)
         + '<path data-edge="" d="M 192,80 H 290 Q 300,80 300,90 V 290 Q 300,300 310,300 H 400"'
           ' fill="none"/>'),
     False)
case("axis-aligned line element",
     svg(node(40, 40) + '<line data-edge="" x1="192" y1="80" x2="400" y2="80"/>'), False)
case("bridge hop is legal",
     svg(node(40, 40) + '<path data-edge="" d="M 40,200 H 290 a 10,10 0 0,1 20,0 H 600"'
                        ' fill="none"/>'), False)
# A ring arc travels hundreds of units in both axes and is legal: an `A` is curved by
# construction and cannot render as a slant, which a bezier with collinear control
# points can. Treating them alike made `loop` unbuildable under its own gate.
case("long ring arc is legal",
     svg(node(40, 40)
         + '<path data-edge="" d="M 706,160 A 300,300 0 0,1 824,240" fill="none"/>',
         kind="loop"),
     False)
case("bezier disguising a diagonal",
     svg(node(40, 40)
         + '<path data-edge="" d="M 100,100 C 300,100 400,400 600,400" fill="none"/>'),
     True, "wearing a bezier")

# --- 4. label clip -----------------------------------------------------------
case("mask clipped by a later node",
     svg('<rect data-label="" x="300" y="60" width="80" height="22" fill="var(--paper)"/>'
         + node(340, 40)), True, "clipped by a node")
case("mask over an earlier node is fine",
     svg(node(340, 40)
         + '<rect data-label="" x="300" y="60" width="80" height="22" fill="var(--paper)"/>'),
     False)
case("badge chip fully inside a later node",
     svg('<rect data-label="" x="360" y="60" width="36" height="18" fill="var(--paper)"/>'
         + node(340, 40)), False)
case("mask over a zone is fine",
     svg('<rect data-label="" x="300" y="60" width="80" height="22" fill="var(--paper)"/>'
         + '<g data-zone=""><rect x="280" y="40" width="400" height="200" fill="none"/></g>'),
     False)

# --- 5. label gap ------------------------------------------------------------
case("mask sitting on its connector",
     svg('<path data-edge="" d="M 100,200 H 600" fill="none"/>'
         + '<rect data-label="" x="300" y="196" width="80" height="22" fill="var(--paper)"/>'),
     True, "gap floor")
case("mask 4 units off — still under the floor",
     svg('<path data-edge="" d="M 100,200 H 600" fill="none"/>'
         + '<rect data-label="" x="300" y="174" width="80" height="22" fill="var(--paper)"/>'),
     True, "gap floor")
case("mask 8 units clear",
     svg('<path data-edge="" d="M 100,200 H 600" fill="none"/>'
         + '<rect data-label="" x="300" y="170" width="80" height="22" fill="var(--paper)"/>'),
     False)

# --- 6. 4-unit grid ----------------------------------------------------------
case("node off the grid", svg(node(41, 40)), True, "off the")
case("node on the grid", svg(node(40, 40)), False)
case("odd width is off the grid", svg(node(40, 40, w=150)), True, "off the")

# --- 7. geometry is not animated ---------------------------------------------
case("keyframes moving width",
     svg(node(40, 40), css="@keyframes grow { 0% { width: 0 } 100% { width: 152px } }"),
     True, "animates width")
case("keyframes moving cx",
     svg(node(40, 40), css="@keyframes drift { 0% { cx: 10 } 100% { cx: 90 } }"),
     True, "animates cx")
case("keyframes moving opacity is fine",
     svg(node(40, 40),
         css="@keyframes pulse { 0%,100% { opacity: .4 } 50% { opacity: 1 } }"), False)
case("translate keyframe on a node",
     svg(node(40, 40, tag='class="box"'),
         css="@keyframes slide { 0%,100% { transform: translateX(0) } "
             "50% { transform: translateX(20px) } } "
             ".box { animation: slide 12s linear infinite; }"),
     True, "stays where the checker measured it")
case("translate keyframe on a free token",
     svg(node(40, 40) + '<circle class="tok" cx="100" cy="300" r="6"/>',
         css="@keyframes slide { 0%,100% { transform: translateX(0) } "
             "50% { transform: translateX(20px) } } "
             ".tok { animation: slide 12s linear infinite; }"),
     False)

# --- 8. legend placement -----------------------------------------------------
case("legend above the lowest node",
     svg(node(40, 400)
         + '<g data-legend=""><text x="40" y="300">LEGEND</text></g>'),
     True, "above the lowest node")
case("legend below every node",
     svg(node(40, 400)
         + '<g data-legend=""><text x="40" y="560">LEGEND</text></g>'), False)
# The node whose mark is not a rect. A rect-only bounding box returns None here,
# the node drops out, and the legend check skips entirely — so a legend drawn
# inside the plot area on a line, scatter or radar board gates clean.
case("legend above a circle-marked node",
     svg('<g data-node=""><circle cx="200" cy="420" r="24"/></g>'
         + '<g data-legend=""><text x="40" y="300">LEGEND</text></g>', kind="scatter"),
     True, "above the lowest node")
case("legend below a circle-marked node",
     svg('<g data-node=""><circle cx="200" cy="420" r="24"/></g>'
         + '<g data-legend=""><text x="40" y="560">LEGEND</text></g>', kind="scatter"),
     False)
case("legend above a polyline-marked node",
     svg('<g data-node=""><polyline points="100,300 200,360 300,320" fill="none"/></g>'
         + '<g data-legend=""><text x="40" y="200">LEGEND</text></g>', kind="line"),
     True, "above the lowest node")

# --- 9. the class is opt-in --------------------------------------------------
UNTAGGED = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 700" data-loop-s="12">
<title>not a diagram</title>
<desc>not a diagram</desc>
<style>:root { --paper: #ffffff; }</style>
<rect width="1200" height="700" fill="var(--paper)"/>
<line x1="10" y1="10" x2="900" y2="600" stroke="var(--paper)"/>
<rect x="41" y="41" width="150" height="63" fill="var(--paper)"/>
</svg>'''
case("untagged file is untouched by the diagram class", UNTAGGED, False)


def main() -> int:
    failures = []
    for name, source, should_fail, needle in CASES:
        errors = run(source)
        got = bool(errors)
        blob = " | ".join(m for _, _, m in errors)
        if got != should_fail:
            failures.append(
                f"{name}: expected {'an error' if should_fail else 'no error'}, "
                f"got {len(errors)} — {blob or '(none)'}")
        elif should_fail and needle and needle not in blob:
            failures.append(f"{name}: fired, but not on the expected rule "
                            f"(wanted {needle!r}) — {blob}")

    extra = no_catalog()
    failures.extend(extra)
    for line in failures:
        print(f"FAIL  {line}")
    total = len(CASES) + 2
    ok = total - len(failures)
    print(f"\n{ok}/{total} fixtures passed "
          f"({sum(1 for c in CASES if c[2]) + 1} negative, "
          f"{sum(1 for c in CASES if not c[2]) + 1} positive)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
