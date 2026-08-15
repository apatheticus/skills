# Tree

Parent → children relationships, drawn as one root, a horizontal bus per tier, and
leaves at the bottom.

Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery); see `THIRD_PARTY.md`.

**Best for:** dependency trees, taxonomies, file trees, decision breakdowns, skill
trees, module ownership. When the nodes are people, teams or agents and the reader's
real question is *who owns what*, `org-chart` is the type — a tree shows generic
hierarchy, an org chart shows responsibility.

## Layout conventions

- Root at top centre with children fanning below, or root at left with tiers running
  right. One axis per figure.
- Node box is the grammar's 152×80 (§6). A bare-name node with no type tag and no
  sublabel may drop to 152×52 or 152×64. At most **two widths** across the whole tree —
  152 plus one of 180 / 200 for a root whose name needs the room.
- Radius 8. Name at `data-role="label"` (18 units minimum), optional mono sublabel at
  `metadata` (16). The 12px/9px pair upstream draws is below both floors here.
- Tier pitch: 64 between the bottom of one tier and the top of the next, so a depth-4
  tree with 80-unit boxes occupies 4×80 + 3×64 = 512 units of height. Sibling gap 40
  or 48.
- Connector shape: the parent drops a short vertical from its **bottom** edge onto a
  horizontal sibling bus, and each child takes a vertical drop into its **top** edge.
  Quarter-arc elbows at `r=10` (grammar §4 rule 1); the bus itself is a plain `<line>`
  because its endpoints share `y`.
- Connectors paint before nodes (grammar §5), which is what lets the bus pass cleanly
  under boxes it does not own.
- Leaf treatment: a lighter stroke (1 unit against a branch node's 1.25), or the `ink`
  at 0.05 store fill, or nothing at all and let terminal position do the work. Pick one
  and hold it for every leaf.
- Depth 4 — root plus three tiers. Breadth 5 per level.

## Budget

`scripts/diagrams.json` gives `tree` the defaults: **9 nodes, 12 edges, 2 focal, 3
zones**, and the unit counted is the node. Depth 4 × breadth 5 reaches 9 nodes long
before either connector or zone limit binds, so the node count is the constraint that
actually fires.

The file permits two focal nodes; a tree usually wants one — the root **or** the leaf
under discussion. Accent both and the reader starts hunting for a relationship between
them that the diagram never draws.

Over budget: split into an overview tree carrying tiers 1–2 with one summarising leaf
per branch, plus a detail tree per branch. Shrinking the type instead produces an
illegible five-tier page. Whatever the split leaves out is recorded in `budget_cuts[]`
in that visual's `viz.json`.

## Motion

A tree is a static claim about structure, so most of it stays still. Two things move
honestly: a dash offset marching down one branch to show traversal or resolution
order, and an ordered opacity emphasis walking root → leaf. Both run 8–14s, seam-exact,
and neither touches a coordinate.

Nothing else. The bus, the boxes, the tier positions and every name are fixed — the
geometry rule in grammar §11 is what keeps a depth reading true at every frame rather
than only at `t=0`.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| Five or more tiers on one page | The leaf type lands under the floor; split instead |
| Node widths varying per node | Two widths maximum, or the tiers stop reading as tiers |
| Diagonal connectors between tiers | Elbows are mandatory and checked |
| A parent wired straight to a grandchild | A skipped level reads as a missing one |
| The accent on the root *and* a leaf | The focal decision has not been made |
| A sibling bus that touches a box it does not connect | Reroute; grammar §4 rule 5 |

## Specimen

`docs/samples/types/tree.svg`.
