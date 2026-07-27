# Charts — the narrow path

Most things a repo wants to "chart" are structural: a flow, a dependency, a
lifecycle, a decision. Those are diagrams, and [viz-production.md](viz-production.md)
covers them. This file governs the other case — a visual whose meaning is carried by
**plotted quantities** — and it is deliberately narrow, because a number rendered
into pixels cannot be greped, diffed, reviewed in a PR, or corrected by the next
person who notices it is wrong.

Read the provenance rule first. If a chart fails it, the answer is not a better
chart.

## 1. The provenance rule

A data chart is permitted **only when the next run can recompute every plotted value
from the repository's own source.**

Note the wording: *recomputable*, not merely *committed*. Those are not the same test,
and the difference is where this rule would otherwise leak. A committed coverage
report, a checked-in benchmark log, a saved query result — each is a file in the tree,
so each satisfies "derived from a committed file", and none of them is recomputable:
they are snapshots of a *run*, not properties of the code. Nothing in the repo can tell
the next run the number has gone stale, which is exactly the failure the rule exists to
prevent.

**Where the two disagree, the Forbidden table below wins.** Provenance is necessary,
not sufficient.

Permitted, because the next run can recompute the value from the repo and will
notice when it moves:

| Source | Example |
| --- | --- |
| A schema or migration | tables per schema, columns per table, indexes per table |
| A dependency manifest | runtime vs dev dependencies, packages per workspace |
| The doc set itself | Tier-1 docs present, visuals per doc against budget |
| The test tree | test files per package, spec count per suite |
| Source layout | modules per layer, public exports per package |
| A committed config | services per compose file, routes per router, environments per IaC file |

**Forbidden.** These are not charts here, in any style, however the user asks:

| Refused | Why |
| --- | --- |
| Live or scraped metrics — request rates, uptime, users | Not in the repo; stale the moment it is drawn |
| Benchmark timings, throughput, latency | Machine- and run-dependent; not recomputable |
| Coverage or pass-rate percentages | A snapshot of a run, not a property of the code — forbidden even when the report is committed |
| Download, star, or contributor counts | Lives on a platform, not in the tree |
| Dates, ages, "as of" anything, roadmap timelines | Decays silently with no signal |
| Any value the author supplies by hand and the repo cannot confirm | Unverifiable by construction |

The test is one question: **can the next run recompute this number from the
repository's source?** If not, it is not a chart — even if a file in the tree happens
to contain it today. Put it in prose, where
`house-style.md` → *No volatile facts* already governs it and where a reader can grep
and fix it.

Refuse with the reason and the alternative, in the run report and to the user. The
wording that works:

> A coverage percentage records what one test run measured, not anything the code
> states, so the next run cannot recompute it — six months from now nothing in the
> repo can tell us the number is wrong. That holds even if the report is committed.
> Coverage belongs in one line of prose in DEVELOPMENT.md, or in a badge that reads
> live. What the repo *can* support is a chart of test files per package, recomputed
> from the tree on every run.

A user who insists after that has been told the cost; note the override in the run
report, name the chart's values in `facts` anyway, and say plainly in the doc body
what the numbers are as of what commit.

## 2. The facts contract

Every plotted value appears as its own entry in the visual's `viz.json` `facts`
array, in the same units it is drawn in.

```json
{
  "producer": "pretty-plain-docs",
  "style": "schematic",
  "facts": [
    "schema tables: core 14",
    "schema tables: billing 6",
    "schema tables: audit 3",
    "source: db/schema.sql"
  ],
  "facts_hash": "…",
  "svg": { "loop_s": 0, "width": 1200, "height": 480 }
}
```

Three things this buys, and they are the whole reason a chart is allowed at all:

- **The number is greppable** in the manifest even though it is pixels in the asset.
- **`facts_hash` moves the moment the data does**, so the next run re-authors the
  chart instead of leaving a stale one in place. That is what makes a chart
  legitimately re-renderable rather than quietly wrong.
- **The source file is itself a fact.** Record the path the values came from
  (`"source: db/schema.sql"`), so a reviewer can check the arithmetic without
  guessing where to look.

`facts_hash` is computed exactly as `embedding.md` defines it — `printf '%s\n'`
semantics over the array, a newline after **every** entry including the last. A chart
whose plotted values are not in `facts` is a gate failure, not an oversight: it is
indistinguishable from a hand-typed number.

## 3. Chart types, and when each is right

| Type | Use when | Notes |
| --- | --- | --- |
| **Horizontal bar** | comparing a quantity across categories — **the default** | Survives long category labels, which is why it is the default. Labels read left-to-right at full size |
| Vertical bar (column) | few categories with short labels, or an ordered sequence | Rotated axis labels are a smell: switch to horizontal bar |
| Line / area | change across an **ordered dimension committed in the repo** — schema version, migration number, release tag in a committed changelog | Never "over time" from dates. Never a projection |
| Donut | composition of one whole, **≤ 5 slices**, values printed | Anything more granular is a horizontal bar. Never nested rings |
| Scatter | two committed dimensions per item — file size against export count | Label the outliers only; do not label all points |

Hard rules, no style relaxes them:

- **No 3D, no perspective, no exploded slices.** The `isometric-3d` style draws
  structures in axonometric projection; that is not licence to give a bar depth.
- **No dual value axis.** Two units on one chart is two charts.
- **No truncated value axis** without an explicit break mark on the axis and the
  baseline value stated in the label. A bar chart's value axis starts at zero.
- **No stacked bars beyond three segments**, and every segment labelled.
- **One chart, one question.** If the caption needs "and", split it.

## 4. Axes, ticks, gridlines, legend, colour

Everything is drawn from the palette roles in `.prettydocs/prettydocs.md`. This is
enforced, not advisory: `svg_check.py`'s palette-conformance check makes an
off-palette series colour a hard `ERROR`, and a derived tint has to be declared as a
custom property in the token block.

| Part | Role | Weight |
| --- | --- | --- |
| Value axis line, tick marks | `dim` (or the system's rule/hairline role) | `1`–`1.5` |
| Gridlines | same as ticks, or omitted | `1`, and only along the value axis |
| Category axis labels, tick labels | `ink` for a label a reader must read; `dim` only for a repeated unit | — |
| Series marks (bars, line, points) | `accent-primary` for one series | — |
| Additional series | further declared accent roles, in the order the system declares them | — |
| The one value worth pointing at | `accent-primary` while the rest go `dim` | — |

Practical consequences:

- **One series needs no legend.** Name it in the `<title>`, the caption, or the axis.
  A legend for a single series is decoration.
- **A legend for two or three series** sits at the top of the plot, horizontal, using
  the same mark shape the chart draws. Never a colour swatch whose shape differs from
  the mark.
- **Gridlines are optional and usually wrong.** With every value printed on its mark
  (below), gridlines carry nothing. Keep them only when a reader genuinely has to
  compare across a long axis.
- **Do not encode a category by colour alone.** Colour distinguishes series;
  position and the label identify the category. Two series must also differ in
  something non-chromatic — fill vs hairline, solid vs dashed — so the chart survives
  greyscale printing, which is one of the reasons a repo chooses this skill.

## 5. Legibility is the binding constraint

A dense category axis is the first thing in this skill that breaches a legibility
floor, and it breaches the tightest one.

- Axis labels, tick labels and value labels are **`data-role="label"`, floor 18
  units**. Value labels genuinely essential to the chart's point are
  `data-role="essential"`, floor 20.
- **The rule when labels do not fit at 18: reduce the categories, or turn the chart
  into a Markdown table. Do not shrink the type, and do not rotate the labels.**
  Shrinking is a gate failure; rotating is a legibility failure the gate cannot see.
  Grouping a long tail into one `other` bar is honest as long as the grouping is
  stated in the label and in `facts`.
- **Print every value on or beside its mark.** A reader must never have to measure a
  pixel against an axis to recover a number. This also means the chart degrades
  gracefully: at any size, the numbers are still readable text.
- Bars need real space. On the 1200 canvas: bar thickness `28`–`44`, gap at least
  `12`, and enough left gutter for the longest category label at 18 units. Eight to
  ten horizontal bars is a comfortable board; sixteen is a table.
- Give the value axis a unit somewhere — in the axis label or the `<title>`.
  "14" without "tables" is not a chart, it is a number.

## 6. The Mermaid fallback

Every structural visual in this skill carries a collapsed `<details>` Mermaid block
(`house-style.md` → quality gate 9, and `embedding.md` → *Embed shape per doc type*).
Charts are covered by the same rule, with one honest limitation: **Mermaid's chart
support is thin.** Map to it where it fits, and to a table where it does not.

| Chart | Fallback |
| --- | --- |
| Vertical bar, line | `xychart-beta` — has axes, a bar series and a line series |
| Donut, single-series composition | `pie showData` — prints the values, which is exactly the rule above |
| Horizontal bar, scatter, stacked, multi-series | **a Markdown table** |

A table is a fully acceptable fallback for a chart — often a better one, because it
gives exact values, sorts, and is greppable. What is **not** acceptable is a stub: a
`<details>` block holding a one-line placeholder, a diagram of the chart's axes, or a
Mermaid `flowchart` faking bars with boxes. If neither Mermaid nor a table can carry
the data, the chart was too complicated.

```markdown
<details>
<summary>Chart source</summary>

| Schema | Tables |
| --- | ---: |
| core | 14 |
| billing | 6 |
| audit | 3 |

Recomputed from `db/schema.sql`.

</details>
```

The table's numbers, the `facts` entries and the pixels must all agree. When they
disagree, the manifest is right and the asset is stale — which is the audit's verdict,
and the next apply run re-authors it.
