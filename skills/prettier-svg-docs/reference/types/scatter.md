# Scatter

Distribution and correlation between two continuous variables, where the relationship —
or the honest absence of one — is the message.

Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery); provenance in `THIRD_PARTY.md`.

**Best for:** finding clusters, outliers and high/low performers; showing that two
measures move together, or that they do not. Both axes are quantities — if one is a
category the type is `bar`, if it is time the type is `line`.

A plotted point is two claims at once, so it may be drawn only if the next run can
**recompute** both coordinates from the repository's source — `reference/charts.md` owns
that rule and the provenance of the ticks.

## Layout conventions

The board is `0 0 1200 600`, or `0 0 1200 672` when a legend names more than one point
treatment — §9 of `reference/diagram-grammar.md` puts it below every node.

| Part | Value |
| --- | --- |
| Plot area | `x` 96 → 1152, `y` 48 → 504 (1056 × 456) |
| X axis | `y = 504`, stroke `var(--ink)` at 0.25, width 1 |
| Y axis | `<line>` at `x = 96`, `y` 48 → 504 |
| Tick labels | Y right-aligned at `x = 88`; X centred below the baseline; both mono |
| Gridlines | 4–6 per axis in `var(--rule)`, hairline. Y ticks 76 or 152 apart, X ticks 176 or 264 — the only spacings that stay on the 4-unit grid at this plot size |
| Standard point | `<circle r="6">` |
| Focal point | `<circle r="8">` |
| Trend line | optional, dashed `4,3` in `var(--ink)` at 0.25 |
| Quadrant dividers | optional, dashed at the median `x` and `y`, labelled in mono |

## Budget

From `scripts/diagrams.json`: **`max_nodes: 30`** points, **`max_edges: 0`**,
`max_focal: 2`, `max_zones: 3`. The unit is the point, so each is a `<g data-node="true">` —
and `<g>` is not a drawn tag, so thirty wrappers cost nothing against a style's
`min_elements` floor.

Thirty is a ceiling, not a target. Below five the relationship is a sentence and the
board should not exist — the don't-draw test in `reference/diagrams.md` §0. Above thirty
the marks smear; bin into a density band, and record what came out in `budget_cuts[]`.

**There are no connectors on this type**, so §4 of the grammar does not apply — the
trend line is an annotation, not a `data-edge`, and takes no arrowhead. Axis honesty
replaces those rules. Both ranges are stated on the board; zero is included when absolute
position carries meaning and omitted when the range is tight and far from zero, in which
case the crop is labelled — an unlabelled crop turns a narrow band into a spread.

## Primitives

```svg
<g data-node="true">
  <!-- opaque mask, so overlapping marks stay countable -->
  <circle cx="X" cy="Y" r="6" fill="var(--paper)"/>
  <circle cx="X" cy="Y" r="6"
          fill="var(--muted)" fill-opacity="0.20"
          stroke="var(--muted)" stroke-width="1"/>
</g>

<g data-node="true" data-focal="true">
  <circle cx="X" cy="Y" r="8" fill="var(--paper)"/>
  <circle cx="X" cy="Y" r="8"
          fill="var(--accent)" fill-opacity="0.15"
          stroke="var(--accent)" stroke-width="1.25"/>
</g>
```

The mask keeps two near-coincident points readable as two; without it they merge into one
darker blob and the reader undercounts.

An annotated point gets a `paper` rect behind its label at the 6–10 unit gap the grammar
asks of connector plates. That rect carries no `data-label` — the attribute pairs a plate
with the connector beside it, and this type has none. Annotate the focal point and one or
two outliers; a label on every point is a table in a chart's costume.

## Motion

The cloud is still. A point's position *is* the measurement, so `cx`, `cy` and `r` are
untouchable under §11 — `r` included, where a pulsing radius reads as a confidence
interval nobody computed.

What may loop, at 8–14s and seam-exact: a halo behind the focal point breathing on
`opacity` alone at a fixed radius, or a dash offset marching along an optional trend line
— which says *fitted* rather than *measured*, the one place motion adds meaning here.
With no focal point and no trend line the board is legitimately static apart from the
resolved style's material pass; forcing motion onto it would mean animating data.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| More than thirty points | The marks smear; nothing is countable |
| A trend line over genuinely scattered data | Asserts a correlation the points do not carry |
| A label on every point | It is a table; write the table |
| Bubble-area size encoding | Area perception is unreliable and the third variable is unreadable |
| An unlabelled truncated axis | A narrow band reads as a wide spread |
| Zero forced onto a tight, distant range | Collapses the cloud into one corner |
| Overlapping points with no mask | Two readings render as one |
| A quadrant divider with no stated median | The quadrants are decorative, not derived |

## Specimen

`docs/samples/types/scatter.svg` — the type drawn at full width, gated as its own `data-diagram`.
