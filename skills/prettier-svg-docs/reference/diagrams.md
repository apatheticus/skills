# Diagrams — the router

A **style** decides what a visual is made of. A **type** decides what it is *shaped
like*. This file picks the type. Read it before drawing any structural visual, then
read exactly one `reference/types/<slug>.md` for the layout grammar you will actually
build against — and `reference/diagram-grammar.md` for the parts every type shares.

Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery). Provenance and what was deliberately left behind are in
`THIRD_PARTY.md` at the repo root.

The machine half of this catalog is `scripts/diagrams.json`. The two must agree
slug-for-slug: `svg_check.py` reads the budgets from there and `validate.mjs` fails the
build if a slug there is missing from this skill's frontmatter.

---

## 0. The don't-draw test

Ask before anything else: **would the reader learn more from this than from a
well-written paragraph?** If no, write the paragraph.

Concretely, don't draw when:

| The content is… | Do this instead |
| --- | --- |
| A list of things | A table or bullets |
| A simple before/after | A two-column table |
| One shape with a caption | Write the sentence |
| Something a three-column table says just as well | Write the table |

This is not a formality. A doc with three honest diagrams reads better than one with
seven, and the budget in `audit_visuals.py` exists because that is the common failure.

## 1. Declare the type before you draw

The type is the one decision no later edit repairs. Changing a style is a re-render;
changing a type is a re-author — different node count, different axis, different
connector grammar, different `viewBox` height.

So the plan phase names it. Every row of the per-visual plan table carries a
`diagram_type` column, the value is written into `viz.json`, and the asset root carries
`data-diagram="<slug>"`. A visual with both has been through this gate and is not
asked again.

## 2. Pattern first, when behaviour carries the meaning

When the thing the reader must understand is *behaviour, state, enforcement or risk* —
not merely which parts exist — choose a **semantic pattern** first, then take its
nearest visual type as the layout grammar. Load `reference/diagram-patterns.md` for the
pattern's own primitives and its tighter budget.

| The reader must understand… | Pattern | Nearest type |
| --- | --- | --- |
| Many arrivals competing for finite service capacity | Fan-in queue / bottleneck | `data-flow` |
| Repeated questions, inputs, controls and outputs across stages | Stage framework with semantic slots | `process` |
| A loose conversation becoming a durable structured record | Unstructured input → structured artifact | `data-flow` |
| Why two policy decisions differ, and where they first diverge | Paired policy-evaluation traces | `flowchart` |
| Which routes cross a trust boundary and which are blocked | Secure paved road | `architecture` |
| Which controls apply at each enforcement surface | Governance / control catalog | `layers` |
| How defences reduce risk, and what risk remains | Compensating security layers | `layers` |

One primary pattern per figure. The pattern owns semantic primitives and the stricter
budget; the type still owns the page axis, connector grammar and spacing. If no pattern
matches, go straight to the type.

## 3. The 27 types

| If you are showing… | Type | Unit counted by the budget |
| --- | --- | --- |
| Components and the connections between them | `architecture` | component |
| A legacy IT landscape grouped by phase or department — the *before* state | `it-state` | system |
| Decision logic with branches | `flowchart` | step |
| Time-ordered messages between actors | `sequence` | lifeline |
| States, transitions and guards | `state` | state |
| Entities, fields and relationships | `er` | entity |
| Events positioned in time | `timeline` | event |
| A cross-functional process with handoffs | `swimlane` | step (lanes are zones) |
| Two-axis positioning or prioritisation | `quadrant` | item |
| Several entities scored across 3–5 criteria | `radar` | series |
| A reinforcing cycle where the last step feeds the first | `loop` | stage |
| Hierarchy expressed through containment | `nested` | container |
| Parent → children relationships | `tree` | node |
| Ownership, reporting, routing, escalation | `org-chart` | role |
| Stacked abstraction levels | `layers` | layer |
| Overlap between sets | `venn` | set |
| Ranked hierarchy or conversion drop-off | `pyramid` | level |
| Quantitative comparison across categories | `bar` | bar |
| Continuous trends over time | `line` | series |
| Tasks and phases on a timeline | `gantt` | task |
| Distribution and correlation between two variables | `scatter` | point |
| An end-to-end data stack on a container cluster | `high-level` | service |
| A multi-actor sequential process with data handoffs | `process` | stage |
| Multi-tier data storage with quality levels and access policies | `medallion` | tier |
| Role-scoped data flow — who does what at each pipeline step | `data-flow` | step |
| Integration topology of a data platform | `dp-integration` | system |
| Per-role or per-component access permissions | `dp-security-matrix` | cell |

Rules of thumb:

- If two types both seem to fit, pick the dominant axis. A semantic pattern may add
  behaviour-specific primitives; it never adds a second layout grammar.
- The five chart types (`bar`, `line`, `gantt`, `scatter`, `radar`) plot numbers, and
  a plotted number is a claim. `reference/charts.md` governs them: a value may be drawn
  only if the next run can **recompute** it from the repository's source.
- Past the budget? Split into an overview and a detail diagram. Do not shrink the type.

**Load exactly one `reference/types/<slug>.md` before drawing.** The index is the cheap
half on purpose — reading the whole directory costs twenty-six files you will not use.

## 4. Budgets

Defaults, from `scripts/diagrams.json`: **9 nodes, 12 edges, 2 focal, 3 zones.** The
per-type overrides live in that file and the checker reports what it actually counted.

Density target is **4 out of 10** — technically complete, not so dense it needs a
guide. Above nine nodes it is usually two diagrams.

**The remove test**, run before drawing rather than after:

- Can any node come out and the reader still understand?
- Do any two nodes always travel together? Then they are one node.
- Is any arrow's relationship already obvious from the layout? Then delete the arrow.
- Does colour or shape already say what a label says? Then delete the label.

**Cuts are recorded, not remembered.** Anything the budget forces out goes into
`budget_cuts[]` in that visual's `viz.json` and is surfaced in the run report. The
point is not bookkeeping: an unrecorded cut is indistinguishable from an omission
nobody noticed, and the next run cannot tell which it was.

## 5. Universal anti-patterns

These are the marks of a generated schematic rather than a designed one. Type-specific
ones live in each `reference/types/<slug>.md`.

| Anti-pattern | Why it fails |
| --- | --- |
| Identical boxes for every node | Erases hierarchy |
| The accent role on every "important" node | The accent is 1–2 editorial marks, not a signalling system |
| Mono type as a blanket "developer" font | Mono is for technical content — ports, commands, URLs. Names are sans. |
| A legend floating inside the diagram area | Collides with nodes |
| An arrow label with no mask | The stroke bleeds through the text |
| An arrow label sitting on its own connector | The reader loses the line they were tracing |
| A label mask overlapping a node | Nodes paint after labels; the fill clips the text to a fragment |
| Diagonal or slanted connectors between off-axis nodes | Rounded right-angle elbows are mandatory |
| Two connectors overlapping or sharing a path | Each connection must be independently traceable |
| Two connectors sharing one attach point on a box | Fan the attach points ≥12px apart |
| A connector routed behind a box that is not its endpoint | Reroute; the dashed-transit exception is narrow |
| Vertical `writing-mode` text on an arrow | Unreadable |
| Reproducing a Mermaid renderer's layout | Imports automatic spacing instead of an editorial one |

## 6. Before you output

The technical half of this list is `svg_check.py`'s `diagram` class, and it is not
repeated here — the checker fails loudly on orthogonality, label geometry, the grid,
budgets and legend placement, and a rule the machine owns does not need saying twice.
Run it. What remains are the questions no checker can answer:

- **For each box on this diagram, which file, config or entry point proves the thing
  exists?** Name it, or cut the box. This is the anti-fabrication rule in its only
  useful form — it produces evidence rather than assent.
- Would a table or a paragraph do the same job? If yes, you should not be here.
- Which one or two elements actually deserve the accent role? If the answer is "four",
  the focal decision has not been made yet.
- Does the legend cover every treatment used, and nothing that isn't?
- Does the collapsed Mermaid source under this diagram say the same thing the picture
  says, and is its Mermaid type consistent with `data-diagram`?
- Is the motion still explaining the same picture at every phase of the loop? Motion
  may not move geometry — see `reference/svg-animation.md`.
