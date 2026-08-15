# Nested containment

Hierarchy expressed by one shape sitting inside another: outer is broader, inner is
more specific.

Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery); see `THIRD_PARTY.md`.

**Best for:** scope boundaries, a config cascade, trust zones, folder nesting, blast
radius. Reach for it when the relationship is *contains*, and for `tree` when it is
*points at*. Depth is the whole message — a nested diagram with two rings is a labelled
rectangle.

## Layout conventions

- Three to five concentric rounded rectangles at radius 10, which is the grammar's zone
  radius (§8), not the node radius.
- Consistent inset between rings: **32–40 units horizontally, 40–44 vertically**. The
  same pair for every step. Irregular insets are the tell that the nesting was drawn
  rather than measured.
- Each ring is labelled at its top-left with an eyebrow at `data-role="metadata"`
  (16 units minimum), tracking about `0.14em`, sitting on a `paper` mask rect straddling
  that ring's top border. Grammar §8 gives the mask; the ≥20 units of clearance between
  the eyebrow and the first thing inside it applies to every ring, not only the outer.
- Stroke hierarchy runs faint to firm as you go in: `rule` on the outer rings, then
  `muted`, then `ink`, then `accent` on the innermost.
- Fill steps the same direction — `ink` at 1.5%, then 2%, then 2.5% — around the
  grammar's flat 2% zone wash, with the accent tint reserved for the innermost ring
  alone.
- A small folded-corner glyph inside a ring hints at what the scope holds —
  `assets/icons/file.svg` is the stock one. Optional, and the same glyph at the same
  size on every ring that gets one.
- One or two editorial callouts in the display stack at `data-role="essential"` (20
  units minimum). Two is the ceiling; a third turns the figure into an annotated page.

## Budget

`scripts/diagrams.json` counts the container, and the override that matters is
**`max_zones: 6`** — a ring is a zone, not a node. Node, edge and focal limits stay at
the defaults: **9 nodes, 12 edges, 2 focal**.

Depth is what the budget is really about. Six rings is the hard ceiling and four is a
comfortable figure; past six the innermost ring has no interior left to hold a label at
the type floor, which is why the limit is geometric rather than a matter of taste. Any
node placed inside a ring counts against the 9 as usual, so a five-ring diagram carrying
content in every ring runs out of nodes before it runs out of zones.

One accent, on the innermost ring or on the ring under discussion. Two accents on
concentric shapes read as a gradient rather than a focal point.

Over budget: promote the inner two or three rings into their own figure and leave a
single summarising ring in the overview. Record the promotion in `budget_cuts[]`.

## Motion

Containment is a still relationship, so the loop should not suggest travel. What works:
a slow ordered emphasis stepping outward-in or inward-out, one ring at a time, at 8–14s
and seam-exact, so the reader is walked through the depth without any ring changing
size. A material pass belonging to the resolved style is also fine.

What is out, beyond the geometry rule in grammar §11: anything that scales, breathes or
pulses a ring. A ring whose `width` or `transform` animates is asserting that the scope
changes size, which is the one thing this type must not say.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| More than six rings | Information disappears inward and the labels drop under the floor |
| Insets that vary between steps | Unaligned nesting reads as accidental |
| Content inside a ring that is not part of the hierarchy | It belongs in a sibling diagram |
| The accent on more than one ring | The depth hierarchy collapses |
| Two rings at the same stroke weight | The containment order stops being visible |
| A ring eyebrow sitting clear of its own border | The label detaches from the thing it names |

## Specimen

`docs/samples/types/nested.svg`.
