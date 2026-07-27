# Design system — the frozen visual contract

Every project this skill touches gets one persisted design system at
`<project>/.prettydocs/prettydocs.md`. It is the single source of truth for **all**
visuals in that project. Freeze it once, early, then
consume it everywhere so the hero, diagrams, badges, and banners read as one designed
unit.

It has two layers, and they own different decisions:

| Layer | Owns | Comes from |
| --- | --- | --- |
| **System** (palette, type, motif, inventory) | *What* the visuals are made of | the product — its brand tokens, logo, semantics |
| **Style** (shape, material, composition, draughtsmanship) | *How* that material is rendered | the run's chosen style idiom (`styles.md`) |

**Style owns form; the product's own brand tokens still own the palette.** A
`neo-brutalist` run on a repo with brand colors uses those brand colors in hard
offset blocks — it does not swap in someone else's black-and-yellow. When a repo
has no identity at all, the style's palette treatment fills the gap.

**Discovery is relaxed; persistence is prescriptive.** Those are two different jobs,
and conflating them is what this file exists to prevent. Finding a design language
means searching whatever a repo happens to carry, in whatever convention its authors
chose. Recording one means exactly one path, so `design_hash` has something stable to
hash and drift stays detectable. Everything under [Finding the design
language](#finding-the-design-language) is intake only.

## What counts as a project

A repo may document several projects, and each one gets its own design system. A
directory is a **project root** when it holds any of:

1. `.prettydocs/` — already managed. This always wins.
2. A package manifest: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`,
   `Gemfile`, `composer.json`, or a `*.csproj`.
3. A managed Tier-1 doc, `README.md` chief among them.

Never a project root: anything gitignored, `node_modules/`, `vendor/`, `.git/`, or
any path inside another project's `.prettydocs/`. The repo root is a project root
whenever it holds a Tier-1 doc.

Most repos resolve to exactly one project, and nothing below changes for them.

## Finding the design language

Resolved once per project, before any visual is produced. Stop at the first hit.

1. **`<project>/.prettydocs/prettydocs.md`** — the frozen contract. Load it as-is
   and stop. Do not re-derive, and do not consult the rungs below.
2. **The nearest ancestor's `.prettydocs/prettydocs.md`**, walking up to the repo
   root. Inherited as this project's base system, which is what keeps a monorepo
   coherent. A project overrides its inheritance by carrying its own file.
3. **An explicit design artifact** — `<project>/DESIGN.md`, then
   `<project>/docs/DESIGN.md`, then `<project>/*/DESIGN.md`.
4. **A doc carrying design language** — `<project>/README.md`, then
   `<project>/*/README.md`: a stated palette, named fonts, a described visual
   identity.
5. **Broad identity sweep** — brand tokens (`--color-*`, `--font-*`), a
   `tailwind.config` theme block, theme or style files, the dominant colors of a
   logo or icon, and the tone of the existing docs.

Two things about that order. Rung 3 outranks rung 4 deliberately: an explicit design
artifact is unambiguous, while "a README that mentions a brand color" is a judgment
call, and letting the judgment win means a passing colour reference beats a real
`DESIGN.md` sitting beside it. And every rung tries the **project directory itself
before its children** — a bare `<project>/*/DESIGN.md` glob silently skips
`<project>/DESIGN.md`, which is where the file usually is.

The **style** resolves separately and later, from `styles.md` — the ladder finds the
*system*. A discovered source that names a look ("we use a blueprint aesthetic") is
evidence for the style derivation, not a substitute for it.

If the **Claude Design** MCP is connected it may also expose a hosted design system
(`list_design_systems`, honouring `is_default`). Treat it as an optional extra
source at rung 4, never a required step: it needs a consent grant a non-interactive
run cannot obtain, so a run must degrade cleanly to the file search when the tool is
absent or refuses. **[UNVERIFIED]** — the response shape has not been confirmed
against a live grant. Validate what it actually returns before mapping from it, and
do not block a run waiting for it.

### A hit below rung 2 is a source, never the contract

The rule that makes relaxed intake safe:

> Anything found at a path other than `<project>/.prettydocs/prettydocs.md` is a
> **source to map from**. It is never the frozen contract. Derive `prettydocs.md`
> from it, record where it came from, and from then on `design_hash` is computed
> over `prettydocs.md` alone.

Skip this and relaxed discovery reintroduces the exact silent drift a single fixed
path used to prevent: two files disagreeing, with no way to tell which one the
committed visuals were built from.

Record the derivation in every following visual's manifest, as `design_source_path`
and `design_source_hash` (see `embedding.md`). A later run recomputes that hash and
**warns** when the upstream source has moved on, offering to re-derive. It does not
force a re-render — only `design_hash` does that.

### Exclusions and tie-breaks are not optional

A relaxed `DESIGN.md` search finds files that are not design systems. Two real
examples, both from the repo that publishes this skill: a
`reference/design-system/DESIGN.md` describing the *HTML report output* of an
unrelated skill, with its tokens in YAML frontmatter; and a gitignored vendored
mirror of this skill's own tree under `.agents/`. Adopting either as a doc design
system produces confidently wrong visuals, and the first one is hard to notice
because it does align with that skill's docs.

So rungs 3 and 4 must:

- **Skip** gitignored paths, `node_modules/`, `vendor/`, and `reference/`.
- **Sniff the schema** before accepting — a markdown `## Frozen system` heading and
  a palette table. Tokens in YAML frontmatter mean a different format for a
  different consumer; reject it.
- On more than one survivor, prefer the **shallowest** path. If that still ties,
  **ask** rather than guess.

## Migrating a project off the old layout

Earlier versions wrote the design system to `docs/assets/src/DESIGN.md` with the
per-visual state beside it. When a project has that layout and no `.prettydocs/`,
**offer the migration** — never derive a second system next to the first.

| Was | Becomes |
| --- | --- |
| `docs/assets/src/DESIGN.md` | `.prettydocs/prettydocs.md` |
| `docs/assets/src/<viz>/` | `.prettydocs/src/<viz>/` |
| `docs/assets/<name>.svg` | unchanged — embeds keep resolving |

The move is free: all three hashes are taken over file **bytes**, so relocating an
unchanged file yields an unchanged hash and triggers zero re-authoring. It is a path
rewrite, not a re-render. Until the user accepts, keep reading the old location —
`audit_visuals.py` resolves either layout.

## When it's frozen, when it's re-derived

- **Frozen for the duration of a run.** Once written, treat `prettydocs.md` as
  read-only while producing that run's visuals. Do not drift the palette or motif
  visual-to-visual.
- **Re-derive only** when the product's identity genuinely changes (a rebrand, a
  new logo, a pivot in what the product is) or when the user explicitly asks.
- If a `prettydocs.md` already exists and still matches the product, reuse it as-is
  — don't regenerate it just because a run started.

## Deriving the system

Fill the template below. The order depends on whether the product already has an
identity.

### No existing identity → derive in this order

1. **Product semantics** — what the repository actually helps people do. The
   system comes from the product, never from a fashionable finish forced onto it.
2. **Existing brand hints** — any logo scrap, screenshot, doc tone, or code style.
3. **Audience** — technical trust, creative energy, research clarity, operational
   confidence. Pick the register the reader expects.
4. **Finish quality** — only now choose palette, type scale, material, motif,
   composition.

Consider a **monochrome technical direction** (black, warm white, two neutral
grays; strict grid, thin rules, mono metadata) before reaching for brand color on
infrastructure, security, systems, or research repos. In style terms that reads as
`swiss-minimal`, `blueprint`, or `terminal-minimalist` — the derivation in
`styles.md` step 5 makes the same call.

### Has a design system / logo / brand tokens / existing style guide → MAP, don't invent

When the product already ships an identity, the product's identity **always wins**
over anything you'd invent. Do not create a parallel aesthetic.

1. **Extract the real tokens** from their authoritative source: CSS custom
   properties (`--color-*`, `--font-*`), a `tailwind.config` theme block, brand
   asset files, whatever the discovery ladder surfaced at rung 3 or 4, or the
   dominant colors of the logo.
2. **Record an explicit mapping table** in `prettydocs.md` — product token → doc role —
   rather than renaming or reinventing. Example:

   | Product token | Value | Doc role |
   | --- | --- | --- |
   | `--brand-900` | `#0d1117` | background |
   | `--surface` | `#161b22` | surface |
   | `--brand-500` | `#58a6ff` | accent-primary |
   | logo mark green | `#3fb950` | accent-secondary |

3. Only fill gaps the product leaves open (e.g. no defined "attention" color) —
   and note each invented value as a gap-fill, not a brand claim.

## The template (fill this into `<project>/.prettydocs/prettydocs.md`)

````markdown
# <Product> — visual design system

One frozen system; all project visuals derive from it. Facts come from the repo
(README, manifests, code), never invented. Frozen for this run.

## Provenance

Derived from: <repo-relative path of the rung 3–5 source, or "no prior identity">
Derived on:   <the run that wrote this file — no date, see the volatile-facts rule>
Mapping:      <"product tokens mapped 1:1" | "mapped with gap-fills, marked below">

Record the same source path and its hash as `design_source_path` /
`design_source_hash` in each visual's manifest, so a later run can tell that the
upstream identity moved without being forced to re-render.

## Story extraction

Audience:     <who this is for — one line>
Value:        <the one-sentence thing the product does>
Proof:        <the strongest evidence it works — real, from the repo>
First action: <the first command/step a newcomer runs>
Theme:        <the visual metaphor, derived from what the product IS/DOES>

## Frozen system

### Palette

| Role | Hex | Notes |
| --- | --- | --- |
| background       | `#______` | page canvas |
| surface          | `#______` | cards / panels |
| ink              | `#______` | primary text |
| accent-primary   | `#______` | main brand accent |
| accent-secondary | `#______` | supporting accent |
| warn / attention | `#______` | used sparingly |

<If mapped from product tokens, include the product-token → doc-role table here.>

### Typography

| Role | Stack |
| --- | --- |
| display | <system/display stack> |
| body    | <system stack> |
| mono    | `ui-monospace, SFMono-Regular, Menlo, monospace` |

**Never load a remote font.** An SVG that references a webfont renders in a
fallback face on GitHub — the sanitiser and the `<img>` context both block the
fetch, and there is no build step here to inline one. So visuals use **system
stacks only**, or text converted to paths when a specific letterform is
load-bearing. `svg_check.py` fails on any remote `href` or `@import`.

### Shape language

Radius family, stroke weight, spacing unit, corner/edge treatment — one of each.

### Motif

<One recurring, PROJECT-DERIVED cue drawn from what the product actually does or
is. Never a stock template; never reused from another repo. This is the strongest
anti-template device — repeat it lightly, never as wallpaper.>

### Composition rules

Density and register (sparse-editorial / compact-technical / expressive-gallery);
one strong composition per visual over several decorative graphics; important
content kept clear of edges.

### Style

| Field | Value |
| --- | --- |
| Slug | `<resolved-slug>` |
| Source | catalog · alias · ad-hoc · derived |
| Primary axis | <what this style decides first> |

- **Intent** — <one line: what the style is for>
- **Palette treatment** — <how the palette above is deployed; the palette itself is unchanged>
- **Shape language** — <corners, stroke weights, geometry>
- **Material / depth** — <flat, shadowed, glassy, extruded, inked>
- **Type treatment** — <weight, case, tracking, family role>
- **SVG recipes** — <the specific patterns visuals in this repo use>
- **Relaxations** — <gate: default → floor, or "none">
- **Never** — <the things that break this style>

For a catalog style, copy these fields from `reference/styles/<slug>.md`. For an
**ad-hoc** style, write all eight fields out here in full and mark the Source row
`ad-hoc` — this file is then the only record of what the style means, and later
runs reproduce the look from it.

## Visual inventory

| Asset | Doc | Depicts | Tier | Source facts |
| --- | --- | --- | --- | --- |
| hero      | README        | <the core idea>           | static-header | <files/config> |
| <diagram> | ARCHITECTURE  | <flow it shows>           | static        | <files/config> |
| <chart>   | <doc>         | <plotted quantity>        | static        | <committed file the values come from> |
| <banner>  | <doc>         | <section marker>          | banner        | — (decorative) |
````

## Rules that hold regardless of derivation path

- **Everything derives from this file.** Any visual whose palette, type, motif, or
  shape language doesn't trace back to `prettydocs.md` is off-system — fix the visual, not
  the system. `svg_check.py` enforces this for color: every `fill` and `stroke` must
  match a palette hex declared above.
- **A project with visuals but no contract is a defect, not a default.** If a
  `pd:viz` marker resolves but no `prettydocs.md` (or legacy `DESIGN.md`) can be
  found for that project, `audit_visuals.py` reports a `PROBLEM` and exits non-zero.
  It does not quietly skip the `DRIFT` check.
- **Style is part of `design_hash`.** `design_hash` is the SHA-256 of this whole
  file, so changing the `## Style` section invalidates every visual in the repo.
  That is correct — a style change is a re-render — but it must be stated in the
  phase-3 plan before any work starts.
- **No volatile facts inside visuals** — no minor/patch versions, no dates. A
  string baked into a visual goes stale silently even when it's greppable text.
- **Every load-bearing depiction is grounded** — the `Source facts` column names
  the code/config each visual asserts. Decorative motif/texture carries no facts.
- Keep this file to the facts and the frozen decisions; no narrative.
