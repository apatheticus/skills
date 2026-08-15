# Pyramid — ranked levels and funnels

Stacked trapezoids whose widths carry a rank or a count, read top to bottom.

Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery), re-expressed for the 1200-unit board. See `THIRD_PARTY.md`.

**Best for:** hierarchies of need, prioritisation ranks, value pyramids, content
importance stacks, and conversion funnels.

## Two orientations — pick one

- **Pyramid**, point up. The narrow apex is the rarest, most valuable or most important
  level; the base is the broadest and most foundational.
- **Funnel**, point down. The wide top is the audience; the narrow end is what converted.

One orientation per figure. Mixing them means the width is measuring two different
things in one drawing.

## Layout conventions

- **Four to six levels.** `svg_check.py` caps `data-node` at 6. Below four, a two-column
  table says the same thing with less ceremony.
- **One level height for the whole stack** — 72, 80 or 88 units. Varying it makes
  height look like a second measurement.
- Each level is a `<polygon>` of four points in a `<g data-node="true">`, built from the two
  half-widths it sits between — never a `<rect>` with a skew transform, which puts one
  level's stroke weight out of step with its neighbours.
- **Widths decrease linearly, and on a funnel they are honest** — proportional to the
  count or percentage at that stage. A funnel drawn with even steps over uneven drops is
  the type's signature lie, and it is the one thing the reader trusts the picture for.
- Each level carries a **name** at the `label` floor (18), centred inside the trapezoid,
  and an optional technical **sublabel** at `metadata` (16). A drop-off figure is a side
  annotation in the margin at `metadata`, not a third line inside the shape.
- **Fill: graded tints, or one flat `surface` with hairline dividers.** Pick one. The
  flat version reads cleaner and is the better default; the graded version is worth it
  only when the gradient direction is itself the message.
- Outer silhouette is a 1-unit `ink` or `muted` stroke; dividers between levels are
  `rule`.
- One level takes the accent — the apex of a pyramid, the converting level of a funnel,
  or a bottleneck worth naming. Never the base.
- Optional left-margin axis: a hairline arrow in `rule` with a `metadata` label
  (`RARER`, `DROP-OFF`). No glyphs baked into the text.

Five levels of height 80 centred on `x=600`, `viewBox="0 0 1200 880"`. Six half-widths
bound five levels — level `k` runs between `half_k` at its bottom edge and `half_k+1` at
its top:

```
half_k = 400 − k × 72     k = 0…5   → 400, 328, 256, 184, 112, 40
y_k    = 720 − k × 80     k = 0…5   → 720, 640, 560, 480, 400, 320
```

The apex closes at a half-width of 40 rather than a point: a true vertex has no room for
the stroke join and reads as a nick. The base level, `k=0`:

```svg
<g data-node="true">
  <polygon points="272,640 928,640 1000,720 200,720"
           fill="var(--surface)" stroke="var(--rule)" stroke-width="1"/>
  <text x="600" y="676" data-role="label" data-bg="surface"
        text-anchor="middle" class="level">Activated</text>
  <text x="600" y="700" data-role="metadata" data-bg="surface"
        text-anchor="middle" class="sub">12,400 accounts</text>
  <text x="1040" y="684" data-role="metadata" data-bg="paper"
        text-anchor="start" class="delta">−38%</text>
</g>
```

## Budget

From `scripts/diagrams.json`: **6 levels, 0 edges**, plus the inherited **2 focal, 3
zones**. Two focal is the ceiling; one is almost always the honest count on this type.

Seven levels is not a taller pyramid, it is an illegible one. Either merge adjacent
levels that always move together, or split into an overview pyramid plus a detail of the
level that needed the room. Whatever comes out goes into `budget_cuts[]`.

## Motion

Widths do not animate. On a funnel the width *is* the number, so growing a level from
zero draws four counts that were never measured; on a pyramid it re-ranks the stack
every frame. Level `y` positions and the silhouette are equally fixed.

What may loop is an ordered emphasis: each level's fill or stroke opacity lifting in
turn, top to bottom, on a duration that divides `data-loop-s`, so the reader is walked
down a stack that is complete and correct in every frame. The accent level may breathe
instead. One of the two, not both.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| Seven or more levels | Illegible — compress or split |
| Even width steps over uneven drop-offs | The one thing the picture is trusted for, falsified |
| A pyramid for non-hierarchical data | Rank is not implied by stacking; use a `tree` or a `bar` |
| The accent on the base level | Dilutes the apex-is-rare reading the shape sets up |
| Mixed orientations in one figure | Width now measures two different things |
| Varying level heights | Reads as a second quantity that was never declared |
| Both graded fills and hairline dividers | Two systems for the same boundary |

## Specimen

`docs/samples/types/pyramid.svg`.
