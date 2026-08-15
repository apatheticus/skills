# Semantic patterns

The 27 types in `reference/diagrams.md` say **how information is arranged**. These seven
patterns say **what a system does**. Choose a pattern first when behaviour, state,
enforcement or risk is load-bearing, then take its nearest visual type as the layout
grammar. If no pattern matches, go straight to the type.

One primary pattern per figure. A second may supply at most one supporting primitive;
if both need full treatment, split the figure into an overview and a detail. **Apply the
stricter of the pattern budget and the type budget** — semantic cells are not permission
to exceed nine nodes.

Because every visual here loops, each pattern below carries a **resting frame** rather
than a static fallback: the picture must be complete and correct at every instant of the
loop, including `t=0`. Motion may emphasise an order; it may never be where the meaning
lives, and it may never move geometry (`reference/diagram-grammar.md` §11).

Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery). See `THIRD_PARTY.md`.

---

## Routing

| The reader must understand… | Pattern | Nearest type |
| --- | --- | --- |
| Many arrivals competing for finite service capacity | Fan-in queue / bottleneck | `data-flow` |
| Repeated questions, inputs, controls and outputs across stages | Stage framework with semantic slots | `process` |
| A loose conversation becoming a durable structured record | Unstructured input → structured artifact | `data-flow` |
| Why two policy decisions differ and where they first diverge | Paired policy-evaluation traces | `flowchart` |
| Which routes cross a trust boundary and which are blocked | Secure paved road | `architecture` |
| Which controls apply at each enforcement surface | Governance / control catalog | `layers` |
| How defences reduce risk and what risk remains | Compensating security layers | `layers` |

## 1. Fan-in queue / bottleneck

**Choose it when** several producers converge on one reviewer, service, gate or
constrained resource, and the story depends on arrival rate, queue depth, wait,
capacity or backpressure.

**Required primitives.** Distinct sources; fanned ingress; an ordered queue with visible
slots and a count; a capacity or service-rate label; one constrained service point;
admitted and deferred outcomes. Label units — `8/hour`, `3 slots` — not "high".

**Budget.** ≤5 sources, ≤5 queue slots, one bottleneck, two outcomes, ≤9 nodes. Aggregate
surplus sources into one named cohort.

**Resting frame.** The representative queue at its typical depth, the numeric count and
capacity, the bottleneck label, and both outcome paths.

**Anti-patterns.** An equal-width pipeline that hides the contention; arrows merged
before they can be traced; capacity implied only by box size; the accent role used as an
overload flag rather than editorially; motion that reorders queue items.

**Nearest type.** `data-flow`; `process` when service stages rather than sources dominate.

## 2. Stage framework with semantic slots

**Choose it when** a lifecycle repeats the same semantic questions across stages —
commonly Question, Input, Governance, Output — and cross-stage comparability matters
more than message timing.

**Required primitives.** Ordered stage headers; a consistent slot grid; explicit
empty/not-applicable slots; stage-to-stage handoff; stable slot labels; one primary
output per stage. Slot order is identical in every stage.

**Budget.** 3–6 stages, 3–4 slot kinds, ≤20 populated cells, ≤2 lines per cell. If a
cell needs prose, split the figure.

**Resting frame.** The full stage × slot matrix with handoffs, and explicit `—` entries
where a slot does not apply. The schema must be legible without motion.

**Anti-patterns.** Each stage inventing its own internal layout; slot meaning carried by
position with no label; dozens of cells as fake precision; confusing stage order with
ownership lanes; shrinking type to keep one canvas.

**Nearest type.** `process`; `swimlane` only when the repeated rows are owners rather
than semantic slots.

## 3. Unstructured input → structured artifact

**Choose it when** dialogue, notes or a rambling request is elicited, normalised and
written into a durable brief, ticket, record or schema.

**Required primitives.** The source utterance; clarifying questions; extracted
field/value pairs; a named transformation; the artifact boundary; provenance links from
representative statements to fields; a visible missing/unknown state.

**Budget.** ≤4 exchanges, ≤6 artifact fields, one transformation, ≤3 provenance links.
Representative content, never a transcript.

**Resting frame.** A short source excerpt beside the completed labelled artifact, with at
least one provenance mapping drawn and any unknown fields visible.

**Anti-patterns.** A sparkle between two boxes standing in for the transformation; the
artifact drawn as another chat bubble; fields with no source; inventing certainty for a
missing fact; a typing effect that is the only place the copy is readable.

**Nearest type.** `data-flow`; `process` when elicitation has several ordered gates.

## 4. Paired policy-evaluation traces

**Choose it when** two otherwise similar requests reach different outcomes and the
reader needs rule-by-rule state plus the first divergence.

**Required primitives.** The same ordered rules on both traces; explicit status **text**
plus a symbol or shape; the inputs that differ; both final outcomes; a labelled
first-divergence marker; and a maintained distinction between `SKIPPED` (an applicable
step deliberately bypassed) and `NOT REACHED` (evaluation stopped earlier).

**Budget.** Exactly 2 traces, 3–6 rules, one first divergence, ≤12 status cells, one
outcome per trace.

**Resting frame.** Every rule state and both outcomes visible at once, with a persistent
bracket and label at the first divergence.

**Anti-patterns.** Comparing two independently ordered flows; green and red dots with no
words; treating skipped and not-reached as synonyms; highlighting every difference;
continuing a denied trace as though downstream rules had run.

**Nearest type.** `flowchart`; `sequence` only when messages between actors and timing
are also load-bearing.

## 5. Secure paved road

**Choose it when** a supported architecture creates a bounded route from intake to
deployment, and trust boundaries, permitted ingress, forbidden ingress and approved
versus blocked deploy paths are the point.

**Required primitives.** Labelled trust boundaries; actors and identities; permitted
ingress with a positive text label; forbidden ingress **terminating at the boundary**;
the approved deployment path; the blocked bypass; a privileged gate; an isolated
runtime; an audit destination. Line style and stop symbols carry the distinction, not
colour alone.

**Budget.** ≤3 trust zones, ≤8 components, ≤10 paths, ≤2 forbidden paths, one privileged
gate. Control detail goes in a separate catalog figure.

**Resting frame.** Every boundary and both permitted and forbidden routes. A blocked path
visibly stops before entry.

**Anti-patterns.** A dashed box labelled "security" with no route semantics; a forbidden
arrow that crosses into the protected zone; secrets or identity implied but unlabelled;
every component styled as trusted; a bypass path that visually rejoins the approved one.

**Nearest type.** `architecture`.

## 6. Governance / control catalog

**Choose it when** a control inventory has to be understood by *where it is enforced* —
authoring, workspace, merge/CI, deploy/runtime — and a flat checklist would hide those
enforcement points.

**Required primitives.** Enforcement-surface groups; named controls; the enforcing actor
(`code`, `platform`, `human`); timing (`write`, `merge`, `deploy`, `run`); the
bypass or exception route; coverage-and-gap notation.

**Budget.** 3–5 surfaces, 3–7 controls per surface, ≤24 controls, ≤3 attributes each.
Summarise counts only when the item list exists elsewhere.

**Resting frame.** The complete grouped catalog with surface headers and text labels for
actor and timing. Gaps and exceptions stay visible.

**Anti-patterns.** Thirty-five tiny pills; grouping by vague theme instead of enforcement
point; mixing aspirations with enforced controls; icons with no control name; claiming
defence in depth without showing surface coverage.

**Nearest type.** `layers`; `dp-security-matrix` when role permissions rather than
enforcement surfaces are the dominant comparison.

## 7. Compensating security layers

**Choose it when** no layer is perfect, each defence covers a failure the previous one
left, and residual risk must visibly narrow, transfer or remain.

**Required primitives.** An ordered threat input; named defensive layers; each layer's
mitigation; its explicit limitation or escape; a residual-risk carrier between layers;
and a final residual risk with its consequence or response. Labels or measured values —
never area alone.

**Budget.** 3–5 layers, one primary risk thread, ≤2 mitigations per layer, one final
residual-risk statement. Unrelated threats get their own figures.

**Resting frame.** The whole propagation chain: initial risk → mitigation → escaped risk
at every layer → final residual risk and response.

**Anti-patterns.** Implying the last layer takes risk to zero; equal opaque slabs with no
propagation drawn; treating audit as prevention; shrinking shapes with no numeric or
verbal meaning; reversing prevention/detection/recovery order without saying why.

**Nearest type.** `layers`; `nested` when containment boundaries rather than ordered
compensation carry the meaning.

---

## Composition

- A pattern may specialise the status, boundary, queue or propagation primitives. The
  type still owns the page axis, connector grammar, spacing and its own limits.
- State and outcome are carried by **stable text**. Colour, motion and position
  reinforce; they never carry meaning alone.
- Whatever the budget forces out goes into `budget_cuts[]` in `viz.json`, the same as
  for a type cut.
