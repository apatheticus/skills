# Org chart

Ownership, reporting, routing and escalation — a hierarchy whose nodes are accountable
for something.

Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery); see `THIRD_PARTY.md`.

**Best for:** human teams, agent teams, support escalation maps, role ownership, routing
maps. Choose it over `tree` whenever the nodes are people, agents, teams or owners: a
tree shows parent → child, an org chart shows who receives the work, how they are
invoked, and where coverage runs out. Choose it over `swimlane` when the question is
*who does what* rather than *in what order*.

## Layout conventions

- The root owner — the front door, the thing that receives ambiguous work — sits top
  centre and takes the one focal treatment.
- Tier 1 is departments, pods, queues or routing buckets, horizontally aligned on a
  single baseline. Tier 2 is the named owners and specialists. More than eight
  specialists means grouping nodes at tier 1, not a longer row.
- Connectors are the same shape as `tree`: vertical drop from the parent's bottom edge,
  horizontal bus, vertical drops into each child's top edge, quarter-arc elbows at
  `r=10`. No diagonals.
- A node answers three questions when the space is there, and the three lines make it
  taller than the grammar's default box — **180×96** rather than 152×80:

  | Line | Role | Content |
  | --- | --- | --- |
  | Name | `label`, sans, ≥18 units | The role, person, team or agent |
  | Invocation | `metadata`, mono, ≥16 | Slack handle, queue, issue prefix, trigger |
  | Scope | `metadata`, sans, ≥16 | Two to four ownership words, not a sentence |

- Owners that are not yet wired up get the grammar's optional treatment (`ink` at 0.02,
  dashed `4,3`) rather than being left off. A missing route is operationally
  interesting; an absent box says nothing.
- Escalation and approval rules go in a side callout or the legend strip, not into extra
  org nodes. Approval gates that genuinely exist take the security-boundary treatment so
  they read as a different thing from reporting.

Node treatment maps straight onto grammar §2: front door → focal, team or pod → the
service treatment, an active individual owner → store, an inactive one → external, an
unwired one → optional, an approval gate → security boundary.

## Budget

`scripts/diagrams.json` overrides the node ceiling for this type: **12 nodes**, with
`max_edges: 12`, `max_focal: 2` and `max_zones: 3` at the defaults. The unit counted is
the role.

Three limits the checker cannot see, so they are questions to answer before drawing:
depth stays at 4 tiers; no parent carries more than 5 direct reports (past that,
introduce a grouping node); and at most 2 side callouts.

One focal node, not two, even though the file allows two. The front door is the single
thing a reader has to find on an org chart, and a second accent costs exactly that.

Past 12 roles, build an overview chart plus one detail chart per pod, and record what
the overview drops in `budget_cuts[]`.

## Motion

The only motion that earns its place here is a routing trace: an ordered opacity or
stroke-weight emphasis stepping front door → bucket → owner along one escalation path,
8–14s, seam-exact. It answers the question the chart exists for.

A dash offset on a single dashed connector is also fine. Everything else is off — no
node moves, no tier reflows, no name animates (grammar §11). A chart whose boxes drift
cannot be read as an ownership claim, because ownership is exactly what position is
carrying.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| Reaching for `swimlane` when the question was "who owns this?" | Lanes explain process, not accountability |
| Every role drawn as an identical box | Hides the front door, the specialists and the gaps |
| A full job description inside a node | Scope is 2–4 words; detail belongs in the prose |
| An unwired owner drawn as an active one | Use the optional treatment so the gap is visible |
| Slack handles repeated in the surrounding paragraph | The sublabel already carries the invocation path |
| A legend floating in the chart area | The strip sits below every node (grammar §9) |
| Six direct reports under one parent | Introduce a grouping node |

## Specimen

`docs/samples/types/org-chart.svg`.
