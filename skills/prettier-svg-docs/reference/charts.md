# Charts — the narrow path

Most of what a repo wants to "chart" is structural, and `reference/diagrams.md` routes
those. This file governs the other case — a visual carrying its meaning in **plotted
quantities**. It is deliberately narrow: a number rendered into pixels cannot be greped,
diffed, reviewed in a PR, or fixed by whoever spots it wrong.

Five types plot numbers: `bar`, `line`, `gantt`, `scatter`, `radar`. Read §1 first: if a
chart fails it, a better chart is not the answer.

---

## 1. The provenance rule

A data chart is permitted **only when the next run can recompute every plotted value
from the repository's own source.**

*Recomputable*, not merely *committed* — the difference is where this rule would otherwise
leak. A committed coverage report, a benchmark log, a saved query result: each is a file
in the tree, so each satisfies "derived from a committed file", and none is recomputable.
They are snapshots of a *run*, not properties of the code, so nothing in the repo can tell
the next run the number went stale — the failure this rule prevents.

**Where the two readings disagree, the Forbidden table wins.** Provenance is necessary,
not sufficient.

Permitted, because the next run recomputes the value and notices when it moves: a schema
or migration (tables per schema, indexes per table), a manifest or committed config (dev
against runtime deps, services per compose file), the doc set, test tree or source layout
(visuals per doc, tests or exports per package).

**Forbidden** — not charts here, in any style, however the user asks:

| Refused | Why |
| --- | --- |
| Live metrics, downloads, stars, contributors | On a platform, not in the tree |
| Benchmark timings, throughput, latency | Machine- and run-dependent |
| Coverage or pass-rate percentages | A snapshot of a run, not a property of the code — forbidden even when committed |
| Dates, ages, "as of" anything, roadmaps | Decays silently, no signal |
| Any hand-supplied value the repo cannot confirm | Unverifiable |

`gantt` most often arrives carrying forbidden data, a schedule of dates being a roadmap.
What the repo supports is an *ordering* — migration sequence, release tags, pipeline
stages — on a positional axis, no dates on it.

Refuse with the reason and the alternative, in the run report and to the user. A user who
insists has been told the cost: log the override and date the values to a commit.

## 2. The facts contract

Every plotted value is its own `viz.json` `facts` entry, in the units drawn, with the path
it came from — `"schema tables: core 14"`, then `"source: db/schema.sql"`.

That keeps the number greppable though the asset is pixels, moves `facts_hash` the moment
the data does so the next run re-authors rather than leave a stale chart standing, and
lets a reviewer check the arithmetic. A value missing from `facts` is a gate failure: it
is indistinguishable from a hand-typed number.

## 3. The five types

Budgets from `scripts/diagrams.json`. Each mark is one `data-node`; the root carries
`data-diagram="<slug>"`.

| Type | Unit | Budget | Use when | Layout |
| --- | --- | --- | --- | --- |
| `bar` | bar | 8 | a quantity across categories, the default | `reference/types/bar.md` |
| `line` | series | 5 | change across a committed ordered dimension | `reference/types/line.md` |
| `gantt` | task | 12 | tasks or phases along an ordering | `reference/types/gantt.md` |
| `scatter` | point | 30 | two committed dimensions per item | `reference/types/scatter.md` |
| `radar` | series | 5, **1 focal** | entities scored on three to five axes | `reference/types/radar.md` |

Horizontal is `bar`'s default: it survives long category labels, and rotated axis labels
say the column form was wrong. Relaxed by no style: no 3D or perspective (`isometric-3d`
is axonometric — not licence to give a bar depth); no dual value axis; no stacked bars past
three segments; one chart, one question. Past budget, split into overview and detail and
record the cut in `budget_cuts[]`. The technical-doc `<details>` fallback (`embedding.md`)
maps thinly: `xychart-beta` for `line`, `gantt` if the ordering survives dateless, a
Markdown table for the rest.

## 4. No connectors — axis honesty instead

All five carry `max_edges: 0`, so grammar §4's six connector rules have nothing to bind to
— no elbows, no label gap, no fanned attach points, no hops. Nothing is relaxed; it does
not apply, and a `data-edge` here is a checker error against a budget of zero. An arrow
means you are drawing a diagram. Axis honesty replaces them, being what a reader cannot
check once the chart is pixels:

- The value axis starts at zero, or carries a break mark and states its baseline.
- Ticks are evenly spaced in value, not in whatever spacing made the labels fit.
- Length or position encodes the value; area, width and opacity carry no data.
- Every category in `facts` is drawn; a dropped tail is a claim, so it goes in the label
  (`other (4)`) and in `facts`.

## 5. Roles, legend, legibility

Roles come from grammar §2, resolved through `reference/design-system.md`. A raw hex is a
checker error; a derived tint is declared as a custom property.

| Part | Role |
| --- | --- |
| Axis line, ticks, gridlines | `rule`, at `1`–`1.5` |
| Category and tick labels | `ink` to be read, `muted` for a repeated unit |
| Marks — bars, line, points, radar polygon | `ink`; a series leaving the system, `link` |
| The one value worth pointing at | `accent`, the rest `muted` |

`accent` obeys the focal rule unchanged — one or two marks, exactly one series on `radar`.
If four bars want it, the chart's point has not been decided. One series needs no legend;
two or three get a `data-legend` strip below every mark (grammar §9). Gridlines are
usually wrong once every value is printed on its mark, and no category is encoded by
colour alone.

A dense category axis then breaches the tightest legibility floor here. Axis, tick and
value labels are `data-role="label"`, floor **18 units** at `viewBox` 1200; a value the
chart's point rests on is `essential`, floor **20**. Each carries a `data-bg` naming its
ground — one resolving to no palette role is a silent `WARN` and the floor goes unapplied.

**Labels that do not fit at 18: cut categories, or write a Markdown table.** Shrinking the
type is a gate failure; rotating is a legibility failure the gate cannot see. Print every
value on or beside its mark, give the axis a unit, and leave room: bar thickness `28`–`44`,
gap ≥ `12`.

## 6. Motion

The seam contract in `reference/svg-animation.md` applies unchanged: `data-loop-s` on the
root, 8–14s, every duration dividing it, every animation `infinite`, no entrances, a
reduced-motion block. Grammar §11's rule applies too and bites harder here than anywhere:

> **Motion never moves geometry.** No animation may mutate `d`, `x`, `y`, `cx`, `cy`,
> `r`, `width`, `height`, `viewBox`, or a `translate`/`scale` transform on a
> `[data-node]` or `[data-edge]`.

A mark's geometry *is* its value, which rules out the obvious idea — bars growing from the
baseline — and every value-revealing animation with it: a line drawing itself left to
right, points fading in by rank, a radar polygon inflating. The reason is mechanical
rather than stylistic. Every geometry check in `svg_check.py` measures the committed
coordinates, so a chart whose bars grow passes its gate in one frame and fails in another,
and what a reader takes away depends on when they looked. A claim is true at every instant
or it is not one.

What may move, none of it touching a plotted value: the material pass belonging to the
resolved style, and an ordered emphasis changing `opacity` or `stroke-width` on marks
whose coordinates never move, walking the reader through the categories in the order the
caption argues. A `stroke-dashoffset` march is legal by the letter of the rule and usually
wrong — on a value axis it reads as flow, and a chart has none. `line` and `radar` invite
draw-on and refuse it; a chart with nothing legitimate to animate sits still at its loop.
