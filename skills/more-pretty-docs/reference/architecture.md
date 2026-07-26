# ARCHITECTURE spec

Explains how the system is built and why, for someone who will work on it. Audience:
engineers. This is the most **fabrication-prone** document — it needs real
understanding of the code, not manifest-reading — so the anti-fabrication rules apply
hardest here. Adaptive in content, consistent in shape. Apply
[house-style.md](house-style.md) throughout.

## The current-state rule

**ARCHITECTURE describes what the repository actually is right now.** Draw only
structure you can verify from the code, configuration, and entry points. Where design
intent isn't recoverable from the code, ask (if it fits the batched questions) or
leave a `<!-- TODO -->` — never draw a plausible-but-fictional box-and-arrow, and
never *animate* one (an animated diagram asserts facts with more authority than
prose — house-style → Anti-fabrication).

State the basis plainly, the way the exemplar does: "This document describes the
current state of the repository." If something notable is absent (no tests, no CI, no
linter), say so rather than implying it exists.

### Greenfield / target-state mode

A pre-code or greenfield repo has no implementation to describe. In that case:

- Write ARCHITECTURE **only if** an authoritative spec, SDD, or design doc exists in
  the repo to ground it. No spec and no code → **defer the document** and report it
  as deferred; don't invent an architecture.
- When you do write from a spec, **label it unmistakably as target-state** at the top
  ("This describes the *intended* architecture per `<spec>`; the implementation does
  not yet exist") and trace claims back to the spec.

## Section order

| Section | Required? | Drawn from |
| --- | --- | --- |
| Intro (what it is, the simulated/real boundary, who built it) | required | manifest, CLAUDE.md |
| Basis note (current-state, or labelled target-state) | required | repo state |
| Design goals and constraints | conditional | spec, CLAUDE.md |
| System context (external actors + systems) | conditional | code, spec |
| Runtime / container view | required | code, configs |
| Code and layer map | required | directory structure |
| Request lifecycle (or main control flow) | conditional | code |
| Key subsystems / seams / boundaries | conditional | code |
| Data model | conditional — when there's a schema | schema files |
| Cross-cutting concerns (accessibility, security, i18n, …) | conditional | code |
| Migration / evolution path | conditional | code, spec |
| References | required | sibling docs + spec |

## Section guidance

- **Runtime/container view.** A diagram with `subgraph`s for browser / server /
  storage (or the equivalent tiers for the project). Show the real runtime boundaries
  and where data actually flows. This is the diagram readers rely on most — keep it
  accurate over complete.
- **Code and layer map.** A `flowchart` grouping the real top-level directories and
  how they depend on each other. Built from the actual tree, not an idealized one.
- **Request lifecycle / control flow.** A `sequenceDiagram` of one representative path
  (a typical request, a CLI invocation, a job run) through the real components.
- **Key subsystems / seams.** When the codebase has deliberate interface boundaries
  (adapters, ports, plugin seams), document each in a table: name · module · what it
  does now · what it's designed to accept later. Only for boundaries that actually
  exist in the code.
- **Data model.** An `erDiagram` of a representative subset (say so when it's a
  subset), with the hub entity central. Pull entity/field names from the real schema.
- **Migration path.** Only when there's a meaningful one (e.g. swap-in points for
  production implementations). Tie each item to the specific module that owns it.

## Visuals

Budget: **1–2 flagship animated SVG diagrams** for this doc. Spend them on the
diagrams with the highest explanatory payoff — for ARCHITECTURE that's almost always
the **runtime/container view** and the **request lifecycle**. A diagram earns
animation only if it would earn a place in a printed engineering doc; motion must
clarify a boundary or a flow, never decorate.

Every animated ARCHITECTURE diagram is **immediately followed by a collapsed
`<details><summary>Diagram source (Mermaid)</summary>` block** holding the equivalent
Mermaid. That Mermaid is the machine-checkable statement of what the animation
depicts: it must parse (validate it — house-style → Diagrams) and it must **agree**
with the animation, node for node. If the picture and the source disagree, the doc is
wrong.

All remaining diagrams (the layer map, the data model, secondary flows) are **static
SVG in the frozen design system** or **plain Mermaid** — not animated. Ground every
depicted component, flow, and label in the code; record the fact list in the visual's
`mpd.json`. Keep versions and dates out of the rendered pixels (house-style → No
volatile facts).

Marker format and hash mechanics live in [embedding.md](embedding.md); production in
[viz-production.md](viz-production.md); styling in [design-system.md](design-system.md).
Don't restate those here.

## Neutral exemplar (shape only)

```markdown
# Architecture

<One paragraph: what the system is and the key boundary it maintains.>

This document describes the current state of the repository. <Honest note on what
exists and what doesn't — e.g. no CI, no test runner.>

## Runtime view

<!-- mpd:viz name="runtime-view" src="docs/assets/src/runtime-view/" facts-hash="…" src-hash="…" -->
<div align="center">
<img src="docs/assets/runtime-view.svg" alt="<Runtime boundaries and data flow: client,
server, storage tiers and the requests between them.>" width="820" />
</div>
<!-- mpd:viz end -->

<details>
<summary>Diagram source (Mermaid)</summary>

​```mermaid
flowchart TB
  subgraph client["Client"]
    ui["UI / entry point"]
  end
  subgraph server["Server"]
    handlers["Request handlers"]
    core["Core logic"]
  end
  subgraph storage["Storage"]
    db[("Datastore")]
  end
  ui -->|request| handlers
  handlers --> core
  core --> db
​```

</details>

## Code and layer map

​```mermaid
flowchart TB
  app["app/ — routes & entry points"]
  lib["lib/ — core logic"]
  data["data/ — persistence"]
  app --> lib
  lib --> data
​```

## Request lifecycle

<!-- mpd:viz name="request-lifecycle" src="docs/assets/src/request-lifecycle/" facts-hash="…" src-hash="…" -->
<div align="center">
<img src="docs/assets/request-lifecycle.svg" alt="<One request's path: client to handler
to datastore and back, in order.>" width="820" />
</div>
<!-- mpd:viz end -->

<details>
<summary>Diagram source (Mermaid)</summary>

​```mermaid
sequenceDiagram
  participant C as Client
  participant H as Handler
  participant DB as Datastore
  C->>H: request
  H->>DB: query
  DB-->>H: rows
  H-->>C: response
​```

</details>

## References

- [DEVELOPMENT.md](DEVELOPMENT.md) — local setup and workflows.
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution process.
- [SECURITY.md](SECURITY.md) — security posture.

<!-- mpd:footer start -->
<!-- … shared footer … -->
<!-- mpd:footer end -->
```
