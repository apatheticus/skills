# House style — shared conventions

Read this first on every run. It holds the conventions every managed document
shares, the configuration schema, and the quality gates — textual **and** visual.
The per-document specs build on top of it.

## Contents

- [Voice and formatting](#voice-and-formatting)
- [Humanize the prose](#humanize-the-prose)
- [No volatile facts](#no-volatile-facts)
- [Diagrams: animated first, Mermaid as source of truth](#diagrams-animated-first-mermaid-as-source-of-truth)
- [The footer block](#the-footer-block)
- [Badges](#badges)
- [Marker comments](#marker-comments)
- [Cross-linking](#cross-linking)
- [Sizing](#sizing)
- [Host awareness](#host-awareness)
- [Project-type adaptation](#project-type-adaptation)
- [The docsmeta config file](#the-docsmeta-config-file)
- [Copyright, ownership, and the identity guardrail](#copyright-ownership-and-the-identity-guardrail)
- [Quality gates](#quality-gates)
- [Anti-fabrication rules](#anti-fabrication-rules)

## Voice and formatting

The documents should read like a careful engineer wrote them for a colleague:
plain, declarative, specific. Concrete facts beat adjectives.

- **Sentence-case headings.** `## Getting started`, not `## Getting Started`. No
  emoji in headings or chrome.
- **Tables for structured facts.** Scripts, environment variables, endpoints,
  dependencies, configuration — anything with a repeating shape — goes in a table,
  not a bulleted sprawl.
- **Short paragraphs, active voice.** Lead with the subject doing the thing.
- **Code spans for anything literal** — file paths, commands, identifiers,
  env vars — so they're copy-pasteable and unambiguous.
- **One idea per sentence.** If a sentence has three clauses joined by dashes, it's
  usually three sentences.

## Humanize the prose

Generated prose carries tells that make it tiring to read and obviously machine-
written. Strip them from any prose **you write or change this run** — never from
prose a human already wrote and you're only preserving.

**Preferred path:** if the `/humanizer` skill is available, run it over your drafted
prose before saving. It's purpose-built for this.

**Fallback (humanizer not installed):** apply this checklist yourself. Note in the
run summary which path you used.

- Cut **em-dash overuse**. An occasional dash is fine; three per paragraph is a tell.
  Prefer a period or a comma.
- Break the **rule of three**. Real writing doesn't deliver everything in tidy
  triplets ("fast, simple, and reliable"). Vary list lengths; sometimes two,
  sometimes five.
- Kill **negative parallelism**: "It's not just X, it's Y" / "This isn't about X —
  it's about Y". State the positive claim directly.
- Drop **inflated symbolism and promotion**: "seamlessly", "robust", "powerful",
  "cutting-edge", "best-in-class", "leverage", "delve", "boasts", "stands as a
  testament". Say what it does.
- Remove **filler openers**: "It's worth noting that", "In today's landscape",
  "When it comes to". Start with the content.
- Replace **vague attributions** ("industry experts agree", "studies show") with a
  specific source or delete the claim.
- Prefer **active voice** over agentless passive ("the seed builds the database",
  not "the database is built").
- Avoid the **"-ing" summary tail** that restates the sentence ("…, ensuring
  reliability and improving performance"). End on the fact.

The goal is prose that sounds like a person chose each word, not a model filling a
template.

## No volatile facts

Docs and visuals managed by this skill must stay true for months without an edit.
Anything that churns with routine releases is **changelog territory and banned
here**:

- **No minor or patch version numbers** — not in prose, tables, badges, alt text,
  or rendered visuals. A major or LTS identifier is allowed only where it's
  load-bearing (`Node 20+` as a hard engine requirement, `Python 3` vs `2`). Never
  `v2.4.1`, never "since 3.11.2".
- **No release dates**, ship dates, or "as of &lt;month year&gt;" qualifiers.
- **No individual feature announcements or bug-fix notes** ("now supports X",
  "fixed the Y crash"). Describe the current capability as a plain fact or leave it
  out.
- The same rules apply **inside animated and static visuals**: a version string or
  date baked into a rendered WebP goes stale silently and can't be greped. The
  visual-audit gate checks each visual's declared fact list for these.

When a spec section or an existing doc contains a volatile fact, replace it with
the durable form (drop the version, keep the capability) rather than refreshing
the number.

## Diagrams: animated first, Mermaid as source of truth

This skill's signature: **key diagrams render as seamless-loop animated WebPs**,
produced by the pipeline in `viz-production.md`, embedded per `embedding.md`, and
styled by the repo's frozen design system (`design-system.md`).

- **Never ASCII art** — not for boxes, trees, flows, or tables-pretending-to-be-
  diagrams. The one exception: a plain text code block for a directory tree (a file
  listing, not a diagram).
- **Which visuals get animated is a budget decision** — see the visual-budget table
  in `SKILL.md`. Diagrams outside the budget are static SVG (also per
  `viz-production.md`) or plain Mermaid.
- **Every animated diagram in a technical doc (ARCHITECTURE, DEVELOPMENT,
  CONTRIBUTING) is immediately followed by a collapsed `<details>` block holding
  the equivalent Mermaid source.** That Mermaid is the machine-checkable statement
  of what the animation depicts; it must parse and must agree with the animation.
  README embeds carry rich alt text instead — no Mermaid fallback there.
- Plain Mermaid (outside any budget) follows the usual craft: pick the fitting type
  (`flowchart`, `sequenceDiagram`, `erDiagram`, `stateDiagram-v2`, `pie showData`,
  `gitGraph`), quote labels containing punctuation/parentheses/slashes/`<br/>`,
  keep to roughly 5–12 nodes, group with `subgraph`, dash simulated/planned links.
- **Validate every Mermaid block** — including the ones inside `<details>`
  fallbacks. Use the Mermaid validator MCP tool if available
  (`mcp__claude_ai_Mermaid_Chart__validate_and_render_mermaid_diagram`; read only
  its `valid`/`diagramType` fields, not the rendered payload), else self-check
  carefully. Never ship a block you couldn't validate.

## The footer block

Every managed Markdown document ends with the same centered footer, wrapped in
marker comments so it can be regenerated wholesale. Build it from `docsmeta`:

```html
<!-- mpd:footer start -->
<div align="center">
<br/>
<img src="{icon_asset}" alt="{org}" width="28" height="28" align="center" />

**Copyright © {year_range} {org}. {rights}**

<sub>{disclaimer}</sub>

</div>
<!-- mpd:footer end -->
```

- `{icon_asset}` — the small brand icon path from `docsmeta.assets.icon`. If none is
  configured, omit the `<img>` line entirely rather than linking a missing file.
- `{org}` — the copyright holder (organisation/legal entity), never a personal name.
- `{year_range}` — see [year policy](#copyright-ownership-and-the-identity-guardrail).
- `{rights}` — **derived from the repo's real `LICENSE`, never hardcoded**:
  - An open-source license (any SPDX id in `docsmeta.license` — `MIT`, `Apache-2.0`,
    `BSD-3-Clause`, `ISC`, `GPL-3.0-only`, …) → `Released under the {license} license.`
  - Proprietary, `UNLICENSED`, or no LICENSE file → `All rights reserved.`
  - `docsmeta.license` disagrees with the actual `LICENSE` file → the file wins; fix
    `docsmeta` rather than the footer.

  "All rights reserved" asserts the opposite of a permissive grant, so pairing it
  with an MIT or Apache LICENSE ships a self-contradicting doc. Gate 3 checks this.
- `{disclaimer}` — the one-line `<sub>` disclaimer, included **only** if
  `docsmeta.disclaimer` is set. Do not manufacture a disclaimer the user hasn't
  asked for. Drop the `<sub>` line if empty.

The footer is identical across all managed docs in a repo. The quality gates check
that consistency. **Exception: LICENSE and NOTICE get no footer, no markers, no
formatting of any kind** — see `tier2/license.md`.

## Badges

Badges appear in the README header only (the other docs link back with small nav
badges, optional). Badges must be **honest** — every badge states a fact that is
actually true of the repo:

- A language/framework/runtime badge only for versions the manifests actually pin —
  and only at major/LTS granularity, per [No volatile facts](#no-volatile-facts).
- A license badge only matching the real `LICENSE`.
- **Never** a "tests passing", "coverage 90%", or "build passing" badge unless that
  workflow genuinely exists in `.github/workflows/`.
- Nav badges that link to sibling docs (Architecture, Development, Contributing,
  Security, Support) are fine and encouraged — they're navigation, not claims.
- Style badges to the frozen design system's palette (shields.io `color=` hex) so
  the header reads as one designed unit with the hero.

Use `https://img.shields.io/badge/...` static badges built from `docsmeta` + the
evidence pass. Wrap the whole badge cluster in `<!-- mpd:badges start -->` /
`<!-- mpd:badges end -->` markers so it regenerates cleanly.

## Marker comments

Three marker families delimit fully generated regions; everything **outside**
markers is matched by heading and edited surgically:

- `<!-- mpd:footer start -->` … `<!-- mpd:footer end -->` — the shared footer.
- `<!-- mpd:badges start -->` … `<!-- mpd:badges end -->` — the README badge row.
- `<!-- mpd:viz … -->` … `<!-- mpd:viz end -->` — each embedded visual, carrying
  the hashes that drive lazy re-rendering. Format and semantics in `embedding.md`.

Rules:

- Don't add markers around prose sections — heading-matching handles those.
- Keep markers balanced; the quality gates verify that.
- **Pre-existing docs without markers:** only when you are already writing to that
  doc, normalize it once — wrap its existing footer/badge block in the markers as
  part of that write. Identify the block by shape (centered footer `<div>` with the
  copyright line; contiguous badge cluster under the title), not by a marker. Never
  add markers to a doc you're otherwise leaving untouched, and never duplicate a
  block.
- **Legacy markers:** if a doc contains `update-docs:` markers from the sibling
  skill, treat them as the same regions and rewrite them to the `mpd:` prefix —
  but only when you're already rewriting that block.
- LICENSE and NOTICE never contain any marker.

## Cross-linking

The doc set is a web, not a pile. Maintain it:

- The README links to every Tier 1 doc (a "Documentation" section and/or nav badges).
- Each Tier 1 doc ends with a short **References** section linking the siblings it
  relates to (ARCHITECTURE ↔ DEVELOPMENT ↔ CONTRIBUTING ↔ SECURITY, etc.).
- Link to specific files and headings with relative paths (`[lib/db.ts](lib/db.ts)`,
  `[Secret scanning](#secret-scanning)`), not bare prose references.
- Every internal link you write must resolve — the link-integrity gate checks this.
  Embedded asset paths (`docs/assets/*.webp`, `*.svg`) count as internal links.

## Sizing

Match a document's depth to the project's real complexity and the truth available.
Never pad to hit a length.

- **Automatic (default):** judge depth from project size and how much real signal
  the evidence pass found. Few modules, no CI, no tests → a lean doc that says so.
- **`--brief`:** the essential sections only, terse.
- **`--full`:** every applicable section, with diagrams and detail, even for a small
  project.

Depth flags size the **prose**; the **visual budget** is a separate axis controlled
by the budget table in `SKILL.md` and `--budget` / `--no-viz` overrides. A `--brief`
README can still carry its animated hero.

Conditional sections only appear when they apply. README §API surface, §Data model,
§Deployment, etc. exist in a doc only when the project actually has those things.

## Host awareness

Several docs prescribe host-specific mechanics (where to report a vulnerability, how
to open an issue/PR). Detect the forge from the git remote and adapt; never emit a
GitHub URL guessed from a folder name.

| Remote host | Vulnerability reporting | Issue/change vocabulary | Health-file location |
| --- | --- | --- | --- |
| `github.com` (first-class) | Private **Security Advisory** (`/security/advisories/new`) | Issues · Pull Requests · Discussions | `.github/` |
| `gitlab.*` | **Confidential issue**, or security email | Issues · Merge Requests | `.gitlab/` |
| `codeberg.*` / Forgejo / Gitea | Security email (advisories vary) | Issues · Pull Requests | `.gitea/` or root |
| `bitbucket.*` | Security email | Issues · Pull Requests | root |
| none / unknown | Security **email** from `docsmeta.support.security_email`, else `<!-- TODO -->` | host-neutral ("the issue tracker", "a change request") | root |

GitHub is the fully-templated, first-class path. For any other forge, keep the same
document **structure** and swap only the mechanics. When there's no remote, stay
host-neutral and leave links as TODOs rather than fabricating them.

Animated WebP embeds render on GitHub, GitLab, and most forges' markdown; the
`<details>` Mermaid fallback covers renderers that don't animate.

## Project-type adaptation

The adaptive docs (README, ARCHITECTURE, DEVELOPMENT) fit themselves to the detected
stack. Read the manifest to decide what the "getting started", "scripts", "stack",
and "project structure" sections should actually say:

- **Node/JS/TS** (`package.json`) — npm/pnpm/yarn scripts table, `engines`, framework
  from deps.
- **Python** (`pyproject.toml` / `setup.cfg` / `requirements.txt`) — venv + install
  flow, console-scripts/entry points, runner (pytest, ruff) only if present.
- **Rust** (`Cargo.toml`), **Go** (`go.mod`), **Ruby** (`Gemfile`), **PHP**
  (`composer.json`), etc. — the idiomatic build/run/test commands for that ecosystem.
- **Polyglot / unclear** — describe what's actually there; don't force a single-stack
  template onto a repo that doesn't fit it.

Pull commands from the manifest's real scripts/targets. Don't invent a `test` script
that isn't defined.

## The docsmeta config file

Persist the un-derivable facts so reruns are unattended. Path: `.github/docsmeta.json`
(committed; holds no secrets). Derive every field you can from authoritative sources
first; only the values you had to ask for need storing here.

```json
{
  "$schema_note": "Config for the make-pretty-docs skill. Committed. No secrets.",
  "org": "Example Org, Inc.",
  "year_policy": "range",
  "first_year": 2026,
  "license": "Apache-2.0",
  "disclaimer": "",
  "assets": { "logo": "docs/assets/logo.png", "icon": "docs/assets/icon.png" },
  "repo_url": "https://github.com/example-org/example",
  "host": "github",
  "support": {
    "issues_url": "https://github.com/example-org/example/issues",
    "discussions_enabled": false,
    "security_email": "",
    "briefing_contact": ""
  }
}
```

- `year_policy`: `range` (default — `first_year`–current), `fixed` (just `first_year`),
  or `current` (the current year only).
- Empty strings mean "not set" → the skill omits the corresponding output (e.g. no
  disclaimer line) rather than inventing it.
- Read the current year from the session date; do not hardcode it and do not write a
  timestamp into this file — it stays stable config so it doesn't churn.
- If a `.github/docsmeta.json` written by the sibling `update-docs` skill exists,
  reuse it as-is; the schema is compatible.

Per-visual state lives elsewhere: each visual's `mpd.json` next to its composition
source (see `embedding.md`), and the repo-wide design system in
`docs/assets/src/DESIGN.md` (see `design-system.md`).

## Copyright, ownership, and the identity guardrail

The **copyright holder is an organisation or legal entity** — or, for a genuinely
personal project, the individual who owns it — and it is **never guessed
silently**.

**Deriving a holder candidate** (in order; first hit wins):

1. **Authoritative repo sources — auto-use.** An existing `LICENSE` holder line,
   `docsmeta.org`, manifest `author`/`organization`, or an existing managed footer.
2. **Forge-owner lookup — auto-use for organisations only.** Take the owner slug
   from the git remote and query the forge's public account endpoint. GitHub:
   `gh api users/<owner>` (read the `type` and `name` fields); unauthenticated
   fallback `curl -s https://api.github.com/users/<owner>`. Other forges have
   equivalent endpoints (GitLab `/api/v4`, Gitea/Forgejo `/api/v1`); no endpoint →
   skip this rung. If `type` is `Organization` and `name` is non-empty, use it and
   persist to `docsmeta.org`. An org display name can still approximate the legal
   entity ("Example Labs" vs "Example Labs, Inc.") — note that in the run report.
3. **Confirm-tier candidates — never auto-use.** A **User**-account display name,
   a bare owner slug (empty `name`), or `git config user.name`. Carry the best one
   into the phase-4 batched questions as the pre-filled recommended answer; it is
   written only after the user confirms it.
4. **Nothing found** → ask with no pre-fill.

Hard rules, regardless of the ladder:

- **Never silently write a personal or guessed name as holder.** A commit author is
  not a holder. The **OS username is never a candidate at any rung** — it's a
  machine account string, not a name.
- A personal name is used **only** where a document genuinely calls for attribution —
  e.g. "adapted from Jane Doe's project", a CODE_OF_CONDUCT enforcement contact the
  user explicitly names, or a NOTICE attribution. Never as a generic author/owner.
- **Year:** with `year_policy: range`, a single year shows as `2026`; once the current
  year is later, it shows `2026–2027`. Preserve an existing `first_year` rather than
  resetting it.

## Quality gates

After writing, run these over **only what you authored or changed this run**. Fix
what you can, re-check, and surface the rest in the summary. Don't audit pre-existing
human content. Gates 1–5 are textual; gates 6–10 are visual and detailed in
`embedding.md` and `viz-production.md`.

1. **Mermaid validity.** Every block you wrote parses — including blocks inside
   `<details>` fallbacks.
2. **Internal link/anchor integrity.** Every relative link, `#heading` anchor, and
   embedded asset path you wrote resolves. (External URL liveness is not checked.)
3. **Boilerplate consistency.** Footer, holder, year, disclaimer, and badge row are
   consistent across all managed docs; marker comments balanced and well-formed. The
   footer's `{rights}` statement matches the real `LICENSE` — "All rights reserved"
   never appears in a repo carrying a permissive or copyleft license, and the license
   badge names that same license.
4. **Cross-doc truth consistency.** Facts you emitted agree with the evidence pass
   and with each other — including facts depicted inside visuals (a component the
   hero animates must exist in ARCHITECTURE's text and the code).
5. **Leak / guardrail check.** No content leaked from another project (persona
   names, palette, jargon); no personal name as copyright holder; no asserted
   tests/CI/tooling the repo doesn't have; no volatile facts (grep managed sections
   and visual fact lists for `\bv?\d+\.\d+\.\d+\b` and date-like strings).
6. **Composition validity.** Every animated visual rendered this run passed
   `hyperframes check` with **0 errors** before render.
7. **Asset presence + size.** Every embedded `.webp`/`.svg` exists at its
   referenced path; every animated WebP is **≤ 2.5 MB**.
8. **Marker/manifest integrity.** Every `mpd:viz` marker pair is balanced, points
   at an existing source dir with a `mpd.json`, and marker hashes match the
   manifest (`scripts/audit_visuals.py` checks this mechanically).
9. **Works without images.** With every image stripped, each doc still makes its
   point: README alt text carries the meaning; technical-doc animations have their
   `<details>` Mermaid equivalent; banners are reinforced by adjacent text.
10. **Budget + placement.** No doc exceeds its visual budget; **LICENSE and NOTICE
    contain zero visuals, badges, or markers** — any visual there is a hard
    violation.

## Anti-fabrication rules

These override the urge to produce a complete-looking document — or a
complete-looking diagram.

- **Don't claim what isn't there — and don't deny what is.** If there's no test
  runner, the docs say there are no automated tests. If CI only runs a secret scan,
  don't imply a full build/lint/test pipeline. But the inverse is just as much a
  truth failure: **understating** real tooling. Read each capability as "present
  and does X" or "absent," never collapse a partially-tooled repo to "none."
- **Ground every visual.** An animated diagram asserts facts with more authority
  than prose — so its depicted components, flows, and labels must all be verifiable
  from the code/config, and its `mpd.json` fact list records exactly which. An
  accurate partial diagram beats a complete fictional one. Decorative motion
  (motif, background texture) carries no facts and needs no grounding.
- **Ask or defer over invent.** When a section needs a fact you can't find and
  can't ask for in the batched set, leave a `<!-- TODO: … -->` describing exactly
  what's needed. A visible gap is honest; a confident fabrication is a bug.
- **Reflect current state.** ARCHITECTURE and the README describe what exists now.
  Target-state belongs only in a clearly-labelled greenfield mode grounded in a
  real spec (see `architecture.md`).
