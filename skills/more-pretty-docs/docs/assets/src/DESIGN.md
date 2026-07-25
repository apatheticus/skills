# more-pretty-docs — visual design system

One frozen system; all repo visuals derive from it. Facts come from the repo
(SKILL.md, reference/, scripts/), never invented. Frozen for this run.

## Story extraction

Audience:     developers who want their repo docs generated, truthful, and designed
Value:        writes standard project docs and authors their key diagrams as seamless-loop animated SVG, with nothing to install
Proof:        every visual in this skill's own README was authored and gated by the skill itself
First action: copy the folder into `.claude/skills/` and run `/more-pretty-docs`
Theme:        the drafted specification — a diagram that states its own tolerances and is checked against them

## Frozen system

No product brand tokens exist for this skill, so the resolved style's palette
treatment fills the gap (`styles.md` → "style owns form; the product's brand tokens
own the palette"). The cyanotype ground below comes from the `blueprint` entry.

### Palette

| Role | Hex | Notes |
| --- | --- | --- |
| background       | `#12324f` | cyanotype ground |
| surface          | `#17405f` | panel tint, title block |
| ink              | `#e8f2fb` | white line work and primary text |
| dim              | `#9fc4e8` | grid, dimension lines, mono annotation |
| accent-primary   | `#e0a33e` | the one warm callout per board |
| warn             | `#e2725b` | rust; stale and failed states only |

### Typography

| Role | Stack |
| --- | --- |
| display | `-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif` |
| body    | same as display |
| mono    | `ui-monospace, SFMono-Regular, Menlo, monospace` |

System stacks only — never a remote font, which an SVG cannot fetch on GitHub.
Dimensions, hashes, slugs and part labels are always mono; sheet titles use the
display stack, uppercase at `+1` tracking.

### Shape language

Radius `0` everywhere (the `blueprint` invariant, enforced as `max_rx: 0`). Three
line weights: `1.6` primary geometry, `0.8` dimension and leader lines, `0.8` dashed
for planned or simulated edges. `1200`-unit-wide canvas, `48+` unit edge margins.

### Motif

The **drafted sheet**: a faint 24-unit grid, white line work over it, leader lines to
mono labels, and a title block in the lower-right corner naming the sheet. Repeated
lightly — grid and title block on every board, never wallpaper.

### Composition rules

Compact-technical register, drafted. One strong composition per visual, reading
left-to-right. Labels sit at the end of leader lines, never on top of geometry.
Important content clear of the edges; legible at rendered width (1200 units in an
820 px embed).

### Motion rules

- Seamless ambient loops, `data-loop-s="12"` on every animated board; every animation
  duration divides 12 exactly.
- A drawing being made: `stroke-dashoffset` extension, then a hold. `linear` for
  continuous travel, `ease-in-out` for a state change. Calm and mechanical.
- No strobing, no flicker, no idle bobbing. Motion communicates flow or a state change.
- Every animated visual carries a `prefers-reduced-motion` block that stops all motion
  and leaves a legible still.

## Style

| Field | Value |
| --- | --- |
| Slug | `blueprint` |
| Source | derived (no brand tokens; docs/spec register) |
| Primary axis | material — the medium is a cyanotype print |

- **Intent** — a drafted specification: white line work on cyanotype, annotated.
- **Palette treatment** — deep blue ground; line work in `ink` at full and `dim` at
  low opacity; exactly one `accent-primary` callout per board.
- **Shape language** — radius `0`; three line weights (`1.6` / `0.8` / `0.8` dashed).
- **Material / depth** — ink on paper. No shadow, gradient, or blur; line weight
  carries depth.
- **Type treatment** — uppercase display at `+1` tracking for titles, mono for
  dimensions, slugs and annotation.
- **Motion character** — geometry draws itself and holds; dimension arrows arrive
  after what they measure; the grid never moves.
- **SVG recipes** — `reference/styles/blueprint.md`: the grid `<pattern>`, the
  `auto-start-reverse` arrow marker, the `stroke-dashoffset` draw cycle.
- **Relaxations** — none. `blueprint` runs on every default gate.
- **Never** — filled colour at full opacity, shadows, gradients, rounded corners,
  labels over geometry, a date or version in the title block.

### Catalog swatches

`docs/assets/styles.svg` is a contact sheet whose subject *is* the style catalog, so
each tile has to show its own style's palette character — those colours are the
content, not the chrome. They are declared here as named roles so nothing enters a
visual as an untraceable hex, and they are scoped to that one asset. No other visual
in this repo uses them.

The sheet is also the one asset in this repo gated **without** `--style`. Every
structural, seam, legibility, contrast, palette and byte gate still applies to it;
only the `blueprint` *form* invariants are lifted, because a plate showing
claymorphism and glassmorphism cannot simultaneously honour `max_rx: 0` and a
gradient ban. Its frame, labels and title block are still blueprint. This exemption
covers exactly one file and is stated in the run report.

| Role | Hex | Notes |
| --- | --- | --- |
| sw-paper       | `#f4f1ea` | swiss-minimal ground |
| sw-inkdark      | `#14181d` | dark line work on light tiles |
| sw-red          | `#d6452b` | swiss-minimal accent |
| sw-blue         | `#1e88e5` | flat-material primary |
| sw-white        | `#ffffff` | cards, glass, highlights |
| sw-metal        | `#4a4f57` | skeuomorphic panel face |
| sw-amber        | `#f0b429` | skeuomorphic LED |
| sw-soft         | `#e8ecf2` | neumorphism surface |
| sw-softshade    | `#b9c2ce` | neumorphism shadow |
| sw-lilac        | `#c9b8ff` | claymorphism volume |
| sw-pink         | `#ff9ec4` | claymorphism accent |
| sw-violet       | `#7c3aed` | glassmorphism ground blob |
| sw-cyan         | `#0ea5e9` | glassmorphism ground blob |
| sw-yellow       | `#ffd400` | neo-brutalist field |
| sw-black        | `#000000` | neo-brutalist rules and offsets |
| sw-orange       | `#ff4d3d` | neo-brutalist field |
| sw-cream        | `#fbf9f4` | editorial paper |
| sw-rust         | `#8c2f1f` | editorial rule |
| sw-magenta      | `#ff2e88` | maximalist |
| sw-teal         | `#00e5c0` | maximalist |
| sw-indigoviolet | `#5b3df5` | maximalist band |
| sw-silver       | `#8fa6c4` | y2k chrome mid-tone |
| sw-hotpink      | `#ff3fb4` | y2k accent |
| sw-termbg       | `#0d1117` | terminal ground |
| sw-termgreen    | `#3fb950` | terminal success |
| sw-offwhite     | `#f7f7f5` | schematic ground |
| sw-blue2        | `#1f6feb` | schematic data class |
| sw-lightgray    | `#f4f5f7` | bento ground |
| sw-indigo       | `#3b5bdb` | bento focal cell |

## Visual inventory

| Asset | Doc | Depicts | Tier | Source facts |
| --- | --- | --- | --- | --- |
| hero | README.md | a hand-authored SVG passes the bundled checker and is committed as-is — no render step in the path | animated-hero | SKILL.md preflight + phase 6; reference/viz-production.md; scripts/svg_check.py |
| lazy-rerender | README.md | the facts/src/design hash triad decides RE-RENDER vs REUSE; a prose edit re-authors nothing | animated-flagship | reference/embedding.md → Lazy re-render decision |
| styles | README.md | the 14 catalog styles, each rendered in its own idiom | animated-flagship | reference/styles.md; reference/styles/*.md; scripts/styles.json |
