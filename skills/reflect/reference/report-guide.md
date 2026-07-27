# Report guide — structure, design, motion, self-containment

The report is the user's permanent record and playbook. It must be
highly polished, easy to skim, and reward drilling down. One HTML file,
opens from `file://`, offline, indefinitely.

## Design system

Use the bundled SaaS Pro design system in `design-system/`. It is a reporting
system: its first principle is "Numbers first — the data is the interface."

- `DESIGN.md` — the visual standard. Colour, type, space, elevation, the
  canonical component rules, iconography, accessibility. Its YAML frontmatter
  mirrors the tokens for machine reads; **the CSS is authoritative** if they
  ever disagree.
- `MOTION.md` — the motion standard. Read it before animating anything.
- `tokens/colors.css`, `tokens/typography.css`, `tokens/spacing.css`,
  `tokens/motion.css` — custom properties plus nine `@keyframes`.
- `components.css` — the `sp-*` class layer.
- `charts/` — seven chart components bundled as **geometry references**. Read
  `charts/README.md`; never ship the JSX.

Inline all five CSS files into one `<style>` block, in this order: colors,
typography, spacing, motion, components. Do not link them.

### Theming — light only

Put `sp-page` on `<body>`. **There is no dark page theme in this system: no
`data-theme` attribute, no toggle, no `prefers-color-scheme` block, and you must
not invent one.** The dark neutrals, lines and washes a page theme needs are not
defined, and improvising them would be a different design system.

What the system has instead is DESIGN.md §2's *two worlds, one page*: a light
page with white cards for KPIs, verdicts and prose, and **`sp-card--dark` under
every chart and every table**. That is the whole dark story. Dark cards never
nest in dark cards, and there is never a third card style.

"Every table" means **every** table, the methodology appendix included — it is the
one that gets forgotten, because it reads as prose rather than as data. There are
exactly two exemptions on the chart side, and they are not loopholes: a
**sparkline inside a stat tile** stays on the white tile, because `Sparkline.jsx`
exists for stat-card footers and a stat tile is white; and an **explanatory
graphic** (role 2 below) is not a data chart, so it sits wherever it reads best.
A role-1 data chart on a white card is a defect.

**Verifying the toggle is gone needs attribute-shaped greps.** The vendored CSS
deliberately contains the strings `data-theme`, `prefers-color-scheme` and
`@import` **inside comments**, precisely to tell a later reader not to reintroduce
them. So `grep -c data-theme <report>.html` returns a non-zero count on a
completely correct report. Match what would actually take effect instead:

```bash
grep -c 'data-theme=' report.html                 # attribute — must be 0
grep -cE '@media[^{]*prefers-color-scheme' report.html   # must be 0
grep -cE '^[[:space:]]*@import[[:space:]]' report.html   # rule, not prose — must be 0
```

### The `sp-*` class API — complete

This is the full list. Nothing else exists; if you need something that is not
here, build it from tokens rather than inventing a class name.

| Family | Classes |
| --- | --- |
| Page | `sp-page` |
| Type | `sp-display` `sp-h1` `sp-h2` `sp-h3` `sp-h4` `sp-lead` `sp-p` `sp-small` `sp-overline` `sp-kpi` `sp-code` |
| Card | `sp-card` `sp-card--hover` `sp-card--dark` `sp-card__title` |
| Glass | `sp-glass` (chrome only — sticky nav, hero shell; never a data surface) |
| Stat tile | `sp-stat` `sp-stat__label` `sp-stat__value` `sp-stat__delta` |
| Table | `sp-table` `sp-table--dark` `sp-table--compact` `sp-table__mono` |
| Badge | `sp-badge` `sp-badge--neutral` `sp-badge--success` `sp-badge--warning` `sp-badge--danger` `sp-badge--info` `sp-badge--brand` `sp-badge--dot` |
| Filter chip | `sp-pill` |
| Alert | `sp-alert` `sp-alert--info` `sp-alert--success` `sp-alert--warning` `sp-alert--danger` `sp-alert__title` `sp-alert__body` |
| Icon tile | `sp-icontile` `sp-icontile--coral` `sp-icontile--green` `sp-icontile--orange` `sp-icontile--purple` `sp-icontile--navy` |
| Progress | `sp-progress` `sp-progress__label` `sp-progress__value` `sp-progress__track` `sp-progress__bar` |
| Ring | `sp-ring` `sp-ring--turn` `sp-ring__arc` `sp-ring__readout` |
| Segment filter | `sp-segment` `sp-segment__btn` (active: add `.is-active`) |
| Search | `sp-search` `sp-search__input` |
| Button | `sp-btn` `sp-btn--primary` `sp-btn--secondary` `sp-btn--ghost` `sp-btn--danger` `sp-btn--sm` `sp-btn--lg` `sp-btn--icon` |
| Tooltip | `sp-tip` (label from `data-tip`) |
| Divider | `sp-divider` |
| Empty state | `sp-empty` `sp-empty__icon` `sp-empty__title` `sp-empty__message` |

Four pieces of state ride on attributes, not classes, because they are data and
because assistive tech reads them: `aria-pressed` on a filter chip,
`data-trend="up|down"` on a stat delta, `data-align="right|center"` on a table
cell, `data-tip` on a tooltip.

Rules worth obeying (DESIGN.md §5): one `sp-btn--primary` per view; the icon
tile is the signature motif, so use it to give the recommendation list
personality, one colour family or a deliberate rainbow, never random per render;
a table's first column is already 600 weight, IDs and counts get
`sp-table__mono`, and a status is always a badge with a single word.

### Contrast — three traps the tokens will walk you into

`components.css` already clears 4.5:1 for every class it defines. Markup and SVG
you author by hand can still fail, and these three are the ways it happens:

1. **`--text-muted` / `--ink-400` is 2.88:1 on white.** It is fine as a
   gridline or a hairline; it is not a text colour. Use `--ink-500` (4.84:1) for
   small text, `--ink-600` (7.60:1) for body copy. On a dark card use
   `--navy-text` (11.99:1) or `--navy-text-dim` (5.24:1).
2. **Small white text on `--grad-brand` fails** — 4.02:1 and 3.68:1 at the outer
   stops. DESIGN.md's "white at ≥ 600 weight, ≥ 12px" is not WCAG large text,
   which needs ≥ 18.66px bold. Gradients are for non-text surfaces and display
   type; a filled control with small white text uses solid `--brand-600`.
3. **A raw semantic hue is a fill, not a text colour.** `--success` on
   `--success-soft` is 2.43:1. Semantic text uses the `--*-strong` ramp
   (`--success-strong`, `--warning-strong`, `--danger-strong`, `--info-strong`),
   which `components.css` defines.

Chart furniture is exempt: a 3:1 gridline would wreck the chart. Anything a
reader must distinguish to read the data — a series colour, a zone band, a
meaningful icon — is not. And never encode meaning in colour alone; pair it with
an icon, a dot, or a label.

- Fonts: two families, Plus Jakarta Sans and JetBrains Mono. **The vendored CSS
  ships no font `@import`** — it was stripped at vendor time, so there is nothing
  to delete at generation time and nothing to restore. Either embed base64
  `@font-face` woff2 subsets, or rely on the fallback stacks already in
  `tokens/typography.css`. Never leave a network `<link>` or `@import` in the file.
- Icons: no Lucide CDN — inline the handful of SVG paths you actually use, at
  DESIGN.md §6's spec: Lucide-style 1.75–2px stroke, round caps, 16/20/24px,
  white inside gradient tiles and `currentColor` everywhere else. No emoji.

## Self-containment rules (hard)

- Zero external requests: no CDN scripts, no `<link>`, no remote images,
  no fetch/XHR. Verify before delivering: `grep -nE 'https?://' report.html`
  should hit only in prose/data, never in `src=`, `href=` (except
  `href="#..."`), `@import`, or `url(...)`.
- Vendor GSAP: `curl -sL https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js`
  (plus `ScrollTrigger.min.js` — you will want it) into the scratchpad, then
  inline into `<script>` blocks. If offline at generation time, fall back to
  advanced CSS (scroll-driven animations, transitions, keyframes) and say so
  in the final message.
- three.js/WebGL: MOTION.md §5 is stricter than "if it earns its place" —
  WebGL is for a hero moment only, brand-coloured geometry, ambient rotation
  ≤ 0.02 rad/frame, always behind content, and **never on a data screen**.
  Most of this report is data, so the honest answer is usually no: a CSS or
  2D-canvas effect in the glass-and-soft-physics register beats ~600 KB of
  three.js. If you do include a scene it is the report's one hero animation
  (MOTION.md §1.3) and nothing else animates on load.

## Structure (top to bottom)

1. **Hero** — title, date, analysis window, session/project counts, and a
   one-paragraph verdict of the period. Subtle ambient motion.
2. **Executive summary** — the ranked recommendation list, most leverage
   first. Each row: rank, verdict badge (new-skill / automation / fix /
   keep-doing), title, leverage score, effort, session count. Clicking
   scrolls to the detail card.
3. **Since last report** (only when a prior report existed) — adopted /
   still-recurring (with streak count) / new.
4. **Focus section** (only when a focus argument was given) — deep dive on
   the focused project/theme.
5. **Detail cards, one per cluster** — collapsed by default to summary +
   verdict; expand to reveal rationale, the concrete example (in a copyable
   `<pre>` block — the exact prompt / skill description / settings line),
   and the evidence: verbatim quotes with session ID, project, and date.
   Corroborated-by-/insights findings get a marker.
6. **Wins & playbook** — effective patterns worth keeping, same evidence
   treatment.
7. **Usage panorama** — charts built as custom inline SVG (see below), each on
   its own `sp-card--dark`, from
   session-meta aggregates: sessions/tokens per project, tool-error rates,
   friction categories over time. Decoration must never displace evidence.
8. **Methodology appendix** — window, counts, triage rules, sampling (if
   any), sessions skipped as unreadable, /insights coverage %, and
   limitations.

## Custom SVG graphics (required)

Author custom inline SVG — never a chart library, never raster images — in
three roles:

1. **Data charts** — every chart in the report is hand-built SVG styled with
   the design-system tokens: bar/column charts for per-project volume,
   line/area for trends over the window, donut/radial gauges for coverage
   and outcome ratios, heatmap grids for activity by day, dot/strip plots for
   session-level distributions. Real axes, labeled ticks, direct labels or
   an accessible legend, `<title>` elements for hover tooltips, and a
   `role="img"` + `aria-label` per chart. Pick the form that fits the data;
   don't repeat one chart shape eight times.

   **Do not derive the geometry from scratch — `design-system/charts/` already
   solves it.** Read `charts/README.md` first, then take from each what it
   works out: `LineChart.jsx` for the padding model, the `*1.15` headroom, five
   dashed gridlines at `[0,.25,.5,.75,1]`, right-aligned tick labels and the
   area path that closes back along the baseline; `BarChart.jsx` for bar width
   `min(26, (w/n)*0.55)`, slot centring, and emphasising the max bar by colour
   instead of adding a legend; `DonutChart.jsx` for segment arcs as dash-array
   circles rotated `-90deg`; `Sparkline.jsx` for min–max (not zero-based)
   normalisation in a stat-tile footer; `LinearGauge.jsx` for zone bands with
   the readout tinted by the zone the value lands in; `SegmentGauge.jsx` for the
   ticked dial, including the `contentH` formula that stops a 270° arc being
   clipped. Those files are references, never shipped code.

   **Gradient and filter ids must be deterministic and unique per file.** The
   two upstream charts that need an id build it from `Math.random()`, which is
   correct in React and wrong here: two charts that collide on one id silently
   share a gradient. Derive the id from the chart's own name —
   `grad-sessions-by-project`.
2. **Explanatory graphics** — where a diagram illustrates a key point better
   than prose, draw one: a flow of a friction loop (prompt → error → retry →
   interrupt), a before/after prompt comparison panel, a pipeline sketch of
   a recommended automation, severity/leverage quadrant maps. These earn
   their place by making a finding land faster.
3. **Aesthetic & effect layers** — decorative SVG in SaaS Pro's glass-and-soft-
   physics register (DESIGN.md §4): brand-gradient hero backdrops running
   135–150°, wide blue-tinted glows, generous radii, glass chrome over the page
   gradient, section dividers, subtle noise/texture via SVG filters
   (`feTurbulence`, `feGaussianBlur`), animated stroke draw-ins
   (`stroke-dasharray` + GSAP/ScrollTrigger), sparkline flourishes in stat
   tiles. Nothing is flat and nothing is harsh — but **max one glowing element
   per region**, and accents (coral, green, orange, purple, teal) appear only as
   icon-tile fills, chart series and soft badge tints, never as a card or page
   ground.

Rules: derive all fills/strokes/type from the design-system tokens — reference
CSS variables, not hard-coded hex. A chart must hold up on **both card
grounds**: dark, which is where DESIGN.md §5 puts every chart, and light, for a
chart placed on a white card. That is the `dark` prop the chart references
already model (`var(--ink-100)` → `rgba(255,255,255,0.09)` gridlines,
`var(--ink-400)` → `var(--navy-text-dim)` labels). It is not a page-level
light/dark theme; this system has none. Animate charts in with GSAP (bars grow,
lines draw, gauges sweep) gated behind `prefers-reduced-motion`; decorative
layers get `aria-hidden="true"`; everything remains inline in the single file.

## Interactivity & motion

- Sticky side/top nav with scrollspy; smooth-scroll anchors.
- Expand/collapse detail cards (accessible: `<details>` or
  `aria-expanded` buttons).
- Filter the summary table by verdict/family; text search across clusters.
- GSAP + ScrollTrigger: staggered entrance reveals, count-up stat numbers,
  progress-bar fills on scroll, hero parallax.
- **Follow MOTION.md, not improvisation.** Its token table (§2) gives the five
  durations and four easings; §3 gives the patterns — entrance fade-up 10px at
  `--dur-base` staggered 40–60ms, press `scale(0.97)`, hover lift
  `translateY(-2px)`, lines drawing via dash-offset in ≤1.3s, bars growing from
  the baseline staggered 50ms, rings and gauges sweeping at `--dur-hero`,
  count-ups ≤1.2s. The nine keyframes are already defined in
  `tokens/motion.css`; reuse them instead of writing new ones.
- **Fast chrome, slow data** (§1.2): controls respond in ≤180ms; a chart may
  take up to 1.3s to draw because it rewards watching. And **one hero animation
  per view** (§1.3, §4) — a single count-up or chart draw for the whole report,
  everything else entering quietly, total settle under 1.2s. Motion emphasizes
  the ranking and key numbers; it never delays reading.
- Reduced motion is §6, and it is specific: under
  `prefers-reduced-motion: reduce`, loops (`sp-float`, `sp-shimmer`) and any
  WebGL rotation stop, entrances become **opacity-only**, and counters and
  charts render their **final state immediately** — not a faster animation.
  `components.css` already does this for its own classes; anything you add by
  hand or drive with GSAP needs the same gate. Never rely on motion to convey
  status.

## Embedded data block (machine-readable — future runs depend on this)

Embed exactly one:

```html
<script type="application/json" id="cc-reflection-data">
{
  "generated": "YYYY-MM-DD",
  "window": {"kind": "30d", "from": "YYYY-MM-DD", "to": "YYYY-MM-DD"},
  "focus": "string or null",
  "sessions_analyzed": 0,
  "projects": ["..."],
  "insights_coverage": 0.0,
  "recommendations": [
    {
      "id": "kebab-case-stable-id",
      "verdict": "new-skill|automation|fix|keep-doing|nothing",
      "title": "...",
      "family": "friction|repetition|wins|environment",
      "leverage": 1,
      "effort": "minutes|hour|day",
      "session_ids": ["..."],
      "streak": 1
    }
  ]
}
</script>
```

Keep `id` values stable across runs for the same underlying issue (derive
from the cluster theme) so trend diffs work. `streak` = consecutive reports
in which this recommendation has appeared unresolved.
