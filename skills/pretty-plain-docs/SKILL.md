---
name: pretty-plain-docs
description: Create and maintain a repository's standard documentation — README, ARCHITECTURE, DEVELOPMENT, DEPLOYMENT, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, SUPPORT, plus on-demand LICENSE, NOTICE, issue/PR templates, and CODEOWNERS — and beautify it with a per-repo design system and hand-authored static SVG visuals, with zero external dependencies — nothing to install and nothing that moves. Use this whenever the user wants beautiful, illustrated, or visually polished project docs as still images; asks for no animation, or for docs that survive printing, PDF export, or a renderer that rasterises SVG; wants a static hero or static diagrams; wants doc visuals refreshed, restyled, or audited for staleness; wants a named visual style such as Swiss minimal, neo-brutalist, blueprint, or bento grid; or invokes /pretty-plain-docs. For animated SVG use the sibling pretty-svg-docs; for animated WebP or HyperFrames use pretty-hyper-docs; for plain text-only docs with no visuals, update-docs fits better.
license: MIT
version: 0.4.0
---

# pretty-plain-docs

Create and maintain a repository's standard documentation so it reflects the
**actual current truth** of the project — then make it genuinely beautiful: a frozen
per-repo design system, a chosen visual style, a designed header image, and static
SVG diagrams where they earn their place, hand-authored and embedded so they render
on GitHub.

**Nothing is rendered and nothing moves.** The `.svg` you write is the committed
asset. Everything the skill needs is `python3` and its own bundled scripts, so a run
never dies on a missing toolchain.

Still images are the point, not a limitation. A static `.svg` needs no renderer
cooperation beyond drawing it once, so the same file is correct on GitHub, in a
documentation-site build, in a PDF export, under a print stylesheet, and in a
reviewer's tool that rasterises SVG. Choose this skill when the docs will be printed
or exported, when a moving README is unwanted, or when motion is simply the wrong
register for the project.

Four principles govern everything:

- **Honesty over polish.** A short, accurate doc beats a long plausible one. Never
  describe tests, CI, tooling, or architecture the repo doesn't contain. A visual
  asserts facts with *more* authority than prose, so every diagram depicts only
  verifiable structure, and records which facts it depicts in its manifest.
- **Visuals enhance, never decorate.** Each doc is written for its audience (see the
  matrix below), and a visual exists only where it communicates something to that
  audience faster than text would.
- **Style is a decision, not a mood.** The look is one named idiom, resolved once,
  written into the design system, and applied to every visual in the repo.
- **A still is a finished composition, not a paused frame.** With no motion to carry
  meaning or hold attention, everything the visual says must be on the canvas: the
  ordering stated, the material drawn, the labels legible.

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
`reference/viz-production.md`; before plotting any value read `reference/charts.md`.

**Filenames:** outputs use conventional uppercase names (`README.md`, `SECURITY.md`,
…). Match existing files case-insensitively; keep a repo's existing convention rather
than creating duplicates.

## Invocation modes

| Invocation | Effect |
| --- | --- |
| `/pretty-plain-docs` | Full pass over Tier 1: content + visuals |
| `/pretty-plain-docs <target> [<target>…]` | Only the named docs (`readme`, `deployment`, `security`, …; Tier 2 by explicit name) |
| `/pretty-plain-docs check` | **Read-only audit** — content verdicts (`CREATE`/`UPDATE`/`OK`) *and* visual verdicts (`OK`/`MISSING`/`UNCENTERED`/`STALE`/`DRIFT`/`CONTRADICTS`/`BUDGET`/`FOREIGN`). Writes nothing. |
| `--style <slug\|free-form>` | Set the visual style for this repo (see below). Persisted; re-runs reuse it. |
| `--style auto` | Force re-derivation of the style from product identity, ignoring the stored slug |
| `--refresh-viz` | Force re-authoring of every in-scope visual regardless of hashes |
| `--no-viz` | Content-only run; leave every existing visual and marker untouched |
| `--budget <doc>=<n>` | Override a doc's visual budget for this run (e.g. `--budget readme=1`) |
| `--brief` / `--full` | Prose-depth override (see house-style → Sizing). Independent of the visual budget. |

### Styles

Thirty-one named idioms, one chosen per repo, listed alphabetically:

`bento-grid` · `blueprint` · `brushed-metal` · `claymorphism` · `codex-leonardo` ·
`console-elbow` · `digital-rain` · `draughtsman-notebook` · `editorial` ·
`flat-material` · `glassmorphism` · `holographic-projection` · `hud` · `ide-dark` ·
`isometric-3d` · `lofi-wireframe` · `maximalist` · `neo-brutalist` · `neumorphism` ·
`oil-impasto` · `patent-drawing` · `pencil-lined-paper` · `rough-sketch` ·
`schematic` · `skeuomorphic` · `swiss-minimal` · `terminal-minimalist` ·
`watercolor` · `whiteboard-marker` · `wood-grain` · `y2k-retrofuturist`

Common aliases resolve without asking (`brutalist`, `glass`, `soft-ui`, `swiss`,
`material`, `clay`, `y2k`, `tui`, `cli`, `bento`, `technical-drawing`, `excalidraw`,
`hologram`, `lcars`, `patent`, `wireframe`, `whiteboard`, `impasto`, …). A free-form
name that names a genuinely recognisable idiom is synthesized into a full spec;
anything unresolvable prompts **one** question. Nothing specified → derived from the
product.

The catalog is identical to the sibling skills', minus their motion vocabulary: every
style here is defined by geometry, material, palette and type, which is exactly the
part a still keeps. Every style ships a full-width **specimen** at
`docs/samples/<slug>.svg`, embedded at the top of its spec file, showing the same
Source → Transform → Store diagram so the idioms are directly comparable.
`docs/assets/styles.svg` is the contact sheet of all thirty-two, composed from those
specimens rather than redrawn.

Each style also declares a **fidelity floor** — the primitives its material is built
from, a minimum filter-chain depth, and a minimum drawn density. `svg_check.py`
enforces it and reports what each visual achieved, so a style cannot be rendered as a
flat imitation of itself and still gate clean. This matters more here than in the
animated siblings: with nothing moving, material and draughtsmanship are all the
visual has. See `styles.md`.

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
| README | Everyone; first visit | Header image + up to 3 diagrams. The **header image carries rich alt text and no Mermaid block**; every body diagram carries a collapsed `<details>` Mermaid source like the technical docs. Purpose/solution/getting-started/usage only — repo-process detail links out to DEVELOPMENT/DEPLOYMENT/CONTRIBUTING. |
| ARCHITECTURE | Engineers | 1–2 flagship diagrams, each + collapsed `<details>` Mermaid source; rest plain Mermaid |
| DEVELOPMENT | Engineers | Same treatment as ARCHITECTURE |
| DEPLOYMENT | Operators/engineers deploying it | Same treatment as ARCHITECTURE; created only when a deploy target exists |
| CONTRIBUTING | Engineers/contributors | Same treatment as ARCHITECTURE |
| SECURITY | Everyone; prescriptive | One attention banner: "report privately, never a public issue" |
| CODE_OF_CONDUCT | Everyone; prescriptive | One attention banner: the core conduct expectation; covenant body untouched |
| SUPPORT | Users seeking help | Designed header at most; the decision tree is usually better as plain Mermaid |
| LICENSE / NOTICE | Legal | **None. Ever.** Verbatim legal text; no markers, badges, or formatting. |

**Every structural visual carries a Mermaid source, README body diagrams included.**
That is a deliberate divergence from `pretty-svg-docs` and `pretty-hyper-docs`, where
a README embed gets rich alt text and no `<details>` block. An animated visual carries
part of its meaning in motion, which no Mermaid graph can express; a static diagram
has no such surplus — everything it says is structure, which is exactly what Mermaid
encodes. The argument in full: `reference/readme.md` → The Mermaid rule.

## Visual budget (defaults; `--budget` overrides per run)

| Doc | Designed SVG | Also allowed |
| --- | --- | --- |
| README | header image + ≤3 diagrams | plain Mermaid as needed |
| ARCHITECTURE / DEVELOPMENT / DEPLOYMENT / CONTRIBUTING | 1–2 flagship each | plain Mermaid for the rest |
| SECURITY / CODE_OF_CONDUCT | ≤1 (the banner) | — |
| SUPPORT | ≤1 header | plain Mermaid for the decision tree |
| LICENSE / NOTICE / templates / CODEOWNERS | 0 — hard gate | 0 — hard gate |

The budget is about the reader's attention, not about cost. Authoring an SVG is
cheap now — which is exactly why the budget matters more, not less. A doc wall-papered
with diagrams has nothing to draw the eye. A diagram that wouldn't earn a place in a
printed engineering doc doesn't earn one here either — and since this skill's output
*is* print-ready, that test is literal rather than a metaphor.

Per asset: **warn at 60 KB, hard fail over 150 KB.** Under-spending the budget is
always allowed.

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
    └── _qa/                       # gitignored — verification screenshots
```

Rendered assets stay under `docs/assets/` so a deployment can exclude the whole
`.prettydocs/` machinery and still serve every embedded visual. Because the
committed `.svg` **is** the source here, `.prettydocs/src/<viz-name>/` holds only
the manifest and the gitignored QA scratch.

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

Also detect **foreign visuals** — any `viz.json` whose `producer` is not
`pretty-plain-docs`, or an embed pointing at `.webp`. A sibling's visuals are foreign
here by design: `pretty-svg-docs` / `more-pretty-docs` means animated SVG, and an
absent `producer` means `pretty-hyper-docs` animated WebP. Both are adoption
candidates (`embedding.md` → Adopting visuals from another producer), and adoption is
**never automatic** — a repo whose visuals animate chose animation, so confirm the
switch to stills before rewriting anything. A legacy `mpd.json` filename or `mpd:`
marker is a **prefix** matter, not a producer one: those parse fine and are rewritten
to the current form on the next touch.

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

### 4. Questions (batched, once, up front)

Ask only what can't be derived or safely defaulted: **ownership/copyright holder,
license, support channels** — plus, when phase 2 could neither resolve nor derive a
style, **one** visual question naming 2–3 candidate styles. Fold it into the same
batch; never a second round. Persist answers to `.github/docsmeta.json` (schema in
house-style), so each is asked once per repo and later runs are unattended.

If phase 1 found a sibling's animated visuals, the confirmation to convert them to
stills goes in **this** batch too — not as a question mid-apply.

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
`pd:viz` markers per `reference/embedding.md`; add the `<details>` Mermaid source
after the closing marker of every structural visual, README body diagrams included.
Humanize the prose you wrote (house-style → Humanize).

### 6. Apply — visuals

For each `RENDER`/`RE-RENDER` visual, follow `reference/viz-production.md` exactly:
author `docs/assets/<name>.svg` → **gate loop** (`scripts/svg_check.py` until 0
errors) → serve over HTTP and **read the pixels** → write `viz.json` + marker hashes
together, plus the `<details>` Mermaid for a structural visual. Write
`.prettydocs/.gitignore` if the project has none yet; its one rule is
project-relative, so it needs no upkeep after.

Read the pixels at the **embedded** width (`820px`), not only full size, and look
specifically for the two defects the checker cannot see: an element left invisible or
parked to one side (the residue of a converted animation), and a composition that
only makes sense as a frame of a sequence.

Charts take the extra gate in `reference/charts.md`: every plotted value must derive
from a committed file and must appear as its own `facts` entry. A request to chart a
coverage percentage, a benchmark timing, or anything with an "as of" is **refused**
with the reason given, and the number goes in prose instead.

Record every `SOFTENED` line the checker emitted into that visual's `relaxed` array.

### 7. Verify

Run the ten quality gates in house-style over what you changed this run: five textual
(Mermaid validity, link/anchor integrity, boilerplate consistency, cross-doc truth,
leak/guardrail + volatile-facts grep) and five visual (`svg_check.py` clean, asset
presence + ≤150 KB, marker/manifest integrity via `scripts/audit_visuals.py`,
works-without-images — every structural visual's Mermaid parses and agrees with its
SVG — and budget + centered embeds + LICENSE/NOTICE placement). Fix and re-check what
you can; surface the rest.

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
- **Any chart refused**, with the value asked for and the volatile-facts reason.
- Degradation paths taken (humanizer skill vs inline checklist; Mermaid validator
  present or not; **pixel review skipped for want of a browser tool**).
- Every `<!-- TODO -->` left; any doc or visual deferred.
- If the repo has CI, a one-line offer (only) to add a docs-drift `check` step.

## Non-negotiables

- **No `<script>` in any committed SVG.** Ever, under any style or flag.
- **Nothing animates.** A single `@keyframes` block, one `animation:` declaration
  (including `animation: none`), or one SMIL tag is a gate failure — not a style
  choice. `data-loop-s` is required on every root `<svg>` and its only permitted
  value is `0`.
- **A static reads as a finished composition, not a paused frame.** No dead channel
  waiting for a pulse, no marker parked at a start position, no ordering a reader has
  to infer.
- **Every structural visual has a Mermaid source that parses and agrees with it** —
  README body diagrams included. The README header image is the one exemption and
  carries rich alt text instead.
- **Charts only from committed data.** Every plotted value derives from a file in the
  repo and appears in `facts`; volatile numbers go in prose (`reference/charts.md`).
- **Zero `svg_check.py` errors before a visual is embedded.** A `SOFTENED` line is a
  pass that must be reported; a `WARN` is advisory; an `ERROR` blocks.
- **Mermaid or produced visuals for every diagram. No ASCII art, ever.**
- **No volatile facts** in docs or visuals — no minor/patch versions, release dates,
  or per-release feature/bugfix notes (house-style → No volatile facts).
- **LICENSE and NOTICE are never visualized or formatted.** Verbatim only.
- **Every doc works with images off** — the Mermaid source, alt text, adjacent banner
  text. This is what makes a softened contrast gate survivable.
- **Ground every visual**; its `viz.json` facts list is part of the truth the gates
  check.
- **Reproduce, don't author, legal text** (`reference/tier2/license.md`).
- **Never delete another producer's artefacts.** Adoption rewrites embeds and reports
  orphans.
- **Reflect reality, not aspiration** — in prose and in pixels.

## References

| File | Read when |
| --- | --- |
| `reference/house-style.md` | First, every run |
| `reference/styles.md` | Phase 2, to resolve the style |
| `reference/styles/<slug>.md` | Phase 2, exactly one — the resolved style |
| `reference/design-system.md` | Phase 2 |
| `reference/<doc>.md` / `reference/tier2/<doc>.md` | Before touching that doc |
| `reference/embedding.md` | Before any embed, marker edit, adoption, or `check` |
| `reference/viz-production.md` | Phase 6, before authoring any SVG |
| `reference/charts.md` | Phase 6, before plotting any value |
| `scripts/svg_check.py` | The phase-6 gate loop (never skip it) |
| `scripts/styles.json` | Read by the checker; keep in step with `reference/styles/` |
| `scripts/audit_visuals.py` | Phase 7 and `check` mode |
