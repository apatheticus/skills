# Process

A multi-actor sequential process with data handoffs — who does what at each stage, and
what crosses between them. Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery); see `THIRD_PARTY.md`.

**Aliases:** `stages`, `operating-model`, `lifecycle` · **Unit counted:** stage

**Best for:** responsibility audits, data-quality gates, cross-divisional handoff maps. Prefer `swimlane` when only the order of work matters; prefer this type when each
stage's input, output and owner must be legible at a glance.

## Layout conventions

Lanes are horizontal `data-zone` bands, one per actor; stages are columns left → right.
The geometry is deterministic — the same lanes and stages give the same coordinates.

```
outer margin 40   label column 176   stage slot 176 (152 node + 24 corridor)
header strip 44   lane height  104   legend strip 96 (below every node)

lane_y_top(k) = 44 + 104k           44, 148, 252
node_y(k)     = lane_y_top(k) + 12  56, 160, 264
stage_cx(j)   = 304 + 176j          304, 480, 656, 832, 1008
node_x(j)     = stage_cx(j) - 76    228, 404, 580, 756, 932
viewBox       = 40 + 176 + n_stages*176 + 40  by  44 + n_lanes*104 + 96
```

Every value is upstream's rescaled ×1.25 onto the 4-unit grid: the `100×64` node becomes
the shared `152×80` box, the `112` slot becomes `176`, and the `80` lane becomes `104` so
the node's `12`-unit inset stays on grid. **Five stages fit the 1200-unit board** (`1136`
wide); a sixth needs `1312`, and the type floors scale with it.

Inside a node the grammar's `40×20` type tag at `(+8, +8)` carries the lane's three-letter
key, the stage name sits at the `label` floor, and then **one** metadata line — the tool or
the payload chips, not both. Upstream stacks four rows in a 64-unit box at 5–9px; at the
16-unit `metadata` floor an 80-unit box holds three. A cell with no work renders nothing
at all — no box, no chip, no label.

Payload chips are `20×12` at `rx=3`, in at `(node_x+8, node_y+56)`, out at `(node_x+124,
node_y+56)`. Codes: `LS` list, `DB` dataset, `TB` table, `FL` file, `WB` public release. **The code carries the payload kind and the chip is drawn in `muted`** —
upstream gives each code its own hex, a second colour axis fighting the accent role.

| Connector | Stroke | When |
| --- | --- | --- |
| Normal | solid `muted` | A handoff between stages |
| Focal in / out | solid `accent` | Any edge entering or leaving the focal node |
| Trigger | dashed `muted` (`4,3`) | An orchestration trigger — scheduler, override |

Routing is a single elbow: leave the source's right edge at its lane mid, run to the
destination column, bend at `r=10`, enter the destination's top or bottom. No diagonals, no
left-side entry, no exit from a top or bottom edge. Arrows are unlabelled by default — the
stage and lane already say what one means; label only a non-stage edge such as a re-test
loop.

## Budget

From `scripts/diagrams.json`: **9 stages, 12 edges, 2 focal, 3 zones** — the catalog
defaults. Lanes are the zones, so three actors is the ceiling; a fourth means the figure
is a `swimlane` (five zones there) or two diagrams. Much tighter than upstream's six lanes
by twelve stages, deliberately: at twelve stages the names fall under the type floor. Over budget, split into an overview and a detail, and record the cut
in `budget_cuts[]`.

Two focal marks: the focal stage's header chip and the node taking the critical
handoff. The accent edges into and out of that node inherit its treatment but are
not `data-focal` themselves; that attribute belongs to node groups.

## Motion

The diagram is a claim about order, so the loop restates that order: a dash marching stage
by stage along the handoff chain, or an ordered emphasis raising each stage's opacity left
to right and settling on a frame where every stage is fully drawn.
8–14s on `data-loop-s`, seam-exact. A payload token on a fixed path is the one motion that
adds information here — it says which way the handoff runs without spending a label.
Nothing moves geometry (`diagram-grammar.md` §11): lane bands do not expand, chips do not
slide, the focal node does not pulse.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| A placeholder box where an actor does no work | A grey box reads as a stage |
| Left-side entry on a vertical-dominant arrow | The arrow punctures the node face |
| More than one focal stage or focal node | The focal decision has not been made |
| An unlabelled lane | The lane is the actor; unnamed, the figure has no subject |
| Every arrow in one treatment | A trigger that looks like a handoff hides control flow |
| A lane tint on every lane | On all of them it is decoration; tint one at most |
| A per-node colour code | The accent is 1–2 editorial marks, not a taxonomy |
| Chips under a two-line stage name | Shorten the name or drop that node's chips |

## Specimen

`docs/samples/types/process.svg`.
