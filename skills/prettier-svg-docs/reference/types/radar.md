# Radar — shape comparison across criteria

Three to five entities on one normalised scale, compared by the shape each one makes.

Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery), re-expressed for the 1200-unit board. See `THIRD_PARTY.md`.

**Best for:** capability matrices, backend or framework evaluations, team scorecards —
where a table has run out of room and each option's *profile* is the point.

**This is a chart, and a plotted number is a claim.** `reference/charts.md` governs the
values: one may be drawn only if the next run can recompute it from the repository's
source. A committed benchmark log is a snapshot of a run, not a property of the code.

## Layout conventions

- **Three to five axes**, equally spaced on a regular polygon, first at the top (`−90°`)
  going clockwise. Above five, split the chart or write the table.
- **Five concentric rings** at `0.2 / 0.4 / 0.6 / 0.8 / 1.0` of the radius, closed
  polygons through the vertices at that fraction. Inner four in `rule` at 0.10, the outer
  at 0.20 — a hint stronger, to give the chart an edge to sit against.
- **Spokes** centre to outer vertex, `rule` at 0.20, no arrowheads: a spoke is a scale,
  not a direction of travel.
- **One word per spoke**, sans at the `label` floor (18), 20 units outside the outer ring
  along the axis vector. Top and bottom `middle`, right `start`, left `end`.
- **Scale ticks on the top axis only**, `metadata` (16) mono, anchored `end` at `cx − 8`.
  Numbers on every spoke turn the chart into a form.
- **Series polygon:** 1.5 stroke, same value filled at 0.18; the focal steps to 1.8 — a
  weight bump, not a second colour.
- **Vertex dots on the focal series only**, `r=6` — what keeps four or five overlapping
  polygons readable. On every series it is a bead curtain.
- **There is no `series-3` role.** `accent` is the focal series and nothing else; the
  rest separate by stroke weight, dash and fill opacity against `muted` and `ink`, or by
  whatever extra roles the repo's own palette declares.
- **Legend** below the plot per `diagram-grammar.md` §9, entries ~200 units apart. The
  swatch is a **20×12 rectangle**, not a circle — it must show stroke and fill together,
  which is how the reader tells the series apart.
- Order inside §5's: rings → spokes → labels → ticks → non-focal series, largest first →
  focal series → focal dots → legend.

## Math

For axis `i` of `N`, value `v` on scale `S`, centre `(cx,cy)`, outer radius `R`:

```
angle = −π/2 + 2π · i / N
x = cx + (v / S) · R · cos(angle)
y = cy + (v / S) · R · sin(angle)
```

At `N=5, cx=600, cy=400, R=240` the outer vertices sit at these offsets from centre —
axes 3 and 4 mirror axes 2 and 1 about `x=600`:

```
i=0 (0,−240)   i=1 (228,−74)   i=2 (141,194)   i=3 (−141,194)   i=4 (−228,−74)
```

Ring `f` is `centre + f × offset`; a vertex at value `v` is `centre + (v/S) × offset`,
and a series is one `<polygon>` of those points.

The skeleton sits on the 4-unit grid: `cx`, `cy`, `R`, the legend, the label baselines.
**Plotted vertices do not**, and must not be nudged onto it — they are the data, and
rounding one moves a score to tidy a `points` string.

## Budget

From `scripts/diagrams.json`: **5 series, 0 edges**, and **`max_focal` is 1** — the only
type in the catalog that tightens the focal rule. The reason is this shape's: four or
five translucent polygons already overlap and compete for the eye, so a second accent
does not add emphasis, it cancels the first. One recommended option, or none.

No connectors either — a spoke is a scale, a polygon edge belongs to a series, so neither
carries `data-edge` and §4 has nothing to check.

Past five, split by question — "best on latency", "best on operations" — rather than
shrinking strokes; record it in `budget_cuts[]`.

## Motion

No point moves. A polygon growing from the centre plots a value nobody measured in every
frame before the last — the one thing a chart may not do — and `points` is geometry the
checks read as committed.

Emphasis may loop: each series' fill opacity lifting in turn while the others drop back,
one at a time, on a duration that divides `data-loop-s`. That is the honest equivalent of
hovering a legend entry, and every frame of it is a correct chart. Rings, spokes, ticks
and labels hold.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| More than five series | Mush — split by question, or write a table |
| Axes on different native scales | Radar compares shapes; unnormalised axes compare nothing at all |
| An inner ring starting above zero | Amplifies differences; if they look small, small is the truth |
| Vertex dots on every series | A bead curtain — dots are what marks the focal one |
| A two-series radar | A paired bar chart or a two-row table is clearer |
| Non-quantitative axes | "Speed", "colour" and "year" cannot share a scale |
| Mono axis labels | Names are sans; mono is for ticks and technical sublabels |

## Specimen

`docs/samples/types/radar.svg`.
