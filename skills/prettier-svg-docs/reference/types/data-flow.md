# Data flow

A pipeline read across role lanes: who initiates, who processes, who publishes, who
consumes. Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery). See `THIRD_PARTY.md`.

**Best for:** a data pipeline with typed payloads and role-scoped access, where the reader
needs *who does what at each step* rather than which components exist. Prefer `swimlane`
for a business process and `process` when the stages carry the structure.

Two semantic patterns in `reference/diagram-patterns.md` name this type as their nearest
layout grammar: the fan-in queue / bottleneck (§1) and the unstructured input → structured
artifact (§3). Load that file first when one applies — the pattern owns its primitives and
the stricter budget; this file owns the axis, routing and spacing.

## Layout conventions

Lanes run horizontally, steps as columns, and a node sits where a role participates in a
step. On the 1200-unit board with 40-unit margins:

```
label_col_w = 176      header_h = 44      lane_h = 120
step_slot_w = floor4((1120 - 176) / n_steps)      # 4 steps -> 236   5 -> 188   6 -> 156
step_cx(j)  = 216 + j * step_slot_w + step_slot_w / 2
lane_y_top(k) = 44 + 120k       node_y(k) = lane_y_top(k) + 12
node_w = 152    node_h = 96     node_x(j) = step_cx(j) - 76
viewBox_h   = 44 + n_lanes * 120 + 72           # 3 lanes -> 1200 x 476
```

Six steps leaves two units of air either side of a node, so a six-step flow narrows the
node to `132` or moves to a 1400-unit board, where the floors scale with it
(`reference/diagram-grammar.md` §3).

The header strip carries one chip per step — the grammar's tag rect at `40×20`, `rx 4` —
with the step name in `metadata` beneath it. Lane names sit in the label column in
uppercase `metadata`: they are identifiers, not prose. A hairline in `rule` divides each
lane and closes the label column's right edge.

Node offsets are from its top-left: the role chip is the grammar's tag rect, `40×20` `rx 4`
at `+12,+8` with its text baseline at `+21`; the title is centred at `+44` in `label`; the
subtitle centred at `+64` in `metadata`; the two payload chips are `36×20` `rx 4` at
`+12,+72` and `+104,+72`, their codes in `metadata`.

Upstream fits four text rows into a 64-px node by running type at 6–9 px; at this skill's
floors that fits in no node height worth drawing, so the tool line folds into the subtitle.
A cell where a role does not participate renders nothing, and those gaps are what make the
lanes readable.

## Primitives

**Payload chips.** The left chip is what enters the node, the right is what leaves; those
positions are the whole convention, so they never swap. Codes are two mono characters, and
the legend spells each out once with a `left = input · right = output` note beside it.

**Connector styles.** Four, bound to topology rather than chosen:

- Standard handoff — `muted`, 1.5, unlabelled.
- Governance trigger enabling downstream work — `muted`, 1.5, dashed `4,3`, unlabelled.
- The focal cross-role handoff — `accent`, 1.5, carrying the one masked label.
- Published or externally consumed output — `link`, 1.5, unlabelled.

Routing follows the grammar's six rules. Same-lane connectors run between side ports;
cross-lane ones leave the source's bottom edge and enter the destination's top edge — the
grammar's port-selection rule, which differs from upstream's always-exit-right.

## Budget

From `scripts/diagrams.json`, the defaults apply: **9 nodes** (the unit is a step in a
lane), **12 edges**, **2 focal**, **3 zones**.

Lanes are zones, so three lanes is the ceiling here, not the four upstream allows. A fourth
role either merges into a neighbour — an admin lane holding only two trigger connectors is
usually part of the engineering lane — or the flow splits into ingestion and analytics.
Record which in `budget_cuts[]`.

The accent appears three times for one decision: the focal node, the connector into it, and
that step's header chip. Only the node group carries `data-focal`, so the gate counts one —
a second focal node means the central claim has not been chosen.

## Motion

The loop that earns its place is a travelling token on each fixed connector path, in
pipeline order. Do **not** march a dash offset along the handoffs on a board that also
draws a governance trigger: this type reserves a `4,3` dash for that trigger, so a
marching dash on a solid handoff makes it read as one. Original wording, kept because
it names the ordering that matters: along the connectors in pipeline
order at 8–14s, seam-exact: it says which way data travels and moves nothing the checker
measures. The focal handoff may instead carry one travelling token on its fixed path. An
empty cell stays empty for the whole loop — a lane that appears to gain a node mid-cycle is
saying something untrue about who participates.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| A placeholder box where a role does not participate | The empty cell is the fact; a box denies it |
| More than one labelled connector | Each one competes with the focal handoff's label |
| Lane names set as node names | They are identifiers, so they take uppercase `metadata` |
| Payload chips swapped or centred | Left-in, right-out is what makes them readable |

## Specimen

`docs/samples/types/data-flow.svg`.
