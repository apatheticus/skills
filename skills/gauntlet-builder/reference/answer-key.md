# answer-key — emit the floor

Turn the finished map into `.gauntlet/<slug>/ANSWER-KEY.md`.

Do not interview here. Everything in this document was already decided; you are
rewriting it into the form a critic can use.

SKILL.md holds the two check forms, the no-score rule, the reference rule, the
two-strangers test, and the not-a-spec rule. This file holds the format, the columns,
the verdict grammar, and the gates.

## The format

````markdown
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
4. **Items under "Unknown" may not be judged.** They are numbered `U1`, `U2`, and so
   on. If the work touches one, report `U<number>: CANNOT JUDGE` and stop on that item.
   Do not guess, do not infer what was probably intended, do not pass it because it
   looks reasonable. Reporting that you cannot judge something is a correct and
   expected outcome, not a failure.
5. Items under "Out of scope" must not be rewarded. Work that adds them is **worse**,
   not better, no matter how impressive it looks.
6. If a check looks arbitrary, open `MAP.md` in this same folder. It holds the
   reasoning behind every check, linked from the last column. Read the reasoning before
   deciding a check is wrong.
7. The Ceiling below is not part of the floor. Losing to it never fails the work.
8. If you built any of this work yourself, stop and say so. Judging your own output is
   not judging.

### Report your verdict exactly like this

One line per bar check, in order. Then one line for each Unknown the work touched. Then
the result. Then the ceiling. Then, only on a failure, one gap.

```
1: PASS
2: FAIL — <what was wrong, in one line>
3: PASS
U2: CANNOT JUDGE
RESULT: FAIL
CEILING: LOSS — <the largest difference against the ceiling reference>
GAP: <the single largest failing thing, specific enough to act on without asking a
     follow-up question>
```

`PASS`, `FAIL` and `CANNOT JUDGE` are the only three verdicts. Bar checks are numbered
plain (`1`, `2`); Unknown items carry their `U`. A bar check is never `CANNOT JUDGE` —
every one was written to be gradeable, so if you cannot grade one, say which and why in
a `FAIL` line rather than inventing a verdict. If you could not inspect the artifact at
all, that is `FAIL` on every check you could not reach — never a pass.

The final lines:

```
RESULT: PASS                  — every bar check passed and no Unknown was touched
RESULT: FAIL                  — any bar check failed
RESULT: BLOCKED — U2, U5      — no bar check failed, but the work touched these Unknowns
CEILING: WIN | LOSS — <gap>   — always present, never changes RESULT
GAP: <one thing>              — present only when there is something to close
```

`BLOCKED` means the work cannot be signed off until a person decides the listed items.
It is not a failure of the work, and it is not something you can resolve by looking
harder — looking harder is exactly what produces an invented answer. `BLOCKED` ends the
loop and hands back to a human; it does not mean try again, and it carries no `GAP`.

`GAP` is the one line a builder receives. It comes from the largest failing bar check
when `RESULT: FAIL`; when every bar check passed but `CEILING: LOSS`, it comes from the
ceiling instead. Everything above it is a verdict; only this line is a brief.

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
once every floor check passes.

## Out of scope

Adding any of these makes the result **worse**. Do not reward them.

1. <thing> — <why it is out>

## Unknown

**These are not gradeable.** Nobody has decided them yet. If the work touches one,
report `U<number>: CANNOT JUDGE` and stop on that item.

- **U1** — <the undecided question, stated plainly>
- **U2** — <the undecided question, stated plainly>
````

## Filling in the columns

**check** — one thing that must be true, phrased so someone can verify it without
asking a follow-up. Take it from the decision's **Check** line in the map. If a decision
produced no check, it does not go on the bar; if it produced two, it is two rows. Never
put a `|` in the cell — it ends the column and silently eats the rest of the row.

**judged by** — exactly `run it` or `A/B pick`, lower case, nothing else. If a check
fits neither, it is not finished: leave it off the bar rather than inventing a third
kind of judgment, and say which one you dropped and why.

**reference** — `—` for every `run it` row, always. For `A/B pick`, a path inside the
engagement folder (`refs/<file>`) or a live URL. It has to open without a build step:
one self-contained file, a screenshot, or a page. Anything needing a server, a database,
or the right branch checked out is a dead link by the time someone grades this, and the
linter treats a path that does not resolve as an error rather than a warning.

An A/B row is judged **blind** — whoever sets up the comparison shows both artifacts
unlabelled and asks which is better. Knowing which one is ours is enough to decide the
answer on its own.

**from decision** — a link back to that decision's section in `MAP.md`. This does real
work: a critic that can read *why* a decision was made judges better than one reading a
one-line summary, and rule 6 above sends it there whenever a check looks arbitrary. A
dead anchor is therefore worse than no link — the critic follows it, finds nothing, and
concludes the check is wrong. The linter resolves every anchor against `MAP.md`.

## Picking the ceiling

The floor is what the work must clear. The ceiling is what it is aiming at, and it is
allowed — usually preferred — to be out of reach. An unreachable ceiling supplies
direction and stops the loop settling at "pretty good."

One ceiling per engagement. It has to be a thing a critic can open, run, or view, the
same as any A/B reference — an adjective is not a ceiling. `reference/bars.md` maps
domains to bar types when nothing obvious presents itself.

The floor outranks the ceiling, always. A ceiling loss never blocks sign-off; it only
supplies the next gap once the floor is clean.

**If the work wins against the ceiling**, the ceiling was set too low. Say so and hand
back to the user to raise it. Do not treat a ceiling win as the end of the work.

## Unknown is the most important section

Everything else on the page has an equivalent somewhere. This does not.

It is a **pre-registered, enumerated list of what nobody has decided**, written before
any judging starts. A critic with no such list, handed something it cannot properly
assess, will assess it anyway — that is the whole problem. This makes not-judging an
available, legitimate, named outcome, and it is the direct defence against a critic
that passes a confident fabrication because the fabrication looked reasonable.

Fill it from two places:

- **Not yet specified** in the map — fog that never cleared.
- Any decision where the honest check was "you would only know by running it with real
  users."

Number them `U1`, `U2`, … so a verdict can name one without colliding with a bar
number. State each as a plain question. Do not soften them into things that sound
decided: "how aggressively to retry failed payments" is right; "retry behaviour to be
refined" is not — it reads like a plan and a critic will grade it.

An empty Unknown section usually means the interview stopped early or the fog got
quietly filled in with plausible answers. Say so rather than shipping a document that
claims certainty nobody has.

## Gates

Run the linter first. It owns everything mechanical, so nothing below repeats it:

```
python3 scripts/check_answer_key.py .gauntlet/<slug>/ANSWER-KEY.md
```

It resolves `--map` to `MAP.md` beside the answer key unless you point it elsewhere.
Errors exit non-zero. Report what it says rather than fixing it silently — a check that
had to be rewritten to pass the linter is a check the interview did not finish.

Then answer these four, which no script can:

1. **Could a stranger who has never seen this project check each row against a finished
   thing and get a yes or a no?** A row that describes what to build — "add a login
   page," "the schema stores a plan tier" — has drifted from answer key into spec. Cut
   it or rewrite it.
2. **Would two different people, given only this line, test it the same way and agree
   on the result?** Name the observable outcome, not the topic. "Billing works
   correctly" is a topic.
3. **Is anything on the bar there because it was easy to check rather than because it
   matters?** Padding reads as a standard and is graded as one.
4. **Does the Unknown section list everything nobody has decided**, including the
   things it would be embarrassing to admit are undecided?

Then write the file. Do not add a problem statement, a solution section, user stories,
implementation decisions, or a module list — not as a header, not as helpful context,
not "just so the critic understands." Every one of those gives a critic something to
nod along to instead of something to check.
