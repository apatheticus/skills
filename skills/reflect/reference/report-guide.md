# Report guide — structure, design, motion, self-containment

The report is the user's permanent record and playbook. It must be
highly polished, easy to skim, and reward drilling down. One HTML file,
opens from `file://`, offline, indefinitely.

## Design system

Use the bundled Neumorphic Fresh design system in `design-system/`:

- `DESIGN.md` — tokens (colors, type scale, radii, spacing, shadows, motion
  curves) and component prose. Source of truth.
- `colors_and_type.css` + `components.css` — runtime CSS. Inline both into a
  `<style>` block (do not link). Use the `nf-*` component classes
  (`nf-card`, `nf-btn`, `nf-badge`, `nf-progress`, `nf-switch`, …) and set
  `data-theme` on `<html>`; include a light/dark toggle defaulting to the
  OS preference.
- Fonts: the CSS expects Sora / Plus Jakarta Sans / JetBrains Mono from
  Google Fonts. For self-containment, either download the woff2 files and
  embed as base64 `@font-face` (subset if practical), or if that fails,
  delete the Google Fonts reference and rely on the fallback stacks —
  never leave a network `<link>` in the file.
- Icons: no Lucide CDN — inline the handful of SVGs you actually use.

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
- three.js/WebGL: include **only if** the design genuinely uses a scene
  (e.g. an ambient hero background). A tasteful 2D canvas or CSS effect that
  fits the neumorphic soft-UI aesthetic usually beats a heavy 3D scene —
  ~600 KB of three.js needs to earn its place.

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
7. **Usage panorama** — charts built as custom inline SVG (see below) from
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
2. **Explanatory graphics** — where a diagram illustrates a key point better
   than prose, draw one: a flow of a friction loop (prompt → error → retry →
   interrupt), a before/after prompt comparison panel, a pipeline sketch of
   a recommended automation, severity/leverage quadrant maps. These earn
   their place by making a finding land faster.
3. **Aesthetic & effect layers** — decorative SVG that reinforces the
   neumorphic soft-UI feel: soft blob/gradient hero backdrops, section
   dividers, subtle noise/texture via SVG filters (`feTurbulence`,
   `feGaussianBlur`), animated stroke draw-ins (`stroke-dasharray` +
   GSAP/ScrollTrigger), sparkline flourishes in stat tiles.

Rules: derive all fills/strokes/type from the design-system tokens (charts
must hold up in both themes — reference CSS variables, not hard-coded hex);
animate charts in with GSAP (bars grow, lines draw, gauges sweep) gated
behind `prefers-reduced-motion`; decorative layers get `aria-hidden="true"`;
everything remains inline in the single file.

## Interactivity & motion

- Sticky side/top nav with scrollspy; smooth-scroll anchors.
- Expand/collapse detail cards (accessible: `<details>` or
  `aria-expanded` buttons).
- Filter the summary table by verdict/family; text search across clusters.
- GSAP + ScrollTrigger: staggered entrance reveals, count-up stat numbers,
  progress-bar fills on scroll, hero parallax. Respect
  `prefers-reduced-motion` — gate all non-essential animation behind it.
- Motion emphasizes the ranking and key numbers; it never delays reading.
  Springy, quick easings per DESIGN.md's motion tokens.

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
