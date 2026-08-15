---
name: gauntlet-builder
description: Build a Gauntlet Loop for a piece of work — the bar it gets judged against, the blind-critic contract, and the runnable aim prompt. Interviews you one question at a time, turns every answer into a binary check, and emits an answer key a fresh critic can open. Use it for a gauntlet loop, aim prompt, blind critic, builder-critic loop, adversarial acceptance, loop engineering, or a one-prompt build — or any time you want an agent to keep improving something against a real bar rather than its own private opinion of good.
when_to_use: Also use it before building anything where the shape is not settled yet — what am I actually building, how would I know if this came out wrong, what does done mean here, write acceptance criteria, set the bar, scope this properly. It runs the interview that produces those answers, records what nobody has decided as explicitly ungradeable, and stops before implementation, because building is a separate session. Also use it to lint an existing answer key, to resume a half-finished engagement under .gauntlet/, or to turn a plan file or spec you already have into a bar and a loop prompt instead of starting the interview from scratch.
license: MIT
version: 1.0.0
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion, Task
---

# gauntlet-builder

An idea has arrived and the way from here to the finished thing is not visible yet.
This skill finds that way by naming where you are going, laying out the questions
standing between here and there, working them one at a time — and turning the result
into a loop that keeps building against a standard nobody had to invent.

Three files come out, in `.gauntlet/<slug>/`:

| File | What it is |
|---|---|
| `MAP.md` | the working document — destination, questions, answers, reasoning, fog |
| `ANSWER-KEY.md` | the **floor**. A binary standard a stranger can judge finished work against, plus an enumerated list of what nobody has decided |
| `GAUNTLET.md` | the **loop**. One pasteable prompt that builds against that floor, judged by a fresh critic every round |

The middle one is the point. A plan says what to build; an answer key says how you
would know it came out wrong. Hand a critic a plan and ask "is this good?" and it has
nothing to check against, so it invents a standard and approves whatever it sees. That
invented standard is the failure this skill exists to prevent, and it is the exact hole
a gauntlet loop has when nobody supplies the bar.

> The interview half is adapted from Matt Pocock's `wayfinder` skill
> (`github.com/mattpocock/skills`). The answer-key output is not part of his design and
> he has not endorsed it. The loop half follows the Gauntlet Loop pattern named by Matt
> Shumer in July 2026 (`somethingbig.ai/gauntlet-loop`).

## Decide, do not build

This skill decides and emits. It does not build the thing, and it does not build
anything *around* the loop either — no harness, no state machine, no scoring framework,
no runner. The method is prompt-level; the prompt is the method. Every agent asked to
produce one reflexively reaches for scaffolding it does not need.

The pull to just start building is the signal you have reached the edge of the map and
it is time to hand off. If the user wants it built, that is a separate session, after
the answer key exists.

**The loop will not finish on its own. The human is the stop condition.** Say that in
the skill, and say it again inside the emitted prompt.

## Two tiers

**Floor** — `ANSWER-KEY.md`. Every row binary, every row gradeable, every row derived
from something the user actually decided. This gates sign-off.

**Ceiling** — one named reference, deliberately out of reach. It supplies direction so
the loop does not settle at "pretty good," and it drives the A/B comparison every round.
It never blocks sign-off: a ceiling loss produces the next gap, nothing more. Winning
against the ceiling means the ceiling was set too low — say so and hand back.

`reference/bars.md` maps domains to bar types when the ceiling is not obvious.

## Every answer produces a check

This is the one thing that makes the output an answer key instead of notes.

After the user settles a question, ask one more: **"How would you know if this came out
wrong?"** The answer to *that* is what goes on the bar, in one of exactly two forms:

| Judged by | Use it when | What the critic does |
|---|---|---|
| `run it` | There is a right answer | Runs the thing and checks the outcome |
| `A/B pick` | It is a matter of taste or feel | Puts it beside a named reference and picks one, blind |

Four rules, canonical here and not restated in the phase files:

- **Never a score.** Not "rate the checkout 1–10," not "assess whether it feels
  premium." Every line is binary. Wanting a third option means the check is not specific
  enough yet — push it back into the conversation rather than softening the judgment.
- **Name the observable outcome, not the topic.** Whoever grades this is a stranger in a
  fresh session with no access to the conversation. "Run it" alone tells them nothing and
  they will invent a procedure, which is the invented-standard problem one level down.
  The test — *would two different people, given only this line, test it the same way and
  agree on the result?* Put a number in it wherever a number exists.
- **A reference is a named, fetchable thing** — "Stripe's checkout page," a file in
  `refs/` — never a category. "A professional checkout" is an invitation to invent one.
- **Reference is `—` whenever the check does the job.** A right answer beats an example.
  Only reach for a reference when there is genuinely no right answer.

## Fog, and out of scope

The map is deliberately incomplete. Beyond the questions you have written down sit the
ones you can tell are coming but cannot yet pin down. That is the fog, and it goes in
**Not yet specified**.

The test is whether you can *state* it precisely now — not whether you can answer it. A
sharp question you cannot answer is a question. Something you cannot phrase sharply is
fog. Do not pre-slice fog into question-sized pieces; one patch may become three
questions, or none. Answering a question clears the fog ahead of it, and whatever became
sharp gets promoted and disappears from the fog — it lives in one place, never both.

Fog that never clears is not a failure. It becomes the answer key's **Unknown** section,
which is the most valuable thing in the document.

Fog only ever gathers *toward* the destination. Work beyond the destination is **out of
scope**, and that section does a job most planning documents cannot do — it is the only
place that can say *adding this makes the result worse*. A critic told to beat a standard
tries to win by adding things. Out of scope is what stops that. Out-of-scope items are
never promoted and never get an entry in Answers; a scope boundary is not a step on the
route.

## Running it

### 0. Route first

Before anything else, look at `.gauntlet/` and at what the user handed you.

| What you find | What to do |
|---|---|
| `.gauntlet/<slug>/ANSWER-KEY.md` exists, `MAP.md` has no open questions | Skip to phase 4 |
| `.gauntlet/<slug>/MAP.md` exists with open questions | Resume at phase 2. Do not re-interview |
| A `.wayfinder/<slug>/` folder | Same shape, older name. Read it, tell the user you are adopting it, and continue from wherever it stopped |
| The user handed over a plan, spec, ticket, or issue | Take the fast path below |
| Nothing | Phase 1 |

The artifact is the record — there is no state file to keep in step, and a second
invocation must not re-ask a question already answered on disk.

**The fast path.** A supplied document is source of truth, not inspiration. Extract its
checkboxes, gates, thresholds, and prohibitions **verbatim** rather than paraphrasing
them; from an HTML or PDF spec take the semantic content and ignore the markup. Derive
candidate checks from it and put them to the user to confirm or reject, one round at a
time, rather than asking everything from scratch. Mark every derived item `DERIVED`
until they confirm it. Anything still `DERIVED` when you emit is reported to the user,
not shipped as decided — a derived check that nobody confirmed is an invented standard
wearing a citation.

### 1. Chart

Read `reference/grill.md`. Then:

1. **Name the destination.** Grill until it is one or two lines, then ask what is out of
   bounds. Seeds Destination and Out of scope.
2. **Grill again, breadth-first.** Sharp questions go to Open questions in running
   order; anything you cannot phrase sharply goes to Not yet specified.
3. **If nothing landed in the fog, stop here.** Tell the user the effort is small enough
   to just do, and do not write a map. This gate prevents a padded answer key, which
   looks like a standard while being filler — and filler on a bar gets graded.
4. **Write `MAP.md`** from `assets/MAP.template.md`, Answers empty.
5. **Start every research question now**, in the background.

### 2. Work the questions

Repeat until Open questions is empty. Several per sitting is expected.

1. **Take the top one.** The list order *is* the running order — there are no blocking
   edges to wire. When new questions arrive, put them where they belong rather than
   appending them.
2. **Resolve it** — grilling with `reference/grill.md`, taste or feel with
   `reference/prototype.md`, a fact with a background agent against primary sources.
3. **Ask how they would know it came out wrong.** Settle the check, the `judged by`, and
   the reference. A question is not resolved until this exists.
4. **Write the answer, the why, and the check into Answers.** Tick the question off.
5. **Update the map.** Promote newly-sharp fog and clear it from Not yet specified; move
   anything past the destination to Out of scope; rewrite or strike any question this
   answer invalidated.

### 3. Emit the floor

When Open questions is empty, or the user calls it. Read `reference/answer-key.md`,
write `.gauntlet/<slug>/ANSWER-KEY.md`, then lint it:

```
python3 scripts/check_answer_key.py .gauntlet/<slug>/ANSWER-KEY.md
```

It resolves `MAP.md` beside the answer key. Errors exit non-zero. Report what it says
rather than quietly rewriting a check to pass it — a check that had to be reworded to
satisfy the linter is a check the interview did not finish.

### 4. Emit the loop

Read `reference/gauntlet.md`. Copy `reference/critic-contract.md` to
`.gauntlet/<slug>/critic-contract.md` so the emitted prompt points at something that
exists outside this skill. Write `GAUNTLET.md` and run its ten-item self-check.

Then stop. Compose-only is the default: the user pastes the prompt wherever they want it
run. Run it here only if they ask.

## Talking to the user

The person running this thinks in outcomes, not files. Ask what the thing should do and
how they would know it was wrong. Do not narrate file paths, line counts, or mechanisms
at them — write the files quietly and talk about the decisions.

The decisions are theirs. An interview where you supply both sides has produced nothing.
It is your opinion with extra steps, and it will read as a standard on camera while being
a guess underneath.

## Do not fabricate

If something can only be settled by actually running it, mark it and move on. An invented
answer in the map becomes an invented standard in the answer key, which becomes a critic
grading real work against a guess — the exact failure this skill exists to prevent, now
automated and running unattended.

## Files

| Path | Read it when |
|---|---|
| `reference/grill.md` | Phases 1 and 2 — the interview |
| `reference/prototype.md` | A taste or feel question that talking cannot settle |
| `reference/answer-key.md` | Phase 3 — the format, columns, verdict grammar, gates |
| `reference/gauntlet.md` | Phase 4 — the emitted prompt and its self-check |
| `reference/critic-contract.md` | Phase 4, and any time the critic's brief is in question |
| `reference/bars.md` | Picking the ceiling, when nothing obvious presents itself |
| `scripts/check_answer_key.py` | End of phase 3, every time |
| `scripts/test_check_answer_key.py` | Changing the linter — CI runs it, so a new rule without a fixture reds the build |
| `assets/*.template.md` | Copied and filled — not read for guidance |
