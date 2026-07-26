---
name: more-pretty-docs
description: Create and maintain a repository's standard documentation — README, ARCHITECTURE, DEVELOPMENT, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, SUPPORT, plus on-demand LICENSE, NOTICE, issue/PR templates, and CODEOWNERS — and beautify it with a per-repo design system and seamless-loop animated SVG visuals authored directly, with zero external dependencies — no renderer, nothing to install. Use this whenever the user wants beautiful, illustrated, animated, or visually polished project docs; wants a README with an animated hero or animated diagrams; wants doc visuals refreshed, restyled, or audited for staleness; wants a named visual style such as Swiss minimal, neo-brutalist, blueprint, or bento grid; or invokes /more-pretty-docs — even when they name only one file or none at all. For plain text-only docs without visuals, the sibling update-docs skill fits better; use the sibling make-pretty-docs only when the user specifically wants WebP or names HyperFrames.
---

# more-pretty-docs

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
README · ARCHITECTURE · DEVELOPMENT · CONTRIBUTING · CODE_OF_CONDUCT · SECURITY · SUPPORT

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
| `/more-pretty-docs` | Full pass over Tier 1: content + visuals |
| `/more-pretty-docs <target> [<target>…]` | Only the named docs (`readme`, `security`, …; Tier 2 by explicit name) |
| `/more-pretty-docs check` | **Read-only audit** — content verdicts (`CREATE`/`UPDATE`/`OK`) *and* visual verdicts (`OK`/`MISSING`/`STALE`/`DRIFT`/`CONTRADICTS`/`BUDGET`/`FOREIGN`). Writes nothing. |
| `--style <slug\|free-form>` | Set the visual style for this repo (see below). Persisted; re-runs reuse it. |
| `--style auto` | Force re-derivation of the style from product identity, ignoring the stored slug |
| `--refresh-viz` | Force re-authoring of every in-scope visual regardless of hashes |
| `--no-viz` | Content-only run; leave every existing visual and marker untouched |
| `--budget <doc>=<n>` | Override a doc's animated-visual budget for this run (e.g. `--budget readme=1`) |
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
product, exactly as before this option existed.

Every style ships a full-width **specimen** at `docs/samples/<slug>.svg`, embedded at
the top of its spec file, showing the same Source → Transform → Store diagram so the
idioms are directly comparable. `docs/assets/styles.svg` is the contact sheet of all
thirty-one, composed from those specimens rather than redrawn.

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
| README | Everyone; first visit | Animated hero + up to 3 animated diagrams; **rich alt text, no Mermaid fallback**. Purpose/solution/getting-started/usage only — repo-process detail links out to DEVELOPMENT/CONTRIBUTING. |
| ARCHITECTURE | Engineers | 1–2 flagship animated diagrams, each + collapsed `<details>` Mermaid source; rest static SVG or plain Mermaid |
| DEVELOPMENT | Engineers | Same treatment as ARCHITECTURE |
| CONTRIBUTING | Engineers/contributors | Same treatment as ARCHITECTURE |
| SECURITY | Everyone; prescriptive | One attention banner: "report privately, never a public issue" |
| CODE_OF_CONDUCT | Everyone; prescriptive | One attention banner: the core conduct expectation; covenant body untouched |
| SUPPORT | Users seeking help | Static designed header at most |
| LICENSE / NOTICE | Legal | **None. Ever.** Verbatim legal text; no markers, badges, or formatting. |

## Visual budget (defaults; `--budget` overrides per run)

| Doc | Animated | Static SVG |
| --- | --- | --- |
| README | hero + ≤3 diagrams | as needed |
| ARCHITECTURE / DEVELOPMENT / CONTRIBUTING | 1–2 flagship each | remaining diagrams |
| SECURITY / CODE_OF_CONDUCT | ≤1 (the banner; static also fine) | — |
| SUPPORT | 0 | ≤1 header |
| LICENSE / NOTICE / templates / CODEOWNERS | 0 — hard gate | 0 — hard gate |

The budget is about the reader's attention, not about cost. Authoring an SVG is
cheap now — which is exactly why the budget matters more, not less. A doc where
everything moves has nothing to draw the eye. A diagram that wouldn't earn a place
in a printed engineering doc doesn't get animated.

Per asset: **warn at 60 KB, hard fail over 150 KB.** Loops run 8–14s and are
seam-exact. Under-spending the budget is always allowed.

## Target-repo layout (the skill maintains this)

```
docs/assets/<viz-name>.svg         # committed — the asset AND its own source
docs/assets/src/DESIGN.md          # committed — frozen design system + resolved style
docs/assets/src/<viz-name>/
├── mpd.json                       # committed — facts, hashes, svg params (embedding.md)
└── _qa/                           # gitignored — filmstrip.html, phase_*.png
```

The skill adds/maintains one `.gitignore` entry:

```
docs/assets/src/**/_qa/
```

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
files), an existing style guide or DESIGN.md. These feed phase 2.

Also detect **foreign visuals** — `mpd.json` files whose `producer` isn't
`more-pretty-docs`, or embeds pointing at `.webp`. Those are adoption candidates
(`embedding.md` → Adopting visuals from another producer).

### 2. Design system and style

Read `reference/styles.md` and resolve the style first — explicit `--style`, then an
alias, then a recognisable free-form idiom, then one question, then derivation from
the product. Read **exactly one** `reference/styles/<slug>.md` for the resolved
style; never the whole directory.

Then read `reference/design-system.md` and derive or load
`docs/assets/src/DESIGN.md`:

- Exists and identity + style unchanged → load it; it is **frozen** for this run.
- Missing → derive it (mapping from product identity when one exists; otherwise from
  product semantics), write the resolved style into its `## Style` section, and — in a
  single-doc-root repo only — save the slug to `.github/docsmeta.json` as `viz.style`.
- Re-derive an existing one only when the product's identity clearly changed, the
  style changed, or the user asked. Changing it invalidates every visual
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
`mpd:viz` markers per `reference/embedding.md`; add the `<details>` Mermaid fallback
in technical docs. Humanize the prose you wrote (house-style → Humanize).

### 6. Apply — visuals

For each `RENDER`/`RE-RENDER` visual, follow `reference/viz-production.md` exactly:
author `docs/assets/<name>.svg` → **gate loop** (`scripts/svg_check.py` until 0
errors) → `scripts/svg_filmstrip.py` → serve over HTTP and **read the pixels** →
write `mpd.json` + marker hashes together. Statics are the same file format minus the
animation block. Maintain the `.gitignore` entry.

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

## Non-negotiables

- **No `<script>` in any committed SVG.** Ever, under any style or flag.
- **Every animated visual carries a `prefers-reduced-motion` block** that stops all
  motion and leaves a legible still — including a `display: none` rule for any
  SMIL-animated element, since CSS cannot stop SMIL.
- **Zero `svg_check.py` errors before a visual is embedded.** A `SOFTENED` line is a
  pass that must be reported; a `WARN` is advisory; an `ERROR` blocks.
- **Mermaid or produced visuals for every diagram. No ASCII art, ever.**
- **No volatile facts** in docs or visuals — no minor/patch versions, release dates,
  or per-release feature/bugfix notes (house-style → No volatile facts).
- **LICENSE and NOTICE are never visualized or formatted.** Verbatim only.
- **Every doc works with images off** — alt text, `<details>` Mermaid, adjacent
  banner text. This is what makes a softened contrast gate survivable.
- **Ground every visual**; its `mpd.json` facts list is part of the truth the gates
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
| `reference/svg-animation.md` | Phase 6, before the first animated visual of a run |
| `scripts/svg_check.py` | The phase-6 gate loop (never skip it) |
| `scripts/svg_filmstrip.py` | Phase 6, to build the scrub harness |
| `scripts/styles.json` | Read by the checker; keep in step with `reference/styles/` |
| `scripts/audit_visuals.py` | Phase 7 and `check` mode |
