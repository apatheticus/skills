# reflect — visual design system

One frozen system; all visuals in this skill derive from it. Facts come from the
skill itself (SKILL.md, reference/), never invented. Frozen for this run.

## Provenance

Derived from: `reference/design-system/tokens/colors.css` (the **SaaS Pro** design
system this skill bundles and renders its report in)
Derived on:   the run that re-derived this file after the report system was swapped
Mapping:      product tokens mapped 1:1, with two computed gap-fills marked below

This file was **re-derived, not discovered.** The design-system discovery ladder
deliberately skips `reference/`, because a relaxed `DESIGN.md` search in this repo
finds this very skill's *HTML report* system and adopting it blindly is the defect
that exclusion exists to prevent. The re-derivation here is the other case: the
product's identity genuinely changed — the bundled system was replaced — so the
mapping was rewritten from the new tokens on purpose. Nothing was inferred from a
path.

Recorded as `design_source_path` / `design_source_hash` in each visual's manifest, so
a later run can tell that the upstream tokens moved without being forced to
re-render.

## Story extraction

Audience:     Claude Code users who want to know what their own setup is costing them
Value:        mines the session transcripts already on disk and returns a ranked, evidence-backed diagnosis as one offline HTML report
Proof:        every recommendation cites a session ID and a verbatim quote, and a `new-skill` verdict needs three distinct sessions behind it
First action: `/reflect 90d`
Theme:        two worlds on one page — a diffuse field of sessions brought into focus behind glass, and each verdict restated on a dark data card where it can carry a number

## Frozen system

This skill ships an identity: it bundles the **SaaS Pro** design system at
`reference/design-system/`, and the report it produces is rendered in it. So the
palette is **mapped** from those tokens rather than invented, and the README visuals
look like the report the skill hands back.

### Palette

| Role | Hex | Notes |
| --- | --- | --- |
| background   | `#F4F6FE` | the light page ground; this system has no dark page theme |
| glass        | `#FFFFFF` | the frosted pane, and the base of every edge gradient |
| pane         | `#DBDCFB` | **computed gap-fill** — the pane's worst-case rendered ground, see below |
| ink          | `#12142B` | primary text; 18.09:1 on glass, 16.77:1 on background |
| body         | `#4C5273` | secondary text and captions; 7.60:1 on glass, 6.85:1 on pane |
| navy         | `#23265E` | the dense-data card — a card surface, never a page ground |
| navy-raised  | `#2E3277` | the lighter stop of the navy card, and its contrast ground |
| navy-ink     | `#F6F7FC` | text on navy; 10.67:1 against navy-raised |
| navy-dim     | `#BEC2D6` | metadata on navy; 6.46:1 against navy-raised |
| brand        | `#5B5FEF` | indigo — the primary accent, and the only ≥3:1 accent stroke |
| brand-strong | `#4A4AE8` | **the only fill that carries small white text** (6.11:1) |
| brand-soft   | `#A3A7FA` | the third blob and a soft fill; a fill, never a stroke |
| blue         | `#3B82F6` | the second structural hue; also the `environment gaps` family |
| success      | `#22B07D` | the `wins and effective patterns` family |
| warning      | `#F59E0B` | the `repetition and missed automation` family |
| danger       | `#EF4458` | the `friction and failure` family |

The mapping, product token → doc role:

| Product token | Value | Doc role |
| --- | --- | --- |
| `--surface-page` | `#F4F6FE` | background |
| `--surface-card` / `--border-glass` | `#FFFFFF` | glass |
| — | `#DBDCFB` | pane — computed, not a token |
| `--ink-900` / `--text-heading` | `#12142B` | ink |
| `--ink-600` / `--text-body` | `#4C5273` | body |
| `--navy-900` | `#23265E` | navy |
| `--grad-navy` first stop | `#2E3277` | navy-raised |
| `--ink-050` | `#F6F7FC` | navy-ink — stands in for `--navy-text` |
| `--ink-300` | `#BEC2D6` | navy-dim — stands in for `--navy-text-dim` |
| `--brand-500` | `#5B5FEF` | brand |
| `--brand-600` | `#4A4AE8` | brand-strong |
| `--brand-300` | `#A3A7FA` | brand-soft |
| `--blue-500` / `--info` | `#3B82F6` | blue |
| `--success` | `#22B07D` | success |
| `--warning` | `#F59E0B` | warning |
| `--danger` | `#EF4458` | danger |

Two gap-fills, both computed rather than chosen:

- **`pane` `#DBDCFB` is a measurement, not a colour decision.** A glass pane is drawn
  as two `glass` layers at `0.60` and `0.45`, which is `0.78` effective coverage, so
  the ground a label actually sits on is `glass` composited over whichever blob is
  behind it. `#DBDCFB` is that composite over the *deepest* blob (`brand`, the lowest
  luminance of the three at `0.732` against `blue`'s `0.766` and `brand-soft`'s
  `0.848`), which is the worst case at any phase of the drift. Text is measured
  against it, never against pure white, because the pane is translucent and the field
  moves: one measurement of one phase would pass a label that is unreadable four
  seconds later. `0.78` rather than a heavier tint because at `0.92` coverage the
  frost stops being visible and the pane is just a white rectangle.
- **`navy-ink` and `navy-dim` flatten the product's white-alpha text.** SaaS Pro states
  text on navy as `rgba(255,255,255,0.92)` and `0.55`; an SVG palette needs a hex, so
  each is the nearest real ink-ramp token to that flattened value.

Three contrast rules this palette inherits from the product and does not relax:

- **`--ink-400` / `--text-muted` `#9297B3` is absent on purpose.** It measures 2.88:1
  on white, and the product's own DESIGN.md §2 says it must not carry text. `--ink-500`
  `#6A7091` is its documented replacement at 4.84:1 — but on *this* system it is also
  absent, because it drops to **4.48:1** on the page ground and **3.60:1** on a pane
  over the deepest blob. Secondary text is `body`, everywhere.
- **Small white text lives on `brand-strong` only.** White on `brand` is 4.85:1 and on
  `blue` only 3.68:1, and the product's "white at ≥600 weight, ≥12px" rule does not
  rescue it — WCAG large text needs ≥18.66px bold.
- **The signal hues are fills, never strokes or text.** `brand-soft` on glass is a
  2.22:1 stroke and 1.65:1 on a pane, under the 3:1 graphic floor; even `brand` only
  reaches 3.61:1 on a pane, so an accent stroke on glass is the softest this system
  allows and nothing lighter is permitted.

### Typography

| Role | Stack |
| --- | --- |
| display | `-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif` |
| body    | `-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif` |
| mono    | `ui-monospace, SFMono-Regular, Menlo, monospace` |

System stacks only — an SVG cannot fetch a font on GitHub, so the product's Plus
Jakarta Sans and JetBrains Mono degrade to the system faces and are not named. Weight
`600` carries labels and `500` the supporting lines; never thinner, because type on
glass is already sitting on a low-contrast ground. Mono is reserved for literals: a
verdict slug, a window argument, a threshold.

### Shape language

Radii come straight from the product's §4 scale: panes `24`, cards `18`, buttons and
chips `10`, pills `999`, icon tiles ≈ `32%` of their size. `4`-unit base grid. Panel
borders are the only strokes and always `1.6` at a gradient tint; content strokes are
`2`–`2.5` in `brand`. Outer margin `64`; gutter `26`.

**Two documented divergences from the catalog style, both forced by the light ground.**
The catalog draws glass on a dark field, where white does the work; here it cannot.
(1) The pane edge is **not** a white ramp — a white border on a near-white pane over a
light page is invisible. It runs `glass` at `0.95` into `brand` at `0.22` and `0.42`,
so the pane catches light on the top-left edge and picks up a brand tint on the
bottom-right. (2) The product's §4 glass recipe ends in an **inset top highlight**, and
this system omits it: on a light pane there is no darker interior for a highlight to
separate from, so it reads as a stray hairline. The edge ramp carries the pane alone.

### Motif

**The frosted pane over the field.** The corpus is a diffuse, saturated field — every
session on disk, none of them decided about. Laying a pane over a region does not
sharpen it; it *frames* it, which is exactly what extraction and clustering do. A
finding only becomes legible when it is restated on a dark data card, where it can
carry a count. That is the skill's own epistemology, and it is the product's own "two
worlds, one page": light chrome for structure, navy for the data world. Navy appears
**once per board and only for the run's own output** — the verdict card carrying its
session threshold, or the report artifact itself. It is never emphasis, never a page
ground, and never a second time on the same board.

### Composition rules

Sparse and calm, read left to right in pipeline order. **At most three glass panes per
board** — the style's cap, and it holds here for a second reason: the product's §4
puts glass on chrome only, so panes frame and solid cards carry. In practice that
means **one or two panes and then solid cards**: a pane frames a region of the field,
white cards hold content, and navy appears once for the output. The blob field
is the only place colour is allowed to spread, because the product forbids accents as
page or card grounds. Content stays `64` units clear of the edges, and nothing is
bordered except glass — solid cards separate by one `feDropShadow` in `navy` at low
opacity, never by a stroke.

### Motion rules

- Seamless ambient loops, `data-loop-s="12"` on every animated board; every duration
  divides 12 exactly.
- Ease `cubic-bezier(0.65,0,0.35,1)` — the product's `--ease-in-out`. Slow and calm.
- **The field drifts; the panes never move.** `20`–`40` units over `12s`, written as
  symmetric `0% / 50% / 100%` keyframes rather than `alternate`, so the state at `t=D`
  is provably the state at `t=0`. A `12s` `alternate` inside a `12s` loop is one
  half-cycle and breaks the seam even though the arithmetic gate passes it.
- One sequencing idea besides the drift: an ordered emphasis on the nodes, `6s` with
  negative delays. Nothing else moves.
- Nothing moves under text, and no element carrying text pulses below `0.35`.
- Every animated visual carries a `prefers-reduced-motion` block that stops all motion
  and leaves a legible still — with the field parked at its base position, which is
  the composed one.

## Style

| Field | Value |
| --- | --- |
| Slug | `glassmorphism` |
| Source | derived — the product's own hero is a glass panel, and `--surface-glass` / `--border-glass` are first-class tokens |
| Primary axis | material — the two blur tiers decide everything else |

- **Intent** — frosted translucent panels floating over a coloured, blurred ground;
  depth through transparency. The right call here because it is not a look chosen for
  the README: the report's own §1 hero is `sp-glass`, and the product defines the
  recipe in §4 as `rgba(255,255,255,0.55–0.72)` plus a blur, a 1px white border and an
  inset top highlight.
- **Palette treatment** — the **ground** carries the colour: three large blobs from
  the brand ramp, heavily blurred. Panes are `glass` at layered opacity with a `1.6`
  gradient border. Ink is near-solid; text is the one thing that is never translucent.
  Unlike the catalog's usual dark rendering this board is **light**, because the
  product is light-only and says so — which also puts dark ink on a near-white pane
  and takes this style out of its most common failure mode.
- **Shape language** — radius `24` on panes, `18` on cards. Large soft blobs behind,
  crisp rectangles in front. Pane borders are the only strokes: always `1.6`, always a
  diagonal ramp, and here `glass` into `brand` rather than white into white — see the
  divergence note under Shape language above.
- **Material / depth** — **SVG has no `backdrop-filter`.** A pane cannot blur what is
  behind it, so the frost is built from two blur tiers: the field at `34`, the pane's
  own blurred copy at `14`. The pane is always the **lower** number — blur the pane
  harder than the field and it reads as fog with a hole in it rather than a sheet of
  glass. Cards may add one `feDropShadow`; one primitive per filter, never a chain.
- **Type treatment** — system sans, `600` for labels and `500` for supporting lines.
  Never thin. The pane tint is chosen *after* the label's ratio is computed against
  the worst point the drift reaches, not before.
- **Motion character** — slow drift. The ground blobs move; the panes stay put. The
  frost means pane content shimmers as the field passes behind it, which is the whole
  payoff and needs no extra motion.
- **SVG recipes** — one `<filter>` per blur tier, each a single `feGaussianBlur`
  (`34` field, `14` frost); the blob geometry declared once in `<defs>` as `#ground`
  and `<use>`d by every copy, with the drift class on the wrapping `<g>` rather than
  on the blobs, so the field and each frosted copy can never desynchronise; a diagonal
  `<linearGradient>` per pane edge; a third single-primitive `feDropShadow` filter for
  solid cards; and a two-stop `navy-raised` → `navy` gradient for the data card.
  **Blob cores go under the panes**, so the frost has something to reveal, and only
  their skirts fall in the negative space. Two placements that look reasonable and are
  not: a core in the outer margin reads as a saturated wall down one edge, and a core
  parked in a gap between panes reads as a glowing bar competing with the type beside
  it. Where a board has one pane and opaque cards, the skirts carry the field.
- **Relaxations** — byte cap `150 KB` → **`200 KB`**, granted because the duplicated
  blurred ground is load-bearing geometry. It is not a licence for more panes.
  Contrast is **not** relaxed and neither is filter depth.
- **Never** — more than three panes per board, translucent text, a `backdrop-filter`
  (it does nothing), frosting the pane harder than the field, a flat edge stroke, a
  pane tint that drops its label below 4.5:1 at any point in the drift, an odd number
  of `alternate` half-cycles, panes that move while the field also moves, duplicating
  the blob geometry instead of `<use>`-ing it, an accent as a page or card ground, or
  promoting `navy` to a page theme.

## Visual inventory

| Asset | Doc | Depicts | Tier | Source facts |
| --- | --- | --- | --- | --- |
| hero | README.md | transcripts already on disk become signals, then cross-session clusters, then one verdict each — gated on how many distinct sessions back it | animated-hero | SKILL.md → Phase 3 steps 1–3, Guardrails |
| pipeline | README.md | the five phases, with `/insights` corroborating rather than gating, and the prior report diffed for trend | animated-flagship | SKILL.md → Phases 0–5 |
