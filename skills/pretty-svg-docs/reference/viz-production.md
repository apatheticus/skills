# Visual production — hand-authored, GitHub-safe animated SVG

The pipeline that turns a design decision into a committed, seamless-loop animated
SVG. There is no renderer and no conversion step: you write the `.svg`, a bundled
`python3` script gates it, and that same file is what ships. Every visual is styled
by the repo's frozen design system (`docs/assets/src/DESIGN.md`, see
`design-system.md`) in the run's resolved style (`styles.md`), and embedded per
`embedding.md`.

Read `svg-animation.md` before authoring your first animated visual in a run — it
holds the motion vocabulary and the seam contract this file assumes.

## Preconditions

- **`python3` on PATH.** Both bundled scripts are stdlib-only; no `pip install`,
  no virtualenv. `SKILL.md`'s preflight already probed for it.
- **A browser tool for the pixel read** (Playwright, claude-in-chrome, or the user
  opening a local page). Optional: without one, step 4 is **skipped and reported**,
  never silently marked passed.

Nothing else. No CLI, no `ffmpeg`, no `img2webp`, no network.

## Where things live

```text
docs/assets/src/DESIGN.md          frozen design system + resolved style (all visuals derive from it)
docs/assets/<viz-name>.svg         committed — the asset AND the source
docs/assets/src/<viz-name>/
  viz.json                         committed — facts, hashes, svg params (see embedding.md)
  _qa/filmstrip.html               gitignored — the scrub harness
  _qa/phase_*.png                  gitignored — verification stills
```

One `.gitignore` entry covers the byproducts:

```
docs/assets/src/**/_qa/
```

The asset is the source, so nothing under `src/<viz-name>/` duplicates the artwork.
That is the one structural difference from the sibling `pretty-hyper-docs` layout;
the marker shape is identical.

## 1. Author `docs/assets/<viz-name>.svg`

### The skeleton

Every visual starts from this shape. The root attributes are load-bearing — the
checker requires `viewBox`, `data-loop-s`, `<title>` and `<desc>`.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 420"
     width="1200" height="420" role="img" data-loop-s="12" data-bg="background">
  <title>Request flow</title>
  <desc>Requests enter the gateway, are authenticated, then routed to one of three services.</desc>
  <style>
    /* token block: one custom property per DESIGN.md palette role.
       Declare colours here and reference them with var() — the checker resolves
       var(), matches each value against the palette, and errors on a stray hex. */
    svg { --background:#0d1117; --surface:#161b22; --ink:#e6edf3;
          --rule:#30363d; --accent:#58a6ff; }

    .bg   { fill: var(--background); }
    .ink  { fill: var(--ink); }
    .rule { stroke: var(--rule); stroke-width: 1.5; fill: none; }
    .flow { stroke: var(--accent); stroke-width: 2.5; fill: none; }

    /* motion — every duration divides data-loop-s (12) */
    .pulse { animation: pulse 4s ease-in-out infinite; }
    @keyframes pulse { 0%,100% { opacity: .35 } 50% { opacity: 1 } }

    @media (prefers-reduced-motion: reduce) {
      .pulse { animation: none; opacity: 1; }
    }
  </style>
  <rect class="bg" x="0" y="0" width="1200" height="420"/>
  <!-- content -->
</svg>
```

`data-bg="background"` on the root names the palette role the checker measures text
contrast against. Any element sitting on a different ground carries its own
`data-bg="surface"`, and the checker uses the nearest ancestor's value.

**Colour provenance.** Every colour must trace somewhere: either it matches a
`DESIGN.md` palette hex, or it is declared as a custom property in the token block
(which is how you assert a *derived tint* — a bevel highlight, a gradient stop).
A raw hex written inline, off-palette and undeclared, is an error. Declared tints
that aren't palette roles get one `WARN` each, so derived colour stays visible in the
run report rather than sneaking in.

### GitHub-safe hard rules

An SVG that violates any of these is silently broken, blank, or unstyled on GitHub.
None of them soften for any style:

- **No `<script>`.** Ever, in a committed asset. GitHub strips it in the `<img>`
  context, and its presence means the file was authored for the wrong target.
- **No `<foreignObject>`.** HTML inside SVG does not render here.
- **No remote anything.** No remote fonts, images, stylesheets, `@import`, or
  `<image href="http…">`. System font stacks
  (`-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`;
  `ui-monospace, SFMono-Regular, Menlo, monospace`) or text converted to paths.
  All imagery is native SVG shapes and paths.
- **No hover states or interaction.** Nothing inside an `<img>` receives pointer
  events.
- **Opaque background.** Supply your own; never rely on the host's page color. The
  visual must read identically on GitHub's light and dark themes, which it does by
  not participating in either. No `prefers-color-scheme` switching — GitHub's theme
  and the reader's OS preference can disagree.
- **No heavy filter stacks.** One filter primitive per element by default. A style
  may raise this to its own declared floor (`skeuomorphic` allows two chained), and
  no further.

### Canvas and layout

- **`1200`-unit-wide `viewBox`** for full-width modules. Typical heights: hero
  `300–420`, section banner `120–170`, diagram `320–760`.
- Set explicit `width`/`height` matching the viewBox, and embed with `width="820"`
  (README, technical docs) or `width="100%"` (banners) so the host doesn't guess.
- **Every embed is centered** in the doc — an `<img>` inside a
  `<div align="center">` wrapper, inside the marker pair. Shape and the traps
  around it: [embedding.md](embedding.md) → Centering. This is the embed's position
  on the page, not the artwork's position in the viewBox; composition inside the
  canvas is the style's call, and several styles compose deliberately left-aligned.
- Include `<title>` and `<desc>` in every file, plus meaningful `alt` on the embed.
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

`svg_check.py` enforces these floors against the `font-size` on each `<text>` (or its
class). It can't tell a title from a caption, so you declare the role with
`data-role` on the element:

| `data-role` | Floor |
| --- | ---: |
| `hero` | `48` |
| `title` | `40` |
| `essential` | `20` |
| `label` *(default when omitted)* | `18` |
| `metadata` | `16` |

So a hero title with no `data-role` only has to clear `18` — the floor is a
*minimum*, not a design instruction. Tag the hero `data-role="hero"` and the checker
holds it to `48`. Tag a genuinely decorative string `data-role="metadata"` to hold it
to `16` rather than inflating it.

Don't fix small text by shrinking the viewBox — the proportions don't change.
Increase text relative to the canvas, cut density, or split the board. Also inspect
a `360px` mobile preview; if a required label fails there, keep the detail in
adjacent Markdown or alt text and use a taller composition.

### Build order

1. Background and structural lines → 2. name + concrete description → 3. real
project material → 4. metadata → 5. only decoration still needed. If it reads after
step 4, stop. Prefer a simplified real architecture, relationship, or output over
generic grids, dots, or glowing "tech" texture.

Add motion last, to a composition that already reads while stopped.

### Byte discipline

| Threshold | Effect |
| --- | --- |
| 60 KB | warn — the visual is dense; check that it earns it |
| 150 KB | **hard fail** |

A style may raise the ceiling only to its own declared floor (`maximalist` 250 KB,
`glassmorphism` 200 KB) and never past it. Remedies, in order: hoist repeated
geometry into `<defs>` + `<use>`, drop decorative texture, reduce path coordinate
precision to 1–2 decimals, split one crowded board into two visuals. Never shrink
labels below the legibility floor and never quietly drop content.

## 2. Gate loop (mandatory, per visual)

Iterate until clean. **Do not write `viz.json` or the marker until this passes.**

```bash
python3 scripts/svg_check.py --design docs/assets/src/DESIGN.md \
  --style <slug> docs/assets/<viz-name>.svg
```

What it checks, in order:

| Class | Check |
| --- | --- |
| Structural | no `<script>`, no `<foreignObject>`, no remote `href`/`@import`; `viewBox`, `<title>`, `<desc>`, `data-loop-s` present |
| Seam | every CSS `animation` duration and SMIL `dur` divides `data-loop-s`; every animation is `infinite`/`indefinite` |
| Motion a11y | a `prefers-reduced-motion` block exists and covers every animated class **and** every SMIL-animated element |
| Legibility | every `font-size` meets its role floor |
| System | every `fill`/`stroke` hex traces to a `DESIGN.md` palette role; text contrast ≥ 4.5:1 against its `data-bg` role |
| Style | the resolved style's `forbid` / `require` invariants |
| **Fidelity** | the style's **minimum**: `require_filter_all` primitives present, deepest chain ≥ `min_filter_depth`, drawn geometry ≥ `min_elements` (specimens only) |
| Size | warn at 60 KB, fail over 150 KB |

Every other class above is a ceiling or a legibility floor, so a flat, styleless
render used to pass clean. The fidelity class is the half that asks whether the file
looks like what it claims — if a visual is authored in `wood-grain`, it must actually
carry the turbulence-and-displacement chain that *is* wood grain, not a gradient that
suggests one.

The checker also emits a positive `NOTE` per file:

```
NOTE  docs/assets/foo.svg: fidelity: deepest chain 3, 2 filter(s), 61 drawn elements,
      primitives feColorMatrix, feComponentTransfer, feTurbulence
```

Read it. `deepest chain 1` on a style that declares a floor of 3 is the tell that the
material was faked, and it is the one line in the report that says so.

Two attributes matter here:

- `data-specimen="true"` on the root marks a visual as a **specimen** of its style —
  a catalog sample, not a working diagram. Only specimens are held to `min_elements`,
  because geometry density is a property of what a diagram says, not of its style.
- `data-style="<slug>"` on a `<filter>` attributes that chain to the style it depicts,
  so a **multi-style** visual (the contact sheet) measures each filter against that
  style's own floor and ceiling instead of the file-wide one.

Exit code is non-zero on any `ERROR`. `SOFTENED` lines are passes that used a
declared style relaxation — they belong in the run report and in `viz.json`'s
`relaxed` array. `WARN` lines are advisory, and identical graphic-contrast warnings
are aggregated with an `(xN)` count.

Zero errors, not "only warnings."

## 3. Build the filmstrip

```bash
python3 scripts/svg_filmstrip.py docs/assets/<viz-name>.svg --phases 6
```

Writes `docs/assets/src/<viz-name>/_qa/filmstrip.html`: six inline copies of the
SVG, each paused at a different phase of the loop via a negative
`animation-delay`, labelled with its timestamp. One screenshot then shows the whole
cycle. The harness is gitignored and never committed, which is why it may use the
`<script>` a committed asset may not.

## 4. Read the pixels

Serve over HTTP — **never** a `file://` URL, browser tools block it:

```bash
python3 -m http.server 8765 --directory docs/assets/src/<viz-name>/_qa
# then open http://localhost:8765/filmstrip.html
```

Screenshot it and **Read the image**. Scan for:

- clipped or overflowing text, and labels colliding at any phase
- sub-legible sizes at the rendered width
- occlusion — a moving element parking on top of a label
- fallback fonts (a serif where the stack asked for system sans)
- **the seam**: the first phase and the wrap-around phase must be identical

Kill the server when done (`lsof -ti:8765 | xargs kill`).

No browser tool available? Say so explicitly in the report: *"pixel review skipped —
no browser tool; `svg_check.py` passed."* Never imply pixels were inspected.

## 5. Commit the state

Only now, and in this order:

1. Write `docs/assets/src/<viz-name>/viz.json` — facts, `facts_hash`, `src_hash`
   over the committed `.svg`, `design_hash`, `producer`, `style`, the `svg` block,
   and the `relaxed` array from step 2.
2. Rewrite the `pd:viz` marker with the same `facts-hash` and `src-hash`.
3. Confirm `docs/assets/src/**/_qa/` is in `.gitignore`.

A marker and manifest that disagree mean one was hand-edited; the audit reports it
and the next apply run re-authors the visual to re-sync.

---

## Statics

A static visual is the same file format with no `<style>` animation block. Set
`data-loop-s="0"` and `"loop_s": 0` in `viz.json`; the checker skips the seam and
reduced-motion classes and applies everything else unchanged. Statics get the same
`<title>`/`<desc>`, the same palette conformance, the same legibility floors, and
the same byte cap.

Use a static when motion would carry no information: a decision tree that is really
a table, a SUPPORT header, a banner whose whole job is one sentence.
