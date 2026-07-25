# Styles — the catalog index

A **style** is the look-and-feel idiom every visual in a repo is rendered in. Read
this file in phase 2 to *choose* one, then read exactly one
`reference/styles/<slug>.md` for the spec you'll actually build against. Don't read
the whole `styles/` directory — the index is the cheap half on purpose.

Two rules govern the whole layer:

- **Style owns form; the product's brand tokens own the palette.** Shape, material,
  type treatment, composition and motion character come from the style. Colors come
  from the repo's own identity when it has one (`design-system.md`).
- **Style wins over taste gates, to a declared floor.** Where a style's look
  conflicts with a soft gate, the style wins and the gate softens to the floor named
  in its entry — never off. Structural and truth gates never soften; the list is at
  the bottom of this file.

## The catalog

| Slug | Aliases | Primary axis | Intent in one line | Natural fit |
| --- | --- | --- | --- | --- |
| `swiss-minimal` | `swiss`, `international`, `grid` | composition | Strict grid, thin rules, type doing the work | Libraries, tooling, standards |
| `flat-material` | `material`, `flat` | material | One elevation step, confident color fields | Apps, SDKs, design systems |
| `skeuomorphic` | `realist`, `textured` | material | Objects that look like objects — bevel, sheen, weight | Audio, hardware, creative tools |
| `neumorphism` | `soft-ui`, `soft` | material | Extruded from a single surface; shadow and highlight, no borders | Consumer apps, dashboards |
| `claymorphism` | `clay`, `3d-soft` | material | Fat rounded volumes, playful pastel depth | Onboarding, education, toys |
| `glassmorphism` | `glass`, `frosted`, `aero` | material | Frosted panels over a colored ground | Media, overlays, showcase repos |
| `neo-brutalist` | `brutalist`, `neubrutalism` | material | Hard offset shadows, black rules, unapologetic color | Opinionated tools, dev-facing |
| `editorial` | `magazine`, `print`, `typographic` | composition | Print hierarchy — a lede, a rule, generous margin | Essays, specs, research |
| `maximalist` | `max`, `dense`, `more` | composition | Density as the message; layered, loud, deliberate | Showcase, awards, expressive |
| `y2k-retrofuturist` | `y2k`, `retrofuture`, `chrome` | era | Chrome gradients, wide tracking, optimistic tech | Nostalgic, playful, media |
| `terminal-minimalist` | `tui`, `cli`, `terminal`, `ascii-adjacent` | material | Mono type on a dark field; a TUI that isn't ASCII art | CLIs, infra, devops |
| `blueprint` | `cyanotype`, `drafting` | material | White line work on cyanotype ground, drafted and annotated | Architecture, systems, protocols |
| `schematic` | `technical-drawing`, `circuit`, `netlist` | composition | Symbol alphabet, net labels, no perspective | Hardware, compilers, pipelines |
| `bento-grid` | `bento`, `cards`, `dashboard` | composition | Unequal cells in one tight grid, each with one job | Feature overviews, dashboards |

**`blueprint` vs `schematic`** — the two nearest neighbours, and the pair most often
confused. `blueprint` is a *medium*: cyanotype blue ground, white lines, drafting
annotation, dimension arrows, a title block in the corner. `schematic` is a
*notation*: light ground, a consistent symbol alphabet, net labels instead of drawn
connections where a wire would clutter, and no perspective or shading anywhere. If
the visual should look **drawn**, pick blueprint. If it should look **specified**,
pick schematic.

## Resolution ladder

1. **Explicit `--style <slug>`** → wins outright.
2. **Alias hit** from the table above → resolve to the slug, no question asked.
3. **Free-form name** → if the idiom is genuinely recognisable — a named design
   language (`swiss-punk`, `memphis`), an era (`bauhaus`, `vaporwave`), a medium
   (`risograph`, `letterpress`, `blueprint`), or a documented house style — then
   synthesize **all nine fields** and write them into the repo's `DESIGN.md`
   `## Style` section marked `(ad-hoc)`. That file becomes the only record, so it
   must be complete enough for a later run to reproduce the look. The skill's own
   `reference/styles/` is read-only at run time and never gains entries.
4. **Not resolvable** → ask **one** question naming 2–3 catalog candidates you think
   come closest. `"make it pop"`, `"modern"`, `"clean"`, and `"professional"` are
   not styles; they land here.
5. **Nothing specified** → derive from product identity and semantics by the usual
   rules in `design-system.md`. Infrastructure, security, systems and research repos
   land on `swiss-minimal`, `blueprint` or `terminal-minimalist`; a product with
   strong brand color and a consumer audience lands on `flat-material` or
   `bento-grid`. `--style auto` forces this path even when `docsmeta` holds a slug.

Persist the result in two places: the slug in `.github/docsmeta.json` as
`viz.style`, and the full nine-field spec under `## Style` in
`docs/assets/src/DESIGN.md`. **The spec in `DESIGN.md` is what visuals derive
from** — and because it lives in that file, changing the style moves `design_hash`
and re-authors every visual in the repo. Say so in the phase-3 plan, with a count,
before touching anything.

## The nine fields

Every catalog entry — and every ad-hoc spec you synthesize — has exactly these:

| Field | What it fixes |
| --- | --- |
| Intent | What the style is *for*; when it's the right call |
| Palette treatment | How the repo's palette is deployed. Not which colors. |
| Shape language | Corner radii, stroke weights, geometry |
| Material / depth | Flat, shadowed, glassy, extruded, inked |
| Type treatment | Weight, case, tracking, which family carries what |
| Motion character | What moves, how much, with what easing |
| SVG recipes | Copy-ready snippets that produce the look |
| Relaxes | Which gates soften, and to what floor |
| Never | The moves that break the style |

## Gate softening

Only four styles relax anything. Everything else runs on the defaults.

| Style | Gate | Default → floor |
| --- | --- | --- |
| `neumorphism` | text contrast | 4.5:1 → **3.0:1** |
| `neumorphism` | UI/graphic contrast | 3.0:1 → **2.0:1** |
| `maximalist` | byte cap | 150 KB → **250 KB** |
| `glassmorphism` | byte cap | 150 KB → **200 KB** |
| `skeuomorphic` | filter depth | 1 → **2** chained primitives per element |

The machine-readable half of this table is `scripts/styles.json`, which
`svg_check.py` reads. The two must agree; a slug in one and not the other is a bug.

When a value falls between the default and the floor, the checker prints one
`SOFTENED` line — not a silent pass. Below the floor it's a plain `ERROR`. Every
softened gate is recorded in the visual's `mpd.json` as `"relaxed":
["contrast-text@3.0"]` and listed in the phase-8 report with the count of visuals
affected.

**Softening has a real cost.** A `neumorphism` repo ships labels at around 3:1,
which some low-vision readers will not be able to read in the image. The mitigation
is the works-without-images gate: the meaning always exists in alt text or the
`<details>` Mermaid, so nothing is only available in the picture.

### Never softens, for any style

- No `<script>`, no `<foreignObject>`, no remote `href` or `@import`
- `viewBox`, `<title>`, `<desc>`, `data-loop-s` present
- Seam exactness — every duration divides the loop, every animation infinite
- Reduced-motion coverage, including the SMIL `display: none` rule
- Works without images
- Grounded facts, and the no-volatile-facts rule
- Zero visuals or markers in LICENSE and NOTICE

Those are GitHub-safety, accessibility floor, and truth. They are not taste.
