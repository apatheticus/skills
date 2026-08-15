# DP security matrix

A grid of platform components against roles, where each intersection states what that role
may do. Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery). See `THIRD_PARTY.md`.

**Best for:** auditing *who can do what* across a platform — rows are components (an SSO
service, a bucket, a catalog, a notebook server), columns are roles or directory groups,
and every cell holds one permission value. Reach for `dp-integration` when the question is
who can *talk to* what rather than who can *write* what.

## Layout conventions

The board is 1200 wide with 40-unit margins, so 1120 units carry the grid. The component
column is fixed and the role columns divide what is left:

```
comp_col_w    = 260                    comp_role_gap = 16      role_col_gap = 20
role_col_w    = floor4((1120 - 276 - (n_roles-1) * 20) / n_roles)
                # 2 roles -> 412   3 -> 268   4 -> 196   5 -> 152   6 -> 124
header_y      = 88     header_h = 64
row_y(k)      = 176 + 52k            row_h = 48
rows_bottom   = row_y(n_components - 1) + 48
legend_y_top  = rows_bottom + 24     viewBox_h = legend_y_top + 72
                # 4 roles x 6 components -> 1200 x 580
```

All of those land on the 4-unit grid the checker measures on `[data-node]` geometry.

The header row carries a two-line cell over the component column (`Component` in `label`, a
qualifier in `metadata`) and one filled banner per role: the role name in `label`, its
directory-group identifier in `metadata` beneath. Banners are the one place here where text
sits on a dark ground, so each banner's text carries `data-bg` naming the banner fill.

Cell treatment comes straight from the grammar's node-treatment table (§2) — no new
palette roles, no per-cell colour scale:

| Permission level | Fill | Stroke | Value text |
| --- | --- | --- | --- |
| Full / admin | `ink` at 0.08 | `ink` at 0.30 | `ink` |
| Read-write | `paper` | `ink` at 0.30 | `ink` |
| Read / select | `muted` at 0.10 | `ink` at 0.30 | `muted` |
| No access | `ink` at 0.02 | `ink` at 0.20, dashed `4,3` | `muted` |
| Focal | `accent` at 0.05 | `accent` | `accent` |

Values sit centred at `row_y(k) + 28` in `label`. The focal cell may run two lines — value
at `+20`, a short qualifier in `metadata` at `+40` — which is why the row is 48 tall rather
than the 44 a single line needs.

A cell with no entry still renders, as a no-access cell with the no-access label. An
unknown permission is neither blank nor no-access; it belongs in prose beside the diagram
until someone finds out.

## Connectors: none

`max_edges` is **0**, so this type has no connector grammar at all: no elbows to route, no
attach points to fan, no label plates to gap, and a `data-edge` anywhere in the file is a
checker error. Alignment carries the relation instead — a cell means what it means because
of the row it shares with a component and the column it shares with a role. An arrow
between two cells claims a flow the matrix cannot express; that belongs in
`dp-integration` or `process`.

## Budget

From `scripts/diagrams.json`: **24 cells** (`max_nodes`), **0 edges**, **2 focal**,
**3 zones**. The unit is the cell, so the grid's two dimensions multiply into one budget:
4 roles buys 6 components, 6 roles buys 4, and 3 roles buys 8.

That binds well before the upstream shape does — a 4 × 8 matrix is 32 cells and over budget
here. Split by component domain (storage, compute, governance) into an overview and a
detail, and record what came out in `budget_cuts[]`.

The gate allows two focal cells, and one is almost always the right answer: the focal names
*the* access rule that distinguishes this platform's posture from a generic permissions
table, and a second mark halves the first one's force. If two cells both want it, ask which
one you would keep if the reader read only one.

## Motion

There is no dash to march and no token to send, so the honest loop here is ordered
emphasis: a row-by-row sweep at 8–14s lifting each component row's stroke opacity in turn
and returning it, walking the reader down the grid the way they would read it. Cell fills
and values stay put — a permission invisible at `t=6s` is a false statement at `t=6s`, and
the cell values are this diagram's whole content. The focal stroke may breathe instead of
the sweep; not both.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| Connectors between cells | The matrix is value-driven; an arrow claims a flow it lacks |
| Whole rows or columns tinted | Collapses the grid into a list and buries the values |
| More than one focal cell | Focal marks the one critical rule; a second erases the first |
| A no-access label standing in for "unknown" | No access is a finding, unknown is an open question, and the cell cannot tell them apart |
| Inventing permission levels per cell | Four plus focal cover it; a fifth is usually wording |
| Showing how permissions are granted | That is a sequence; this shows the resulting state |

## Specimen

`docs/samples/types/dp-security-matrix.svg`.
