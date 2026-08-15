#!/usr/bin/env python3
"""Both-polarity fixtures for audit_visuals.py's description-parity check.

Every clause is exercised twice: once with a description that has drifted from the
drawing and must be reported, and once with the legal case that must NOT be. A gate
that only ever sees red input is a gate nobody has proved is reachable, and a gate
that only ever sees green input is a gate nobody has proved fires.

The last case is not a synthetic one. It reproduces the shape of the real defect —
a board drawing 9 under GATE CLASSES, captioned "the ninth is diagram", described as
"the eight classes ... the eighth being fidelity" — which shipped in this repo at
0.19.0 and passed every gate that existed at the time.

    python3 scripts/test_alt_parity.py

No dependencies, no network, no fixture files on disk — every case is a string,
which describe_parity's pure-function signature is what makes possible.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from audit_visuals import describe_parity, embed_alt  # noqa: E402


def svg(body: str, desc: str = "", root_extra: str = "") -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 520"
     data-loop-s="12" {root_extra}>
<title>fixture</title>
<desc>{desc}</desc>
<style>
  .val {{ font: 700 64px sans-serif; }}
  .cap {{ font: 400 16px sans-serif; }}
</style>
<rect width="1200" height="520" fill="var(--paper)"/>
{body}
</svg>'''


def val(text: str) -> str:
    return f'<text class="val" x="40" y="80" data-role="essential">{text}</text>'


CASES: list[tuple[str, str, str, str, bool, str]] = []


def case(name: str, source: str, alt: str, facts: str,
         should_fail: bool, needle: str = "") -> None:
    CASES.append((name, source, alt, facts, should_fail, needle))


# --- 1. a headline numeral must be described ---------------------------------
case("numeral described as a numeral", svg(val("32")), "A board reading 32 idioms.",
     "", False)
case("numeral not described at all", svg(val("32")), "A board about the catalog.",
     "", True, "draws 32")
case("numeral described in the <desc> only", svg(val("32"), desc="Thirty-two idioms."),
     "", "", False)

# --- 2. number-word equivalence ----------------------------------------------
case("numeral described as a hyphenated word", svg(val("32")),
     "The catalog holds thirty-two idioms.", "", False)
case("numeral described as a spaced word", svg(val("32")),
     "The catalog holds thirty two idioms.", "", False)
case("numeral described as the wrong word", svg(val("32")),
     "The catalog holds thirty-one idioms.", "", True, "draws 32")
case("single-digit as a word", svg(val("9")), "Nine gate classes.", "", False)
case("zero as a word", svg(val("0")), "Zero errors, always.", "", False)
# The ordinal is an accepted spelling of the cardinal: a board drawing 9 under
# GATE CLASSES is fairly described as "the ninth is diagram".
case("numeral described by its ordinal", svg(val("9")), "The ninth is diagram.",
     "", False)

# --- 3. numerals that are not claims -----------------------------------------
# 01/02/03 are step markers on a pipeline, not values. Requiring the alt to recite
# them would fire on every process board in the catalog.
case("zero-padded step markers are ignored",
     svg(val("01") + val("02") + val("03")), "Author, then gate, then commit.",
     "", False)
case("a node containing a number is not a node that IS one",
     svg('<text class="cap" x="40" y="200">SCALE 1:1 — SHEET 3 OF 7</text>'),
     "A drafted board.", "", False)
case("comma-grouped value, described with the comma",
     svg(val("1,200")), "The canvas is 1,200 units wide.", "", False)
case("comma-grouped value, described without the comma",
     svg(val("1,200")), "The canvas is 1200 units wide.", "", False)
case("comma-grouped value, undescribed", svg(val("1,200")), "A wide canvas.",
     "", True, "draws 1,200")

# --- 4. text that is never painted is not the drawing ------------------------
# The <desc> must not satisfy the check by being read as part of the board, or the
# whole check is circular: a stale description would prove itself.
case("a numeral only in <desc> is not treated as drawn",
     svg('<text class="cap" x="40" y="200">no values here</text>', desc="Seven cells."),
     "Seven cells.", "", False)
case("a numeral in <style> is not treated as drawn",
     svg('<text class="cap" x="40" y="200">label</text>'), "A labelled board.",
     "", False)

# --- 5. an ordinal in the description must be drawn --------------------------
case("ordinal contradicts the board's ordinal",
     svg(val("9") + '<text class="cap" x="40" y="200">the ninth is diagram</text>'),
     "Nine classes, the eighth being fidelity.", "", True, "says eighth")
case("ordinal agrees with the board's ordinal",
     svg(val("9") + '<text class="cap" x="40" y="200">the ninth is diagram</text>'),
     "Nine classes, the ninth being diagram.", "", False)
case("numeric ordinal form is read too",
     svg(val("9") + '<text class="cap" x="40" y="200">the ninth is diagram</text>'),
     "Nine classes, the 8th being fidelity.", "", True, "says eighth")
case("facts[] can carry the ordinal instead of the board",
     svg(val("9")), "Nine classes, the ninth being diagram.",
     "svg_check.py applies nine classes; the ninth is diagram", False)
# Without this gate, ordinary positional prose fires on every board that does not
# number itself — reflect's hero ("the first, extract … the second, cluster") was
# the measured case.
case("positional prose on a board with no ordinals does not fire",
     svg(val("3")), "Three cards. The first extracts, the second clusters, "
                    "the third reports.", "", False)

# --- 6. the specimen opt-out --------------------------------------------------
# A contact sheet's numbers belong to the tiles it indexes, not to the sheet. This
# single exclusion took the measured false positives over this repo's corpus from
# 146 to 0.
SHEET = svg(val("18,402") + val("300") + val("42") + val("7"),
            root_extra='data-specimen="true"')
case("a specimen is exempt", SHEET, "A contact sheet of thirty-two specimens.",
     "", False)
case("the same board without the specimen flag is not exempt",
     svg(val("18,402") + val("300") + val("42") + val("7")),
     "A contact sheet of thirty-two specimens.", "", True, "draws")
# Anchoring the opt-out on the first ">" in the file rather than on "<svg" would let
# a prolog hide the attribute and reopen all 146.
case("the opt-out survives an <?xml?> prolog",
     '<?xml version="1.0" encoding="UTF-8"?>\n' + SHEET,
     "A contact sheet of thirty-two specimens.", "", False)

# --- 7. the real defect -------------------------------------------------------
HERO = svg(
    '<text class="cap" x="40" y="60">STYLE CATALOG</text>' + val("32")
    + '<text class="cap" x="40" y="140">GATE CLASSES</text>' + val("9")
    + '<text class="cap" x="40" y="220">the ninth is diagram</text>'
    + '<text class="cap" x="40" y="300">LOOP</text>' + val("12"),
    desc="Two cells count what the skill carries: thirty-two catalog idioms, and "
         "the eight classes the bundled checker applies, the eighth being fidelity. "
         "The loop is twelve seconds.")
case("regression — the 0.19.0 hero as it shipped", HERO,
     "Board of eight cells. Thirty-two catalog idioms, and the eight classes the "
     "bundled checker applies, the eighth being fidelity. Twelve seconds, "
     "seam-exact.", "", True, "draws 9")
case("regression — the same hero after the fix",
     HERO.replace("the eight classes", "the nine classes")
         .replace("the eighth being fidelity", "the ninth being diagram"),
     "Board of eight cells. Thirty-two catalog idioms, and the nine classes the "
     "bundled checker applies, the ninth being diagram. Twelve seconds, "
     "seam-exact.", "", False)


def alt_extraction() -> list[str]:
    """embed_alt must survive a '>' inside the alt, and prefer the <img> arm.

    This is the documented trap that once made a correctly centered embed report
    UNCENTERED: a naive [^>]* reads "client -> server" as the end of the tag.
    """
    problems = []
    block = ('<div align="center">\n<img src="docs/assets/a.svg" '
             'alt="Flow: client -> server -> store, three hops." width="820" />\n</div>')
    got = embed_alt(block)
    if got != "Flow: client -> server -> store, three hops.":
        problems.append(f"alt-extraction: '>' inside alt truncated it — got {got!r}")
    if embed_alt("![a plain markdown image](docs/assets/a.svg)") \
            != "a plain markdown image":
        problems.append("alt-extraction: markdown alt not read")
    if embed_alt("<div align=\"center\"><img src=\"a.svg\" /></div>") != "":
        problems.append("alt-extraction: a missing alt should be '', not a match")
    return problems


def main() -> int:
    failures = []
    for name, source, alt, facts, should_fail, needle in CASES:
        findings = describe_parity(source, alt, facts)
        got = bool(findings)
        blob = " | ".join(findings)
        if got != should_fail:
            failures.append(
                f"{name}: expected {'a finding' if should_fail else 'no finding'}, "
                f"got {len(findings)} — {blob or '(none)'}")
        elif should_fail and needle and needle not in blob:
            failures.append(f"{name}: fired, but not on the expected clause "
                            f"(wanted {needle!r}) — {blob}")

    extra = alt_extraction()
    failures.extend(extra)
    for line in failures:
        print(f"FAIL  {line}")
    total = len(CASES) + 3
    ok = total - len(failures)
    print(f"\n{ok}/{total} fixtures passed "
          f"({sum(1 for c in CASES if c[4])} negative, "
          f"{sum(1 for c in CASES if not c[4]) + 3} positive)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
