# ANSWER KEY — <thing>

## How to use this document

You are judging finished work against this standard. Read these rules before you judge
anything.

1. Judge **only** the checks in "The bar" below. Do not judge anything else, however
   obviously good or bad it looks.
2. Every check is binary — it passes or it fails. Never give a score, a rating, or a
   percentage. There is no partial credit.
3. Do not invent a standard. If something matters and is not on this list, that is
   deliberate — it is either out of scope or undecided, both of which are listed below.
4. **Items under "Unknown" may not be judged.** They are numbered `U1`, `U2`, and so on.
   If the work touches one, report `U<number>: CANNOT JUDGE` and stop on that item. Do
   not guess, do not infer what was probably intended, do not pass it because it looks
   reasonable. Reporting that you cannot judge something is a correct and expected
   outcome, not a failure.
5. Items under "Out of scope" must not be rewarded. Work that adds them is **worse**,
   not better, no matter how impressive it looks.
6. If a check looks arbitrary, open `MAP.md` in this same folder. It holds the reasoning
   behind every check, linked from the last column. Read the reasoning before deciding a
   check is wrong.
7. The Ceiling below is not part of the floor. Losing to it never fails the work.
8. If you built any of this work yourself, stop and say so. Judging your own output is
   not judging.

### Report your verdict exactly like this

One line per bar check, in order. Then one line for each Unknown the work touched. Then
the result, the ceiling, and — only when there is something to close — one gap.

```
1: PASS
2: FAIL — <what was wrong, in one line>
U2: CANNOT JUDGE
RESULT: FAIL
CEILING: LOSS — <the largest difference against the ceiling reference>
GAP: <the single largest failing thing, specific enough to act on without asking a follow-up question>
```

`PASS`, `FAIL` and `CANNOT JUDGE` are the only three verdicts. A bar check is never
`CANNOT JUDGE` — if you cannot grade one, say which and why in a `FAIL` line. If you
could not inspect the artifact at all, that is `FAIL` on every check you could not
reach, never a pass.

The closing lines, and when each one applies. This is a legend, not a second example —
emit one `RESULT`, one `CEILING`, and at most one `GAP`.

```
RESULT: PASS                  — every bar check passed and no Unknown was touched
RESULT: FAIL                  — any bar check failed
RESULT: BLOCKED — U2, U5      — no bar check failed, but the work touched these Unknowns
CEILING: WIN | LOSS — <gap>   — always present, never changes RESULT
GAP: <one thing>              — present only when there is something to close
```

`BLOCKED` ends the loop and hands back to a human. It is not a failure of the work, it
is not something you can resolve by looking harder, and it carries no `GAP`.

`GAP` is the one line a builder receives. It comes from the largest failing bar check on
a `FAIL`; when every bar check passed but the ceiling lost, it comes from the ceiling.
Everything above it is a verdict. Only this line is a brief.

## Destination

<one or two lines: what done looks like>

## The bar

| # | check | judged by | reference | from decision |
|---|-------|-----------|-----------|---------------|
| 1 | <what must be true, stated so it can be checked> | run it | — | [<question>](MAP.md#<anchor>) |
| 2 | <what must be true> | A/B pick | refs/<file> | [<question>](MAP.md#<anchor>) |

## Ceiling

**Reference:** <one named thing a critic can open, deliberately better than the floor>
**Reachable:** no
**Why this one:** <one sentence>

Losing to the ceiling is expected and does not fail the work. It supplies the next gap
once every floor check passes. Winning against it means the ceiling was set too low —
say so and hand back rather than declaring the work finished.

## Out of scope

Adding any of these makes the result **worse**. Do not reward them.

1. <thing> — <why it is out>

## Unknown

**These are not gradeable.** Nobody has decided them yet. If the work touches one,
report `U<number>: CANNOT JUDGE` and stop on that item.

- **U1** — <the undecided question, stated plainly>
- **U2** — <the undecided question, stated plainly>
