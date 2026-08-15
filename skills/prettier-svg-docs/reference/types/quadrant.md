# Quadrant — two-axis positioning

A cross of two independent axes, with items placed where they actually fall.

Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery), re-expressed for the 1200-unit board. See `THIRD_PARTY.md`.

**Best for:** prioritisation (impact × effort), positioning (reach × frequency),
portfolio maps, and 2×2 decision frames.

## Layout conventions

- **A 1-unit `ink` cross through the centre**, single-ended arrows outward, stopping
  80–100 units inside the `viewBox` edge so the labels have somewhere to live.
- **Axis labels are one word at each tip.** No arrow glyphs in the text (`↑`, `→`), no
  parentheticals, no HIGH/LOW modifiers. The word is the label. `metadata` floor (16),
  uppercase, tracked, regular weight — bolding them makes the frame shout its own
  scaffolding. Never label the midpoint, and never sit a label on the axis line.
  - top tip: `text-anchor="middle"`, 16 above · bottom tip: `middle`, 24 below
  - left tip: `end`, 16 left · right tip: `start`, 16 right — both `dominant-baseline="middle"`
- **Items are small dots at `r=6`** in a `<g data-node="true">`, the name 12 units clear at the
  `label` floor. A label may not cross an axis line; flip its anchor rather than let it
  straddle the cross.
- **Nothing sits on an axis.** A point on the line has no quadrant, and the reader will
  assume you could not decide.
- The accent goes on one item — usually the do-first corner.
- Quadrant grounds stay unfilled, or take one flat 2% `ink` wash at most. Four coloured
  cells is decoration; position and label already carry the reading.

Axis cross at `(600,440)` on `viewBox="0 0 1200 880"`: tips at `y=144` and `y=736`,
`x=184` and `x=1016`; label baselines at `y=128`, `y=760`, and `x=168` / `x=1032`.

```svg
<g data-node="true" data-focal="true">
  <circle cx="792" cy="288" r="6" fill="var(--accent)"/>
  <text x="808" y="292" data-role="label" data-bg="paper"
        text-anchor="start" class="item">Token cache</text>
</g>
```

## The scenario variant

Same axes, four **named** cells instead of positioned dots. Use it when the reader should
leave with four named bets rather than a point cloud — scenario planning, positioning
frames. Not when position *inside* a cell means anything; that is the standard quadrant.
What changes, and only this:

| | Standard | Scenario |
| --- | --- | --- |
| Axis arrows | single-ended | double-ended, `marker-start` and `marker-end` |
| Cell content | dot plus label | a name at `label` and one to three lines at `metadata` |
| Corner tag | short tag | `NN · DIMENSION-A / DIMENSION-B`, matching the axis words exactly |
| Accent | one item | one whole cell — 4% `accent` wash, `accent` stroke, `accent` corner tag |
| Axis stroke | 1 | 1.2 — the axes carry more of the figure |

Cells are equal, **320×200** (320×240 when descriptions run long), set 48–76 units back
from the cross so the axes pass *between* them, not through them. Arrow tips sit 24–48
units outside the outermost cell edge. Non-focal cells take the store treatment from
`diagram-grammar.md` §2 — `ink` at 0.04, `muted` at 0.28 stroke.

## Budget

From `scripts/diagrams.json`: **12 items, 0 edges**, plus the inherited **2 focal, 3
zones**. The scenario variant spends four of the twelve.

There are no connectors. Position against the two axes is the whole relation, so §4 has
nothing to check and the failure modes below are all labelling and placement.

Past twelve items, cluster the near-identical ones into one named group with a count, or
split into an overview quadrant plus a detail of the crowded corner. Record it in
`budget_cuts[]`; do not shrink the dots.

## Motion

Item positions never animate. Position is the measurement here, so a dot that drifts is
a different score in every frame, and the checks read only the committed coordinates.

What may loop: the focal item's dot or the focal cell's wash breathing between two
opacities, or a single ordered emphasis walking the four quadrants in reading order —
one, not both. Axis strokes, arrowheads and every label hold still throughout.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| Four quadrant grounds in four colours | Colour noise weakens what position and label already say |
| An item sitting on an axis line | Ambiguous quadrant, and it reads as an undecided call |
| Unnamed axes | The positions mean nothing without the two words |
| Arrow glyphs, parentheticals or HIGH/LOW in an axis label | The tip already says which direction; the rest is clutter |
| Bolded axis labels | The scaffolding out-shouting the content |
| A corner tag that disagrees with its axis words | The reader parses it as a bug in about three seconds |
| Cells named "Scenario 1/2/3/4" in a shipped figure | Fine as a blank template, not as a finished artifact |
| Dots positioned inside scenario cells | If position matters, use the standard quadrant |
| A 3×3 or 2×3 grid | A different diagram, not a variant of this one |
| Two accented items or cells | The do-first signal only works once |

## Specimen

`docs/samples/types/quadrant.svg`.
