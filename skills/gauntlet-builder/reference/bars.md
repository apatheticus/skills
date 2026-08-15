# bars — picking the ceiling

Load this when the ceiling is not obvious. The floor comes out of the interview; the
ceiling is chosen, and choosing it badly is the most common way a gauntlet loop stalls.

A good bar is **external, specific, and mechanically comparable**. The test is whether a
critic in a fresh session can open it, run it, view it, or measure against it. If it
cannot, it is not a bar — it is an adjective with a reference-shaped hole around it.

## Domain → bar type

| Domain | Bar type | Concrete examples |
|---|---|---|
| Games, real-time 3D | Reference screenshots and video from a shipped title | Frame captures from a named title; a named indie game's feel |
| Web, marketing sites | Best-in-class sites in the same category | Named products' live pages, at matching viewport sizes |
| UI components | Design-system reference plus rendered screenshots | A named component library, plus contrast and keyboard-nav checks |
| Backend engineering | Executable criteria | Test suite, p99 latency at a stated concurrency, a chaos scenario with a recovery window, a reference implementation |
| Data pipelines | Golden datasets and reconciliation | Known-correct output for a fixed input; row-count and checksum parity |
| Prose, long-form | Reference paragraphs at the target clarity and density | A named writer's paragraphs, used to test clarity — not to imitate voice |
| Research, analysis | A published analysis of comparable depth, plus a fact-verification pass | A named report; every claim traceable to a source |
| Compliance, proposals | The solicitation's own evaluation criteria as a matrix, plus a strong exemplar | Sections L and M mapped to a compliance matrix; a prior winning response as a quality comp |
| Slide decks | A named deck at the target production quality | Rendered slides compared side by side at presentation size |
| Developer tooling, CLIs | A named tool's output, error messages, and help text | `--help` and a failure path from a tool people like using |
| Documentation | A named project's docs at the target level | A specific page, compared for what a reader can do after reading it |

## Rules

1. **Inspectable beats aspirational.** If the critic cannot open it, it is not a bar.
2. **Specific beats broad.** "As clear as these six paragraphs" beats "clear writing."
3. **Unreachable is allowed and usually preferable.** It sets direction. The original
   run of this method never beat its reference; it was stopped while still improving.
4. **Multiple bars are fine when each maps to a different piece** — a visual bar for the
   render, a test-suite bar for the logic, a latency bar for the service. One ceiling
   per engagement is the default; more than one is a decision to make deliberately.
5. **Where no bar exists, finding one is the first task.** Never let the loop invent its
   own definition of good in private. Ask the user; if they have nothing, say what you
   would propose and why in one sentence, and get a yes.

## When the interview produced the reference

A prototype the user picked is a legitimate ceiling reference, and often a better one
than anything external — it is the only kind that captures taste nobody has published.
It has to be parked the way `reference/prototype.md` requires: one double-clickable file
or one image, inside `.gauntlet/<slug>/refs/`.

A prototype makes a poor ceiling in one case: when the user picked it as "the least bad
of three." That is a floor, not an aspiration. Say so and look outward instead.

## Two failure shapes to recognise

**A bar too vague to lose against** produces a loop that runs forever with no
improvement, because every round wins. If three consecutive critics pass without naming
a gap, the ceiling is the suspect, not the work.

**A bar that is really a design** produces imitation. The reference sets a *level*, not
a layout — say so in the ceiling's one-sentence justification, because a critic reading
"be like X" and a critic reading "be as clear as X" behave differently.
