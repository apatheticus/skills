---
name: prettier-svg-docs
description: Create and maintain a repository's standard documentation — README, ARCHITECTURE, DEVELOPMENT, DEPLOYMENT, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, SUPPORT, plus on-demand LICENSE, NOTICE, issue/PR templates, and CODEOWNERS — and beautify it with a per-repo design system, a 27-type diagram grammar, and seamless-loop animated SVG authored directly, with zero external dependencies — no renderer, nothing to install. Every diagram is checked for orthogonal connectors, label geometry, contrast and a seam-exact loop before it may be embedded.
when_to_use: Use whenever the user wants beautiful, illustrated, animated, or visually polished project docs; a README with an animated hero or animated diagrams; doc visuals refreshed, restyled, or audited for staleness; or invokes /prettier-svg-docs. Use it for a single diagram too — architecture, it-state, flowchart, sequence, state, er, timeline, swimlane, quadrant, radar, loop, nested, tree, org-chart, layers, venn, pyramid, bar, line, gantt, scatter, high-level, process, medallion, data-flow, dp-integration, dp-security-matrix — or for the semantic patterns fan-in bottleneck, stage framework, structured artifact, paired policy traces, secure paved road, control catalog, and compensating security layers. Styles include swiss-minimal, neo-brutalist, blueprint, bento-grid, glassmorphism, and soft-vinyl. For text-only docs the update-docs skill fits better; use pretty-hyper-docs only for WebP or HyperFrames, and pretty-plain-docs for still images or an explicit no-animation request.
---

# prettier-svg-docs

Create and maintain a repository's standard documentation so it reflects the
**actual current truth** of the project — then make it genuinely beautiful: a frozen
per-repo design system, a chosen visual style, an animated hero, and seamless-loop
animated SVG diagrams where they earn their place, hand-authored and embedded so
they render on GitHub.

**Nothing is rendered.** The `.svg` you write is the committed asset. Everything the
skill needs is `python3` and its own bundled scripts, so a run never dies on a
missing toolchain.

Three principles govern everything:

- **Honesty over polish.** A short, accurate doc beats a long plausible one. Never
  describe tests, CI, tooling, or architecture the repo doesn't contain. A visual
  asserts facts with *more* authority than prose, so every diagram — animated or
  static — depicts only verifiable structure, and records which facts it depicts in
  its manifest.
- **Visuals enhance, never decorate.** Each doc is written for its audience (see the
  matrix below), and a visual exists only where it communicates something to that
  audience faster than text would.
- **Style is a decision, not a mood.** The look is one named idiom, resolved once,
  written into the design system, and applied to every visual in the repo.

## Preflight (probe and warn — never a STOP)

```bash
command -v python3          # required by both bundled scripts
```

- **`python3` missing** → warn loudly and run content-only. Every visual becomes
  `DEFERRED`; report why. Don't attempt a visual you can't gate.
- **Note whether a browser tool is available** (Playwright, claude-in-chrome). Without
  one, the pixel-read step is **skipped and reported**, never silently passed.
- Nothing else to check. There is no renderer, no `ffmpeg`, no `img2webp`, no CLI,
  and no network dependency.

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
conventions live in `reference/house-style.md` — **read it first on every run**, then
the spec for each doc you touch. Before any embed or audit read
`reference/embedding.md`; before authoring any visual read
`reference/viz-production.md` and `reference/svg-animation.md`.

**Filenames:** outputs use conventional uppercase names (`README.md`, `SECURITY.md`,
…). Match existing files case-insensitively; keep a repo's existing convention rather
than creating duplicates.

## Invocation modes

| Invocation | Effect |
| --- | --- |
| `/prettier-svg-docs` | Full pass over Tier 1: content + visuals |
| `/prettier-svg-docs <target> [<target>…]` | Only the named docs (`readme`, `deployment`, `security`, …; Tier 2 by explicit name) |
| `/prettier-svg-docs check` | **Read-only audit** — content verdicts (`CREATE`/`UPDATE`/`OK`) *and* visual verdicts (`OK`/`MISSING`/`STALE`/`DRIFT`/`CONTRADICTS`/`BUDGET`/`FOREIGN`). Writes nothing. |
| `--style <slug\|free-form>` | Set the visual style for this repo (see below). Persisted; re-runs reuse it. |
| `--style auto` | Force re-derivation of the style from product identity, ignoring the stored slug |
| `--refresh-viz` | Force re-authoring of every in-scope visual regardless of hashes |
| `--no-viz` | Content-only run; leave every existing visual and marker untouched |
| `--budget <doc>=<n>` | Override a doc's animated-visual budget for this run (e.g. `--budget readme=1`) |
| `--brief` / `--full` | Prose-depth override (see house-style → Sizing). Independent of the visual budget. |

### Styles

Thirty-two named idioms, one chosen per repo, listed alphabetically:

`bento-grid` · `blueprint` · `brushed-metal` · `claymorphism` · `codex-leonardo` ·
`console-elbow` · `digital-rain` · `draughtsman-notebook` · `editorial` ·
`flat-material` · `glassmorphism` · `holographic-projection` · `hud` · `ide-dark` ·
`isometric-3d` · `lofi-wireframe` · `maximalist` · `neo-brutalist` · `neumorphism` ·
`oil-impasto` · `patent-drawing` · `pencil-lined-paper` · `rough-sketch` ·
`schematic` · `skeuomorphic` · `soft-vinyl` · `swiss-minimal` · `terminal-minimalist` ·
`watercolor` · `whiteboard-marker` · `wood-grain` · `y2k-retrofuturist`

Common aliases resolve without asking (`brutalist`, `glass`, `soft-ui`, `swiss`,
`material`, `clay`, `y2k`, `tui`, `cli`, `bento`, `technical-drawing`, `excalidraw`,
`hologram`, `lcars`, `patent`, `wireframe`, `whiteboard`, `impasto`, …). A free-form
name that names a genuinely recognisable idiom is synthesized into a full spec;
anything unresolvable prompts **one** question. Nothing specified → derived from the
product, exactly as before this option existed.

Every style ships a full-width **specimen** at `docs/samples/<slug>.svg`, embedded at
the top of its spec file, showing the same Source → Transform → Store diagram so the
idioms are directly comparable. `docs/assets/styles.svg` is the contact sheet of all
thirty-two, composed from those specimens rather than redrawn.

Each style also declares a **fidelity floor** — the primitives its material is built
from, a minimum filter-chain depth, and a minimum drawn density. `svg_check.py`
enforces it and reports what each visual achieved, so a style cannot be rendered as a
flat imitation of itself and still gate clean. See `styles.md`.

Two dials cut across the catalog and are usually the right answer when a request
lands *between* two styles: **roughness** (the hand-drawn family is one displacement
scale, `0.7` ruled → `4.5` improvised) and **grain ratio** (the material family is
one `feTurbulence` x:y ratio, equal → isotropic, extreme → directional). Move the
dial rather than inventing a style.

Three cautions the catalog cannot design away, all detailed in `reference/styles.md`:
display fonts are **never fetched** and degrade to system handwriting faces;
`watercolor`, `oil-impasto` and `lofi-wireframe` are **decorative** — their contrast
floor is *not* relaxed, so each names the move that earns its labels back; and
`console-elbow`, `holographic-projection` and `digital-rain` reproduce a visual
language only — **decline to add logos, insignia, wordmarks or fictional alphabets**
on request rather than treating them as a customisation option.

**Style owns form; the product's brand tokens still own the palette.** Full rules and
the resolution ladder: `reference/styles.md`.

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

The budget is about the reader's attention, not about cost. Authoring an SVG is
cheap now — which is exactly why the budget matters more, not less. A doc where
everything moves has nothing to draw the eye. A diagram that wouldn't earn a place
in a printed engineering doc doesn't get animated.

Per asset: **warn at 60 KB, hard fail over 150 KB.** Loops run 8–14s and are
seam-exact. Under-spending the budget is always allowed.

## Target layout (the skill maintains this)

One block per project. A repo documenting several projects repeats it per project
root — see `design-system.md` → What counts as a project.

```
<project>/docs/assets/<viz-name>.svg   # committed — the asset AND its own source
<project>/.prettydocs/
├── .gitignore                     # committed — byproduct rules, self-contained
├── prettydocs.md                  # committed — frozen design system + resolved style
└── src/<viz-name>/
    ├── viz.json                   # committed — facts, hashes, svg params (embedding.md)
    └── _qa/                       # gitignored — filmstrip.html, phase_*.png
```

Rendered assets stay under `docs/assets/` so a deployment can exclude the whole
`.prettydocs/` machinery and still serve every embedded visual. Because the
committed `.svg` **is** the source here, `.prettydocs/src/<viz-name>/` holds only
the manifest and the gitignored QA harness.

Ignore rules go in **`<project>/.prettydocs/.gitignore`**, not the project's root
one. A pattern containing a slash anchors to its own `.gitignore`'s directory, so
this resolves correctly and the folder stays self-contained:

```
src/**/_qa/
```

**Pre-existing repos** may carry the older layout — `docs/assets/src/DESIGN.md`
with the per-visual state beside it. Offer the migration (`design-system.md` →
Migrating a project off the old layout); never write a second system alongside the
first. Every hash is taken over file bytes, so the move re-renders nothing.

## Workflow

Run the phases in order. Don't skip the evidence pass.

### 1. Evidence pass

Gather facts in priority order (later never overrides earlier): existing docs →
manifests/lockfiles → repo signals (`LICENSE`, CI workflows, `CLAUDE.md`/`AGENTS.md`
are first-class) → code structure → git (remote/forge, default branch). Detect
project type and forge (house-style → Host awareness / Project-type adaptation).
**Derive a copyright-holder candidate** via the ladder in house-style → identity
guardrail: authoritative repo sources first, then the forge-owner lookup (an
**organisation** account's display name is auto-used; a user-account name or
`git config user.name` only becomes the pre-filled default for phase 4; the OS
username is never a candidate). **Additionally detect the product's visual
identity:** logos/icons, brand tokens (CSS custom properties, Tailwind config, theme
files), an existing style guide or DESIGN.md. These feed phase 2. **Also resolve the
project roots** — a repo may document more than one, and each carries its own design
system.

Also detect **foreign visuals** — `viz.json` files whose `producer` is neither
`prettier-svg-docs` nor the legacy `more-pretty-docs`, or embeds pointing at `.webp`.
Those are adoption candidates (`embedding.md` → Adopting visuals from another
producer). A legacy `mpd.json` filename or `mpd:` marker is **not** foreign — it is
this skill's own older output, and it is rewritten in place on the next touch.

### 2. Design system and style

Read `reference/styles.md` and resolve the style first — explicit `--style`, then an
alias, then a recognisable free-form idiom, then one question, then derivation from
the product. Read **exactly one** `reference/styles/<slug>.md` for the resolved
style; never the whole directory.

Then read `reference/design-system.md`, walk its discovery ladder per project, and
derive or load `<project>/.prettydocs/prettydocs.md`:

- **Own contract exists** and identity + style unchanged → load it; **frozen** for
  this run.
- **An ancestor's exists** → inherit it as the base. A project overrides by carrying
  its own.
- **A design source was found instead** (a `DESIGN.md`, a README stating a palette,
  brand tokens) → derive `prettydocs.md` *from* it and record `design_source_path` /
  `design_source_hash`. A source is never the contract.
- **Nothing found** → derive it (mapping from product identity when one exists;
  otherwise from product semantics), write the resolved style into its `## Style`
  section, and — in a single-project repo only — save the slug to
  `.github/docsmeta.json` as `viz.style`.
- **Old layout found** (`docs/assets/src/DESIGN.md`, no `.prettydocs/`) → offer the
  migration rather than deriving a second system.
- Re-derive an existing contract only when the product's identity clearly changed,
  the style changed, or the user asked. Changing it invalidates every visual
  (design-hash drift), so say so in the plan.

### 3. Plan

Classify every in-scope doc: `CREATE` / `UPDATE` / `OK`. Prose-style differences are
not drift. Classify every in-scope visual per the lazy rules in `embedding.md`:
`RENDER` (new) / `RE-RENDER` (facts, source, or design hash changed; asset missing;
marker mismatch; `--refresh-viz`) / `REUSE` / `OK`. Respect the budget table; a pure
prose change must plan zero re-authoring.

**If the style changed, say so explicitly with a count** — "style `editorial` →
`neo-brutalist`: `design_hash` moves, all 5 visuals will be re-authored" — before any
work starts. A style switch is the one edit that touches everything.

**Every structural visual gets a `diagram_type` in the same table**, chosen from
`reference/diagrams.md` — which starts with the test for whether to draw at all. Type
is the one decision no later edit repairs: a style change is a re-render, a type change
is a re-author, because the node count, the page axis, the connector grammar and the
`viewBox` height all move with it. Where behaviour rather than structure carries the
meaning, pick a semantic pattern first (`reference/diagram-patterns.md`) and take its
nearest type.

A hero, a banner or a decorative board has no type; leave the column empty and it
carries no `data-diagram`, so the diagram gate never fires on it. A visual that already
records `diagram_type` in `viz.json` and carries `data-diagram` on its root has been
through this step — do not ask again.

Name the cuts here too. Anything the type's budget forces out is written to
`budget_cuts[]` in that visual's `viz.json` and repeated in the phase-8 report, the
same way `relaxed[]` records a softened gate. An unrecorded cut and an unnoticed
omission are indistinguishable to the next run.

### 4. Questions (batched, once, up front)

Ask only what can't be derived or safely defaulted: **ownership/copyright holder,
license, support channels** — plus, when phase 2 could neither resolve nor derive a
style, **one** visual question naming 2–3 candidate styles. Fold it into the same
batch; never a second round. Persist answers to `.github/docsmeta.json` (schema in
house-style), so each is asked once per repo and later runs are unattended.

Holder question mechanics (ladder detail in house-style → identity guardrail): skip
it entirely when phase 1 auto-resolved the holder (authoritative source or org
display name). When phase 1 produced only a confirm-tier candidate (a user-account
display name, a bare owner slug, or `git config user.name`), offer it as the
**pre-filled recommended answer** — one keystroke to accept, but never written to
LICENSE, footers, or `docsmeta` without that confirmation. No candidate at all → ask
with no pre-fill.

### 5. Apply — docs

On a repo with existing docs, write after planning; on a brand-new repo, present the
plan and get a go-ahead first. Edit **section by section**, never whole-file
regeneration. Preserve human prose; update facts in place. Insert embeds and
`pd:viz` markers per `reference/embedding.md`; add the `<details>` Mermaid fallback
in technical docs. Humanize the prose you wrote (house-style → Humanize).

### 6. Apply — visuals

For each `RENDER`/`RE-RENDER` visual, follow `reference/viz-production.md` exactly:
author `docs/assets/<name>.svg` → **gate loop** (`scripts/svg_check.py` until 0
errors) → `scripts/svg_filmstrip.py` → serve over HTTP and **read the pixels** →
write `viz.json` + marker hashes together. Statics are the same file format minus the
animation block. Write `.prettydocs/.gitignore` if the project has none yet; its
one rule is project-relative, so it needs no upkeep after.

Record every `SOFTENED` line the checker emitted into that visual's `relaxed` array.

### 7. Verify

Run the ten quality gates in house-style over what you changed this run: five textual
(Mermaid validity, link/anchor integrity, boilerplate consistency, cross-doc truth,
leak/guardrail + volatile-facts grep) and five visual (`svg_check.py` clean, asset
presence + ≤150 KB, marker/manifest integrity via `scripts/audit_visuals.py`,
works-without-images, budget + centered embeds + LICENSE/NOTICE placement). Fix and
re-check what you can; surface the rest.

In `check` mode: run the same gates read-only over the existing docs, plus
`scripts/audit_visuals.py`, and judge `CONTRADICTS` for each visual's stored facts
against the fresh evidence pass. Write nothing.

### 8. Report

In-chat summary only (the git diff is the audit trail):

- Per-doc table: `CREATED`/`UPDATED`/`OK`/`DEFERRED` + a terse note.
- Per-visual table: `RENDERED`/`RE-RENDERED`/`REUSED`/`OK` + byte sizes; in check
  mode the audit verdicts instead.
- **The resolved style**, how it was resolved (flag / alias / ad-hoc / derived), and
  **every softened gate** with the count of visuals affected. Never let a relaxation
  pass silently.
- Metadata saved to `.github/docsmeta.json`; design-system status (loaded / derived /
  re-derived).
- Any adoption performed: embeds rewritten, plus the full `ORPHANED` list. Nothing
  was deleted.
- Degradation paths taken (humanizer skill vs inline checklist; Mermaid validator
  present or not; **pixel review skipped for want of a browser tool**).
- Every `<!-- TODO -->` left; any doc or visual deferred.
- If the repo has CI, a one-line offer (only) to add a docs-drift `check` step.

## What is enforced, and by what

Most of the rules that used to live here are owned by a script, and a rule a script
fails loudly on does not need saying twice. This table says who owns what, so that a
rule's absence from the prose is never mistaken for a rule's absence.

| Rule | Owner | What failure looks like |
| --- | --- | --- |
| No `<script>` or `<foreignObject>`; no remote reference, `@import` or off-host `url()`; no DOCTYPE | `svg_check.py` structural | `ERROR`, blocks the embed |
| Seam arithmetic — every duration divides `data-loop-s`, every animation `infinite`, no entrance | `svg_check.py` seam | `ERROR` |
| A `prefers-reduced-motion` block on every animated visual, including `display: none` for SMIL | `svg_check.py` motion-a11y | `ERROR` |
| Type floors per `data-role`, contrast against the declared `data-bg` ground | `svg_check.py` legibility + system | `ERROR`; a `data-bg` that names no palette role is a `WARN` and the contrast floor then goes unapplied — treat that `WARN` as a failure |
| Palette discipline — every colour through a declared token, no raw hex | `svg_check.py` system | `ERROR` |
| Style invariants and fidelity floors | `svg_check.py` style + fidelity | `ERROR`, with a positive `NOTE` reporting what it counted |
| Byte budget | `svg_check.py` size | `ERROR` over the cap, `WARN` when dense |
| Diagram budgets, orthogonal connectors, label clip and gap, the 4-unit grid, legend placement, geometry-is-not-animated | `svg_check.py` diagram | `ERROR`, on any visual whose root carries `data-diagram` |
| Embeds centered, one `pd:viz` pair per visual, per-doc visual budget, LICENSE/NOTICE never visualized, foreign producers never overwritten | `audit_visuals.py` | non-zero exit |
| Alt text and `<desc>` still describe what the visual draws — a number on the board is named in the description, an ordinal in the description is on the board | `audit_visuals.py` | `MISDESCRIBED`, non-zero exit |
| Every diagram type in `diagrams.json` is named in the frontmatter | `validate.mjs` | CI fails the build |

A `SOFTENED` line is a pass that must be reported into `relaxed[]`, a `WARN` is
advisory, an `ERROR` blocks. Zero errors before a visual may be embedded.

## What no script can check

These are the judgments. Each is a question with an answer, because a prohibition only
tells you that you have failed, and a question tells you what to produce.

- **For each box on this diagram, which file, config or entry point proves the thing
  exists?** Name it, or cut the box. Same question for a prose claim, a plotted value
  (which additionally must be *recomputable* — `reference/charts.md`), and a fact in
  `viz.json`.
- **Which sentence here would be wrong after the next release?** A minor or patch
  version, a release date, a per-release feature note — cut it. Docs record what the
  project *is*, not what it shipped last week.
- **Read this doc with images off. Is anything now missing?** Alt text, the collapsed
  Mermaid source, the text beside a banner. This is what makes a softened contrast gate
  survivable rather than a quiet regression.
- **Is this doc describing what the project does, or what someone hopes it will do?**
  In prose and in pixels alike.
- **Is any of this legal text something you composed?** LICENSE and NOTICE are
  reproduced verbatim, never authored and never formatted
  (`reference/tier2/license.md`).
- **Did anything here get drawn as ASCII art?** Every diagram is a produced visual or a
  Mermaid block.
- **Whose artefact is this?** A visual another producer made is adopted or left alone —
  the embed is rewritten and the orphan reported, and nothing is deleted.

## References

| File | Read when |
| --- | --- |
| `reference/house-style.md` | First, every run |
| `reference/styles.md` | Phase 2, to resolve the style |
| `reference/styles/<slug>.md` | Phase 2, exactly one — the resolved style |
| `reference/design-system.md` | Phase 2 |
| `reference/diagrams.md` | Phase 3, before the plan names a `diagram_type` |
| `reference/types/<slug>.md` | Phase 6, exactly one per diagram — the chosen type |
| `reference/diagram-grammar.md` | Phase 6, before the first diagram of a run |
| `reference/diagram-patterns.md` | Phase 3, when behaviour rather than structure carries the meaning |
| `reference/charts.md` | Before plotting any number |
| `reference/annotation.md` | Only when a diagram earns an editorial callout |
| `reference/icons.md` | Only when a diagram earns an icon |
| `reference/<doc>.md` / `reference/tier2/<doc>.md` | Before touching that doc |
| `reference/embedding.md` | Before any embed, marker edit, adoption, or `check` |
| `reference/viz-production.md` | Phase 6, before authoring any SVG |
| `reference/svg-animation.md` | Phase 6, before the first animated visual of a run |
| `scripts/svg_check.py` | The phase-6 gate loop (never skip it) |
| `scripts/svg_filmstrip.py` | Phase 6, to build the scrub harness |
| `scripts/styles.json` | Read by the checker; keep in step with `reference/styles/` |
| `scripts/diagrams.json` | Read by the checker and by `validate.mjs`; keep in step with `reference/types/` |
| `scripts/test_diagram_check.py` | After any change to the `diagram` check class |
| `scripts/test_alt_parity.py` | After any change to `describe_parity` in `audit_visuals.py` |
| `scripts/audit_visuals.py` | Phase 7 and `check` mode |
