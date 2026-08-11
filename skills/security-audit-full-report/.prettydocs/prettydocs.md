# security-audit-full-report — visual design system

One frozen system; all visuals in this skill derive from it. Facts come from the
skill itself (SKILL.md, assets/template.html), never invented. Frozen for this run.

## Story extraction

Audience:     engineers and security reviewers who want a codebase audited until it stops yielding, not audited once
Value:        loops one security audit per cycle until findings converge, then merges every run into a single interactive HTML report
Proof:        convergence is decided on disk — two consecutive cycles adding zero new medium-or-higher findings, deduped structurally on each finding's sink file and scope
First action: `/security-audit-full-report ./services/api`
Theme:        a sweep repeated until it comes back empty — each pass marks what it found, and only a pass that adds nothing advances the counter

## Frozen system

This skill ships an identity: `assets/template.html` carries the **SaaS Pro** token
set, and that template is the artefact a reader actually receives. So the palette is
**mapped** from those tokens rather than invented, and the visuals here look like the
report the skill produces.

### Palette

| Role | Hex | Notes |
| --- | --- | --- |
| background     | `#F6F7FC` | page ground — the flat value of the report's page wash |
| surface        | `#FFFFFF` | the light card world: KPIs, summary, finding cards |
| surface-deep   | `#23265E` | the dark navy card world: donut and verified-clean grid |
| ink            | `#12142B` | primary text on light ground |
| muted          | `#4C5273` | secondary text and captions; 7.11:1 on background |
| accent-primary | `#5B5FEF` | the brand hue — orchestration, the report itself |
| accent-secondary | `#3B82F6` | info; the second structural hue and nothing else |
| high           | `#EF4458` | severity: high. Labels on it go near-black, never white |
| medium         | `#F59E0B` | severity: medium |
| clean          | `#2ECC9A` | verified clean, and a converged cycle |
| high-lift      | `#FF7A8A` | the only place high appears as *text*, and only on `surface-deep` |
| rule           | `#DDDFEB` | hairline between cards and along a track |

The mapping, product token → doc role:

| Product token | Value | Doc role |
| --- | --- | --- |
| `--ink-050` | `#F6F7FC` | background |
| `--white` | `#FFFFFF` | surface |
| `--navy-900` | `#23265E` | surface-deep |
| `--ink-900` | `#12142B` | ink |
| `--ink-600` | `#4C5273` | muted |
| `--brand-500` | `#5B5FEF` | accent-primary |
| `--blue-500` | `#3B82F6` | accent-secondary |
| `--danger` | `#EF4458` | high |
| `--warning` | `#F59E0B` | medium |
| `--accent-green` | `#2ECC9A` | clean |
| `--accent-coral` | `#FF7A8A` | high-lift |
| `--ink-200` | `#DDDFEB` | rule |

Two decisions worth stating. `high-lift` exists because `#EF4458` on the navy card
measures 3.73:1 and cannot carry text there, while the same red at `#FF7A8A` clears
5.56:1 — the severity meaning survives, the legibility floor is not softened. And a
label on any severity fill is **near-black**: white on `#EF4458` is 3.72:1, which is
the exact trap `flat-material` warns about.

### Typography

| Role | Stack |
| --- | --- |
| display | `-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif` |
| body    | `-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif` |
| mono    | `'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace` |

System stacks only — an SVG cannot fetch a font on GitHub, so the product's Plus
Jakarta Sans degrades to the system sans and is not named. Mono is reserved for
literals: a path, a status value, a ledger key, a count.

### Shape language

Rounded rectangles at radius `8`, the same radius on every card. One stroke weight,
`2`, and only where a boundary is not already a colour change. Cards are filled, not
outlined. Grid gutter `24`; outer margin `64`.

### Motif

The **cycle chip**: a numbered run tile carrying one number — how many *new*
medium-or-higher findings that cycle added. It is the unit the whole skill is built
on. A chip reading `0 new` is drawn quiet, and two quiet chips in a row is literally
the stop condition (`consecutive_zero_new_medplus >= 2`). Repeat it lightly; it is a
counter, not wallpaper.

### Composition rules

Compact-technical. One strong composition per board, read left to right in the order
the skill runs: target → cycles → decision → report. Content stays `64` units clear
of the edges. Numbers lead; labels explain them.

### Motion rules

- Seamless ambient loops, `data-loop-s="12"` on every animated board; every duration
  divides 12 exactly.
- Ease `cubic-bezier(.4,0,.2,1)` — the Material standard curve. Fills and opacity,
  never a bounce.
- One motion idea per board, two at most: a sweep that advances through the cycles,
  and a single ripple where a decision lands.
- Nothing moves under text, and no element pulses below `0.35`.
- Every animated visual carries a `prefers-reduced-motion` block that stops all
  motion and leaves a legible still — the stopped frame is the composed board.

## Style

| Field | Value |
| --- | --- |
| Slug | `flat-material` |
| Source | derived — the product ships a Material-shaped identity in `assets/template.html` |
| Primary axis | material — one honest elevation step decides everything else |

- **Intent** — flat colour fields with exactly one step of elevation. The right call
  for a repo that already ships a Material-derived palette, which this one does: the
  report template's card worlds, radii and single shadow scale are that idea already.
- **Palette treatment** — confident, saturated fields. The accent is a *surface*
  colour, not a line colour. Two elevation tiers only: `background` for the canvas,
  `surface` (or `surface-deep`) for anything raised.
- **Shape language** — rounded rectangles, radius `8` across the board; circular
  containers on-idiom; stroke `2` for the rare outline.
- **Material / depth** — one drop shadow, one primitive deep, soft and short: offset
  `0 2`, blur `4`, low opacity. Every raised element shares that same shadow.
- **Type treatment** — system sans. `700` titles, `500` labels, `400` body, sentence
  case, tabular figures where numbers sit in a column.
- **Motion character** — purposeful and eased on `cubic-bezier(.4,0,.2,1)`; things
  grow from where they are or ripple outward once.
- **SVG recipes** — one `<filter id="e1">` holding a single `feDropShadow`, reused by
  every raised element; a ripple that ends invisible so its reset is unseen.
- **Relaxations** — none. One `feDropShadow` is exactly the default filter depth.
- **Never** — two shadow recipes in one repo, no elevation at all, a gradient standing
  in for elevation, a radial gradient at all, white text on a mid-value accent, more
  than one accent doing the same job, or a radius that drifts card to card.

## Visual inventory

| Asset | Doc | Depicts | Tier | Source facts |
| --- | --- | --- | --- | --- |
| hero | README.md | one cycle per run, deduped against the ledger, stopping at two consecutive zero-new cycles or `max_cycles`, then one merged report | animated-hero | SKILL.md → §4, §5 |
| two-mode | README.md | preflight is the only interactive mode; every cycle after it runs unattended, each heavy step delegated to a cold agent | animated-flagship | SKILL.md → the two-mode contract, §1–§3, §4 |
