# Chart geometry references — read these, never ship them

These seven files are **upstream SaaS Pro React components, bundled as geometry
specifications.** They are reference material only. Nothing here is ever copied into a
report, imported, transpiled, or shipped: the report is a single static HTML file with no
React, no build step and no external requests.

`report-guide.md` requires every chart to be hand-built inline SVG — no chart library, no
raster images. These files are how you build one correctly instead of guessing: each is a
worked solution to the padding, scaling, tick and path problems for its chart form, in
50 lines or fewer, colouring entirely from the design tokens.

**How to use one:** read it, take the maths and the SVG structure, and emit static
`<svg>` markup with the values already computed. The `React.useState` mount flags exist
only to trigger a CSS transition on first paint — in a static report, either animate with
a CSS keyframe from `tokens/motion.css` or render the final state directly.

## What each file solves

| File | Take from it |
| --- | --- |
| `LineChart.jsx` | The reference implementation. `pad = {l:42,r:14,t:16,b:26}` reserves the y-axis gutter; `max = Math.max(...data) * 1.15` gives headroom; five gridlines at `[0,.25,.5,.75,1]` dashed `3 4`; right-aligned tick labels at `x = pad.l - 8`; the area path closes the line back along the baseline; `sp-draw` with an explicit `--draw-len`; a highlight marker with its own callout chip |
| `BarChart.jsx` | Bar width `Math.min(26, (w / n) * 0.55)`, centred per slot at `(i + 0.5) * (w / n)`; `rx={4}`; the max bar gets `--brand-500` at full opacity while the rest sit at 0.75 — direct emphasis instead of a legend; `transformOrigin` at the baseline so `sp-bar-grow` grows upward, staggered 50ms |
| `DonutChart.jsx` | Segment arcs as one `<circle>` each with `strokeDasharray = frac*circ` and `strokeDashoffset = -acc*circ`, the SVG rotated `-90deg` to start at twelve o'clock; `strokeLinecap="butt"` so segments abut cleanly; the accent-ordered palette; centre value + legend with per-segment percentages |
| `Sparkline.jsx` | Min–max normalisation (not zero-based) so small variation stays visible; 2px inset padding; end-point dot with a white ring. For stat-tile footers |
| `LinearGauge.jsx` | Zone bands as flex widths at 0.22 opacity, the needle positioned `left: calc(pct% - 1.5px)`, and the readout tinted by the **zone the value lands in** — the pattern for "is this number good?" |
| `SegmentGauge.jsx` | Ticked dial: `startAngle 225`, `sweep 270`, the polar helper, and `contentH = ceil(cy + rOuter·cos45° + cap)` — the height calculation that stops a 270° arc from being clipped at the bottom. Copy that formula; a naive `height = size` crops the tips |
| `AnimatedCounter.jsx` | Ease-out-cubic count-up over 1.2s, `tabular-nums` so digits don't jitter. Under `prefers-reduced-motion` render the final number immediately (MOTION.md §6) |

`Gauge.jsx` (the solid-arc sibling of `SegmentGauge`) and `ProgressRing.jsx` live upstream
under `components/feedback/` and are not bundled; `components.css` covers the ring as
`sp-ring`, and the same arc maths appears here in `SegmentGauge.jsx`.

## Four traps

**The `-90deg` rotation belongs to two of these components, not to all of them.**
`ProgressRing` and `DonutChart` build their arcs from `stroke-dasharray`, which starts at
three o'clock, so they rotate the whole SVG to move the origin to twelve. `Gauge` and
`SegmentGauge` compute polar coordinates from `startAngle 225` and are already oriented —
rotating one turns it on its side and inverts its aspect ratio. In CSS the rotation is
therefore opt-in via `sp-ring--turn`, and applying it to a gauge is a bug, not a style
choice.

**`Sparkline.jsx`'s end dot overflows its own viewBox by about a pixel.** It insets the x
range by 2px each side (`(i/(n-1))*(width-4)+2`) but then draws a terminal circle at
`r="3.2"` on the last point, so the dot's right edge lands at roughly `width + 1.2`. At
the sizes it is used this clips a sliver of the dot. Inset by the radius, not by 2.

**Gradient ids must be stable and unique.** `LineChart.jsx:8` and `Sparkline.jsx:11`
derive theirs from `Math.random()`, which is correct for a React app and wrong for a
single-file report: a re-render changes the id, and two charts sharing one id silently
collapse to a single gradient. Use a deterministic id derived from the chart's own
name — `grad-sessions-by-project` — unique within the file.

**`dark` is a card ground, not a theme.** Every chart takes a `dark` prop that swaps
gridline and label colours (`var(--ink-100)` → `rgba(255,255,255,0.09)`,
`var(--ink-400)` → `var(--navy-text-dim)`). Per DESIGN.md §5 every chart and table sits
on a dark card, so the dark branch is the normal case — but the light branch must stay
correct for any chart placed on a white card. That is what "hold up on both card
grounds" means; it is not a page-level light/dark theme, which this system does not have.

The `.prompt.md` beside each component is upstream's one-line usage note. Kept for the
props it names.
