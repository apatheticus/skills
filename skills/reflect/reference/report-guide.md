# Report guide — structure, design, motion, self-containment

The report is the user's permanent record and playbook. It must be
highly polished, easy to skim, and reward drilling down. One HTML file,
opens from `file://`, offline, indefinitely.

## Design system — Neumorphic Fresh

**The report is styled in Neumorphic Fresh. It is not bundled with this skill —
read it from the user's own maintained copy:**

```
/Users/luke/scratch/Styles/Neumorphic Fresh Design System/
```

If that path is missing, stop and ask rather than substituting another system.
A report in the wrong visual language is a defect, not a variation — week-to-week
editions have to look like the same publication.

What to read, in this order:

- `DESIGN.md` — the portable spec (design.md format): token front matter plus
  prose. The tool-agnostic source of truth.
- `README.md` — brand narrative, content and visual foundations, iconography.
- `colors_and_type.css` — all custom properties (colour, type, space, radius,
  elevation, motion) for both themes.
- `components.css` — the `nf-*` class layer.
- `ui_kits/dashboard/Widgets.jsx` — **chart and KPI geometry reference.** Read it
  before authoring the panorama: it works out the stat-card layout, the area-chart
  gradient-under-line pattern, the conic-gradient donut with an inset hub, and the
  inline legend rows. Reference only; never ship the JSX.
- `preview/` — specimen cards for every token and component.

Inline `colors_and_type.css` then `components.css` into one `<style>` block, in
that order, followed by the report's own layout layer. Do not link them.

**Strip the font `<link>` first.** The comment header at the top of
`colors_and_type.css` contains two literal Google Fonts `<link>` lines. They are
documentation, but they are live markup the moment you paste the file into a
`<style>` block's neighbourhood. Delete them at inline time.

### The five brand rules (from SKILL.md — obey them)

1. **One tonal base per theme.** Surfaces are the *same colour* as the page and
   are raised by paired light/dark shadows (`--el-1/2/3`, `--inset-1/2`). **Never
   give a card a different fill colour.** There is no dark card, no navy card, no
   inverted chart panel — a chart sits on the same ground as the prose around it.
2. **Fresh accent.** The mint→teal→cyan gradient (`--grad-fresh`) on primary
   actions, with a soft `--glow-accent` bloom. Lively, not grey.
3. **Generous, pillowy rounding** and airy spacing.
4. **Springy motion** — hover lifts, press sinks (`--ease-spring`).
5. **Sentence case, warm calm copy, no emoji** in chrome.

### Theming — light *and* dark, with a real toggle

Put `data-theme="light"` or `data-theme="dark"` on `<html>`. Both themes are
fully defined in `colors_and_type.css`; the report ships a working toggle in the
sticky nav that persists to `localStorage` and falls back to
`prefers-color-scheme` on first load.

Because every colour comes from a token, the toggle is free — *provided* nothing
is hard-coded. A literal hex anywhere in the markup or SVG is the one thing that
breaks it. Verify before delivering:

```bash
grep -cE '#[0-9a-fA-F]{3,8}\b' report.html   # only inside the vendored CSS + base64 fonts
grep -c 'data-theme=' report.html            # must be >= 1 — the toggle is required
```

### Token groups you will actually use

| Group | Tokens |
| --- | --- |
| Ground | `--bg` `--bg-2` `--surface` `--surface-2` `--surface-inset` |
| Elevation | `--el-1` `--el-2` `--el-3` `--el-float` `--inset-1` `--inset-2` |
| Text | `--fg1` (body) `--fg2` (secondary) `--fg3` (muted/labels) `--fg-on-accent` |
| Accent | `--accent` `--accent-press` `--accent-wash` `--grad-fresh` `--grad-fresh-soft` `--glow-accent` |
| Brand hues | `--mint` `--mint-soft` `--mint-strong` `--teal` `--cyan` `--lime` |
| Semantic | `--success` `--warning` `--danger` `--info` + each `--*-wash` |
| **Chart series** | **`--c-1` … `--c-6`** — the categorical ramp. Use these, in order, for every multi-series chart. |
| Lines | `--line` `--line-strong` `--c-track` |
| Type | `--font-display` (Sora) `--font-body` (Plus Jakarta Sans) `--font-mono` (JetBrains Mono), `--fs-*`, `--weight-*`, `--tracking-*`, `--lh-*` |
| Shape | `--r-xs` `--r-sm` `--r-md` `--r-lg` `--r-xl` `--r-2xl` `--r-pill` |
| Motion | `--dur-fast` `--dur-base` `--dur-slow` `--dur-slower`, `--ease-out` `--ease-in-out` `--ease-spring` |

### The `nf-*` class API — complete

`nf-avatar` `nf-badge` (`--neutral --success --warning --danger --info`)
`nf-btn` (`--primary --ghost --danger --icon --sm --lg`) `nf-card` `nf-card--hover`
`nf-check` `nf-chip` `nf-divider` `nf-divider--soft` `nf-dot` (`--live --warn --off`)
`nf-dots` `nf-field` `nf-glass` `nf-input` `nf-inset` `nf-label` `nf-progress`
`nf-progress--striped` `nf-radio` `nf-range` `nf-segment` `nf-select` `nf-skeleton`
`nf-spinner` `nf-surface` `nf-surface-sm` `nf-surface-lg` `nf-switch` `nf-textarea`
`nf-tip`

Nothing else exists. Anything the report needs beyond this — the exec row, the
finding card, the chart card, the KPI tile — is built **from tokens** in the
report's own layout layer, using `background: var(--surface)` plus
`box-shadow: var(--el-1|2)` so it reads as part of the same tonal system.

### Contrast

Body text is `--fg1`, secondary prose `--fg2`, labels and axis ticks `--fg3`.
Everything the reader must *read* clears WCAG AA (4.5:1) in both themes; chart
furniture — gridlines, hairlines, track fills — is exempt. Never encode meaning
in colour alone: pair a series colour with a direct label, a dot, or an icon.

- Fonts: three families — Sora (display), Plus Jakarta Sans (body), JetBrains
  Mono. **Embed base64 woff2 subsets as `@font-face`**; never leave a network
  `<link>` or `@import` in the file. The fallback stacks in `colors_and_type.css`
  are the safety net, not the plan.
- Icons: Lucide-style, inline SVG only, 2px rounded stroke at 16/20/24px,
  `currentColor`. No CDN, no emoji.

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
- No three.js, no WebGL. This is a data report in a soft-UI register; a CSS or
  inline-SVG effect beats ~600 KB of scene graph every time.

## Structure (top to bottom)

The order below is a **spec, not a suggestion**. Renaming or reordering sections
makes week-to-week editions unscannable, and it is the single most common defect
in this report. Copy the headings verbatim.

1. **Hero** — title, date, analysis window, session/project counts, and a
   one-paragraph verdict of the period. The `<h1>` verdict line is the one piece
   of free text in the whole report. Subtle ambient motion; a KPI stat row under it.
2. **Executive summary** — the ranked recommendation list, most leverage
   first. Each row: rank, verdict badge (new-skill / automation / fix /
   keep-doing / observation), title, leverage score, effort, session count.
   Clicking a row opens and scrolls to its detail card. Filter chips by
   **verdict *and* family**, plus a text search across all clusters.
3. **Since last report** (only when a prior report existed) — see the layout
   spec below. Three columns: **Adopted / Still recurring / New**.
4. **Focus section** (only when a focus argument was given) — deep dive on
   the focused project/theme.
5. **Wins & playbook** — effective patterns worth keeping, same evidence
   treatment as a detail card.
6. **Usage panorama** — the dashboard. See its own spec below.
7. **Findings & recommendations** — detail cards, one per cluster, **collapsed
   by default** to summary + verdict; expand to reveal rationale, the concrete
   example (in a copyable `<pre>` block — the exact prompt / skill description /
   settings line), and the evidence: verbatim quotes with session ID, project,
   and date. Corroborated-by-/insights findings get a marker.
8. **Methodology appendix** — window, counts, triage rules, sampling (if
   any), sessions skipped as unreadable, /insights coverage %, and
   limitations.

Findings sit **after** the panorama deliberately: the summary ranks them up top
for the skimmer, the panorama gives the reader the shape of the week, and the
long evidence cards are the reference material you drill into last.

### "Since last report" — layout spec

Three equal columns on one row (`repeat(3, 1fr)`, collapsing to one column under
~860px), each a card on `var(--surface)` with `var(--el-2)`. This section is
read at a glance, so the formatting rules are tight:

- **Column header**: an `nf-badge` in the bucket's semantic colour
  (Adopted → success, Still recurring → warning, New → info) with the count
  beside it. Not a bare `<h3>`.
- **One item per row**, and a row is **exactly two lines**: the recommendation
  title (600 weight, `--fg1`, `--fs-sm`), and one meta line beneath it in
  `--font-mono` / `--fs-2xs` / `--fg3`. Never wrap a paragraph of rationale
  into this section — it belongs in the detail card.
- **The meta line carries the bucket's own fact, not a generic one**: Adopted →
  the report it was first raised in; Still recurring → `streak ×N` plus the
  session count; New → the family and the session count.
- **Long titles truncate, never reflow the grid.** Two-line clamp
  (`-webkit-line-clamp: 2`), `overflow-wrap: anywhere`, and `min-width: 0` on
  every flex/grid child — without that last one a single long `code` token
  blows the column out and the three-column grid stops being three columns.
- **A row links to its detail card** (same behaviour as an exec-summary row).
- **An empty bucket renders an empty state**, not an empty card: one muted line
  saying what emptiness means ("nothing was adopted since 24 Aug").

## The Usage panorama — dashboard spec

This section is a **reporting dashboard**, not a stack of charts. It is judged
against real analytics products: dense, aligned, scannable, no wasted space, no
chart bigger than the question it answers.

**Layout.** One 12-column CSS grid, `gap: 18px`, spanning the content width.
Every tile declares its span; nothing is `auto`. A tile is a card on
`var(--surface)` with `var(--el-2)`, `--r-lg`, 20–24px padding.

Use this rhythm, top to bottom:

| Band | Content | Spans |
| --- | --- | --- |
| KPI strip | 4–6 compact stat tiles: sessions, tool calls, tokens, active hours, guard blocks, error rate. Overline label, big `--font-display` number, a sparkline or a delta badge. | `2` each |
| Trend | The one wide time-series (activity over the window, series per project or per kind) with an area fill. | `8` |
| Composition | The donut it pairs with (session mix, model mix) — legend inline to the right of the ring, never below. | `4` |
| Detail row | Two to three mid-size tiles side by side: top tools, tool error rate, friction categories over time. | `6` / `6`, or `4`/`4`/`4` |
| Token row | Token consumption: a stacked column per day (input / cache-write / cache-read / output), and a bar of tokens by project. | `7` / `5` |
| Distribution | Activity heatmap (day × hour) — full width, it needs the pixels. | `12` |
| Placement | **"Where each recommendation sits"** — the leverage × effort quadrant map. It belongs here, in the dashboard, not next to the findings. | `12` |

**Sizing.** Author each SVG at its true rendered width — a `6`-span tile is
`viewBox="0 0 520 h"`, a `12`-span tile is `viewBox="0 0 1060 h"`. Never draw at
520 and let a full-width card scale it up 2×: strokes, type and tick labels all
inflate and the tile reads as a blown-up thumbnail. Heights: 150–190 for a KPI
sparkline, 240–280 for a mid tile, 300–340 for a wide one.

**Axes.** Round the axis maximum to a clean step before drawing — `1/2/2.5/5 ×
10ⁿ` over five ticks — so the reader sees `0 / 200 / 400 / 600 / 800 / 1k`, never
`0 / 138 / 276 / 414`. Abbreviate above four digits (`1.2k`, `4.8M`).

**Equal-height rows.** Tiles in the same grid row must be the same height, or the
dashboard reads as ragged offcuts. Let the grid stretch them (`align-items:
stretch`), make each tile a flex column, and give the sub-copy `margin-bottom:
auto` so the charts bottom-align across the row while the prose takes the slack.

**A data table is not a chart.** Wrap it in its own `overflow-x: auto` container
with a `min-width` on the table — otherwise it pushes a horizontal scrollbar onto
the whole document at phone widths. Check the sticky nav there too: a single
flex row with a search box in it overflows a 375px viewport unless it wraps.

**Density rules.** Direct-label a series wherever it fits and drop the legend
entirely. One number per tile gets the display face; everything else is
`--font-mono` at `--fs-xs`. No tile is taller than it is wide unless it is a
ranked bar list. If a chart needs a paragraph to explain it, it is the wrong
chart.

**Token usage is required when the data is available.** Claude Code transcripts
carry `message.usage` on every assistant record — `input_tokens`,
`cache_creation_input_tokens`, `cache_read_input_tokens`, `output_tokens`, and
`output_tokens_details.thinking_tokens`. Dedupe by `message.id` before summing:
streaming writes the same usage block on every partial, and naive counting
inflates the total several-fold. Report the four components separately — the
cache-read share is the interesting number, not the sum. If a corpus predates
the field, say so in the methodology appendix rather than omitting the tile
silently.

## Custom SVG graphics (required)

Author custom inline SVG — never a chart library, never raster images — in
three roles:

1. **Data charts** — every chart is hand-built SVG styled with design-system
   tokens. Bar/column for per-project volume, line/area for trends, donut for
   composition, heatmap grids for activity by day/hour, lollipop or ranked bars
   for top-N lists, quadrant scatter for placement. Real axes, labeled ticks,
   direct labels or an inline legend, `<title>` elements for hover tooltips, and
   `role="img"` + `aria-label` per chart. Pick the form that fits the data; don't
   repeat one shape eight times.

   Take the geometry from `ui_kits/dashboard/Widgets.jsx`: the area path that
   closes back along the baseline under a `linearGradient` fading to zero alpha;
   the drawn line via `stroke-dasharray`/`stroke-dashoffset`; the end-point dot
   ringed in `var(--surface)`; the donut as a `conic-gradient` disc with an
   `--inset-1` hub carrying the total; the legend row as
   `swatch · label · mono value`.

   **Series colours come from `--c-1` … `--c-6`, in order.** Gradient and filter
   ids must be deterministic and unique per file — derive from the chart's own
   name (`grad-sessions-by-project`), never `Math.random()`.
   **A scatter of ranked findings needs a beeswarm and a label lane.** Points
   sharing a cell must spread across the column so none are hidden, direct labels
   go in a reserved gutter to the right of the plot with leader lines and a greedy
   vertical de-collision pass, and the label text is clipped to the character
   count the gutter actually holds. Crop the value axis to the data's own floor —
   a leverage scale drawn 0–10 when nothing scores below 5 wastes half the tile.

2. **Explanatory graphics** — where a diagram lands a finding faster than prose:
   a friction loop (prompt → error → retry → interrupt), a before/after prompt
   panel, a pipeline sketch of a recommended automation.
3. **Aesthetic layers** — decorative SVG in the soft-UI register: blurred
   mint/teal blobs behind the hero, a drawn hero line, section dividers, sparkline
   flourishes in stat tiles. Decorative layers get `aria-hidden="true"`. Max one
   glowing element per region, and decoration never displaces evidence.

All fills and strokes reference CSS variables, so every chart survives the theme
toggle. Animate charts in with GSAP (bars grow from the baseline, lines draw,
donuts sweep) gated behind `prefers-reduced-motion`.

## Interactivity & motion

- Sticky top nav with scrollspy and smooth-scroll anchors, plus the theme toggle
  and the search box.
- Expand/collapse detail cards (`<details>`), collapsed by default.
- Filter the summary by verdict **and** family; text search across clusters.
- Copy buttons on every `<pre>` example block.
- GSAP + ScrollTrigger: staggered entrance reveals (fade-up ~20px, 40–60ms
  stagger), count-up stat numbers (≤1.4s), bars growing from the baseline,
  donuts drawing, hero parallax on the blobs.
- **Fast chrome, slow data**: controls respond in ≤180ms; a chart may take up to
  1.3s to draw because it rewards watching. Motion emphasises the ranking and the
  key numbers; it never delays reading.
- Under `prefers-reduced-motion: reduce`: loops stop, entrances become
  opacity-only, counters and charts render their **final state immediately** —
  not a faster animation. Never rely on motion to convey status.
- **Prove the ticker is alive before setting any from-state.** Every reveal is a
  `gsap.from()`, which applies the *from* values the instant it is created. If
  `requestAnimationFrame` never fires — a throttled background tab, a low-power
  browser, an embedded preview pane — the tweens never advance and **the entire
  report renders at `opacity: 0` with empty charts and counters stuck at zero**.
  This is not hypothetical; it is what the 27 July and 24 August editions do in
  any throttled context. Gate the whole motion block:

  ```js
  var ticked = false;
  requestAnimationFrame(function () { ticked = true; });
  setTimeout(function () { if (ticked) startMotion(); }, 260);
  ```

  With no ticker the page simply renders — fully drawn, readable, unanimated.
  Verify it: load the report and assert every card, row and heading computes to
  `opacity: 1` and every `.grow-bar` has a non-zero height before any scrolling.

## Embedded data block (machine-readable — future runs depend on this)

Embed exactly one:

```html
<script type="application/json" id="cc-reflection-data">
{
  "generated": "YYYY-MM-DD",
  "window": {"kind": "30d", "from": "YYYY-MM-DD", "to": "YYYY-MM-DD"},
  "focus": "string or null",
  "design_system": "Neumorphic Fresh",
  "sessions_analyzed": 0,
  "projects": ["..."],
  "insights_coverage": 0.0,
  "tokens": {"input": 0, "cache_create": 0, "cache_read": 0, "output": 0},
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
