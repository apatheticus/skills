# Line

Continuous trends over time or a sequential index, where the direction and rate of change
between points is the message.

Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery); provenance in `THIRD_PARTY.md`.

**Best for:** signups over weeks, revenue by month, latency over releases. Use it when the
reader's question is *which way is this going* rather than *which is biggest* — that
second question is a `bar`.

A plotted value is a claim, so a vertex may be drawn only if the next run can **recompute**
it from the repository's source — `reference/charts.md` owns that rule and the provenance
of the ticks.

## Layout conventions

The board is `0 0 1200 600`, or `0 0 1200 672` once a legend is present — §9 of
`reference/diagram-grammar.md` puts it below every node under a hairline, at about 72
units of extra height.

| Part | Value |
| --- | --- |
| Plot area | `x` 96 → 1152, `y` 48 → 504 (1056 × 456) |
| Baseline | `y = 504`, stroke `var(--ink)` at 0.25, width 1 |
| Value axis | `<line>` at `x = 96`, `y` 48 → 504 |
| Tick labels | right-aligned at `x = 88`, mono, `data-role="metadata"` |
| Index labels | centred on each vertex `x`, below the baseline, mono |
| Focal series | `<polyline>` `fill="none"`, `stroke="var(--accent)"`, width 2 |
| Other series | same shape at width 1.25, in `var(--muted)` and its tints |
| Vertex dots | focal series only, `r = 5` |
| Legend swatch | 20 × 12 rect, items about 200 units apart |

**The point count is constrained by the grid, not by taste.** Vertices sit at
`96 + k × 1056/(n−1)`, and that step is a multiple of 4 only for `n` in **4, 5, 7, 9, 12**
— six points puts every vertex on `211.2`. Four to twelve is the readable range: fewer is
a sentence, more is a period aggregate. Pick one of those five counts, or aggregate to it.

An optional area fill is a `<polygon>` closing back to `y = 504` at 0.08 opacity, focal
series only, and only when the area under the line means something.

## Budget

From `scripts/diagrams.json`: **`max_nodes: 5`** series, **`max_edges: 0`**,
`max_focal: 2`, `max_zones: 3`. The unit is the series, so each one is a
`<g data-node="true">` wrapping its polyline and its dots — **not** its legend entry.
The checker takes a node's extent as the union of every shape inside its group, so a
swatch parked there stretches the node down into the legend strip and the legend then
reports as sitting above the lowest node edge. Legend entries belong inside
`<g data-legend="true">`. Draw the swatch as a stroked segment plus a dot rather than
a filled rect: a rect cannot show the dash pattern separating two same-family series,
and `charts.md` §5 asks for the mark shape the chart actually uses.

Five lines is already dense; past that they read as hatching. Split by subject rather
than by time, and record the cuts in `budget_cuts[]`.

**There are no connectors on this type.** A polyline is data, not a `data-edge`, so §4's
elbow, gap and hop rules do not apply and a diagonal segment is correct here. What
replaces them is axis honesty: the value axis includes zero whenever absolute magnitude
matters, and a truncated axis is annotated as truncated rather than left to imply a
steeper trend than the numbers support.

## Primitives

```svg
<g data-node="true" data-focal="true">
  <polyline points="96,412 360,336 624,268 888,180 1152,124"
            fill="none" stroke="var(--accent)" stroke-width="2"
            stroke-linejoin="round" stroke-linecap="round"/>
  <circle cx="96" cy="412" r="5" fill="var(--accent)"/>
  <!-- one per vertex -->
</g>

<g data-node="true">
  <polyline points="96,436 360,428 624,404 888,412 1152,388"
            fill="none" stroke="var(--muted)" stroke-width="1.25"
            stroke-linejoin="round"/>
</g>
```

Dots on the focal series only — with three or more lines, dots everywhere turn each
crossing into a knot. Series colour comes from the repo's palette through the role
mapping in `reference/design-system.md`: `accent` for the focal line, tints of `muted`
for the rest, applied in order rather than picked per line.

A discontinuity is a gap — end the polyline, start another in the same `data-node` group.

## Motion

The line itself is fixed: a draw-on is an entrance animation, which the seam contract in
`reference/svg-animation.md` rules out, and animating `points` moves geometry.

What may loop, at 8–14s and seam-exact: a token riding the focal polyline on a fixed
path — the one motion §11 names explicitly, and its own element outside any
`[data-node]` — or an ordered emphasis raising one series' `stroke-opacity` at a time so
a five-series board reads in sequence. No phase may leave a series invisible; the board
is complete at every instant, including the one a reader screenshots.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| More than five series | Visual mush; the reader traces nothing |
| Spline smoothing over sampled data | Invents curvature between readings that were points |
| A truncated value axis presented as a trend | The slope is an artifact of the crop |
| Dots on every series | Every crossing becomes a knot |
| Two filled areas | They occlude; neither is readable |
| A straight segment across a data gap | Draws readings that do not exist |
| Series colours picked per line | The order is the encoding; skipping it makes it arbitrary |

## Specimen

`docs/samples/types/line.svg` — the type drawn at full width, gated as its own `data-diagram`.
