# IT current-state

The legacy landscape a modernization proposal argues against — systems grouped by phase
or department, hand-offs named. Ported from
[`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery); provenance in `THIRD_PARTY.md`.

**Best for:** the *before* picture — siloed scripts, manual file shuffles, a shared drive
with no version control, one portal everything queues behind. Its companion is
`dp-integration`, which draws the after.

Mechanics live in `reference/diagram-grammar.md`: elbows and ports §4, zones §8, the node
box §6, connector labels §7, the legend §9.

## Layout conventions

**Zones are phases, two or three of them.** Collection → Processing → Dissemination, or
Survey → Analysts → Reports, or plain department names. They run along one axis and the
systems stack across it: zones left-to-right means systems stack vertically inside each.
One orientation per board.

**The hand-off labels are the argument.** `CSV`, `EXCEL`, `EMAIL`, `COPY` — this type
earns its place by naming the wire, and an unlabelled connector is the strongest claim on
the board going unmade. Labels follow §7.

**Focal is the bottleneck, not everything that hurts.** Two at most (§2), resolved by one
question: *which system, if replaced tomorrow, would remove the most manual work?*
Everything painful but not headline stays `muted` and says so in its sublabel. A system
outside the org's control takes §2's external treatment — `ink` at 0.03, dashed — rather
than a focal accent.

**Cross-cutting services go in a footer band below the zones, and emit no connectors.**
An identity manager applies to everything; wiring it to one system understates its scope
and wiring it to all of them costs more connectors than the board has. The band is a
full-width `data-zone` between the zones and the legend.

### Geometry

Upstream measured these on a 960-unit canvas, so every number below is its source value
scaled by 1.25 and rounded to the 4-unit grid.

```
pad = 20        zone_gap = 24     zone_y = 64      zone_h = 448
comp_pad_x = 24                   comp_gap = 40
comp_h = 72                       # 84 for a focal box or a two-line sublabel
comp_y(i,k) = zone_y + 36 + k * (comp_h + comp_gap)
icon = 32 square at comp_x + 16   name_x = comp_x + 56
name_y = comp_y + comp_h/2 - 4    sub_y  = comp_y + comp_h/2 + 20
attach_gap = 20                   # §4 fanning, where sources share a destination edge
```

The zone label mask breaks the zone border at `y = zone_y - 12`, 20 units tall. Three
zones of three systems fills 396 of the 448 units of zone height; the slack absorbs a
focal box and a wrapped sublabel without reflowing the board. Zone widths of
`320 / 448 / 344` sum to exactly 1200 with the pads and gaps, for a height of 608 once
§9's legend is added.

**Arrowheads have a body, and it points backwards.** The marker extends back along the
path from its endpoint, so entering a top edge while travelling *upward* buries the body
inside the box, where the node fill paints over it. Enter a top edge going down, or a
side edge going toward it — and when source and destination rows overlap in y, one
horizontal path into the side edge is the simplest route and the visible one.

## Budget

Nine systems, twelve hand-offs, two focal, three zones — the defaults; `it-state`
declares no override in `scripts/diagrams.json`.

Three zones of three systems is therefore the largest legal board, sitting on all four
ceilings at once — an outer edge, not a target. Upstream allowed sixteen components at
five per zone; that ceiling did not come across, and a landscape needing it splits by
phase, with the omissions recorded in `budget_cuts[]`.

**`zone_h = 448` has the same slack.** Against rows at 100 / 212 / 324 it leaves 116 units under the last node — "fills 396 of the 448" measures an absolute y, not a fill. The specimen uses `zone_h = 380` with widths 380 / 452 / 280, which sum to 1200 by the same arithmetic as 320 / 448 / 344, and a board height of 540. Every other number in the Geometry block is correct as published.

## Motion

The friction is the subject, so the friction is what may move: a dash offset marching the
file hand-offs, saying those copies keep being made by hand. One speed for all of them —
varying it implies a throughput measurement this type has no data for. Nothing queues,
accumulates or drains; a fan-in that visibly backs up is the bottleneck pattern in
`reference/diagram-patterns.md`, on a `data-flow` layout. And no animation moves geometry
(§11) — a landscape that rearranges itself mid-loop is wrong in at least one frame.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| Focal on everything painful | Focal is ≤2 bottlenecks; the rest carry their pain in the sublabel |
| A tiny text badge standing in for an icon | Below the `metadata` floor; use an icon or nothing |
| A footer band wired to one system | The band exists because the service is layer-wide |
| The target platform on the same board | This type is the *before*; the after is `dp-integration` |
| An arrowhead short of the destination edge, or on its centroid | Short reads unfinished; centroid buries the marker under the node fill |
| Mixed orientation between zones | The reading order stops existing |
| A hand-off with no protocol label | The one thing this type says better than a paragraph, unsaid |

## Specimen

`docs/samples/types/it-state.svg`.
