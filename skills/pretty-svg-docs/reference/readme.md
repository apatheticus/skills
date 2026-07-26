# README spec

The front door. It tells a newcomer what the project is, whether it's for them, and
how to run it — then routes them to the deeper docs. Highly adaptive: its sections
flex to the project type and size. Apply [house-style.md](house-style.md) throughout.

## What the README is for — and what it isn't

The README covers a tight set of things: **what the repo is, the problem it solves,
the solution, getting started, and usage.** That's the whole job. A reader should
learn what this project does, decide whether it's for them, and get it running.

Everything else routes out. CI/CD detail, testing controls, and dev-procedure
content do **not** get full sections here — they demote to a one-line link-out to
`DEVELOPMENT.md` or `CONTRIBUTING.md`. The one exception: when that tooling **is**
the product (the repo ships a test runner, a CI system, a linter), it's a feature and
belongs in the body like any other feature.

## Section order

Required sections are always present. Conditional sections appear only when the
project actually has the thing they describe.

| Section | Required? | Drawn from |
| --- | --- | --- |
| Header (logo, title, one-line description) | required | docsmeta, manifest |
| Badge cluster | required | evidence pass (see house-style → Badges) |
| Animated hero | required (unless `--no-viz`) | the project's core idea |
| Important callout | conditional — when a critical caveat exists (e.g. demo-only) | user / docsmeta |
| Table of contents | conditional — when the README is long | self |
| What this is | required | manifest, CLAUDE.md, user |
| Who it's for | conditional | user, spec |
| Features | conditional | code, spec |
| Architecture (summary + at most 1 animated diagram, links to ARCHITECTURE.md) | conditional | code |
| Technology stack | required | manifests |
| Data model | conditional — when there's a schema | schema files |
| API surface | conditional — when there's an API | route/handler layout |
| Project structure | required | directory tree |
| Getting started (prerequisites, install, run, usage) | required | manifest, configs |
| Deployment | conditional — one-line link-out unless deployment is the product | configs, CI |
| Testing | link-out — one line pointing to DEVELOPMENT.md, unless testing is the product | test setup |
| Documentation (links every Tier 1 doc) | required | the doc set |
| License | required | LICENSE, docsmeta |
| Footer | required | house-style footer block |

## Section guidance

- **Header.** Centered logo from `docsmeta.assets.logo` (omit if unset), the project
  name as `#`, and a single bold sentence stating what it is. No tagline fluff.
- **Important callout.** Use a GitHub `> [!IMPORTANT]` blockquote only for a caveat a
  reader must not miss (demo-only, not-for-production, pre-release). Don't add one
  just to have one.
- **What this is.** Two or three short paragraphs. Concrete: what problem it solves,
  what it does, who runs it. No marketing voice (house-style → humanize).
- **Technology stack.** A two-column table (Area | Choice) built from the manifests.
  Only list runtimes/frameworks the manifest actually pins, and only at major/LTS
  granularity — **no minor or patch versions** (house-style → No volatile facts). A
  cell reads `Node 20+`, never `Node 20.11.1`.
- **Getting started.** The real prerequisites (runtime at major/LTS granularity only,
  any native-build toolchain), then copy-pasteable install/run commands pulled from
  actual manifest scripts, then a short usage example. Keep prerequisites durable —
  no pinned patch versions, no "as of" dates.
- **Project structure.** A plain ```` ``` ```` code block directory tree (this file
  listing is the one allowed non-Mermaid, non-animated "diagram"), annotated with one
  short note per top-level entry. Generate it from the real tree; don't list folders
  that don't exist.
- **Deployment / Testing.** One line each, pointing at `DEVELOPMENT.md` /
  `CONTRIBUTING.md`, unless that tooling is the product. Don't reproduce the pipeline
  or the test matrix in the README.
- **Documentation.** Link every Tier 1 doc that exists, each with a half-line of what
  it covers. This is the hub of the cross-link web.
- **License.** One line naming the license and linking `LICENSE`; link `NOTICE` if it
  exists.

## Visuals

The README is the most visual document in the set. Its budget:

- **One animated hero**, placed immediately below the badge cluster. It carries the
  project's core idea in motion — the thing the project *does* — not a decorative
  banner. This is the flagship visual for the whole repo.
- **Up to 3 animated diagrams** in the body (architecture summary, a key flow, a data
  shape) — only where a moving picture genuinely orients a newcomer faster than prose.
  Fewer is better; don't spend the budget just to fill it.

That's the ceiling: **hero + at most 3 animated diagrams.** A `--brief` README still
gets its hero; `--no-viz` drops all of them and the doc must still read cleanly.

Every README visual is an animated SVG embedded through a `pd:viz` marker (format
and hash mechanics in [embedding.md](embedding.md)), produced by the pipeline in
[viz-production.md](viz-production.md), and styled by the frozen design system in
[design-system.md](design-system.md). Don't restate the marker or hash mechanics
here — point at those specs.

**Every embed is centered**, hero and body diagrams alike, each in its own
`<div align="center">` wrapper inside its marker pair. The hero looks centered
already because the header block encloses it; that inheritance is not the rule and
disappears the moment the embed moves. Shape and the traps around it:
[embedding.md](embedding.md) → Centering.

**README animations carry rich alt text instead of a Mermaid fallback.** Unlike the
technical docs, a README embed gets **no** `<details>` Mermaid block. Its `alt`
attribute must convey the diagram's actual meaning — the components, the direction of
flow, the point being made — so the README stays fully meaningful with images off.
Write alt text a screen-reader user could act on, not "architecture diagram."

Anything beyond the animated budget is a static SVG (frozen design system) or plain
Mermaid. Keep versions and dates **out** of every rendered visual (house-style → No
volatile facts) — a baked-in `v2.4.1` goes stale silently and can't be greped.

## Neutral exemplar (shape only — strip all of this content)

```markdown
<div align="center">

<img src="<logo>" alt="<Org>" width="380" />

# <Project Name>

**<One-sentence description of what this project is and does.>**

<!-- pd:badges start -->
[![<Runtime> <major>](https://img.shields.io/badge/<runtime>-<major>-<hex>)](<url>)
[![License: <SPDX>](https://img.shields.io/badge/License-<SPDX>-<hex>.svg)](LICENSE)
[![Architecture](https://img.shields.io/badge/Architecture-design-112E51)](ARCHITECTURE.md)
[![Contributing](https://img.shields.io/badge/Contributing-guidelines-112E51)](CONTRIBUTING.md)
[![Security](https://img.shields.io/badge/Security-policy-112E51)](SECURITY.md)
<!-- pd:badges end -->

<!-- pd:viz name="hero" src=".prettydocs/src/hero/" facts-hash="…" src-hash="…" -->
<div align="center">
<img src="docs/assets/hero.svg" alt="<Rich description: what the project does, the
pieces involved, and how they connect — meaningful with images off.>" width="820" />
</div>
<!-- pd:viz end -->

</div>

## What this is

<Two or three concrete paragraphs: the problem, the solution, who runs it.>

<!-- pd:viz name="<body-diagram>" src=".prettydocs/src/<body-diagram>/" facts-hash="…" src-hash="…" -->
<div align="center">
<img src="docs/assets/<body-diagram>.svg" alt="<Rich description of the one thing
this diagram shows, in the order a reader meets it.>" width="820" />
</div>
<!-- pd:viz end -->

## Technology stack

| Area | Choice |
| --- | --- |
| Language | <language + major/LTS only> |
| Framework | <framework, no patch version> |
| <…> | <…> |

## Project structure

​```
<project>/
├── src/        <what lives here>
├── tests/      <what lives here>
└── <…>
​```

## Getting started

### Prerequisites

- <runtime, major/LTS granularity only>
- <toolchain, if any>

### Install and run

​```bash
<install command>
<run command>
​```

<Short usage example — the smallest thing that shows the project working.>

## Testing

See [DEVELOPMENT.md](DEVELOPMENT.md#testing) for how tests are run.

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — system design and diagrams.
- [DEVELOPMENT.md](DEVELOPMENT.md) — local setup and workflows.
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to propose changes.
- [SECURITY.md](SECURITY.md) — reporting a vulnerability.
- [SUPPORT.md](SUPPORT.md) — where to get help.

## License

Released under the [<License Name>](LICENSE).

<!-- pd:footer start -->
<div align="center">
<br/>

**Copyright © <year> <Org>. Released under the <SPDX-id> license.**

</div>
<!-- pd:footer end -->
```
