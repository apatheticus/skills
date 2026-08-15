<div align="center">

# gauntlet-builder

**A Claude Code skill that interviews you into an answer key — a binary standard for judging finished work — then emits the loop that builds against it.**

<!-- pd:badges start -->
[![License: MIT](https://img.shields.io/badge/License-MIT-0d1117.svg)](../../LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-skill-0d1117)](SKILL.md)
[![Check forms](https://img.shields.io/badge/check_forms-2-0d1117)](#every-answer-becomes-a-check)
[![Linter rules](https://img.shields.io/badge/linter_rules-20-0d1117)](#what-comes-out)
<!-- pd:badges end -->

<!-- pd:viz name="hero" src=".prettydocs/src/hero/" facts-hash="331b04aeeee7732f23dabda950dbbafd9b76022188cdb308bd896bc3d987b26e" src-hash="97fbc1003a68107c063344027dc5d9c280ae7b4f6707facf58876f03905e17b3" -->
<div align="center">
<img src="docs/assets/hero.svg" alt="An animated terminal pane titled gauntlet-builder, with a blinking block cursor at the prompt and a green scan mark stepping down the rows of an answer key held at .gauntlet/checkout/ANSWER-KEY.md. The pane has three columns: the check, what it is judged by, and a reference. Three binary checks are listed — that upgrading mid-month charges the prorated difference, judged by run it against no reference; that the checkout reads as trustworthy at a glance, judged by A/B pick against refs/stripe.png; and that a failed card shows retry without leaving the page, judged by run it against no reference. Below a rule, in amber, sits U1, whether shoppers trust the badge at all, with a question mark where a judgement would go and the words not gradeable in the reference column. A green status strip along the bottom reads: exit 0, check_answer_key.py, 3 binary, 1 not gradeable." width="820" />
</div>
<!-- pd:viz end -->

</div>

> [!IMPORTANT]
> This skill decides and emits. It does not build the thing, and it does not build a
> harness, a state machine, or a scoring framework around the loop either. Building is a
> separate session, after the answer key exists.

## What this is

Hand an agent a plan and ask whether the result is good, and it has nothing to check
against. So it invents a standard, then grades the work against the standard it just
invented — and approves it. That invented standard is the failure this skill exists to
prevent.

The fix is an **answer key**: a list of things that must be true, written down *before*
any work starts, each one binary enough that a stranger in a fresh session can open the
artifact and say pass or fail without asking a follow-up question. A plan says what to
build. An answer key says how you would know it came out wrong.

Getting one out of a person is the hard part, and it is the part this skill does. It
interviews you a question at a time, and after each answer settles it asks one more
thing — *how would you know if this came out wrong?* The answer to **that** is what goes
on the bar. Then it writes the loop that builds against it.

The interview half is adapted from Matt Pocock's `wayfinder` skill. The loop half
follows the Gauntlet Loop pattern named by Matt Shumer. Neither has endorsed this.

## Every answer becomes a check

A check takes one of exactly two forms. There is no third.

| Judged by | Use it when | What the critic does |
| --- | --- | --- |
| `run it` | There is a right answer | Runs the thing and checks the outcome |
| `A/B pick` | It is a matter of taste or feel | Puts it beside a named reference and picks one, blind |

Four rules hold that line, and each of them closes a way the bar goes soft:

- **Never a score.** Not "rate the checkout 1–10", not "assess whether it feels
  premium". Wanting a middle option means the check is not specific enough yet, so it
  goes back into the conversation rather than getting a softer verdict.
- **Name the observable outcome, not the topic.** Whoever grades this has no access to
  the conversation. The test is whether two different people, given only that line,
  would test it the same way and agree on the result.
- **A reference is a named, fetchable thing** — Stripe's checkout page, a file in
  `refs/` — never a category. "A professional checkout" is an invitation to invent one.
- **The reference is `—` whenever the check does the job.** A right answer beats an
  example, so `A/B pick` is the fallback rather than the default.

Anything nobody has decided does not get a guess. It is enumerated `U1`, `U2`, and
marked ungradeable, so a critic that reaches it reports `CANNOT JUDGE` and stops there.
That section is usually the most valuable thing in the document.

## The loop

<!-- pd:viz name="gauntlet-loop" src=".prettydocs/src/gauntlet-loop/" facts-hash="a0ecaee332c55de89ee90c70b9216ac45a13b5749cd4c6b4b07a52e99054f610" src-hash="6f1824acb5d4938e6c842dfb0d2384ec07cee97857c087f22effbf2f3f2e20f3" -->
<div align="center">
<img src="docs/assets/gauntlet-loop.svg" alt="An animated flowchart of the gauntlet loop, running top to bottom. The lead writes a CONTRACT for one piece; a builder subagent runs BUILD and produces the artifact with its evidence; a fresh critic runs AUDIT, drawn as the focal step. Beside AUDIT, three lines say what crosses the boundary: the critic gets the answer key, the artifact and the evidence; never the builder rationale or prior notes; and a new critic runs every retry. AUDIT leads to a verdict diamond with two labelled exits. WIN or TIE goes right to PASSED, evidence logged. LOSS goes down to ONE GAP, the only brief, which travels back along a dashed return path up the left margin to become the next contract. A green status mark advances one step at a time through contract, build and audit. Nothing on the board counts rounds." width="820" />
</div>
<!-- pd:viz end -->

Five things hold the loop up, and it collapses into an ordinary "do it well and check
your work" prompt if any one of them goes:

1. **Goal, not implementation.** The prompt states the destination. It does not
   prescribe the architecture, the module list, or the technology inside the stack.
2. **A bar a critic can open.** "Amazing" and "production-ready" are not bars. Every row
   of the answer key is openable, runnable, or viewable.
3. **The lead decides the split.** The prompt says *split it*; it never lists the pieces.
4. **The builder never grades itself.** Separate agent, fresh context, no builder
   reasoning, and a new critic per retry — one that watched the previous draft grades
   improvement rather than the bar, and improvement always looks like progress.
5. **No round count.** Not three passes, not "iterate twice". **The human is the stop
   condition, and the loop will not finish on its own.**

The critic returns the full pre-registered verdict block and then one `GAP:` line. That
looks like a punch list and is not one. A punch list is harmful because the critic
*invents* the items; a binary checklist written before any work started invents nothing,
so it is a verdict. The brief is the single gap, and it is the only line a builder sees.

## Floor and ceiling

The bar has two tiers, and only one of them can fail the work.

| Tier | What it is | What it gates |
| --- | --- | --- |
| **Floor** | `ANSWER-KEY.md` — every row binary, gradeable, and traceable to something you actually decided | Sign-off |
| **Ceiling** | One named reference, deliberately out of reach | Nothing. It supplies the next gap once the floor passes |

Losing to the ceiling is expected and never fails the work — it is what stops the loop
settling at "pretty good". Winning against it means the ceiling was set too low, which
is a signal to hand back rather than a declaration that the work is finished.

## What comes out

Three files, in `.gauntlet/<slug>/`:

| File | What it is |
| --- | --- |
| `MAP.md` | The working document — destination, questions, answers, the reasoning, and the fog |
| `ANSWER-KEY.md` | The floor, plus the enumerated list of what nobody has decided |
| `GAUNTLET.md` | One pasteable prompt that builds against that floor, judged blind every round |

`GAUNTLET.md` is composed, not run. You paste it wherever you want it run, which is
usually a different session and often a different day.

Before the answer key is handed to anything, a bundled linter reads it:

```bash
python3 scripts/check_answer_key.py .gauntlet/<slug>/ANSWER-KEY.md
```

Twenty rules, and the two that matter most are the ones that used to fail in silence. A
`from decision` link into `MAP.md` whose anchor no longer resolves sends a critic to read
the reasoning behind a check, where it finds nothing and concludes the check is wrong. An
`A/B pick` whose reference is not a real file is a dead reference nobody notices until
judging time. Both are now errors that exit non-zero. The rest cover the shape of the
bar: the `judged by` value, score vocabulary, build instructions that drifted in from a
spec, unquantified language, contiguous numbering, and an `Out of scope` section that is
empty.

The linter reports rather than repairs, and the skill is explicit that you report what it
says instead of rewording a check until it passes. A check that had to be reworded to
satisfy a linter is a check the interview did not finish.

## Technology stack

| Area | Choice |
| --- | --- |
| Format | Claude Code skill — Markdown with YAML frontmatter |
| Runtime | Python 3 for the bundled linter; nothing else, and no network access |
| Tools used | `Read`, `Write`, `Edit`, `Grep`, `Glob`, `Bash`, `AskUserQuestion`, `Task` |
| Invocation | Manual only — `/gauntlet-builder`; the skill does not fire on its own |
| License | MIT |

## Project structure

```
gauntlet-builder/
├── SKILL.md                        the skill: routing, the four phases, the rules that stay in context
├── reference/
│   ├── grill.md                    the interview — the design tree, rounds, the frontier
│   ├── prototype.md                rough variations for a question talking cannot settle
│   ├── answer-key.md               the format, the columns, the verdict grammar, the gates
│   ├── gauntlet.md                 the emitted prompt and its ten-item self-check
│   ├── critic-contract.md          the blind auditor brief, fail-closed and injection-guarded
│   └── bars.md                     domain to bar-type catalog, for picking a ceiling
├── scripts/
│   ├── check_answer_key.py         the linter
│   └── test_check_answer_key.py    its fixtures, run in CI
├── assets/                         the three templates, copied and filled, never read for guidance
├── docs/assets/                    this README's two animated SVGs
└── .prettydocs/                    the frozen design system they derive from, and their manifests
```

## Getting started

### Prerequisites

Python 3, for the linter. Nothing else — no dependencies, no network, no build step.
Without Python the skill still runs the interview and writes all three files; you lose
the gate that proves the bar is checkable.

### Install

```bash
npx skills add apatheticus/skills --skill gauntlet-builder
```

Or as part of the Claude Code plugin bundle:

```
/plugin marketplace add apatheticus/skills
/plugin install apatheticus-skills@apatheticus
```

Or copy the folder straight into a repo's skill directory:

```bash
cp -R skills/gauntlet-builder /path/to/repo/.claude/skills/gauntlet-builder
```

### Use

Invoke it by name, with the thing you are about to build:

```
/gauntlet-builder I want to add usage-based billing to the app
/gauntlet-builder set the bar for the onboarding rewrite
```

It names the destination, asks what is out of bounds, then charts the questions and works
them one at a time. Several sittings is normal, and it resumes from `.gauntlet/` rather
than re-asking anything already answered on disk. Hand it a plan file, spec, or ticket
you already have and it derives candidate checks from that instead of starting the
interview cold — everything derived is marked `DERIVED` until you confirm it, and
anything still `DERIVED` at the end is reported rather than shipped as decided.

One gate is worth knowing about before you start. If the charting pass turns up nothing
you cannot already phrase sharply, the skill stops and tells you the job is small enough
to just do. It does not write a map. A padded answer key reads as a standard while being
filler, and filler on a bar still gets graded.

Testing the linter, which the repository's CI also runs:

```bash
python3 scripts/test_check_answer_key.py
```

`npm run validate` at the repository root checks this skill's frontmatter and its entries
in both distribution manifests. See [CONTRIBUTING.md](../../CONTRIBUTING.md) for how
changes are proposed and reviewed.

## Documentation

- [`SKILL.md`](SKILL.md) — the skill itself: routing, the phases, the canonical rules.
- [`reference/grill.md`](reference/grill.md) — how the interview actually runs.
- [`reference/answer-key.md`](reference/answer-key.md) — the answer-key format and the verdict grammar.
- [`reference/gauntlet.md`](reference/gauntlet.md) — the emitted prompt and what invalidates it.
- [`reference/critic-contract.md`](reference/critic-contract.md) — the blind auditor's brief.
- [`CONTRIBUTING.md`](../../CONTRIBUTING.md) — repository-wide contribution rules.

## License

Released under the [MIT License](../../LICENSE) of the repository that ships it.

The interview half is adapted from the MIT-licensed
[`wayfinder`](https://github.com/mattpocock/skills) skill by Matt Pocock. The answer-key
output and the loop half are not part of that design, and its author has not endorsed
them. The loop follows the Gauntlet Loop pattern named by Matt Shumer.

<!-- pd:footer start -->
<div align="center">
<br/>

**Copyright © 2026 Zerø Effort. Released under the MIT license.**

</div>
<!-- pd:footer end -->
