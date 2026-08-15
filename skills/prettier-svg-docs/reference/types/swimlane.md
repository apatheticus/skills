# Swimlane

A process split into horizontal bands, one per owner, so a handoff is visible as a step
crossing a line. Ported from
[`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery); see `THIRD_PARTY.md`.

**Best for:** cross-functional processes, RACI-style flows, vendor handoffs, multi-team
shipping workflows — anything where *who does it* matters as much as *what happens*.

## Layout conventions

| Part | Value |
| --- | --- |
| `viewBox` | `0 0 1200 H`, with `H = 96 + lanes × 128 + 72` for the legend |
| Lane band | 128 units tall; the 80-unit node sits centred, 24 units clear top and bottom |
| Lane label gutter | `x=40` → `x=200`, mono eyebrow, right-aligned |
| Step area | `x=200` → `x=1160` |
| Column pitch | 192 — a 152-unit node plus a 40-unit gap |
| First column | `x=224`; columns then at 416, 608, 800, 992 |
| Lane divider | 1-unit hairline in `rule` between bands |

Time runs left to right across every lane at once, so a step's column is its position in
the process and its band is its owner. A step belongs to exactly one lane: a box
straddling two bands means the owner was never decided, and drawing it that way hides
the decision rather than making it.

Lanes need not hold equal step counts. A lane with one step is a legitimate result — it
says that owner touches the process once, which is often the finding.

**Handoffs are the edges that matter.** A connector crossing a lane boundary is where
coupling and latency live, so the accent role goes to the one handoff that costs the
most, not to a step. Everything else is `muted`. Connectors follow the grammar's six
rules unchanged: rounded right-angle elbows, fanned attach points, no overlaps.

## Budget

From `scripts/diagrams.json`: **5 zones, 9 nodes, 12 edges, 2 focal.**

Lanes are counted as **zones, not nodes** — `max_zones: 5` is the swimlane's one
override, and `max_nodes` stays at the default 9. So five lanes and nine steps is the
ceiling, and the two numbers are independent: five lanes carrying two steps each is
already over on steps, while three lanes of three is comfortable.

This is also why the shared grammar caps ordinary zones at three and points here: a
diagram wanting four or five grouping bands *is* a swimlane, and should declare itself
as one rather than stretching `architecture`.

Past nine steps, split by phase — an overview swimlane of the whole process, then one
detail board per phase — rather than adding a sixth lane or shrinking the nodes.

## Primitives

```svg
<!-- one lane: a zone, not a node -->
<g data-zone="true">
  <rect x="200" y="LANE_Y" width="960" height="128"
        fill="var(--ink)" fill-opacity="0.02"/>
  <line x1="40" y1="LANE_Y" x2="1160" y2="LANE_Y"
        stroke="var(--rule)" stroke-width="1"/>
  <text x="184" y="LANE_Y+68" data-role="metadata" data-bg="background"
        text-anchor="end" class="eyebrow">PLATFORM</text>
</g>
```

Lane eyebrows sit in the gutter at the `metadata` floor of 16 units. Steps are the
standard node box from `reference/diagram-grammar.md` §6 — 152×80, name at the `label`
floor of 18.

## Motion

The process is sequential, so the honest loop is an ordered emphasis: each step
brightening in process order, one at a time, around the ring of columns and back to the
first, at 12s. A dash-offset march along the handoff connectors reads well and stays
inside the contract, because a dash offset changes no coordinate.

Motion never moves geometry, and this type has a specific temptation: a token that
*slides between lanes* to dramatise a handoff. That token is fine — it is a free
element on a fixed path. Animating the step box itself, or a connector's `d`, is not:
the lane a box sits in is its owner, and a box that travels has changed owner mid-loop.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| An unlabelled lane | The lane is the owner; without the label it is empty space |
| A step drawn across two lanes | Pick one owner — that is the decision the type exists to force |
| Connectors snaking backwards repeatedly | Reorder the steps; one genuine return loop is fine, four is a layout failure |
| Padding lanes to equal step counts | Invents work to make the picture symmetrical |
| The accent on a step rather than a handoff | The costly edge is the finding here |
| A sixth lane | Over the zone budget, and past five bands the reader loses the row |

## Specimen

`docs/samples/types/swimlane.svg`.
