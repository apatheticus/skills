# reflect — visual design system

One frozen system; all visuals in this skill derive from it. Facts come from the
skill itself (SKILL.md, reference/), never invented. Frozen for this run.

## Story extraction

Audience:     Claude Code users who want to know what their own setup is costing them
Value:        mines the session transcripts already on disk and returns a ranked, evidence-backed diagnosis as one offline HTML report
Proof:        every recommendation cites a session ID and a verbatim quote, and a `new-skill` verdict needs three distinct sessions behind it
First action: `/reflect 90d`
Theme:        pressing on a flat field until the shape shows — signals lifted out of a recessed bed of sessions, clustered, then weighed one at a time

## Frozen system

This skill ships an identity: it bundles the **Neumorphic Fresh** design system at
`reference/design-system/`, and the report it produces is rendered in it. So the
palette is **mapped** from those tokens rather than invented, and the README visuals
look like the report the skill hands back.

### Palette

| Role | Hex | Notes |
| --- | --- | --- |
| background     | `#E6E9EF` | the single surface everything is extruded from |
| surface        | `#E6E9EF` | identical to background by design — shape comes from shadow, not fill |
| surface-raised | `#EDF0F5` | a subtly lifted section, used once per board at most |
| surface-inset  | `#E1E5EC` | a pressed well: the raw, unprocessed material |
| ink            | `#2B303B` | primary text; 10.87:1 on background |
| muted          | `#5B6472` | secondary text and captions; 4.92:1 on background |
| accent-primary | `#11D3A3` | mint — the verdict hue, and the only saturated fill |
| accent-strong  | `#0BB98D` | mint at weight, for a filled marker or a rule |
| accent-cool    | `#12B5C9` | teal — the second structural hue, corroboration |
| danger         | `#FB6B6B` | friction and failure signals |
| warning        | `#F5A623` | repetition and missed automation |
| nm-light       | `#FFFFFF` | the light half of every shadow pair — light from top-left |
| nm-dark        | `#C3CAD6` | the dark half of every shadow pair |

The mapping, product token → doc role:

| Product token | Value | Doc role |
| --- | --- | --- |
| `--bg` | `#E6E9EF` | background |
| `--surface` | `#E6E9EF` | surface |
| `--surface-2` | `#EDF0F5` | surface-raised |
| `--surface-inset` | `#E1E5EC` | surface-inset |
| `--fg1` | `#2B303B` | ink |
| `--fg2` | `#5B6472` | muted |
| `--mint` | `#11D3A3` | accent-primary |
| `--mint-strong` | `#0BB98D` | accent-strong |
| `--teal` | `#12B5C9` | accent-cool |
| `--danger` | `#FB6B6B` | danger |
| `--warning` | `#F5A623` | warning |
| `--nm-light` | `#FFFFFF` | nm-light |
| `--nm-dark` | `#C3CAD6` | nm-dark |

The accents are **fills, never text**: mint on the background measures 1.59:1. Every
label stays `ink` or `muted`, both of which clear 4.5:1 outright — so this system does
not spend the contrast relaxation `neumorphism` offers, and no visual here declares
one.

### Typography

| Role | Stack |
| --- | --- |
| display | `-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif` |
| body    | `-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif` |
| mono    | `'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace` |

System stacks only — an SVG cannot fetch a font on GitHub, so the product's Sora and
Plus Jakarta Sans degrade to the system sans and are not named. Weight `600` carries
labels; the softness belongs in the surfaces, never in the text. Mono is reserved for
literals: a verdict slug, a session path, a window argument.

### Shape language

Generously rounded: radius `18–26`, never under `16`. Wide, soft shapes; no thin
elements, because a hairline has nowhere to put a shadow. Pills for verdict chips.
Outer margin `64`; gutter `24`.

### Motif

The **pressed well**: a recessed bed at `surface-inset` holding the raw material — the
session field, before anything is decided about it. Every finding the pipeline
promotes is drawn as a card *lifting out of* that bed, and a cluster below the
evidence bar stays in it. It is the skill's own shape: triage scores what is in the
bed, extraction lifts signals, and only a cluster with enough sessions behind it
becomes a card. Repeat it lightly — one well per board.

### Composition rules

Sparse and calm. One strong composition per board, read left to right in pipeline
order. Wide spacing between raised elements so their shadows never overlap; content
stays `64` units clear of the edges. Nothing is bordered.

### Motion rules

- Seamless ambient loops, `data-loop-s="12"` on every animated board; every duration
  divides 12 exactly.
- Ease `cubic-bezier(.4,0,.4,1)`, over `4s` or `6s`. Slow and breathing.
- Nothing travels far — `4`–`8` units is plenty. Elements press in and release; a
  raised copy cross-fades over a pressed one. No bounce, no drift.
- Nothing moves under text, and no element pulses below `0.35`.
- Every animated visual carries a `prefers-reduced-motion` block that stops all motion
  and leaves a legible still — for a cross-fade that means the raised state, not the
  pressed one.

## Style

| Field | Value |
| --- | --- |
| Slug | `neumorphism` |
| Source | derived — the product bundles the Neumorphic Fresh system and renders its report in it |
| Primary axis | material — the dual shadow decides everything else |

- **Intent** — everything extruded from one continuous surface: no borders, no colour
  fields, just a light shadow and a dark shadow on the same background colour. The
  right call here because it is not a look chosen for the README, it is the look of
  the artefact the skill produces.
- **Palette treatment** — one surface colour for nearly everything; the card and the
  canvas share a hex and the shape is legible only from its shadows. The accent
  appears in markers and one active state, never as a card fill.
- **Shape language** — radius `18–26`, never under `16`. Soft, wide shapes; pills for
  chips, circles for markers.
- **Material / depth** — the dual shadow is the entire style. Raised elements take
  light from top-left; a pressed element carries the same pair at halved offset,
  halved blur and halved opacity — all three halved, or it reads as a smaller raised
  element rather than a pressed one.
- **Type treatment** — system sans, `600` for labels, sentence case, normal tracking.
  Type contrast stays high even though the surfaces are low-contrast.
- **Motion character** — slow and breathing on `cubic-bezier(.4,0,.4,1)`; a raised
  copy cross-fades over a pressed one, which is the canonical neumorphic motion.
- **SVG recipes** — one `<filter id="raise">` holding the `feDropShadow` pair (dark at
  `+7,+7`, white at `−7,−7`) and one `<filter id="press">` at half of each, both
  reused; a `<linearGradient>` from `nm-dark` to `nm-light` for a recessed track.
- **Relaxations** — the style permits text at 3.0:1 and graphics at 2.0:1. **This
  system does not use either**: every label is `ink` or `muted`, both above 4.5:1.
  Filter depth `2` is used, and is the shadow pair itself.
- **Never** — an accent-filled card, a visible border, thin strokes, a pressed state
  built as a true inner shadow (SVG has none) or one that halves only the offset,
  radius under `16`, more than two primitives in one filter, or spending the text
  relaxation just because it is available.

## Visual inventory

| Asset | Doc | Depicts | Tier | Source facts |
| --- | --- | --- | --- | --- |
| hero | README.md | transcripts already on disk become signals, then cross-session clusters, then one verdict each — gated on how many distinct sessions back it | animated-hero | SKILL.md → Phase 3 steps 1–3, Guardrails |
| pipeline | README.md | the five phases, with `/insights` corroborating rather than gating, and the prior report diffed for trend | animated-flagship | SKILL.md → Phases 0–5 |
