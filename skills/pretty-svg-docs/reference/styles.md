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

Thirty-one idioms, listed alphabetically.

| Slug | Aliases | Primary axis | Intent in one line | Natural fit |
| --- | --- | --- | --- | --- |
| `bento-grid` | `bento`, `cards`, `dashboard` | composition | Unequal cells in one tight grid, each with one job | Feature overviews, dashboards |
| `blueprint` | `cyanotype`, `drafting` | material | White line work on cyanotype ground, drafted and annotated | Architecture, systems, protocols |
| `brushed-metal` | `brushed-steel`, `machined-panel`, `nameplate` | material | Anisotropic grain, a travelling sheen, engraved type | Firmware, embedded, industrial |
| `claymorphism` | `clay`, `3d-soft` | material | Fat rounded volumes, playful pastel depth | Onboarding, education, toys |
| `codex-leonardo` | `codex`, `renaissance-study`, `iron-gall` | era | Brown ink on aged rag, cross-hatch, mirrored marginalia | Research, speculative design |
| `console-elbow` | `lcars`, `okudagram`, `retro-console` | era | Elbow frame on black, flat colour as zoning | Control planes, orchestration |
| `digital-rain` | `matrix-rain`, `phosphor-crt`, `falling-glyphs` | era + material | Falling glyph columns, structure in the negative space | Streaming, log pipelines, security |
| `draughtsman-notebook` | `engineers-notebook`, `graphite-draft` | era | Graphite on gridded stock — precise, but drawn by a person | Design records, ADRs |
| `editorial` | `magazine`, `print`, `typographic` | composition | Print hierarchy — a lede, a rule, generous margin | Essays, specs, research |
| `flat-material` | `material`, `flat` | material | One elevation step, confident color fields | Apps, SDKs, design systems |
| `glassmorphism` | `glass`, `frosted`, `aero` | material | Frosted panels over a colored ground | Media, overlays, showcase repos |
| `holographic-projection` | `hologram`, `holo`, `projection` | material | Glowing wireframe in a projection cone, scanlines | Simulation, 3D, digital twins |
| `hud` | `heads-up-display`, `targeting-hud`, `telemetry` | composition | Reticles, tick scales, brackets instead of boxes | Monitoring, tracing, profiling |
| `ide-dark` | `editor-dark`, `dev-tool`, `ide` | material | Rounded dark panes, hairline dividers, syntax palette | Language tooling, extensions |
| `isometric-3d` | `isometric`, `iso`, `axonometric` | composition | Three lit faces per block, shadows that track height | Stacks, tiers, deployment topology |
| `lofi-wireframe` | `wireframe`, `greybox`, `lo-fi` | composition | Greyboxes and squiggles — deliberately unfinished | Proposals under discussion, RFCs |
| `maximalist` | `max`, `dense`, `more` | composition | Density as the message; layered, loud, deliberate | Showcase, awards, expressive |
| `neo-brutalist` | `brutalist`, `neubrutalism` | material | Hard offset shadows, black rules, unapologetic color | Opinionated tools, dev-facing |
| `neumorphism` | `soft-ui`, `soft` | material | Extruded from a single surface; shadow and highlight, no borders | Consumer apps, dashboards |
| `oil-impasto` | `impasto`, `oil-paint`, `painterly` | material | Lit height field, canvas weave, travelling gloss | Narrative, essays, launch posts |
| `patent-drawing` | `patent`, `uspto-figure`, `figure-drawing` | era | Black on white, reference characters, no colour at all | Protocols, algorithms, references |
| `pencil-lined-paper` | `lined-paper`, `graphite-notes`, `legal-pad` | material | Handwriting on ruled stock, graphite grain | Notes, teaching, retrospectives |
| `rough-sketch` | `excalidraw`, `roughjs`, `rough` | composition | Doubled strokes and hachure fills — the meeting diagram | Onboarding, contributor docs |
| `schematic` | `technical-drawing`, `circuit`, `netlist` | composition | Symbol alphabet, net labels, no perspective | Hardware, compilers, pipelines |
| `skeuomorphic` | `realist`, `textured` | material | Objects that look like objects — bevel, sheen, weight | Audio, hardware, creative tools |
| `swiss-minimal` | `swiss`, `international`, `grid` | composition | Strict grid, thin rules, type doing the work | Libraries, tooling, standards |
| `terminal-minimalist` | `tui`, `cli`, `terminal`, `ascii-adjacent` | material | Mono type on a dark field; a TUI that isn't ASCII art | CLIs, infra, devops |
| `watercolor` | `watercolour`, `wash`, `aquarelle` | material | Transparent washes that multiply, ink line laid last | Narrative, community, onboarding |
| `whiteboard-marker` | `whiteboard`, `napkin`, `dry-erase` | material | Fat marker strokes at 88% — thinking out loud | Brainstorms, incident timelines |
| `wood-grain` | `wood`, `timber`, `pyrography` | material | Wandering grain, travelling varnish, burned labels | Craft tools, publishing, hobby hardware |
| `y2k-retrofuturist` | `y2k`, `retrofuture`, `chrome` | era | Chrome gradients, wide tracking, optimistic tech | Nostalgic, playful, media |

## Two dials that cut across the catalog

Several styles are the same recipe at different settings. Knowing which dial you are
on is faster than comparing six specs.

**Roughness** — the hand-drawn family is one `feDisplacementMap` scale:

| Scale | Style | Reads as |
| --- | --- | --- |
| `0.7` | `patent-drawing` | Ruled — inked with instruments |
| `1.6` | `draughtsman-notebook` | Precise but human |
| `2.0` | `codex-leonardo` | An investigation in progress |
| `2.2` + `2.6` doubled | `rough-sketch` | A collaborative diagram |
| `2.4` | `lofi-wireframe` | Deliberately unfinished |
| `4.5` | `whiteboard-marker` | Improvised |

Below `1` reads as ruled, `2`–`3` as sketched, above `4` as improvised. If a request
lands between two of these, move the scale rather than inventing a seventh style.

**Grain ratio** — the material family shares `feTurbulence` and differs only in the
x:y `baseFrequency` ratio. Equal is isotropic; extreme is directional.

| baseFrequency | Style | Effect |
| --- | --- | --- |
| `1.6 0.006` | `brushed-metal` | Grain across; highlights smear along it |
| `0.006 0.055` | `wood-grain` | Long wandering grain with figure |
| `0.045 0.09` | `oil-impasto` | Raised paint with directional relief |
| `0.62 0.62` | `oil-impasto` (canvas) | Even bidirectional tooth |
| `0.5` | `watercolor` (paper) | Fine cold-press texture |
| `1.3` | `pencil-lined-paper` | Pencil deposit |

Ratio is the dial; everything else is colour.

## Nearest neighbours

Five clusters produce almost every mis-selection. Read the distinction before
choosing, not after.

**The four drafting idioms.** `blueprint` is a *medium* — cyanotype ground, white
lines, dimension arrows, a title block. `schematic` is a *notation* — light ground, a
consistent symbol alphabet, net labels instead of drawn connections, no perspective
or shading. `patent-drawing` is a *convention* — black on white, uniform stroke,
numbered reference characters, and a real external standard behind it.
`draughtsman-notebook` is a *hand* — the same rigour, drawn by a person on their own
paper. Drawn → blueprint. Specified → schematic. Claimed → patent-drawing.
Reasoned-through → draughtsman-notebook.

**`terminal-minimalist` vs `ide-dark`.** A TUI versus the GUI around it. Radius `0`,
mono everywhere, a character grid, stepped redraws → terminal. Rounded panes, a
sidebar, mixed proportional and mono type, eased motion → ide-dark.

**`rough-sketch` vs `whiteboard-marker`.** Both hand-drawn, opposite registers.
Finished and agreed, thin doubled strokes, hachure fills → rough-sketch. In progress,
fat round marker at 88% opacity → whiteboard-marker.

**`console-elbow` vs `hud`.** Both instrument idioms. A panel you *operate* — blocks
of flat colour, zoning, chrome around the content → console-elbow. An overlay on
something being *watched* — brackets, ticks, reticles on a dark field → hud.

**`watercolor` vs `oil-impasto`.** Transparent, multiplying, paper showing through,
nothing raised → watercolor. Opaque, lit, relief following the strokes → oil-impasto.

**`skeuomorphic` vs `brushed-metal`.** A whole object — bezel, sheen, lamp, cable →
skeuomorphic. One material applied flat across the board → brushed-metal.

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

Persist the full nine-field spec under `## Style` in `.prettydocs/prettydocs.md`.
In a repo with a single doc root, also record the bare slug in
`.github/docsmeta.json` as `viz.style`; **omit that key when the repo has more than
one doc root**, since it is repo-wide and would then name the wrong style for every
root but one. **The spec in `DESIGN.md` is what visuals derive
from** — and because it lives in that file, changing the style moves `design_hash`
and re-authors every visual in the repo. Say so in the phase-3 plan, with a count,
before touching anything.

## Three things a style may not fix

Some idioms carry a cost the catalog cannot design away. Say so when you pick one;
never discover it at review.

**Fonts are never fetched.** Every hand-drawn and painted style names a display face
(Caveat, Virgil, Balsamiq Sans, Architects Daughter, Gabriola, Rockwell) with a
system fallback chain. A remote `@import` or font `href` is a hard gate failure, so on
GitHub the chain usually resolves to Segoe Print, Bradley Hand or Comic Sans MS —
degraded but still in character. Promise the *class* of face, not the exemplar's.
Subsetting and embedding as base64 is the fix where fidelity actually matters.

**Some styles are decorative, and the contrast floor does not move for them.**
`watercolor`, `oil-impasto` and `lofi-wireframe` fail 4.5:1 on their native palettes.
Their specs do **not** relax contrast; instead each names the move that earns the
labels back — a reserved-paper plate, a far darker ink, or drawing the low-contrast
element as a shape rather than as `<text>`. Choose them where the labels carry no
load and the alt text does the work. If a diagram's meaning lives in its labels, pick
a different style.

**Doubled type must be hidden from screen readers.** `brushed-metal`, `wood-grain`
and `skeuomorphic` engrave and burn by drawing the same string twice. The underlying
copy is a highlight, not a word: it takes `aria-hidden="true"`, or every label is
announced twice. `codex-leonardo`'s mirrored marginalia has the same problem in
reverse — it is normal text in the DOM and is read aloud unmirrored, so it stays
decorative and out of the meaning path.

**Three styles reproduce a visual language, not a protected work.** `console-elbow`,
`holographic-projection` and `digital-rain` carry geometry, palette, type class and
motion behaviour, and deliberately no logos, insignia, wordmarks, vessel or
organisation names, characters, fictional alphabets, or specific objects from any
source work. Design styles are not copyrightable; specific expressions and trademarks
are. **Decline to add a mark on request** rather than treating it as a customisation
option.

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

## The fidelity floor

Every gate above is a **ceiling** (max filter depth, max radius, max bytes) or a
**legibility floor** (font size, contrast, stroke width). None of them asks whether a
visual looks like the style it claims. That gap was real: the contact sheet once
rendered `oil-impasto` as flat gradients and `wood-grain` with no displacement at all,
and passed with zero errors.

So each style also declares a minimum, in the same `scripts/styles.json` entry:

| Key | Meaning |
| --- | --- |
| `require_filter_all` | Every named primitive must be present. `require_filter` (now `require_filter_any`) is a *menu* satisfied by one entry — right for "blur or drop-shadow", wrong for a material built from a specific chain, where one bare `feTurbulence` used to satisfy `wood-grain`. |
| `min_filter_depth` | The deepest chain in the file must reach this. The mirror of the `filter_depth` ceiling, and the gate that actually kills a single-primitive imitation. |
| `min_elements` | Minimum drawn geometry. **Binds only on specimens** — a root carrying `data-specimen="true"`. A README flow diagram with four boxes is correct at 23 elements, and padding it to hit a density number would be worse output. |

The filter gates apply to **every** visual: if a repo's diagram claims `wood-grain`,
it has to actually have wood grain. Only the density floor is specimen-scoped.

`svg_check.py` also reports what a file *achieved* — deepest chain, filter count,
drawn elements, primitives used — because silent success is how a flat render ships.
A `NOTE` reading `fidelity: deepest chain 1, 5 filter(s), 299 drawn elements` is the
tell, and it is now impossible to miss in a run report.

Each style's specimen lives at `docs/samples/<slug>.svg`, is gated under its own
`--style`, and is embedded at the top of that style's spec file. The contact sheet
composes those same specimens rather than redrawing them, so it cannot be less
faithful than the catalog it indexes.

## Gate softening

Twenty-one of the thirty-one styles relax something; the other ten run entirely on
the defaults. Almost every relaxation is filter depth, because texture and material
are what cost primitives.

**Filter depth** — the default is `1` chained primitive per `<filter>`. The gate
counts primitives inside a single `<filter>` element, not filters on the board, so a
shape drawn twice through two one-primitive filters is still depth 1.

| Floor | Styles | What the chain is |
| --- | --- | --- |
| **2** | `claymorphism`, `codex-leonardo`, `digital-rain`, `holographic-projection`, `hud`, `ide-dark`, `lofi-wireframe`, `neumorphism`, `patent-drawing`, `rough-sketch`, `whiteboard-marker`, `y2k-retrofuturist` | A roughen chain (turbulence → displacement), a glow (blur → merge), or a shadow pair |
| **3** | `brushed-metal`, `draughtsman-notebook`, `pencil-lined-paper`, `skeuomorphic`, `watercolor`, `wood-grain` | A grain chain (turbulence → desaturate → alpha), or a wash (turbulence → displace → blur) |
| **5** | `oil-impasto` | Turbulence → displacement → lighting → composite → blend, all off one noise node |

**Everything else:**

| Style | Gate | Default → floor |
| --- | --- | --- |
| `neumorphism` | text contrast | 4.5:1 → **3.0:1** |
| `neumorphism` | UI/graphic contrast | 3.0:1 → **2.0:1** |
| `maximalist` | byte cap | 150 KB → **250 KB** |
| `glassmorphism` | byte cap | 150 KB → **200 KB** |

`neumorphism` is the **only** style in the catalog that relaxes contrast, and it does
so because its shapes are literally defined by near-background shadows. No other
style gets that, including the three decorative ones — see *Three things a style may
not fix* above.

Relaxing **nothing at all**: `bento-grid`, `blueprint`, `console-elbow`, `editorial`,
`flat-material`, `isometric-3d`, `neo-brutalist`, `schematic`, `swiss-minimal`,
`terminal-minimalist`.

The machine-readable half of these tables is `scripts/styles.json`, which
`svg_check.py` and `audit_visuals.py` both read. The two must agree; a slug in one
and not the other is a bug.

When a value falls between the default and the floor, the checker prints one
`SOFTENED` line — not a silent pass. Below the floor it's a plain `ERROR`. Every
softened gate is recorded in the visual's `viz.json` as `"relaxed":
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
