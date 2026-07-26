# Visual production — Method A (HyperFrames → animated WebP)

The pipeline that turns a design decision into a GitHub-safe, seamless-loop
animated WebP: author an HTML composition, gate it, render an MP4, convert to a
budgeted WebP. Every visual is styled by the repo's frozen design system
(`.prettydocs/prettydocs.md`, see `design-system.md`) and embedded per
`embedding.md`. This file is self-contained; follow it in order per visual.

## Preconditions

- **HyperFrames skills current.** `SKILL.md`'s preflight already gated this; don't
  re-run the skill refresh here.
- **`ffmpeg` present** on PATH.
- **`img2webp` present.** macOS ffmpeg is usually built without libwebp, so WebP
  assembly uses Google's separate tool: `brew install webp`. The conversion script
  checks this and prints the remedy if it's missing.

## Where things live

```text
.prettydocs/prettydocs.md          frozen design system (all visuals derive from it)
.prettydocs/src/<viz-name>/        one composition per visual
  index.html                       the HyperFrames composition (committed)
  viz.json                         per-visual state + grounded fact list (committed)
  hyperframes.json, package.json,  scaffold config written by `hyperframes init`
  meta.json                        (committed — the CLI needs them to re-render;
                                   meta.json here is HyperFrames' own file, NOT ours)
  render.mp4                       rendered output (gitignored)
  renders/                         default render output dir (gitignored)
  frames/                          extracted PNG frames (gitignored)
  snapshots/                       snapshot stills (gitignored)
  qa_*.png                         verification stills (gitignored)
  check.json                       hyperframes check report (gitignored)
docs/assets/<viz-name>.webp        final committed WebP
```

Committed per visual: `index.html`, `viz.json`, the small scaffold config files
(`hyperframes.json`, `package.json`, and HyperFrames' own `meta.json` — do not
confuse it with `viz.json`), and the final `docs/assets/<viz-name>.webp`. The
skill writes `.prettydocs/.gitignore` once; its rules are relative to that file, so
they need no per-visual upkeep.

## 1. Scaffold

One project per visual:

```bash
HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes init .prettydocs/src/<viz-name> \
  --non-interactive --example blank
```

`HYPERFRAMES_SKIP_SKILLS=1` skips the skill-refresh churn on init.

## 2. Author `index.html`

Read `/hyperframes-core` before authoring — it's the composition contract. Then
apply this doctrine (proven; from the reference pipeline):

- **One paused GSAP timeline.** A single clip spans the full duration; all motion
  lives on the single registered, paused timeline.
- **JS is the single source of truth for diagram geometry.** One JS layout map
  generates both the HTML node cards and the SVG edge paths — never hand-place the
  same node twice.
- **Fonts self-host.** System stack plus `@font-face { src: local(...) }` for named
  fonts, or embedded data URIs — **never a remote font** (lint requires it, and
  it's the design-system rule).
- **Z-index discipline.** An SVG overlay that draws over HTML cards needs an
  explicit z-index above them, or edges vanish behind nodes.
- **All styling from `.prettydocs/prettydocs.md`** — palette, type, motif, motion
  character. Nothing off-system.

### Seamless-loop rules (mandatory — the loop is steady-state)

The visual replays forever with no visible seam. Every rule below is load-bearing:

- **State at t=D must equal state at t=0.** The last frame and first frame are
  identical.
- **Every periodic cycle count must divide the duration** — a pulse or travel that
  doesn't complete a whole number of cycles within D leaves a jump at the seam.
- **No entrance animations.** The loop is steady-state; anything that "arrives"
  replays its entrance every loop. Start already in the composed state.
- **Yoyo motions need an even half-cycle count** so the element returns to its
  start by t=D. (Yoyo sine pulses with an even half-cycle count are the reliable
  form.)
- **MotionPath loops phase-split at the loop boundary.** For path travel with a
  phase offset φ, split across the seam: partial `φ→1`, then whole cycles, then
  partial `0→φ`, so travel is continuous through t=0.
- **Nested per-cycle choreography replays via `tweenFromTo`.** Complex per-cycle
  motion goes in a nested paused timeline replayed with `tweenFromTo(0, cycle)` at
  each cycle boundary; phase-shift by splitting at the seam.

Durations run **8–14s** (design-system motion rule). No strobing, no flicker, no
idle bobbing — motion always communicates flow or a state change.

## 3. Gate loop (mandatory, per visual)

Iterate here until clean. **Do not render until all three pass.**

```bash
npx hyperframes lint
npx hyperframes snapshot --at <t1,t2,t3>
npx hyperframes check
```

- **`lint`** — run continuously while authoring.
- **`snapshot --at t1,t2,t3`** — writes stills at those times. **Read the snapshot
  frames with the Read tool — actually look at the pixels.** This catches label
  collisions, occlusions, and clipped text that no linter sees.
- **`check`** — must report **0 errors** (catches WCAG contrast failures, text
  occlusion, and overlap). Zero, not "only warnings."

## 4. Render

Only after the gate is clean:

```bash
npx hyperframes render --quality high --output render.mp4
```

## 5. Convert to WebP

Use the bundled script (don't hand-run the two commands unless debugging):

```bash
scripts/viz_to_webp.sh .prettydocs/src/<viz-name> docs/assets/<viz-name>.webp
```

Parameters and defaults:

| Position | Meaning | Default |
| --- | --- | --- |
| 1 | composition dir (holds `render.mp4`) | — (required) |
| 2 | output `.webp` path | — (required) |
| 3 | fps | `15` |
| 4 | width (px) | `1200` |
| 5 | quality (`img2webp -q`) | `68` |

Under the hood it runs:

```bash
ffmpeg -y -i render.mp4 -vf "fps=15,scale=1200:-2" frames/f_%04d.png
img2webp -loop 0 -d 67 -lossy -q 68 -m 6 frames/f_*.png -o <output.webp>
```

`-d 67` is the per-frame duration in ms (≈15fps: 1000/15 ≈ 67). If you pass a
different fps, the script recomputes `d = round(1000/fps)`. A typical 12s loop
lands around 1–1.7 MB.

**Hard budget: output ≤ 2.5 MB or the script fails** (deletes the oversized file).
Remedies, in order:

1. Shorten the loop (fewer frames).
2. Reduce `-q` (quality).
3. Reduce width.
4. Simplify motion so more regions stay static frame-to-frame.

## 6. Verify real pixels

Never hand off unverified. Check the actual output, not the source:

- **Extract stills from the final render and Read them:**
  ```bash
  ffmpeg -i render.mp4 -vf fps=1/5 qa_%03d.png
  ```
  Read `qa_*.png` — scan for blank/black frames, misaligned overlays, text
  overflow, fallback fonts, and a visible seam at the loop boundary.
- **View a doc with embeds over HTTP**, never a `file://` URL (browser tools block
  it): `python3 -m http.server` in the doc's dir, then open `http://localhost:<port>/`.

State which frames/timestamps you inspected and that seams/overlays/fonts passed.

## 7. Byproduct hygiene

`render.mp4`, `renders/`, `frames/`, `snapshots/`, `qa_*.png`, and `check.json`
are gitignored by `.prettydocs/.gitignore`. Committed: `index.html`,
`viz.json`, the scaffold config (`hyperframes.json`, `package.json`, HyperFrames'
own `meta.json`), and the final `docs/assets/<viz-name>.webp`.

---

## Static-SVG production (non-flagship visuals and banners)

Visuals outside the animated budget are hand-authored SVG, styled strictly from
`.prettydocs/prettydocs.md`. These must survive GitHub's SVG sanitizer and read on
both themes.

### GitHub-safe hard rules

An SVG that violates any of these is silently broken on GitHub:

- **No `<script>`.**
- **No `<foreignObject>`.**
- **No remote fonts, images, stylesheets, or CSS `@import`.** Use system font
  stacks (`-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`;
  `ui-monospace, SFMono-Regular, Menlo, monospace`) or convert text to paths. All
  imagery is native SVG shapes/paths — no remote `<image href>`.
- No essential hover states or SVG-embedded animation (GitHub won't play it).
- No heavy filters that produce dirty or oversized shadows.

### Canvas and layout

- **`1200`-unit-wide `viewBox`** for full-width modules. Typical heights: hero
  `300–420`, section banner `120–170`, diagram `320–760`.
- Include `<title>` and `<desc>` on every major module, plus meaningful `alt` on
  the embed. Embed with `width="820"` (README, technical docs) or `width="100%"`
  (banners) so the host doesn't guess.
- **Every embed is centered** in the doc — an `<img>` inside a
  `<div align="center">` wrapper, inside the marker pair. Shape and the traps
  around it: [embedding.md](embedding.md) → Centering. This is the embed's position
  on the page, not the artwork's position in the canvas.
- Keep important content `48–64` units from the edges.

### Legible at rendered scale

The `viewBox` is a coordinate system, not a display width. A `1200`-unit SVG in a
`900px` column renders at 75%, so multiply SVG font sizes by `displayed ÷ viewBox`.
Using `900px` as a conservative desktop width:

| Role | Min SVG size | ≈ at 900px |
| --- | ---: | ---: |
| Hero / project title | `48+` | `36px+` |
| Section title | `40+` | `30px+` |
| Essential diagram/card text | `20+` | `15px+` |
| Supporting label | `18+` | `13.5px+` |
| Nonessential metadata only | `16+` | `12px+` |

Don't fix small text by shrinking the viewBox — the proportions don't change.
Increase text relative to the canvas, cut density, or split the board. Also
inspect a `360px` mobile preview; if a required label fails there, keep the detail
in adjacent Markdown/alt text and use a taller composition.

### Both-theme legibility

Text must read on GitHub light **and** dark backgrounds. The safest full-width SVG
supplies its own opaque background; otherwise test the asset against both themes.

### Build order and check

1. Background and structural lines → 2. name + concrete description → 3. real
project material → 4. metadata → 5. only decoration still needed. If it reads
after step 4, stop. Prefer a simplified real architecture/relationship/output over
generic grids, dots, or glowing "tech" texture.

Render each SVG (`sips -s format png in.svg --out /tmp/out.png`, or a browser /
`rsvg-convert`) and inspect for clipped text, sub-legible sizes, weak contrast,
off-project decoration, and missing `<title>`/`<desc>`/`viewBox`/alt.
