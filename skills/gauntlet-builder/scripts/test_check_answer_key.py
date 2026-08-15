#!/usr/bin/env python3
"""Test suite for check_answer_key.py. No fixture files on disk.

    python3 test_check_answer_key.py

Every fixture is a string assembled from a known-clean base with exactly one thing
changed, so a case that reds names the rule that broke rather than the file.

The suite was mutation-tested before being trusted. Disabling the vacuous-pass guard,
the anchor resolution, the `A/B pick` path resolution and the score-vocabulary regex
each reds a distinct case, and restoring them returns the suite to green. A suite that
passes on its first run has proved nothing.
"""

import sys

import check_answer_key as c

FAILURES = []
RUN = 0

MAP = """# MAP — a thing

## Answers

### The pricing model

**Answer:** annual only.

### Checkout layout

**Answer:** single column.
"""

REFS = {"refs/checkout.html"}
EXISTS = REFS.__contains__

ROW1 = ("| 1 | Upgrading to annual on day 10 of a 30-day month charges the annual "
        "price minus two-thirds of the monthly price already paid | run it | — | "
        "[The pricing model](MAP.md#the-pricing-model) |")
ROW2 = ("| 2 | The checkout reads as trustworthy at a glance | A/B pick | "
        "refs/checkout.html | [Checkout layout](MAP.md#checkout-layout) |")

CEILING = """## Ceiling

**Reference:** https://stripe.com/checkout
**Reachable:** no
**Why this one:** it is the page everyone in this category is measured against.
"""

OOS = """## Out of scope

1. Multi-currency — the destination is one market.
"""

UNKNOWN = """## Unknown

- **U1** — how aggressively to retry a failed payment.
"""


def key(rows=(ROW1, ROW2), ceiling=CEILING, oos=OOS, unknown=UNKNOWN, bar_head=True):
    """Assemble an answer key from parts. Everything defaults to clean."""
    bar = ""
    if bar_head:
        bar = ("## The bar\n\n"
               "| # | check | judged by | reference | from decision |\n"
               "|---|-------|-----------|-----------|---------------|\n"
               + "".join(r + "\n" for r in rows) + "\n")
    return f"# ANSWER KEY — a thing\n\n## Destination\n\nA thing.\n\n{bar}{ceiling}\n{oos}\n{unknown}"


def codes(text, map_text=MAP, exists=EXISTS):
    return {f.code for f in c.check(text, map_text, exists)}


def case(name, text, expect=(), reject=(), map_text=MAP, exists=EXISTS):
    """Assert which finding codes fire for one fixture."""
    global RUN
    RUN += 1
    got = codes(text, map_text, exists)
    for code in expect:
        if code not in got:
            FAILURES.append(f"{name}: expected {code!r}, got {sorted(got)}")
    for code in reject:
        if code in got:
            FAILURES.append(f"{name}: {code!r} should not fire, got {sorted(got)}")


ALL = ["no-bar-rows", "bad-columns", "bad-judged-by", "run-it-reference",
       "ab-no-reference", "ab-category", "ab-dead-reference", "score-vocabulary",
       "build-instruction", "no-decision-link", "no-map", "dead-anchor",
       "bar-numbering", "ceiling-missing", "out-of-scope-empty", "unknown-numbering",
       "unquantified", "row-conjunction", "unknown-empty"]

# --- the clean baseline ------------------------------------------------------
# Nothing at all may fire on a correct file. Every case below is this file with one
# thing changed, so a rule that fires here would fire on all of them.

case("clean", key(), reject=ALL)

# --- vacuous-pass guard ------------------------------------------------------

case("no bar section at all", key(bar_head=False), expect=["no-bar-rows"])
case("bar heading with no rows",
     key().replace(ROW1 + "\n", "").replace(ROW2 + "\n", ""),
     expect=["no-bar-rows"])

# --- columns -----------------------------------------------------------------

case("pipe inside a cell",
     key(rows=(ROW1.replace("day 10", "day 10 | 20"), ROW2)),
     expect=["bad-columns"])
case("five cells is fine", key(), reject=["bad-columns"])

# --- judged by ---------------------------------------------------------------

case("review is not a verdict form",
     key(rows=(ROW1.replace("| run it |", "| review |"), ROW2)),
     expect=["bad-judged-by"])
case("case matters",
     key(rows=(ROW1.replace("| run it |", "| Run It |"), ROW2)),
     expect=["bad-judged-by"])
case("both legal forms pass", key(), reject=["bad-judged-by"])

# --- run it references -------------------------------------------------------

case("a run-it row with a reference",
     key(rows=(ROW1.replace("| — |", "| refs/checkout.html |"), ROW2)),
     expect=["run-it-reference"])
case("em dash is the only legal run-it reference", key(), reject=["run-it-reference"])

# --- A/B references ----------------------------------------------------------

case("A/B with no reference",
     key(rows=(ROW1, ROW2.replace("| refs/checkout.html |", "| — |"))),
     expect=["ab-no-reference"])
case("A/B against a category",
     key(rows=(ROW1, ROW2.replace("| refs/checkout.html |", "| a professional checkout |"))),
     expect=["ab-category"])
case("A/B against a path that is not there",
     key(rows=(ROW1, ROW2.replace("refs/checkout.html", "refs/gone.html"))),
     expect=["ab-dead-reference"])
case("A/B against a URL is a note, not an error",
     key(rows=(ROW1, ROW2.replace("refs/checkout.html", "https://stripe.com/checkout"))),
     expect=["ab-url"], reject=["ab-category", "ab-dead-reference"])
case("A/B against a real file", key(), reject=["ab-dead-reference", "ab-category"])

# --- score vocabulary --------------------------------------------------------

for bad in ("Rate the checkout 1-10 for trust",
            "The reviewer scores the flow",
            "Assess whether it feels premium",
            "Judge how well the empty state reads",
            "Give it a rating out of 10"):
    case(f"score language: {bad[:24]}",
         key(rows=(ROW1, f"| 2 | {bad} | A/B pick | refs/checkout.html | "
                        "[Checkout layout](MAP.md#checkout-layout) |")),
         expect=["score-vocabulary"])

# A bare percent sign is a legitimate numeric threshold, not a score. This is the
# rule that was deliberately NOT written; the case exists so nobody adds it back.
case("a percentage threshold is not a score",
     key(rows=("| 1 | p99 latency stays under 200ms for 99% of requests at 500 "
               "concurrent users | run it | — | "
               "[The pricing model](MAP.md#the-pricing-model) |", ROW2)),
     reject=["score-vocabulary"])
case("the word rate inside a sentence about rates",
     key(rows=("| 1 | The retry rate stays under 3 attempts per invoice | run it | — | "
               "[The pricing model](MAP.md#the-pricing-model) |", ROW2)),
     reject=["score-vocabulary"])

# --- build instructions ------------------------------------------------------

for bad in ("Add a login page",
            "Implement the retry policy",
            "As a customer I want to see my balance",
            "Build an admin dashboard"):
    case(f"build instruction: {bad[:22]}",
         key(rows=(f"| 1 | {bad} | run it | — | "
                   "[The pricing model](MAP.md#the-pricing-model) |", ROW2)),
         expect=["build-instruction"])

# "Adding" is a gerund opening a real check, not a leading imperative.
case("a gerund opening is not a build instruction",
     key(rows=("| 1 | Adding a second admin leaves the owner's 4 permissions "
               "unchanged | run it | — | "
               "[The pricing model](MAP.md#the-pricing-model) |", ROW2)),
     reject=["build-instruction"])

# --- decision links ----------------------------------------------------------

case("no link at all",
     key(rows=(ROW1.replace("[The pricing model](MAP.md#the-pricing-model)", "pricing"),
               ROW2)),
     expect=["no-decision-link"])
case("a link with no anchor",
     key(rows=(ROW1.replace("MAP.md#the-pricing-model", "MAP.md"), ROW2)),
     expect=["no-decision-link"])
case("an anchor that does not resolve",
     key(rows=(ROW1.replace("#the-pricing-model", "#the-pricing-modle"), ROW2)),
     expect=["dead-anchor"])
case("no map supplied at all", key(), map_text=None, expect=["no-map"])
case("anchors resolve", key(), reject=["dead-anchor", "no-map", "no-decision-link"])

# Heading slugs drop inline markdown and punctuation, so a question written with
# emphasis or a question mark still matches its anchor.
case("slug drops markdown and punctuation",
     key(rows=(ROW1.replace("#the-pricing-model", "#how-do-we-price-it"), ROW2)),
     map_text=MAP + "\n### How do we **price** it?\n",
     reject=["dead-anchor"])

# --- numbering ---------------------------------------------------------------

case("bar rows out of order",
     key(rows=(ROW1.replace("| 1 |", "| 2 |", 1), ROW2)),
     expect=["bar-numbering"])
case("a gap in bar numbering",
     key(rows=(ROW1, ROW2.replace("| 2 |", "| 3 |", 1))),
     expect=["bar-numbering"])
case("contiguous from 1", key(), reject=["bar-numbering"])

case("a gap in unknown numbering",
     key(unknown="## Unknown\n\n- **U1** — a thing.\n- **U3** — another thing.\n"),
     expect=["unknown-numbering"])
case("unknowns contiguous",
     key(unknown="## Unknown\n\n- **U1** — a thing.\n- **U2** — another.\n"),
     reject=["unknown-numbering"])

# --- ceiling -----------------------------------------------------------------

case("no ceiling section", key(ceiling=""), expect=["ceiling-missing"])
case("ceiling with no reachable flag",
     key(ceiling="## Ceiling\n\n**Reference:** https://stripe.com/checkout\n"),
     expect=["ceiling-missing"])
case("a complete ceiling", key(), reject=["ceiling-missing"])

# --- out of scope ------------------------------------------------------------

case("no out-of-scope section", key(oos=""), expect=["out-of-scope-empty"])
case("an out-of-scope heading with nothing under it",
     key(oos="## Out of scope\n\nAdding any of these makes the result worse.\n"),
     expect=["out-of-scope-empty"])
case("a bulleted out-of-scope entry",
     key(oos="## Out of scope\n\n- Multi-currency — one market only.\n"),
     reject=["out-of-scope-empty"])

# --- unknown -----------------------------------------------------------------

case("no unknown section", key(unknown=""), expect=["unknown-empty"])
case("an unknown heading with nothing under it",
     key(unknown="## Unknown\n\nThese are not gradeable.\n"),
     expect=["unknown-empty"])
case("one unknown is enough", key(), reject=["unknown-empty"])

# --- the two advisory rules --------------------------------------------------

case("a conjunction in a check",
     key(rows=("| 1 | The invoice shows 2 line items and the total | run it | — | "
               "[The pricing model](MAP.md#the-pricing-model) |", ROW2)),
     expect=["row-conjunction"])
case("no conjunction", key(), reject=["row-conjunction"])

# The literal "no number in this row" rule was measured against 22 real check-shaped
# lines, fired on 18 of them, and every hit was a correct check. These cases pin the
# narrowed rule that replaced it: a quantity named in words rather than measured.

for vague in ("p99 latency stays under a stated target at a stated concurrency",
              "The report loads reasonably quickly on a cold cache",
              "An appropriate number of retries before the invoice is abandoned",
              "The sidebar collapses on small screens",
              "Most users reach checkout without help"):
    case(f"unquantified: {vague[:26]}",
         key(rows=(f"| 1 | {vague} | run it | — | "
                   "[The pricing model](MAP.md#the-pricing-model) |", ROW2)),
         expect=["unquantified"])

# "p99" contains a digit, which is exactly why the rule cannot be gated on `\d` --
# a metric name would read as a threshold and silence the one genuinely vague row.
case("a digit in a metric name does not excuse a stated target",
     key(rows=("| 1 | p99 latency stays under a stated target | run it | — | "
               "[The pricing model](MAP.md#the-pricing-model) |", ROW2)),
     expect=["unquantified"])

# Found by running the rule against a real answer key rather than the corpus: "at most
# 1536" is exact, and a bare \bmost\b reported it as vague.
for fine in ("`description` plus `when_to_use` measures at most 1536 characters",
             "The invoice retries at least 3 times before it is abandoned",
             "The empty state names the next action",
             "The test suite passes",
             "Every claim is traceable to a source",
             "The landing page loads in under 2 seconds on a cold cache",
             "The invoice lists every line item"):
    case(f"quantified enough: {fine[:24]}",
         key(rows=(f"| 1 | {fine} | run it | — | "
                   "[The pricing model](MAP.md#the-pricing-model) |", ROW2)),
         reject=["unquantified"])

case("a numbered check", key(), reject=["unquantified"])

# --- severity contract -------------------------------------------------------
# The advisory rules must never block, and the silent-failure rules must always block.

def sev_of(text, code, map_text=MAP, exists=EXISTS):
    hits = [f for f in c.check(text, map_text, exists) if f.code == code]
    return hits[0].sev if hits else None


for code, want, fixture in [
    ("row-conjunction", "WARN",
     key(rows=("| 1 | The invoice shows 2 line items and the total | run it | — | "
               "[The pricing model](MAP.md#the-pricing-model) |", ROW2))),
    ("unquantified", "WARN",
     key(rows=("| 1 | The report loads reasonably quickly | run it | — | "
               "[The pricing model](MAP.md#the-pricing-model) |", ROW2))),
    ("unknown-empty", "WARN", key(unknown="")),
    ("ab-url", "NOTE",
     key(rows=(ROW1, ROW2.replace("refs/checkout.html", "https://stripe.com/x")))),
    ("dead-anchor", "ERROR",
     key(rows=(ROW1.replace("#the-pricing-model", "#nope"), ROW2))),
    ("ab-dead-reference", "ERROR",
     key(rows=(ROW1, ROW2.replace("refs/checkout.html", "refs/gone.html")))),
    ("no-bar-rows", "ERROR", key(bar_head=False)),
]:
    RUN += 1
    got = sev_of(fixture, code)
    if got != want:
        FAILURES.append(f"severity: {code} should be {want}, got {got}")

# A clean file exits zero; the advisory rules alone must not change that.
RUN += 1
if any(f.sev == "ERROR" for f in c.check(key(), MAP, EXISTS)):
    FAILURES.append("exit contract: a clean answer key must produce no ERROR")

RUN += 1
advisory = key(rows=("| 1 | The empty state names the next action and says why | "
                     "run it | — | [The pricing model](MAP.md#the-pricing-model) |",
                     ROW2))
if any(f.sev == "ERROR" for f in c.check(advisory, MAP, EXISTS)):
    FAILURES.append("exit contract: WARN-only findings must not produce an ERROR")

# --- the NOTE actually counts something ---------------------------------------
# A green run that counted nothing is the shape this repo has shipped twice.

RUN += 1
note = [f for f in c.check(key(), MAP, EXISTS) if f.code == "counted"]
if not note or "2 bar row(s)" not in note[0].msg or "1 A/B" not in note[0].msg:
    FAILURES.append(f"NOTE should report what it counted, got {note and note[0].msg!r}")


if __name__ == "__main__":
    for line in FAILURES:
        print(f"FAIL  {line}")
    print(f"{RUN - len(FAILURES)}/{RUN} passed")
    sys.exit(1 if FAILURES else 0)
