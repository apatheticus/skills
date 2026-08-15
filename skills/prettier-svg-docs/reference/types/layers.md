# Layer stack

Stacked abstraction levels: full-width bands, one above another, where vertical position
carries the whole meaning.

Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery); see `THIRD_PARTY.md`.

**Best for:** the OSI model, a CSS cascade, a context hierarchy, a tech stack, a memory
hierarchy. The test is whether every band sits genuinely above or below its neighbours —
if the bands are peers, this is a `swimlane` or an `architecture` diagram.

## Patterns that land here

`reference/diagram-patterns.md` names `layers` as the nearest type for two semantic
patterns, and both narrow this file rather than replace it: **§6 governance / control
catalog**, when the reader has to know where each control is enforced, and **§7
compensating security layers**, when the point is what risk each defence leaves for the
next one. Load the pattern for its own primitives and its tighter budget; the band
geometry, type ramp and anti-patterns below still apply underneath it.

## Layout conventions

- Horizontal bands stacked vertically, every band at the same `x` and the same width.
  On a 1200-unit board that is `x=40, width=1120`; anything from 1000 to 1120 works as
  long as it never varies between bands.
- Band height **72–88 units**, identical for every band unless a difference is being
  asserted deliberately and the figure says what it means.
- Each row reads left to right:

  | Position | Role | Content |
  | --- | --- | --- |
  | Far left | `metadata`, mono, ≥16 units | Index tag — `L3`, `07`, `APPLICATION` |
  | Left of centre | `label`, sans, ≥18 | Layer name |
  | Far right | `metadata`, mono, ≥16, `muted` | Sublabel or note |

- Divider between bands: a 1-unit hairline in `rule`. The outer silhouette is 1 unit of
  `ink` or `muted`.
- Fills: either alternating `paper` and `surface`, or `paper` throughout with hairline
  dividers doing the separating. Pick one for the figure and hold it.
- A direction indicator lives in the **left margin, outside the stack** — a small
  arrow plus a mono label such as `abstraction ↑` or `packets ↓`. It is what stops a
  reader guessing which end is the bottom.
- Bands are `[data-node]`, not `[data-zone]`: they are the counted unit, and a zone here
  would be a grouping *of* bands.

## Budget

`scripts/diagrams.json` overrides the node ceiling to **6**, which is the layer count —
four to six is the working range and three is fine. `max_edges: 12`, `max_focal: 2` and
`max_zones: 3` stay at the defaults, though a clean layer stack usually draws no
connectors at all; the vertical adjacency *is* the relationship, and an arrow between
two touching bands repeats what the layout already said.

One accent band, not two: the bottleneck, the layer that pays rent, the one under
discussion. Stroke plus a subtle tint, per grammar §2.

Past six layers, split into an overview stack whose bands are groups and a detail stack
per group, and record what the overview merged into `budget_cuts[]`. Compressing seven
bands into the same height instead drives the band under the type floor.

## Motion

The honest loop here is a traversal: an ordered opacity or stroke-weight emphasis moving
up or down the stack one band at a time, in the direction the margin indicator points,
at 8–14s and seam-exact. It re-states the axis rather than decorating it. A flow token
travelling a fixed path down the left margin does the same job.

No band may move, resize or reorder (grammar §11), and the index tags never animate —
a stack whose bands shift is a stack whose ordering claim is only true in some frames.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| Bands that are not actually hierarchical | Use `swimlane` or `architecture` |
| Skipped numbering with no explanation | A missing L4 reads as a mistake, not an omission |
| A different colour per band | The hierarchy becomes invisible and the accent means nothing |
| Band heights varying for no stated reason | Height reads as importance whether or not it was meant to |
| Band widths varying | Breaks the one thing that makes a stack a stack |
| No direction indicator | Nothing says which end is the bottom |
| Arrows between adjacent bands | Adjacency already carries it |

## Specimen

`docs/samples/types/layers.svg`.
