# Design system — the frozen visual contract

Every repo this skill touches gets one persisted design system at
`docs/assets/src/DESIGN.md`. It is the single source of truth for **all** visuals
in that repo — animated WebPs and static SVGs alike. Freeze it once, early, then
consume it everywhere so the hero, diagrams, badges, and banners read as one
designed unit.

## When it's frozen, when it's re-derived

- **Frozen for the duration of a run.** Once written, treat `DESIGN.md` as
  read-only while producing that run's visuals. Do not drift the palette or motif
  visual-to-visual.
- **Re-derive only** when the product's identity genuinely changes (a rebrand, a
  new logo, a pivot in what the product is) or when the user explicitly asks.
- If a `docs/assets/src/DESIGN.md` already exists and still matches the product,
  reuse it as-is — don't regenerate it just because a run started.

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
infrastructure, security, systems, or research repos.

### Has a design system / logo / brand tokens / existing style guide → MAP, don't invent

When the product already ships an identity, the product's identity **always wins**
over anything you'd invent. Do not create a parallel aesthetic.

1. **Extract the real tokens** from their authoritative source: CSS custom
   properties (`--color-*`, `--font-*`), a `tailwind.config` theme block, brand
   asset files, an existing `DESIGN.md` / style guide, or the dominant colors of
   the logo.
2. **Record an explicit mapping table** in `DESIGN.md` — product token → doc role —
   rather than renaming or reinventing. Example:

   | Product token | Value | Doc role |
   | --- | --- | --- |
   | `--brand-900` | `#0d1117` | background |
   | `--surface` | `#161b22` | surface |
   | `--brand-500` | `#58a6ff` | accent-primary |
   | logo mark green | `#3fb950` | accent-secondary |

3. Only fill gaps the product leaves open (e.g. no defined "attention" color) —
   and note each invented value as a gap-fill, not a brand claim.

## The template (fill this into `docs/assets/src/DESIGN.md`)

````markdown
# <Product> — visual design system

One frozen system; all repo visuals derive from it. Facts come from the repo
(README, manifests, code), never invented. Frozen for this run.

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

Rendered visuals must **self-host or `local()` their fonts — never load a remote
font.** SVGs use system stacks only; HyperFrames compositions declare named fonts
with `@font-face { src: local(...) }` or embedded data URIs.

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

### Motion rules

- Seamless ambient loops, **8–14s** each; state at t=D equals state at t=0.
- Ease character: <e.g. power2/power3 in-out>; calm, purposeful.
- No strobing, no flicker, no idle bobbing. Motion always communicates flow
  direction or a state change.
- Keep motion calm out of respect for motion-sensitive readers; nothing frantic.

## Visual inventory

| Asset | Doc | Depicts | Tier | Source facts |
| --- | --- | --- | --- | --- |
| hero      | README        | <core idea in motion>     | animated-flagship | <files/config> |
| <diagram> | ARCHITECTURE  | <flow it shows>           | animated          | <files/config> |
| <banner>  | <doc>         | <section marker>          | banner            | — (decorative) |
| <figure>  | <doc>         | <static relationship>     | static            | <files/config> |
````

## Rules that hold regardless of derivation path

- **Everything derives from this file.** Any visual whose palette, type, motif, or
  motion doesn't trace back to `DESIGN.md` is off-system — fix the visual, not the
  system.
- **No volatile facts inside visuals** — no minor/patch versions, no dates. A
  string baked into a WebP goes stale silently and can't be greped.
- **Every load-bearing depiction is grounded** — the `Source facts` column names
  the code/config each visual asserts. Decorative motif/texture carries no facts.
- Keep this file to the facts and the frozen decisions; no narrative.
