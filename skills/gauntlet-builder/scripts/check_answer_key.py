#!/usr/bin/env python3
r"""Lint an ANSWER-KEY.md against the format reference/answer-key.md prescribes.

    python3 check_answer_key.py .gauntlet/<slug>/ANSWER-KEY.md [--map PATH]

Reports, never rewrites. ERROR exits non-zero; WARN and NOTE do not.

Why this exists rather than a checklist in prose: every rule below is mechanically
checkable AND easy to skip silently under context pressure, which is the exact test
for pushing a requirement out of a sentence and into a script. Two of them fail
*quietly* in a way no reader would catch -- a `from decision` anchor that no longer
resolves, and an `A/B pick` reference that is not a real file. In both cases the
document still reads correctly; the failure only surfaces weeks later, when a critic
follows the link, finds nothing, and concludes the check itself is wrong.

Three deliberate non-rules, recorded so a later run does not "fix" them back in:

  * A bare `%` is NOT score vocabulary. "p99 under 200ms for 99% of requests" is a
    legitimate numeric threshold, and banning the character would red more correct
    checks than incorrect ones. Only unambiguous score language is matched.
  * "and" in a check cell is a WARN, not an ERROR. Measured against 22 check-shaped
    lines taken from the source material -- none of them written with this rule in
    mind -- it fires 6 times, of which 4 are genuine two-things-in-one-row and 2 are
    "Black and Decker" and "terms and conditions". A third of its hits are wrong, so
    it advises rather than blocks.
  * "This row has no number in it" was measured and DROPPED. On the same corpus it
    fired on 18 of 22 lines, every one of them a correct check -- a warning that
    reds four rows in five is noise, and noise trains people to skip the output. What
    replaced it fires on the vagueness the number rule was really aiming at ("under a
    stated target", "reasonably quickly", "an appropriate number of retries"): 7 hits
    in 25 lines, no false positives, nothing missed. Note the trap that killed the
    obvious version -- "p99 latency under a stated target" CONTAINS a digit, so any
    rule gated on `\d` reads a metric name as a threshold and stays silent on the one
    line that is actually unquantified.

The vacuous-pass guard matters as much as any rule: a file whose bar table did not
parse would otherwise satisfy every check trivially and print zero errors.
"""

import argparse
import pathlib
import re
import sys
from dataclasses import dataclass

JUDGED_BY = ("run it", "A/B pick")
DASH = "—"

# Unambiguous score language only. See the docstring on why `%` is absent.
SCORE_RE = re.compile(
    r"\bscor(?:e|es|ed|ing)\b"
    r"|\brating\b"
    r"|\brate (?:it|the|this|each|how)\b"
    r"|\b1\s*(?:-|–|—|to)\s*(?:5|10)\b"
    r"|\bout of (?:5|10|ten)\b"
    r"|\bassess whether\b"
    r"|\bhow well\b"
    r"|\bpartial credit\b",
    re.I,
)

# A check that tells someone what to build rather than how to check it. Only the two
# forms that cannot be read any other way -- a leading bare imperative, and a user
# story. Softer signals are left to the human gates in reference/answer-key.md, because
# a regex for them reds correct checks.
BUILD_RE = re.compile(
    r"^\s*(?:add|create|implement|build|write|refactor|migrate|install|support|"
    r"set up|make)\s+(?:a|an|the)\s"
    r"|^\s*as an?\b.*\bi want\b",
    re.I,
)

# A quantity named in words instead of measured. This is what the "put a number in it"
# rule was actually reaching for; see the docstring for why the literal version was
# measured and thrown away.
# `at most 1536` and `at least 3` are exact, so `most` needs the lookbehind. That one
# was not in the measurement corpus and only surfaced when the rule was run against a
# real answer key -- which is the argument for the self-run step over a bigger corpus.
VAGUE_RE = re.compile(
    r"\b(?:a stated|some|several|a few|many|(?<!at )most|quick(?:ly)?|fast|slow(?:ly)?"
    r"|soon|large|small|big|enough|reasonabl[ey]|appropriate(?:ly)?|sufficient(?:ly)?"
    r"|adequate(?:ly)?|acceptable|minimal|significant|multiple|various|numerous)\b",
    re.I,
)

URL_RE = re.compile(r"^https?://\S+$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*#*$")


@dataclass
class Finding:
    sev: str
    code: str
    line: int
    msg: str


def slugify(heading: str) -> str:
    """GitHub's anchor slug for a heading -- lowercase, punctuation dropped, spaces
    hyphenated. Inline markdown is stripped first so `### **Q1** foo` matches."""
    text = re.sub(r"`([^`]*)`", r"\1", heading)
    text = re.sub(r"\*\*?([^*]*)\*\*?", r"\1", text)
    text = LINK_RE.sub(lambda m: m.group(0).split("]")[0][1:], text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", "-", text)


def sections(text):
    """Map each `## ` heading to (start_line, [body lines]). 1-indexed lines."""
    out, current, body, start = {}, None, [], 0
    for i, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            if current is not None:
                out[current] = (start, body)
            current, body, start = line[3:].strip(), [], i
        elif current is not None:
            body.append((i, line))
    if current is not None:
        out[current] = (start, body)
    return out


def table_rows(body):
    """Pipe-table data rows as (line_no, [cells]). Header and separator dropped."""
    rows = []
    for lineno, line in body:
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            continue
        if [c.lower() for c in cells[:3]] == ["#", "check", "judged by"]:
            continue
        rows.append((lineno, cells))
    return rows


def check(key_text, map_text=None, exists=lambda p: False):
    """Lint an answer key. Pure function on strings.

    map_text  -- MAP.md's contents, or None when there is no MAP.md to resolve against.
    exists    -- callable(relative_path) -> bool, used for `A/B pick` references.
    """
    f = []
    add = lambda sev, code, line, msg: f.append(Finding(sev, code, line, msg))
    secs = sections(key_text)

    # --- the bar -------------------------------------------------------------
    bar = secs.get("The bar")
    rows = table_rows(bar[1]) if bar else []

    if not rows:
        # Vacuous-pass guard. Without it a file whose table failed to parse -- a
        # renamed heading, a wrapped row, a stray fence -- satisfies every rule below
        # by having nothing to test, and prints a clean bill of health.
        add("ERROR", "no-bar-rows", bar[0] if bar else 1,
            "no bar rows parsed under a `## The bar` heading, so every check below "
            "would pass by having nothing to look at")

    anchors = set()
    if map_text is not None:
        for line in map_text.splitlines():
            m = HEADING_RE.match(line)
            if m:
                anchors.add(slugify(m.group(1)))

    numbers = []
    for lineno, cells in rows:
        if len(cells) != 5:
            add("ERROR", "bad-columns", lineno,
                f"row has {len(cells)} cells, expected 5 — a `|` inside a cell ends "
                "the column and silently eats the rest of the row")
            continue
        num, chk, judged, ref, decision = cells

        numbers.append((lineno, num))

        if judged not in JUDGED_BY:
            add("ERROR", "bad-judged-by", lineno,
                f"`judged by` is {judged!r}; the only legal values are "
                f"{JUDGED_BY[0]!r} and {JUDGED_BY[1]!r}")
        elif judged == "run it":
            if ref != DASH:
                add("ERROR", "run-it-reference", lineno,
                    f"a `run it` row carries reference {ref!r}; it must be {DASH!r}, "
                    "because a right answer beats an example")
            m = VAGUE_RE.search(chk)
            if m:
                add("WARN", "unquantified", lineno,
                    f"{m.group(0)!r} names a quantity instead of measuring one — two "
                    "people will read it differently, which is the disagreement a "
                    "number is the cheapest way to prevent")
        else:  # A/B pick
            if ref in (DASH, ""):
                add("ERROR", "ab-no-reference", lineno,
                    "an `A/B pick` row needs a named, fetchable reference; without one "
                    "the critic invents the standard, which is the failure this "
                    "document exists to prevent")
            elif URL_RE.match(ref):
                add("NOTE", "ab-url", lineno,
                    f"reference is a URL and was not fetched — confirm {ref} still "
                    "opens before a long run starts")
            elif "/" not in ref and "." not in ref:
                add("ERROR", "ab-category", lineno,
                    f"reference {ref!r} is a category, not a thing. A critic cannot "
                    "open it, so it will imagine one")
            elif not exists(ref):
                add("ERROR", "ab-dead-reference", lineno,
                    f"reference {ref!r} does not resolve to a file. A reference that "
                    "cannot be opened is a dead link by the time someone grades this")

        if SCORE_RE.search(chk):
            add("ERROR", "score-vocabulary", lineno,
                "score language on the bar — every check is binary, and a third "
                "verdict is what lets a critic pass work it is unsure about")

        if BUILD_RE.search(chk):
            add("ERROR", "build-instruction", lineno,
                "this row says what to build rather than how to check it, which is "
                "the drift from answer key into spec")

        if re.search(r"\band\b", chk, re.I):
            add("WARN", "row-conjunction", lineno,
                "\"and\" in the check — a row with two things in it can half-pass, "
                "and half-pass is the score the format bans")

        links = LINK_RE.findall(decision)
        if not links:
            add("ERROR", "no-decision-link", lineno,
                "no link back to the decision in MAP.md — rule 6 sends a critic there "
                "whenever a check looks arbitrary, and there is nowhere to go")
            continue
        for target in links:
            if "#" not in target:
                add("ERROR", "no-decision-link", lineno,
                    f"link {target!r} has no `#anchor`, so it lands on the top of the "
                    "map rather than on the reasoning")
                continue
            path, _, anchor = target.partition("#")
            if map_text is None:
                add("ERROR", "no-map", lineno,
                    f"this row links to {path or 'MAP.md'} and no map was supplied, so "
                    "the anchor could not be resolved — checking it is the whole point")
            elif anchor not in anchors:
                add("ERROR", "dead-anchor", lineno,
                    f"`#{anchor}` does not resolve to a heading in the map. A critic "
                    "told to read the reasoning finds nothing and concludes the check "
                    "is wrong")

    # --- numbering -----------------------------------------------------------
    for i, (lineno, num) in enumerate(numbers, 1):
        if num != str(i):
            add("ERROR", "bar-numbering", lineno,
                f"row is numbered {num!r} where {i} was expected — a verdict line can "
                "name a row that does not exist, or miss one that does")
            break

    # --- ceiling -------------------------------------------------------------
    ceiling = secs.get("Ceiling")
    if not ceiling:
        add("ERROR", "ceiling-missing", 1,
            "no `## Ceiling` section. Without one the loop settles at the floor, which "
            "is the level the work must clear rather than the level it is aiming at")
    else:
        body = "\n".join(l for _, l in ceiling[1])
        for field in ("Reference:", "Reachable:"):
            if field not in body:
                add("ERROR", "ceiling-missing", ceiling[0],
                    f"the Ceiling section has no `{field}` line")

    # --- out of scope --------------------------------------------------------
    oos = secs.get("Out of scope")
    if not oos or not any(re.match(r"\s*(?:[-*]|\d+\.)\s+\S", l) for _, l in oos[1]):
        add("ERROR", "out-of-scope-empty", oos[0] if oos else 1,
            "Out of scope is empty, so the destination was never scoped and nothing "
            "stops a critic rewarding work that made the result worse")

    # --- unknown -------------------------------------------------------------
    unk = secs.get("Unknown")
    u_nums = []
    if unk:
        for lineno, line in unk[1]:
            m = re.match(r"\s*[-*]\s+\**U(\d+)\**", line)
            if m:
                u_nums.append((lineno, int(m.group(1))))
    if not u_nums:
        add("WARN", "unknown-empty", unk[0] if unk else 1,
            "Unknown is empty. That usually means the interview stopped early or the "
            "fog got filled in with plausible answers — say so out loud rather than "
            "shipping a document that claims certainty nobody has")
    for i, (lineno, n) in enumerate(u_nums, 1):
        if n != i:
            add("ERROR", "unknown-numbering", lineno,
                f"Unknown is numbered U{n} where U{i} was expected — a "
                "`RESULT: BLOCKED` line names these, so a gap in them names nothing")
            break

    note = (f"{len(rows)} bar row(s), {len(u_nums)} unknown(s), "
            f"{sum(1 for _, c in rows if len(c) == 5 and c[2] == 'A/B pick')} A/B, "
            f"{len(anchors)} map anchor(s) resolvable")
    f.insert(0, Finding("NOTE", "counted", 0, note))
    return f


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("answer_key")
    ap.add_argument("--map", dest="map_path", default=None,
                    help="MAP.md to resolve `from decision` anchors against "
                         "(default: MAP.md beside the answer key)")
    args = ap.parse_args()

    key = pathlib.Path(args.answer_key)
    if not key.is_file():
        print(f"ERROR  not-a-file  {key}: no such file")
        return 1

    map_path = pathlib.Path(args.map_path) if args.map_path else key.parent / "MAP.md"
    map_text = map_path.read_text(encoding="utf-8") if map_path.is_file() else None

    findings = check(
        key.read_text(encoding="utf-8"),
        map_text,
        exists=lambda p: (key.parent / p).is_file(),
    )

    for f in findings:
        where = f"{key}:{f.line}" if f.line else str(key)
        print(f"{f.sev:<5}  {f.code:<19}  {where}  {f.msg}")

    counts = {s: sum(1 for f in findings if f.sev == s) for s in ("ERROR", "WARN")}
    print(f"{counts['ERROR']} error(s), {counts['WARN']} warning(s)")
    return 1 if counts["ERROR"] else 0


if __name__ == "__main__":
    sys.exit(main())
