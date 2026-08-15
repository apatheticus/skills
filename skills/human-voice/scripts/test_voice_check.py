#!/usr/bin/env python3
"""Test suite for voice_check.py. No fixture files on disk.

    python3 test_voice_check.py

Every fixture is a string. Each case asserts that a given finding code is present
or absent for a given register, so a check that silently stops firing reds here
rather than in a real run.

The suite was mutation-tested before being trusted: disabling the code-span mask,
the quotation mask, the Tier-2b register gate and the vacuous-pass guard each
reds a distinct case, and restoring them returns the suite to green. A suite that
passes on its first run has proved nothing.
"""

import sys

import voice_check as v

FAILURES = []
RUN = 0

# Enough clean filler to clear the vacuous-pass guard's 15-word floor without
# tripping any check the fixture is not about.
PAD = ("The team met on Tuesday and agreed the schedule for the next quarter, "
       "then wrote the dates into the shared plan so nobody had to ask again. ")


def check(name, text, register, expect=(), reject=()):
    """Assert which finding codes fire for one fixture."""
    global RUN
    RUN += 1
    findings, _ = v.run(text, register)
    codes = {f.code for f in findings}
    for code in expect:
        if code not in codes:
            FAILURES.append(f"{name}: expected {code!r}, got {sorted(codes)}")
    for code in reject:
        if code in codes:
            FAILURES.append(f"{name}: {code!r} should not fire, got {sorted(codes)}")


def check_sev(name, text, register, code, sev):
    """Assert a finding's severity, not just its presence."""
    global RUN
    RUN += 1
    findings, _ = v.run(text, register)
    hit = [f for f in findings if f.code == code]
    if not hit:
        FAILURES.append(f"{name}: no {code!r} finding at all")
    elif hit[0].sev != sev:
        FAILURES.append(f"{name}: {code!r} is {hit[0].sev}, expected {sev}")


# --- carve-outs -------------------------------------------------------------
# The single most-repeated rule in the skill, and the one most easily broken.

check("tier-1 in prose fires",
      PAD + "We will utilize the new pipeline.", "P", expect=["tier-1"])

check("tier-1 inside an inline code span is not a finding",
      PAD + "Run `utilize --flag` to start.", "P", reject=["tier-1"])

check("tier-1 inside a fenced block is not a finding",
      PAD + "\n\n```bash\nutilize --delve\n```\n", "P", reject=["tier-1"])

check("tier-1 inside an unterminated fence is not a finding",
      PAD + "\n\n```\nutilize forever\n", "P", reject=["tier-1"])

check("tier-1 inside a link target is not a finding",
      PAD + "See [the guide](https://example.com/delve-deeper).", "P",
      reject=["tier-1"])

check("tier-1 inside straight quotation is not a finding",
      PAD + 'She wrote "this is a testament to the team" in the note.', "P",
      reject=["tier-1"])

check("tier-1 inside curly quotation is not a finding",
      PAD + "She wrote “this is a testament to the team” there.", "P",
      reject=["tier-1"])

check("tier-1 inside a blockquote is not a finding",
      PAD + "\n\n> We must utilize synergy across the board.\n", "P",
      reject=["tier-1"])

check("link text outside the target is still checked",
      PAD + "See [why we utilize it](https://example.com/ok).", "P",
      expect=["tier-1"])

check("an apostrophe does not swallow the document",
      PAD + "It doesn't matter. We will utilize the pipeline regardless.", "P",
      expect=["tier-1"])

# --- vocabulary tiers -------------------------------------------------------

check_sev("tier-1 is an ERROR", PAD + "A myriad of options.", "P",
          "tier-1", "ERROR")

check_sev("tier-3 phrase is an ERROR",
          PAD + "In conclusion the project is late.", "P", "tier-3", "ERROR")

check_sev("tier-2 is a QUERY, never an ERROR",
          PAD + "We built a robust reporting layer.", "P", "tier-2", "QUERY")

check("tier-2 in a code span is not even a query",
      PAD + "The `robust` flag is set.", "P", reject=["tier-2"])

check_sev("filler phrase is a WARN",
          PAD + "We met in order to agree the plan.", "P", "filler", "WARN")

# --- register gating --------------------------------------------------------
# The same word, the same sense, a different verdict.

check("'shall' is flagged in Professional",
      PAD + "The vendor shall deliver the report.", "P", expect=["tier-2b"])

check("'shall' is carried in Regulated",
      PAD + "The vendor shall deliver the report.", "R", reject=["tier-2b"])

check("'subsequently' is flagged in Editorial",
      PAD + "Subsequently the team shipped the change.", "E", expect=["tier-2b"])

check("'subsequently' is carried in Technical",
      PAD + "Subsequently the team shipped the change.", "T", reject=["tier-2b"])

check("hyphen pairs are checked in Professional",
      PAD + "The report is high-quality and the team is cross-functional.", "P",
      expect=["hyphen-pair"])

check("hyphen pairs are off in Technical",
      PAD + "The report is high-quality and the team is cross-functional.", "T",
      reject=["hyphen-pair"])

check("em dashes are budgeted in Professional",
      PAD + "One — two — three — four — five.", "P", expect=["dashes"])

check("em dashes are off in Regulated, where house style governs",
      PAD + "One — two — three — four — five.", "R", reject=["dashes"])

check("emoji are banned in Technical",
      PAD + "Ship it \U0001F680", "T", expect=["emoji"])

check("a single emoji is allowed sparingly in Editorial",
      PAD + "Ship it \U0001F680", "E", reject=["emoji"])

check("title case is checked in Professional",
      "## Strategic Negotiations And Global Partnerships\n\n" + PAD, "P",
      expect=["title-case"])

check("title case is off in Technical, where the project style guide wins",
      "## Strategic Negotiations And Global Partnerships\n\n" + PAD, "T",
      reject=["title-case"])

# --- sentence length --------------------------------------------------------

LONG = ("The agency reviews each application against the published criteria and "
        "then notifies the applicant of the outcome in writing within thirty "
        "days of the decision being recorded in the case management system. ")

check_sev("a sentence over 30 words is an ERROR in Regulated",
          PAD + LONG, "R", "length-cap", "ERROR")

check("the 30-word cap does not apply outside Regulated",
      PAD + LONG, "E", reject=["length-cap"])

check("an even cadence trips burstiness in Editorial",
      " ".join(["The team shipped the change on Tuesday afternoon."] * 6), "E",
      expect=["burstiness"])

check("Regulated has no burstiness limit",
      " ".join(["The team shipped the change on Tuesday afternoon."] * 6), "R",
      reject=["burstiness"])

# --- openers ----------------------------------------------------------------

check("a repeated sentence opener is reported",
      "## Section\n\n" + ("Teams shipped on Tuesday. " * 4), "P",
      expect=["openers"])

check("common articles are exempt from the opener check",
      "## Section\n\n" + ("The build ran green on Tuesday. " * 4), "P",
      reject=["openers"])

# --- vacuous-pass guard -----------------------------------------------------
# The hole this repo has documented three times: a check that examines nothing
# and reports zero findings reads as a pass.

check("an all-fenced document is a PROBLEM, not a clean pass",
      "```\n" + ("utilize delve synergy myriad paramount\n" * 8) + "```\n", "P",
      expect=["nothing-to-check"], reject=["tier-1"])

check("an all-quotation document is a PROBLEM",
      '"utilize the thing" ' * 12, "P", expect=["nothing-to-check"])

check("an empty document is a PROBLEM",
      "\n\n", "P", expect=["nothing-to-check"])

check("ordinary prose is not reported as unchecked",
      PAD * 2, "P", reject=["nothing-to-check"])

check("a genuinely short but checkable draft is not reported as unchecked",
      "We shipped the change on Tuesday and told the customer the same day.",
      "P", reject=["nothing-to-check"])

# --- exit-code contract -----------------------------------------------------

RUN += 1
_f, _ = v.run(PAD + "We will utilize it.", "P")
if not any(f.sev == "ERROR" for f in _f):
    FAILURES.append("exit contract: a tier-1 hit must produce an ERROR")

RUN += 1
_f, _ = v.run(PAD + "We built a robust reporting layer.", "P")
if any(f.sev == "ERROR" for f in _f):
    FAILURES.append("exit contract: a tier-2 QUERY must not produce an ERROR")

RUN += 1
_f, _ = v.run(PAD + "The report is high-quality.", "P")
if any(f.sev == "ERROR" for f in _f):
    FAILURES.append("exit contract: a style WARN must not produce an ERROR")


if __name__ == "__main__":
    for line in FAILURES:
        print(f"FAIL  {line}")
    print(f"{RUN - len(FAILURES)}/{RUN} passed")
    sys.exit(1 if FAILURES else 0)
