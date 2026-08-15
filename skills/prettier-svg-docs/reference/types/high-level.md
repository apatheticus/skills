# High-level

An end-to-end data stack on a container cluster — ingest → store → query → analyse →
visualize, under a banner naming each phase. Ported from
`cathrynlavery/diagram-design` (MIT © 2025 Cathryn Lavery); see `THIRD_PARTY.md`.

**Best for:** the one-page answer to *what is this platform made of, and what stage does
each piece serve?* Not how data moves through it (`data-flow`), and not what it
integrates with (`dp-integration`).

Mechanics live in `reference/diagram-grammar.md`: elbows and ports §4, zones §8, node box
§6, connector labels §7, legend §9.

## Layout conventions

**The chevron banner is the legend, and that holds only if every node's centre sits on its
chevron's centre.** `node_cx == chevron_cx` is the rule this type cannot bend. A node
parked half a column off its phase turns the banner into decoration, and nothing else on
the board recovers the mapping.

**Two zones, in two materials.** External sources sit in a dashed rectangle on the left,
dashed because the signal is *outside the cluster*; everything the platform runs sits in
a solid-bordered cluster boundary. A solid border on the sources erases the only
structural claim the left column makes.

**Cross-cutting concerns are bands, not nodes.** An orchestration bar spans the cluster
top; identity, observability or backup bands span the body width below it. A band emits
no connectors except the bar's trigger drops — dashed verticals into the nodes it
schedules — and a node fanning out past three targets is an unnamed hub.

**A right-hand strip of rotated chevrons labels the bands.** Labels only: no node is
assigned to a vertical chevron and the strip emits no connectors. Each pairs one-to-one
with a band or the bar; one with nothing to pair with is an unfinished diagram.

### Geometry

Upstream measures this type on a 1000-unit canvas, so every number below is its source
value ×1.2, rounded to the 4-unit grid. The node box is the exception, pinned to §6's
`152 × 80` so a service is the size of a component anywhere else.

```
strip_w = 36   strip_x = 1164   strip_margin = 12   # margin stays empty
effective_w = 1152               # every horizontal element ends here
banner_y = 8   banner_h = 36     # notch 16, minimum chevron width 144
zone_y = 48    zone_h = 404      # source zone and cluster share both
bar_y = zone_y + 16              bar_h = 52
node_top = zone_y + 28           # 144 in a column carrying the bar
node_gap = 20  src_top = zone_y + 24, stride 104
band_y(k) = 464 + k * 52         # bands 48 tall
```

That is a 608-unit height with one band and §9's legend.

## Budget

Nine services, twelve connections, two focal, three zones — the defaults; `high-level`
declares no override in `scripts/diagrams.json`. The count is every `[data-node]`:
sources, cluster nodes, and the orchestration bar, which is a service with a name, an
icon and outgoing edges. Bands carry `data-zone` and spend the zone ceiling instead.

Both bind harder than they look, so do the arithmetic first. Three sources, five cluster
services and one bar is nine exactly; the source zone and cluster boundary are two zones,
leaving room for one band. Upstream's canonical example — four sources, five services, a
bar and two bands — is a node over and a zone over. At that size the honest move is two
diagrams, the stack and the concerns wrapping it, with the split in `budget_cuts[]`.

## Primitives

**Chevron.** A polygon with a 16-unit notch: leftmost flat-backed, middle ones notched
left and pointed right, rightmost flat-fronted so it lands square on `effective_w`. Fills
alternate between two `ink` steps; labels are `metadata` role in `paper`. Vertical
chevrons mirror this top-to-bottom, labels rotated −90°.

**Four numbers in the block above were measured against a board this type cannot legally draw, and a budget-legal board needs them changed.** `zone_y = 48` puts the zone eyebrow inside the banner's `8..44` band; `zone_h = 404` is sized for a source column of three or four at stride 104 and leaves about 128 units of dead space under one source; `src_top = zone_y + 24` then floats that source 72 units above the cluster row and forces an elbow through a 32-unit gutter; and `strip_x 1164 + strip_w 36` is exactly 1200, so the label strip touches the canvas edge. The specimen at `docs/samples/types/high-level.svg` uses banner 32, `zone_y` 64, `zone_h` 296, the source aligned to the cluster row, `strip_x` 1152 and a board height of 504. Prefer those.

## Motion

The banner is the structure, so the banner is what may move: an ordered emphasis walking
phase by phase, each chevron lifting in opacity for its turn and returning where it
began. It reads as the path through the stack without asserting a byte of throughput. The
alternative — not both on one board — is one flow token on the ingest → serve path over
fixed geometry. 8–14s, seam-exact, and nothing moves geometry (§11): the cluster boundary
never moves at all, because a boundary that breathes is one whose extent is a guess.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| A node centre off its chevron centre | The banner stops being a legend |
| No banner at all | Nothing maps a column to the stage it serves |
| More than one storage hub marked focal | The hub is what makes it a platform |
| A solid border around the external sources | Deletes the left column's one claim |
| A vertical chevron over the cluster, not in the strip | Overlaps what it annotates |
| A vertical chevron with no band or bar to pair with | Labels a concern not drawn |
| An identity band inside the cluster boundary | It applies to everything, not just what is inside |
| Orchestration drops drawn solid | A schedule trigger is not a data flow |

## Specimen

`docs/samples/types/high-level.svg`.
