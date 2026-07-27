---
name: pretty-hyper-docs
description: Requires the HyperFrames toolchain, ffmpeg, and img2webp. Creates and maintains a repository's standard documentation — README, ARCHITECTURE, DEVELOPMENT, DEPLOYMENT, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, SUPPORT, plus on-demand LICENSE, NOTICE, issue/PR templates, and CODEOWNERS — and beautifies it with a per-repo design system and seamless-loop animated WebP visuals rendered from HTML compositions via HyperFrames. Use this only when the user specifically wants WebP visuals or names HyperFrames, or invokes /pretty-hyper-docs, or is maintaining a repo whose existing visuals were already produced this way. For a generic request for beautiful, illustrated, animated, or visually polished docs — and on any machine without the HyperFrames toolchain installed — the sibling pretty-svg-docs skill is the better fit. For still images, printed or PDF'd docs, or an explicit no-animation request, use pretty-plain-docs; for plain text-only doc maintenance without visuals, update-docs fits better.
---

# pretty-hyper-docs

Create and maintain a repository's standard documentation so it reflects the
**actual current truth** of the project — then make it genuinely beautiful:
a frozen per-repo design system, an animated hero, and seamless-loop animated
WebP diagrams where they earn their place, produced with HyperFrames and
embedded so they render on GitHub.

Two principles govern everything:

- **Honesty over polish.** A short, accurate doc beats a long plausible one.
  Never describe tests, CI, tooling, or architecture the repo doesn't contain.
  A visual asserts facts with *more* authority than prose, so every diagram —
  animated or static — depicts only verifiable structure, and records which
  facts it depicts in its manifest.
- **Visuals enhance, never decorate.** Each doc is written for its audience
  (see the matrix below), and a visual exists only where it communicates
  something to that audience faster than text would.

## Preflight gate (run before anything else)

This skill renders visuals with the HyperFrames toolchain. Check it first:

```bash
npx hyperframes skills check --json
```

- **Non-zero exit** (core skill set incomplete or stale): **STOP. Do not start
  the run.** Tell the user what's missing and print the fix:
  1. `npx hyperframes skills update`
  2. If the HyperFrames CLI itself is unavailable:
     `npx skills add heygen-com/hyperframes --all`

  Then end the turn so they can install and re-invoke.
- Also probe `command -v ffmpeg` and `command -v img2webp` now and **warn** if
  absent (macOS: `brew install webp` for img2webp). These hard-fail only at
  render time, so a `check` or `--no-viz` run may proceed without them.
- `--no-viz` and `check` runs skip the HyperFrames gate too — they render
  nothing — but still report toolchain state in the summary.

## Documents in scope

**Tier 1 — managed on every default run:**
README · ARCHITECTURE · DEVELOPMENT · DEPLOYMENT · CONTRIBUTING · CODE_OF_CONDUCT · SECURITY · SUPPORT

DEPLOYMENT is **signal-gated**: written only when the evidence pass finds a real
deploy target (platform config, container/IaC artefacts, a deploying CI workflow,
migrations plus a service). No signal → report it `N/A — no deploy target` and write
nothing; publish/release mechanics stay in DEVELOPMENT and CONTRIBUTING. The signal
list and the DEVELOPMENT boundary are in `reference/deployment.md`.

**Tier 2 — only when explicitly named or a clear signal demands it:**
LICENSE · NOTICE · `.github/ISSUE_TEMPLATE/*` · `PULL_REQUEST_TEMPLATE.md` · CODEOWNERS

**Out of scope:** CHANGELOG (release tooling owns it) and product/spec docs.

Each doc has a spec in `reference/` (Tier 2 under `reference/tier2/`). Shared
conventions live in `reference/house-style.md` — **read it first on every
run**, then the spec for each doc you touch. Before any embed or audit read
`reference/embedding.md`; before any render read `reference/viz-production.md`.

**Filenames:** outputs use conventional uppercase names (`README.md`,
`SECURITY.md`, …). Match existing files case-insensitively; keep a repo's
existing convention rather than creating duplicates.

## Invocation modes

| Invocation | Effect |
| --- | --- |
| `/pretty-hyper-docs` | Full pass over Tier 1: content + visuals |
| `/pretty-hyper-docs <target> [<target>…]` | Only the named docs (`readme`, `deployment`, `security`, …; Tier 2 by explicit name) |
| `/pretty-hyper-docs check` | **Read-only audit** — content verdicts (`CREATE`/`UPDATE`/`OK`) *and* visual verdicts (`OK`/`MISSING`/`STALE`/`DRIFT`/`CONTRADICTS`/`BUDGET`). Writes nothing. |
| `--refresh-viz` | Force re-render of every in-scope visual regardless of hashes |
| `--no-viz` | Content-only run; leave every existing visual and marker untouched |
| `--budget <doc>=<n>` | Override a doc's animated-visual budget for this run (e.g. `--budget readme=1`) |
| `--brief` / `--full` | Prose-depth override (see house-style → Sizing). Independent of the visual budget. |

## Audience matrix

| Doc | Audience | Visual treatment |
| --- | --- | --- |
| README | Everyone; first visit | Animated hero + up to 3 animated diagrams; **rich alt text, no Mermaid fallback**. Purpose/solution/getting-started/usage only — repo-process detail links out to DEVELOPMENT/DEPLOYMENT/CONTRIBUTING. |
| ARCHITECTURE | Engineers | 1–2 flagship animated diagrams, each + collapsed `<details>` Mermaid source; rest static SVG or plain Mermaid |
| DEVELOPMENT | Engineers | Same treatment as ARCHITECTURE |
| DEPLOYMENT | Operators/engineers deploying it | Same treatment as ARCHITECTURE; created only when a deploy target exists |
| CONTRIBUTING | Engineers/contributors | Same treatment as ARCHITECTURE |
| SECURITY | Everyone; prescriptive | One attention banner: "report privately, never a public issue" |
| CODE_OF_CONDUCT | Everyone; prescriptive | One attention banner: the core conduct expectation; covenant body untouched |
| SUPPORT | Users seeking help | Static designed header at most |
| LICENSE / NOTICE | Legal | **None. Ever.** Verbatim legal text; no markers, badges, or formatting. |

## Visual budget (defaults; `--budget` overrides per run)

| Doc | Animated | Static SVG |
| --- | --- | --- |
| README | hero + ≤3 diagrams | as needed |
| ARCHITECTURE / DEVELOPMENT / DEPLOYMENT / CONTRIBUTING | 1–2 flagship each | remaining diagrams |
| SECURITY / CODE_OF_CONDUCT | ≤1 (the banner; static also fine) | — |
| SUPPORT | 0 | ≤1 header |
| LICENSE / NOTICE / templates / CODEOWNERS | 0 — hard gate | 0 — hard gate |

Under-spending the budget is always allowed. A diagram that wouldn't earn a
place in a printed engineering doc doesn't get animated.

## Target layout (the skill maintains this)

One block per project. A repo documenting several projects repeats it per project
root — see `design-system.md` → What counts as a project.

```
<project>/docs/assets/<viz-name>.webp   # committed — embedded animated visuals
<project>/docs/assets/<viz-name>.svg    # committed — static visuals
<project>/.prettydocs/
├── .gitignore                     # committed — byproduct rules, self-contained
├── prettydocs.md                  # committed — frozen design system + provenance
└── src/<viz-name>/
    ├── index.html                 # committed — HyperFrames composition (or source .svg for statics)
    ├── viz.json                   # committed — facts, hashes, render params (see embedding.md)
    ├── hyperframes.json, package.json, meta.json   # committed — init scaffold config
    │                              #   (meta.json is HyperFrames' own file, not ours)
    └── render.mp4, renders/, frames/, snapshots/, qa_*.png, check.json   # gitignored
```

Rendered assets stay under `docs/assets/` so a deployment can exclude the whole
`.prettydocs/` machinery and still serve every embedded visual.

Ignore rules go in **`<project>/.prettydocs/.gitignore`**, not the project's root
one. A pattern containing a slash anchors to its own `.gitignore`'s directory, so
these resolve correctly and the folder stays self-contained:

```
src/**/render.mp4
src/**/renders/
src/**/frames/
src/**/snapshots/
src/**/qa_*.png
src/**/check.json
src/**/node_modules/
```

**Pre-existing repos** may carry the older layout — `docs/assets/src/DESIGN.md`
with the per-visual state beside it. Offer the migration (`design-system.md` →
Migrating a project off the old layout); never write a second system alongside the
first. Every hash is taken over file bytes, so the move re-renders nothing.

## Workflow

Run the phases in order. Don't skip the evidence pass.

### 1. Evidence pass

Gather facts in priority order (later never overrides earlier): existing docs →
manifests/lockfiles → repo signals (`LICENSE`, CI workflows, `CLAUDE.md`/
`AGENTS.md` are first-class) → code structure → git (remote/forge, default
branch). Detect project type and forge (house-style → Host awareness /
Project-type adaptation). **Derive a copyright-holder candidate** via the ladder
in house-style → identity guardrail: authoritative repo sources first, then the
forge-owner lookup (an **organisation** account's display name is auto-used; a
user-account name or `git config user.name` only becomes the pre-filled default
for phase 4; the OS username is never a candidate). **Additionally detect the
product's visual identity:** logos/icons, brand tokens (CSS custom properties,
Tailwind config, theme files), an existing style guide or DESIGN.md. These feed
phase 2. **Also resolve the project roots** — a repo may document more than one,
and each carries its own design system.

### 2. Design system

Read `reference/design-system.md` and walk its discovery ladder per project, then
derive or load `<project>/.prettydocs/prettydocs.md`:

- **Own contract exists** and identity unchanged → load it; **frozen** for this run.
- **An ancestor's exists** → inherit it as the base. A project overrides by
  carrying its own.
- **A design source was found instead** (a `DESIGN.md`, a README stating a palette,
  brand tokens) → derive `prettydocs.md` *from* it and record
  `design_source_path` / `design_source_hash`. A source is never the contract.
- **Nothing found** → derive from product identity when one exists, otherwise from
  product semantics, and write it.
- **Old layout found** (`docs/assets/src/DESIGN.md`, no `.prettydocs/`) → offer the
  migration rather than deriving a second system.
- Re-derive an existing contract only when the product's identity clearly changed
  or the user asked. Changing it invalidates every visual (design-hash drift), so
  say so in the plan.

### 3. Plan

Classify every in-scope doc: `CREATE` / `UPDATE` / `OK`. Prose-style
differences are not drift. Classify every in-scope visual per the lazy rules in
`embedding.md`: `RENDER` (new) / `RE-RENDER` (facts, source, or design hash
changed; asset missing; marker mismatch; `--refresh-viz`) / `REUSE` / `OK`.
Respect the budget table; a pure prose change must plan zero renders.

### 4. Questions (batched, once, up front)

Ask only what can't be derived or safely defaulted: **ownership/copyright
holder, license, support channels** — plus, when phase 2 found *no* identity
signals and the motif choice is genuinely ambiguous, at most **one** visual
question (motif/tone direction) in the same batch. Persist answers to
`.github/docsmeta.json` (schema in house-style), so each is asked once per repo
and later runs are unattended.

Holder question mechanics (ladder detail in house-style → identity guardrail):
skip it entirely when phase 1 auto-resolved the holder (authoritative source or
org display name). When phase 1 produced only a confirm-tier candidate (a
user-account display name, a bare owner slug, or `git config user.name`), offer
it as the **pre-filled recommended answer** — one keystroke to accept, but never
written to LICENSE, footers, or `docsmeta` without that confirmation. No
candidate at all → ask with no pre-fill.

### 5. Apply — docs

On a repo with existing docs, write after planning; on a brand-new repo,
present the plan and get a go-ahead first. Edit **section by section**, never
whole-file regeneration. Preserve human prose; update facts in place. Insert
embeds and `pd:viz` markers per `reference/embedding.md`; add the `<details>`
Mermaid fallback in technical docs. Humanize the prose you wrote (house-style →
Humanize).

### 6. Apply — visuals

For each `RENDER`/`RE-RENDER` visual, follow `reference/viz-production.md`
exactly: scaffold → author to `prettydocs.md` → **gate loop** (lint → snapshot at 3
timestamps and read the frames → `hyperframes check` with 0 errors) → render →
`scripts/viz_to_webp.sh` (enforces the 2.5 MB cap) → verify real pixels →
update `viz.json` + marker hashes together. Statics: author per the
static-SVG section of the same reference. Write `.prettydocs/.gitignore` if the
project has none yet; its rules are project-relative, so they need no upkeep after.

### 7. Verify

Run the ten quality gates in house-style over what you changed this run: five
textual (Mermaid validity, link/anchor integrity, boilerplate consistency,
cross-doc truth, leak/guardrail + volatile-facts grep) and five visual
(composition check clean, asset presence + ≤2.5 MB, marker/manifest integrity
via `scripts/audit_visuals.py`, works-without-images, budget + centered embeds +
LICENSE/NOTICE placement). Fix and re-check what you can; surface the rest.

In `check` mode: run the same gates read-only over the existing docs, plus
`scripts/audit_visuals.py`, and judge `CONTRADICTS` for each visual's stored
facts against the fresh evidence pass. Write nothing.

### 8. Report

In-chat summary only (the git diff is the audit trail):

- Per-doc table: `CREATED`/`UPDATED`/`OK`/`DEFERRED` + a terse note.
- Per-visual table: `RENDERED`/`RE-RENDERED`/`REUSED`/`OK` + sizes; in check
  mode the audit verdicts instead.
- Metadata saved to `.github/docsmeta.json`; design-system status (loaded /
  derived / re-derived).
- Degradation paths taken (humanizer skill vs inline checklist; Mermaid
  validator present or not; any visual downgraded to static for size).
- Every `<!-- TODO -->` left; any doc or visual deferred.
- If the repo has CI, a one-line offer (only) to add a docs-drift `check` step.

## Non-negotiables

- **Preflight before work; STOP on a failed HyperFrames check.**
- **Mermaid or produced visuals for every diagram. No ASCII art, ever.**
- **No volatile facts** in docs or visuals — no minor/patch versions, release
  dates, or per-release feature/bugfix notes (house-style → No volatile facts).
- **LICENSE and NOTICE are never visualized or formatted.** Verbatim only.
- **Every doc works with images off** — alt text, `<details>` Mermaid, adjacent
  banner text.
- **Ground every visual**; its `viz.json` facts list is part of the truth the
  gates check.
- **Reproduce, don't author, legal text** (`reference/tier2/license.md`).
- **Reflect reality, not aspiration** — in prose and in pixels.

## References

| File | Read when |
| --- | --- |
| `reference/house-style.md` | First, every run |
| `reference/<doc>.md` / `reference/tier2/<doc>.md` | Before touching that doc |
| `reference/design-system.md` | Phase 2 |
| `reference/embedding.md` | Before any embed, marker edit, or `check` |
| `reference/viz-production.md` | Phase 6, before any render or static SVG |
| `scripts/viz_to_webp.sh` | Called by phase 6 (never hand-roll the conversion) |
| `scripts/audit_visuals.py` | Phase 7 and `check` mode |
