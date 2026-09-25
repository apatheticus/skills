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


def check(name, text, register, expect=(), reject=(), gov=False):
    """Assert which finding codes fire for one fixture."""
    global RUN
    RUN += 1
    findings, _ = v.run(text, register, gov=gov)
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

# --- government-scoped checks (--gov, Regulated or Commercial) -------------

check("a hidden verb is flagged under --gov",
      PAD + "The agency will make a determination on your application.",
      "R", expect=["gov-hidden-verb"], gov=True)

check("a hidden verb is silent without --gov",
      PAD + "The agency will make a determination on your application.",
      "R", reject=["gov-hidden-verb"])

check("a hidden verb inside a code span is not flagged",
      PAD + "Call `make a determination` on the handler.",
      "R", reject=["gov-hidden-verb"], gov=True)

check("stacked negations are flagged under --gov",
      PAD + "No application is ineligible unless the applicant has failed to file.",
      "R", expect=["gov-negation"], gov=True)

check("stacked negations are silent without --gov",
      PAD + "No application is ineligible unless the applicant has failed to file.",
      "R", reject=["gov-negation"])

check("one negation in a sentence is not flagged",
      PAD + "You must file the form before the deadline, and no fee applies.",
      "R", reject=["gov-negation"], gov=True)

check("plain government prose trips neither government check",
      PAD + "We will decide on your application and tell you the result. "
            "We review your file before we approve it.",
      "R", reject=["gov-hidden-verb", "gov-negation"], gov=True)

# --- Commercial register (reference/commercial.md) -------------------------

check("an unbounded obligation fires in Commercial",
      PAD + "Supplier will provide ongoing support as required.",
      "C", expect=["commercial-unbounded"])

check("an unbounded obligation is silent in Professional",
      PAD + "Supplier will provide ongoing support as required.",
      "P", reject=["commercial-unbounded"])

check("the client's own words in quotes are not flagged",
      PAD + 'The RFP asks for "ongoing support as required" in section 4.',
      "C", reject=["commercial-unbounded"])

check("a hedged modal fires in Commercial",
      PAD + "Supplier should deliver the accuracy report by 3 March.",
      "C", expect=["commercial-modal"])

check("a structural metaphor fires in Commercial",
      PAD + "The data-access dependency is load-bearing for the programme.",
      "C", expect=["commercial-metaphor"])

check("a journey metaphor with one word inside still fires",
      PAD + "Supplier will support your underwriting journey.",
      "C", expect=["commercial-metaphor"])

check("repeated party openers are the Commercial house pattern",
      "## Scope\n\n" + PAD + "Supplier will design the service. Supplier will build "
      "the service. Supplier will deliver the service by 3 March.",
      "C", reject=["openers"])

check("the same repeated openers still warn in Professional",
      "## Scope\n\n" + PAD + "Supplier will design the service. Supplier will build "
      "the service. Supplier will deliver the service by 3 March.",
      "P", expect=["openers"])

check("a customer journey map is a deliverable, not a metaphor",
      PAD + "Supplier will deliver a customer journey map by 3 March.",
      "C", reject=["commercial-metaphor"])

check("a significance cleft fires in Commercial",
      PAD + "This is the difference between an hour and a week of rework.",
      "C", expect=["commercial-cleft"])

check("a plain difference between two figures is not a cleft",
      PAD + "The difference between the two quotes is 3,000 dollars.",
      "C", reject=["commercial-cleft"])

check("two broad disclaimers warn",
      PAD + "Supplier does not warrant accuracy. Supplier is not responsible for hosting.",
      "C", expect=["commercial-disclaimer"])

check("one broad disclaimer is allowed",
      PAD + "Supplier does not warrant accuracy outside the test set in Table 4.",
      "C", reject=["commercial-disclaimer"])

check("two parentheticals in one sentence warn",
      PAD + "Supplier will deliver the pipeline (D4) by Sprint 3 (see section 7.2).",
      "C", expect=["commercial-parens"])

check("one parenthetical in a sentence is allowed",
      PAD + "Supplier will deliver the pipeline by the end of Sprint 3 (D4).",
      "C", reject=["commercial-parens"])

check("a footnote warns in Commercial",
      PAD + "Supplier will deliver the pipeline by Sprint 3.[^1]",
      "C", expect=["commercial-footnote"])

check("first person warns in Commercial",
      PAD + "We will deliver the pipeline to you by Sprint 3.",
      "C", expect=["commercial-person"])

check("U.S. and US are not first person",
      PAD + "Supplier will host the service in a US region under U.S. law.",
      "C", reject=["commercial-person"])

# Exactly two: the register-wide budget allows two, so only the Commercial
# one-per-section rule can fire here.
check("two dashes in one section warn in Commercial",
      "## Scope\n\n" + PAD + "A *Use Case* — a single workflow — has one test.",
      "C", expect=["dashes"])

check("the same two dashes pass in Professional",
      "## Scope\n\n" + PAD + "A *Use Case* — a single workflow — has one test.",
      "P", reject=["dashes"])

check("one appositive dash per section is allowed in Commercial",
      "## Scope\n\n" + PAD + "A *Use Case* is a single workflow — one test, one owner.",
      "C", reject=["dashes"])

check("even-length sentences are not a burstiness problem in Commercial",
      PAD + "Supplier will deliver the ingestion pipeline by Sprint 3. "
            "Client will provide the claims extract by Sprint 1. "
            "Supplier will deliver the evaluation notebook by Sprint 4. "
            "Client will name a technical owner by the kick-off date. "
            "Supplier will deliver the accuracy report by Sprint 4.",
      "C", reject=["burstiness"])

LONG = ("Supplier will deliver the trained extraction model, the evaluation "
        "notebook, the written accuracy report and the deployment runbook to "
        "Client's nominated technical owner at the Sprint 4 review meeting held "
        "at Client's London office on the date set out in the milestone table.")

check("a sentence over about 35 words warns in Commercial",
      PAD + LONG, "C", expect=["length-split"])

check("the split warning is Commercial-only",
      PAD + LONG, "P", reject=["length-split"])

check("the government checks run under Commercial with --gov",
      PAD + "Supplier will make a determination on the change request.",
      "C", expect=["gov-hidden-verb"], gov=True)

check("a journey map with a word in between is still a deliverable",
      PAD + "This customer journey map is due to Client by 3 March.",
      "C", reject=["commercial-metaphor"])

check("a curly apostrophe does not hide an unbounded obligation",
      PAD + "Supplier will revise the design to Client\u2019s satisfaction.",
      "C", expect=["commercial-unbounded"])

check("proven is a banned intensifier in Commercial",
      PAD + "Supplier brings a proven delivery method to the programme.",
      "C", expect=["commercial-intensifier"])

check("a leading provider is a banned intensifier",
      PAD + "Supplier is a leading provider of extraction services.",
      "C", expect=["commercial-intensifier"])

check("leading to is not an intensifier",
      PAD + "The delay in data access is the leading cause of rework in Phase 1.",
      "C", reject=["commercial-intensifier"])

check("a preamble's quoted defined terms are not stacked parentheticals",
      PAD + 'Brightline Analytics Ltd ("Supplier") and Northwind Mutual plc ("Client") agree as follows.',
      "C", reject=["commercial-parens"])

check("a 31-word sentence warns in Commercial",
      PAD + "Supplier will deliver the trained model, the evaluation notebook and "
            "the written accuracy report to the nominated technical owner of "
            "Client at the review meeting that closes Sprint 4 of Phase 1.",
      "C", expect=["length-split"])

check_sev("an unbounded obligation is an ERROR",
          PAD + "Supplier will provide ongoing support.", "C",
          "commercial-unbounded", "ERROR")

check_sev("first person is a WARN, because a cover note may keep it",
          PAD + "We look forward to working with Client.", "C",
          "commercial-person", "WARN")

# The --gov register guard lives in main(), so drive the CLI. A missing file makes
# an accepted combination return 1 with a PROBLEM line; a rejected one exits 2
# from argparse before the file is ever opened.
def cli_exit(argv):
    import contextlib, io
    saved = sys.argv
    sys.argv = ["voice_check.py", "/nonexistent/voice-check-fixture.md"] + argv
    try:
        with contextlib.redirect_stdout(io.StringIO()), \
             contextlib.redirect_stderr(io.StringIO()):
            return v.main()
    except SystemExit as exc:
        return exc.code
    finally:
        sys.argv = saved


RUN += 1
if cli_exit(["--register", "C", "--gov"]) != 1:
    FAILURES.append("cli: --gov must be accepted with --register C")

# A .docx is not UTF-8 text: the checker must report PROBLEM and return 1, not
# crash with a traceback.
_bin = __import__("tempfile").NamedTemporaryFile(suffix=".docx", delete=False)
_bin.write(b"PK\x03\x04\x14\x00\xff\xfe\x00binary"); _bin.close()
RUN += 1
_saved = sys.argv
sys.argv = ["voice_check.py", _bin.name, "--register", "C"]
try:
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()) as _out:
        _rc = v.main()
    if _rc != 1 or "PROBLEM" not in _out.getvalue():
        FAILURES.append("cli: a binary .docx must print PROBLEM and return 1")
except Exception as exc:  # a traceback is exactly the failure under test
    FAILURES.append(f"cli: a binary .docx raised {type(exc).__name__}")
finally:
    sys.argv = _saved

RUN += 1
if cli_exit(["--register", "P", "--gov"]) != 2:
    FAILURES.append("cli: --gov must be rejected with --register P")

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
