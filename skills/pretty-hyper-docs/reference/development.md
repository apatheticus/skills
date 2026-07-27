# DEVELOPMENT spec

The hands-on guide for running, building, and troubleshooting the project locally.
Audience: engineers. Adaptive to the project type; everything here must be a real
command that works. Apply [house-style.md](house-style.md) throughout.

## The honesty rule

Every command, script, env var, and tool named here must actually exist in the repo.
Pull commands from the real manifest scripts/targets. If a capability is absent (no
linter, no formatter, no tests, no CI), the **tooling status** section says so
plainly — the exemplar does exactly this, and that candor is the point. Don't
document a `lint` script that isn't defined.

**Scope boundary.** This doc is the *local* guide. Deploy-time configuration,
environments, promotion, and rollback belong to DEPLOYMENT.md on a repo that deploys
(see [deployment.md](deployment.md)) — link to it in one line rather than duplicating
it here.

## Section order

| Section | Required? | Drawn from |
| --- | --- | --- |
| Intro (what the project is, one line, link to ARCHITECTURE) | required | manifest |
| Prerequisites | required | manifest engines, native deps, configs |
| Quick start (diagram + commands) | required | manifest scripts |
| Scripts / tasks | required | manifest |
| Environment variables | conditional — when any exist | code, configs |
| Build / data / seed workflows | conditional | scripts, configs |
| Project-specific workflows (e.g. fixtures, codegen) | conditional | code |
| Coding standards (summary; link CONTRIBUTING) | conditional | configs, CLAUDE.md |
| Quality checks (lint, format, types, a11y, …) | conditional | configs |
| Troubleshooting | required | common failure modes for the stack |
| Tooling status | required | actual tooling present |
| References | required | sibling docs |

## Section guidance

- **Prerequisites.** The runtime at major/LTS granularity (from `engines` or
  equivalent — `Node 20+`, not `Node 20.11.1`; house-style → No volatile facts), and
  any native toolchain a dependency needs to compile (call out the platform-specific
  steps for macOS/Linux/Windows when a native build is involved). Only list what's
  genuinely required.
- **Quick start.** A short clone → install → (build/seed) → run → open pipeline,
  followed by the same steps as copy-pasteable shell. Keep the diagram and the
  commands in sync.
- **Scripts / tasks.** A table: `Script` · `Command` · `What it does`, one row per real
  manifest script. Don't editorialize scripts that don't exist.
- **Environment variables.** A table: `Variable` · `Default` · `Purpose`. Include only
  variables the code actually reads. Note which are optional. Never include secret
  values — only names and purposes.
- **Troubleshooting.** Real, stack-appropriate failure modes (native rebuild after a
  runtime upgrade, port already in use, stale lockfile/db, missing toolchain). Each
  with the concrete fix command. Keep fixes durable — don't tie one to a specific
  patch release.
- **Tooling status.** The candid inventory: what's configured (linter, formatter, git
  hooks, CI) and what isn't. If there are no automated tests, say so. If CI only does
  one thing, say only that.

## Visuals

Budget: **1–2 flagship animated WebP diagrams** for this doc. Spend them where motion
buys the most comprehension — for DEVELOPMENT that's usually the **dev loop**
(the clone → install → build → run → open quick-start pipeline) or the **environment
topology** (services/processes a running dev setup spins up). A build/seed/reset
workflow with several stages can justify the second one. If a diagram wouldn't earn a
place in a printed engineering doc, it stays static.

Every animated DEVELOPMENT diagram is **immediately followed by a collapsed
`<details><summary>Diagram source (Mermaid)</summary>` block** with the equivalent
Mermaid, which must parse (validate it) and **agree** with the animation step for
step. All other diagrams are **static SVG in the frozen design system** or **plain
Mermaid**. Keep versions, dates, and per-release notes out of the rendered pixels
(house-style → No volatile facts).

Marker format and hashes live in [embedding.md](embedding.md); production in
[viz-production.md](viz-production.md); styling in [design-system.md](design-system.md).

## Neutral exemplar (shape only)

```markdown
# Development guide

How to set up, run, and troubleshoot <project> locally. For how the pieces fit
together, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Prerequisites

- <runtime, major/LTS granularity only>
- <native toolchain, per platform, if needed>

## Quick start

<!-- pd:viz name="dev-loop" src=".prettydocs/src/dev-loop/" facts-hash="…" src-hash="…" -->
<div align="center">
<img src="docs/assets/dev-loop.webp" alt="<Local dev loop in order: clone, install,
build/seed, run, open — the exact steps below.>" width="820" />
</div>
<!-- pd:viz end -->

<details>
<summary>Diagram source (Mermaid)</summary>

​```mermaid
flowchart LR
  A["Clone"] --> B["<install>"] --> C["<build/seed>"] --> D["<run>"] --> E["Open <url>"]
​```

</details>

​```bash
git clone <repo-url>
cd <project>
<install>
<run>
​```

## Scripts

| Script | Command | What it does |
| --- | --- | --- |
| `<name>` | `<command>` | <description> |

## Troubleshooting

- **<Symptom>.** <Cause and the fix command.>

## Tooling status

- **Linting.** <configured / not configured>.
- **Tests.** <how to run / "no automated tests yet">.
- **CI.** <what actually runs / "none">.

## References

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)

<!-- pd:footer start -->
<!-- … shared footer … -->
<!-- pd:footer end -->
```
