# Architecture

Components and the connections between them: system overviews, integration maps, infra
topology. Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery); provenance in `THIRD_PARTY.md`.

**Best for:** a system a reader has to hold in one glance — which parts exist, which tier
or trust zone each one sits in, and what talks to what.

The shared grammar owns the mechanics this type leans on hardest and they are not
restated here: elbow paths, port selection and the bridge/hop are
`reference/diagram-grammar.md` §4, the zone rectangle and its eyebrow are §8, and the
node box is §6. What follows is only what `architecture` decides for itself.

## Layout conventions

**One axis, chosen before the first node lands.** The primary flow runs left→right or
top→down, and it does not change halfway. A board that starts horizontal and finishes
vertical reads as two diagrams sharing a frame, and no amount of connector craft
recovers it.

**Group by tier or by trust boundary — one or the other.** Frontend → backend → data is
a tier partition; public → private is a trust partition. They are two different
partitions of the same nodes, so drawing both puts every node inside two rectangles and
the reader cannot tell which one the node is being claimed to belong to. Pick the one
the doc is actually arguing about.

**The dash is what separates the two.** A tier zone is §8's rectangle — a 2% ink wash
with a `rule` hairline. A trust boundary is the security-boundary row of §2 instead:
`accent` at 0.05, stroke `accent` at 0.50, dashed `4,4`, with its label on a `paper`
mask over the boundary stroke at the top left, `metadata` role. The wash says *these are
alike*; the dash says *crossing this changes who is trusted*. If nothing on the board
crosses your dashed rectangle, it is a tier — draw it as one.

**Connector colour carries the boundary, so a legend rarely has to.** `muted` for a
connection inside the system, `link` for one that leaves it (§2). Between those two
roles and the dashed boundary, most architecture boards need a legend of two items or
none.

**Which nodes earn focal.** Two at most, and the candidates are narrow: the primary
integration point, the primary data store, or the node where a routing decision is
actually made. Not "the most important service" — every service is important to whoever
owns it. The answerable question is: *if this node stops, does the picture stop being
true?* Two yeses is the ceiling. Four means the focal decision has not been made yet.

**A component that lives on both sides of a boundary is two nodes.** A gateway that
terminates public traffic and calls private services is a public listener and a private
client, and drawing one box straddling the dashed line asserts the boundary runs through
the middle of a process. Draw the two halves, or move the boundary.

## Budget

Nine components, twelve connections, two focal, three zones — `architecture` declares no
override in `scripts/diagrams.json`, so it takes the defaults, and `svg_check.py` reports
the counts it actually found.

Past the budget, split into an overview and a detail: the overview keeps every zone and
collapses each to a single node, the detail expands one zone at full fidelity. Shrinking
the type instead — smaller boxes, thinner gaps — buys nothing the reader can use.
Whatever the split leaves out goes in `budget_cuts[]`.

## Motion

An architecture board is a claim about what exists, and the claim has to hold in every
frame, so motion is a reading aid rather than a simulation. One flow token travelling the
primary axis along a fixed path, or a dash offset marching one connector, is the whole
vocabulary; 8–14s, seam-exact, `data-loop-s` on the root.

What does not belong here: anything that moves geometry (§11), and anything that implies
throughput, queueing or timing. Those are claims about behaviour, and behaviour has its
own types — `data-flow` and `sequence`.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| Accent on every box that someone called important | Hierarchy collapses; the accent stops meaning anything |
| A tier zone and a trust boundary drawn with the same rectangle | The reader cannot tell alikeness from privilege |
| A dashed boundary nothing crosses | It is a tier wearing a boundary's costume |
| One box straddling a boundary line | Asserts the trust edge runs through the middle of a process |
| A bidirectional arrow where one direction is obvious from context | Two arrowheads to say what the layout already said |
| A legend floating inside the diagram area | Collides with nodes; the legend strip is below them (§9) |
| Both a tier grouping and a department grouping on one board | Every node lands in two rectangles |

## Specimen

`docs/samples/types/architecture.svg`.
