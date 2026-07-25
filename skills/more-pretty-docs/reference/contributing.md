# CONTRIBUTING spec

How an outside (or inside) contributor proposes a change: the branching model, commit
conventions, and the PR checklist. Audience: engineers. Structurally stable; the
specifics (branch tiers, checklist items) adapt to the project's real workflow, which
often lives in CLAUDE.md or the git history. Apply
[house-style.md](house-style.md) throughout.

## Truth sources for the workflow

- **CLAUDE.md / AGENTS.md** frequently document the exact branching model, commit
  format, and review gates — mine them first and mirror them faithfully.
- **Git history** reveals the real conventions: branch-name patterns, whether commits
  follow Conventional Commits, squash vs merge.
- **`.github/`** reveals required checks and existing PR templates.

Don't impose a workflow the project doesn't use. If the repo squash-merges feature
branches into an integration branch, document *that*, not a generic fork-and-PR flow.

## Section order

| Section | Required? | Drawn from |
| --- | --- | --- |
| Intro + Code of Conduct link | required | docsmeta |
| Before you start (what to read) | conditional | spec, ARCHITECTURE |
| Development setup (link DEVELOPMENT) | required | — |
| Branching model (gitGraph) | required | CLAUDE.md, git history |
| Commit messages | required | git history / convention |
| Pull request process (flowchart) + checklist | required | CI, CLAUDE.md |
| Coding standards (summary; link DEVELOPMENT) | conditional | configs |
| Reporting bugs / requesting features | required | host (SUPPORT) |
| Security issues (link SECURITY) | required | — |
| License (inbound = outbound) | required | LICENSE |
| Footer | required | house-style |

## Section guidance

- **Branching model.** A `gitGraph` showing the project's real tiers (e.g.
  feature → integration → main). Mirror the actual branch names and merge style. If
  the project has no formal model yet, describe a simple, honest default and say it's
  the starting convention.
- **Commit messages.** If the project uses Conventional Commits, document the types
  and scopes actually in use (from history). Show two or three real-style examples.
- **Pull request process.** A `flowchart TD` of branch → commit → push → open PR →
  review → merge, adapted to the forge vocabulary (PR vs MR — house-style → Host
  awareness). Follow with a **checklist** of the project's genuine pre-review gates
  (the example's checklist is project-specific: determinism, accessibility, no
  network calls, etc. — derive the equivalent real gates, don't copy those).
- **License (inbound = outbound).** State that contributions are accepted under the
  project's license. Name the real license.

## The checklist is project-specific

The PR checklist is where this doc earns its keep. Build it from the project's actual
invariants — the things a reviewer truly verifies — sourced from CLAUDE.md, CI checks,
and the coding standards. A generic "[ ] tests pass" is useless if there are no tests;
a real gate ("[ ] `npm run typecheck` is clean", "[ ] no new dependencies without
review") is what helps. Leave a `<!-- TODO -->` if the real gates aren't yet known.

## Visuals

Budget: **1–2 flagship animated SVG diagrams** for this doc. For CONTRIBUTING the
highest-payoff choice is the **contribution / PR lifecycle** (branch → commit → push →
open → review → merge); the **branching model** `gitGraph` is the natural second if
the project's tiers are non-trivial. Animate a diagram only if it would earn a place
in a printed engineering doc — a moving picture of a two-branch flow decorates rather
than clarifies.

Every animated CONTRIBUTING diagram is **immediately followed by a collapsed
`<details><summary>Diagram source (Mermaid)</summary>` block** with the equivalent
Mermaid, which must parse (validate it) and **agree** with the animation. All other
diagrams are **static SVG in the frozen design system** or **plain Mermaid**. Keep
versions and dates out of the rendered pixels (house-style → No volatile facts).

Marker format and hashes live in [embedding.md](embedding.md); production in
[viz-production.md](viz-production.md); styling in [design-system.md](design-system.md).

## Neutral exemplar (shape only)

```markdown
# Contributing

Thanks for your interest in <project>. This guide explains how to propose changes.
By taking part, you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Development setup

See [DEVELOPMENT.md](DEVELOPMENT.md) for prerequisites and the quick start.

## Branching model

​```mermaid
gitGraph
  commit id: "main"
  branch integration
  checkout integration
  commit id: "work"
  branch feature
  checkout feature
  commit id: "feat: change"
  checkout integration
  merge feature
  checkout main
  merge integration tag: "release"
​```

## Commit messages

Use <convention>. Example:

​```text
feat(<scope>): <subject>
​```

## Pull request process

<!-- mpd:viz name="pr-lifecycle" src="docs/assets/src/pr-lifecycle/" facts-hash="…" src-hash="…" -->
<img src="docs/assets/pr-lifecycle.svg" alt="<Contribution lifecycle in order: branch
from base, commit, push, open PR, review, and either loop back or merge.>" width="820" />
<!-- mpd:viz end -->

<details>
<summary>Diagram source (Mermaid)</summary>

​```mermaid
flowchart TD
  A["Branch from <base>"] --> B["Commit"] --> C["Push"] --> D["Open <PR/MR>"]
  D --> E["Review"] --> F{"Checks pass?"}
  F -->|No| B
  F -->|Yes| G["Merge"]
​```

</details>

Before requesting review:

- [ ] <real gate 1>
- [ ] <real gate 2>

## Security issues

Don't open a public issue for a vulnerability — see [SECURITY.md](SECURITY.md).

## License

Licensed under <license> (see [LICENSE](LICENSE)). Contributions are accepted under
the same license.

<!-- mpd:footer start -->
<!-- … shared footer … -->
<!-- mpd:footer end -->
```
