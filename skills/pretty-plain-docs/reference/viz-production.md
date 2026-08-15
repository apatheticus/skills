# Visual production — hand-authored, GitHub-safe static SVG

The pipeline that turns a design decision into a committed static SVG. There is no
renderer and no conversion step: you write the `.svg`, a bundled `python3` script
gates it, and that same file is what ships. Every visual is styled by the repo's
frozen design system (`.prettydocs/prettydocs.md`, see `design-system.md`) in the
run's resolved style (`styles.md`), and embedded per `embedding.md`.

**Nothing animates.** A single `@keyframes` block, one `animation:` declaration or
one SMIL tag is a gate failure, not a style choice — see *The animation ban* below.
A visual that needs motion to make its point belongs in the sibling
`prettier-svg-docs` (animated SVG) or `pretty-hyper-docs` (animated WebP).

Data charts have their own narrow, provenance-gated path: [charts.md](charts.md).
Read it before plotting any value; most "charts" should be structural diagrams.

## Preconditions

- **`python3` on PATH.** Both bundled scripts are stdlib-only; no `pip install`,
  no virtualenv. `SKILL.md`'s preflight already probed for it.
- **A browser tool for the pixel read** (Playwright, claude-in-chrome, or the user
  opening a local page). Optional: without one, step 3 is **skipped and reported**,
  never silently marked passed.

Nothing else. No CLI, no `ffmpeg`, no `img2webp`, no network.

## Where things live

```text
.prettydocs/prettydocs.md          frozen design system + resolved style (all visuals derive from it)
docs/assets/<viz-name>.svg         committed — the asset AND the source
.prettydocs/src/<viz-name>/
  viz.json                         committed — facts, hashes, svg params (see embedding.md)
  _qa/*.png                        gitignored — verification stills
```

One `.gitignore` entry covers the byproducts:

```
src/**/_qa/
```

The asset is the source, so nothing under `src/<viz-name>/` duplicates the artwork.
That is the one structural difference from the `pretty-hyper-docs` layout; the
marker shape is identical across all three skills.

## 1. Author `docs/assets/<viz-name>.svg`

### The skeleton

Every visual starts from this shape. The root attributes are load-bearing — the
checker requires `viewBox`, `data-loop-s`, `<title>` and `<desc>`.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 420"
     width="1200" height="420" role="img" data-loop-s="0" data-bg="background">
  <title>Request flow</title>
  <desc>Requests enter the gateway, are authenticated, then routed to one of three services.</desc>
  <style>
    /* token block: one custom property per prettydocs.md palette role.
       Declare colours here and reference them with var() — the checker resolves
       var(), matches each value against the palette, and errors on a stray hex. */
    svg { --background:#0d1117; --surface:#161b22; --ink:#e6edf3;
          --rule:#30363d; --accent:#58a6ff; }

    .bg   { fill: var(--background); }
    .ink  { fill: var(--ink); }
    .rule { stroke: var(--rule); stroke-width: 1.5; fill: none; }
    .flow { stroke: var(--accent); stroke-width: 2.5; fill: none; }
  </style>
  <rect class="bg" x="0" y="0" width="1200" height="420"/>
  <!-- content -->
</svg>
```

`data-loop-s="0"` is the static declaration. It is required, it must be `0`, and it
is what makes this skill's output legible to the sibling skills' tooling — a
`prettier-svg-docs` checker reading one of these files sees a declared static and
holds it to exactly the same rule.

`data-bg="background"` on the root names the palette role the checker measures text
contrast against. Any element sitting on a different ground carries its own
`data-bg="surface"`, and the checker uses the nearest ancestor's value.

**The value must be a palette role name, spelled exactly as the Palette table spells
it.** This is the one place a mistake degrades quietly: a `data-bg` the checker cannot
resolve is not an error, it is

```
WARN  text has no data-bg ground in scope — contrast unchecked
```

and the contrast floor is then **not applied to that text at all**. `data-bg="accent"`
against a table that calls the role `accent-primary` reads as a pass. Treat that WARN
as a failure and fix the name — a run with zero errors and four of those has four
labels whose contrast nobody checked.

**Colour provenance.** Every colour must trace somewhere: either it matches a
`prettydocs.md` palette hex, or it is declared as a custom property in the token
block (which is how you assert a *derived tint* — a bevel highlight, a gradient
stop). A raw hex written inline, off-palette and undeclared, is an error. Declared
tints that aren't palette roles get one `WARN` each, so derived colour stays visible
in the run report rather than sneaking in.

### The animation ban

There is no motion vocabulary in this skill, and no partial case. All of these are
an `ERROR`:

- any `animation:` or `animation-name:` declaration, including `animation: none`;
- any `@keyframes` block, even one no rule references;
- any SMIL tag — `<animate>`, `<animateTransform>`, `<animateMotion>`, `<set>`,
  `<animateColor>`;
- any `data-loop-s` value other than `0`.

`@media (prefers-reduced-motion: reduce)` is not required and has nothing to do:
a static already honours that preference. The relevant accessibility work here is
the `<title>`, the `<desc>`, the embed's `alt`, and — for every structural visual —
the `<details>` Mermaid source. See `house-style.md` → quality gates.

**Converting an animated visual.** A file arriving from `prettier-svg-docs` is
adopted by folding each `@media (prefers-reduced-motion: reduce)` rule's resting
declarations onto the base rule, then deleting the keyframes, the animation
declarations and the reduce block, and flipping `data-loop-s` to `0`. The reduce
block is the *specification* for the resting state, not a hint: it is what the
original author decided the composition should look like when stopped. Do not pose
the element somewhere new — that is a redraw, and it needs the author's call.
`animation: none` alone parks an element at its **base attribute** state, not its
first keyframe, so a reduce block reading `{ animation: none; opacity: 0 }` means
that `opacity: 0` has to move onto the class or the element has to go.

### GitHub-safe hard rules

An SVG that violates any of these is silently broken, blank, or unstyled on GitHub.
None of them soften for any style:

- **No `<script>`.** Ever, in a committed asset. GitHub strips it in the `<img>`
  context, and its presence means the file was authored for the wrong target.
- **No `--` inside an XML comment.** It is not well-formed XML, and the checker can
  only report it as `not well-formed XML — invalid token` at a line and column, with no
  hint as to why. It bites precisely when documenting this skill's own flags: write
  *the force flag*, not `<!-- --refresh-viz forces it -->`.
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

Because a static `.svg` needs no renderer cooperation beyond drawing it once, this
list is the whole compatibility surface. That is this skill's argument: the output
is the most portable form the three siblings produce — it survives a PDF export, a
print stylesheet, a rasterising reviewer's Markdown renderer and a
documentation-site build with nothing lost, because there was never a second frame
to lose.

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

A static carries more reading matter per square unit than an animated visual of the
same size, because nothing arrives later — everything the visual says is on screen
at once. That makes the legibility floors bind harder here, not less: the honest
remedy for a crowded board is to split it, never to shrink the type.

### Build order

1. Background and structural lines → 2. name + concrete description → 3. real
project material → 4. metadata → 5. only decoration still needed. If it reads after
step 4, stop. Prefer a simplified real architecture, relationship, or output over
generic grids, dots, or glowing "tech" texture.

There is no step for motion. The composition reading as a finished, deliberate
still — not as one paused frame of something else — is the entire product. A visual
with an obvious empty channel where a pulse "would" travel, or a marker parked at a
start position waiting to move, has been authored for the wrong skill.

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
python3 scripts/svg_check.py --design .prettydocs/prettydocs.md \
  --style <slug> docs/assets/<viz-name>.svg
```

What it checks, in order:

| Class | Check |
| --- | --- |
| Structural | no `<script>`, no `<foreignObject>`, no remote `href`/`@import`; `viewBox`, `<title>`, `<desc>`, `data-loop-s` present — **and the static contract**: `data-loop-s` is `0` and the file does not animate (no `@keyframes`, no `animation:`, no SMIL) |
| Legibility | every `font-size` meets its role floor |
| System | every `fill`/`stroke` hex traces to a `prettydocs.md` palette role; text contrast ≥ 4.5:1 against its `data-bg` role |
| Style | the resolved style's `forbid` / `require` invariants |
| **Fidelity** | the style's **minimum**: `require_filter_all` primitives present, deepest chain ≥ `min_filter_depth`, drawn geometry ≥ `min_elements` (specimens only) |
| Size | warn at 60 KB, fail over 150 KB |

Six classes, where `prettier-svg-docs`' checker has eight: the animation ban replaces
its seam and motion-accessibility classes, and lives inside the structural class
because it is a rule about what a committed file may contain.

Every class above except fidelity is a ceiling or a legibility floor, so a flat,
styleless render used to pass clean. The fidelity class is the half that asks whether
the file looks like what it claims — if a visual is authored in `wood-grain`, it must
actually carry the turbulence-and-displacement chain that *is* wood grain, not a
gradient that suggests one. This matters more in a static skill than in an animated
one: with no motion to hold attention, material and draughtsmanship are all the
visual has.

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

## 3. Read the pixels

Serve over HTTP — **never** a `file://` URL, browser tools block it:

```bash
python3 -m http.server 8765 --directory docs/assets
# then open http://localhost:8765/<viz-name>.svg
```

The asset is the source, so this is the finished artefact, not a harness. Screenshot
it and **Read the image**. Scan for:

- clipped or overflowing text, and labels colliding
- sub-legible sizes at the rendered width
- fallback fonts (a serif where the stack asked for system sans)
- an element left invisible or parked off to one side — the residue of a converted
  animation, and the one defect the checker cannot see
- whether it reads as a finished still: no dead channel, no unexplained gap, nothing
  that only makes sense as a frame of a sequence

Also open it at the width it will actually be embedded at (`820px` for a README or
technical doc), not just full size. Kill the server when done
(`lsof -ti:8765 | xargs kill`).

No browser tool available? Say so explicitly in the report: *"pixel review skipped —
no browser tool; `svg_check.py` passed."* Never imply pixels were inspected.

## 4. Commit the state

Only now, and in this order:

1. Write `.prettydocs/src/<viz-name>/viz.json` — facts, `facts_hash`, `src_hash`
   over the committed `.svg`, `design_hash`, `producer`, `style`, the `svg` block
   with `"loop_s": 0`, and the `relaxed` array from step 2.
2. Rewrite the `pd:viz` marker with the same `facts-hash` and `src-hash`.
3. For a structural visual, write or update its `<details>` Mermaid block and
   confirm it parses and still agrees with the SVG node for node.
4. Confirm `src/**/_qa/` is in `.gitignore`.

A marker and manifest that disagree mean one was hand-edited; the audit reports it
and the next apply run re-authors the visual to re-sync.
