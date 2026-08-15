# Bar

Quantitative comparison across categories — one value per category, where the spread
between the bars is the message.

Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery); provenance in `THIRD_PARTY.md`.

**Best for:** sprint velocity, monthly revenue, feature adoption, cohort counts. Each
category carries a single number and the reader's takeaway is the ranking or the gap.

A plotted value is a claim, so a bar may be drawn only if the next run can **recompute**
its height from the repository's source. `reference/charts.md` owns that rule, and the
tick-provenance test with it — a committed report of a run is not a property of the code.

## Layout conventions

**Horizontal bars by default**, which is `reference/charts.md` §3's position and it
wins: horizontal survives long category labels, and a rotated axis label is the tell
that the column form was wrong. The coordinate table below is the vertical
arithmetic; for the horizontal form the value axis sits at `x=96`, bar thickness 40,
pitch 56, the category name inside the bar and the value outside its cap, on a
1200-wide board. Reach for vertical columns when the category names are short and
ordered by something read left to right, such as time — or when they are long enough to
need rotating. The board is `0 0 1200 600`, every number below on the 4-unit grid.

| Part | Value |
| --- | --- |
| Plot area | `x` 96 → 1152, `y` 48 → 504 (1056 × 456) |
| Zero baseline | `y = 504`, stroke `var(--ink)` at 0.25, width 1 |
| Value axis | `<line>` at `x = 96`, `y` 48 → 504 |
| Tick labels | right-aligned at `x = 88`, mono, `data-role="metadata"` |
| Column pitch | 132 — eight pitches is 1056, the plot width exactly |
| Bar width | 92, leaving a 40-unit gutter (20 each side of the pitch) |
| Bar `x` | `116 + 132k`, `k` 0…7 |
| Category label | centred under the bar, sans, `data-role="label"` |
| Value label | 10 units above the bar cap, mono, `data-role="metadata"` |

Gridlines are 4–6 horizontals in `var(--rule)` at hairline weight. At a plot height of
456 the only tick spacings that stay on the grid are **76** (six intervals) and **152**
(three); if the data wants five ticks, move the plot top rather than the ticks off-grid.

The bar stays at or above half the pitch — 92/132 is 70%, room to widen the gutter for
six bars but not to narrow the bar for ten.

## Budget

From `scripts/diagrams.json`: **`max_nodes: 8`** bars, **`max_edges: 0`**, `max_focal: 2`,
`max_zones: 3`. The unit is the bar, so each one is a `<g data-node="true">`.

Two accented bars is the ceiling the checker enforces; one is usually the honest answer,
since the comparison is already carried by the heights. Past eight bars, group into
periods or split into an overview and a detail board — the type does not shrink to fit,
and whatever came out goes into `budget_cuts[]`.

**There are no connectors on this type**, so §4 of `reference/diagram-grammar.md` does
not apply. What replaces it is axis honesty: the baseline sits at zero, every tick value
is recomputable, and a truncated range is not presented as a trend. A bar chart whose
axis starts above zero is drawing a difference and labelling it a magnitude.

## Primitives

```svg
<g data-node="true">
  <!-- opaque mask, so nothing behind a translucent fill shows through -->
  <rect x="116" y="Y" width="92" height="H" fill="var(--paper)"/>
  <rect x="116" y="Y" width="92" height="H"
        fill="var(--muted)" fill-opacity="0.15"
        stroke="var(--muted)" stroke-width="1"/>
  <text x="162" y="Y-10" data-role="metadata" data-bg="paper"
        class="val" text-anchor="middle">1.8k</text>
</g>

<!-- the focal bar: same geometry, plus data-focal, plus the accent treatment —
     fill var(--accent) at 0.12, stroke var(--accent) at 1.25, accent label -->
```

Every value goes through a declared custom property; a raw hex is a `svg_check.py` error.
Grouped bars put two columns inside one pitch and accent the primary series only; stacked
bars accent one segment and label the total above the cap. Either way each drawn bar
counts one `data-node` against the eight.

## Motion

Bars do not grow. §11 of the grammar forbids animating `width`, `height` or a `scale`
transform on a `[data-node]`, and a bar is a node — so the grow-then-hold idiom that
belongs to a bento cell's chartlet is not available to a board tagged
`data-diagram="bar"`. The height *is* the measurement, and a board reading a different
value at `t=3s` than at `t=9s` is correct one frame in twelve.

What may loop, at 8–14s and seam-exact: an ordered emphasis walking the categories left
to right, changing `fill-opacity` or `stroke-width` and nothing else; or a hairline sweep
along a gridline. The bar caps, the baseline and every label stay where the data put them.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| A baseline above zero | Distorts the magnitude comparison the type exists to make |
| More than eight bars, ungrouped | Illegible at embed width; the pitch falls under the label |
| The accent role on three or more bars | The focal decision has not been made |
| 3-D extrusion, or a shadow under the cap | Depth encodes nothing and reads as a second value |
| Category labels rotated past 45° | Shorten the names or turn the chart horizontal |
| A gutter wider than its bar | Reads as missing categories rather than spacing |

## Specimen

`docs/samples/types/bar.svg` — the type drawn at full width, gated as its own `data-diagram`.
