# more-pretty-docs — visual design system

One frozen system; all repo visuals derive from it. Facts come from the repo
(SKILL.md, reference/, scripts/), never invented. Frozen for this run.

## Story extraction

Audience:     developers who want their repo docs generated, truthful, and designed
Value:        writes standard project docs and authors their key diagrams as seamless-loop animated SVG, with nothing to install
Proof:        every visual in this skill's own README was authored and gated by the skill itself
First action: copy the folder into `.claude/skills/` and run `/more-pretty-docs`
Theme:        the artefact that reports its own state — a board of cells, each holding one checked fact

## Frozen system

No product brand tokens exist for this skill, so the palette below was filled from a
style's palette treatment when the system was first derived. **It does not change
when the style changes.** Style owns form; the palette is the product's, even when
the product had nothing to say and a style had to speak for it (`styles.md` →
precedence). The cyanotype hexes are therefore unchanged under `bento-grid`, and the
result is a dark board rather than the light one bento is usually seen in.

### Palette

| Role | Hex | Notes |
| --- | --- | --- |
| background       | `#12324f` | board ground |
| surface          | `#17405f` | cell fill |
| ink              | `#e8f2fb` | primary text and values |
| dim              | `#9fc4e8` | cell hairlines and labels |
| accent-primary   | `#e0a33e` | the one focal cell per board |
| warn             | `#e2725b` | rust; stale and failed states only |

### Typography

| Role | Stack |
| --- | --- |
| display | `-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif` |
| body    | same as display |
| mono    | `ui-monospace, SFMono-Regular, Menlo, monospace` |

System stacks only — never a remote font, which an SVG cannot fetch on GitHub. Cell
labels use the display stack at `600`; a cell's one value uses `700`, or the mono
stack when the value is a literal (a filename, a hash, a command).

### Shape language

Radius `16` on every cell, identical. **One gutter value: `20`.** Six columns on the
1200 canvas with `40` outer margins: `x = 40 + col × 190`, cell width
`span × 170 + (span − 1) × 20`. Spans of 1, 2 and 3 only — the unequal spans are the
composition. Cells carry a `1`-unit `dim` hairline and no shadow.

### Motif

The **verdict cell**: every board carries exactly one cell that reports the state of
the thing the board describes — `0 errors`, `all match`, `14 / 14`. Live motion is
confined to a single status pulse that visits one cell at a time, and to that verdict
cell's own fill; the cells themselves never move. Derived from what the product does
(nothing ships until the bundled checker reports zero errors), so it survives a change
of style.

### Composition rules

One tight grid per board, no leftover slivers. Each cell does exactly one job: one
label, at most one value. A cell that needs three lines of body text is two cells.
Important content clear of the edges; legible at rendered width (1200 units in an
820 px embed).

### Motion rules

- Seamless ambient loops, `data-loop-s="12"` on every animated board; every animation
  duration divides 12 exactly.
- **The grid never moves.** Motion is confined to the verdict cell and to a staggered
  status pulse that runs one cell at a time, phase-shifted with negative delays.
- Ease `ease-in-out` for a state change, `linear` for a bar filling. Calm.
- No strobing, no flicker, no idle bobbing. Motion communicates flow or a state change.
- Every animated visual carries a `prefers-reduced-motion` block that stops all motion
  and leaves a legible still.

## Style

| Field | Value |
| --- | --- |
| Slug | `bento-grid` |
| Source | catalog (`--style bento-grid`) |
| Primary axis | composition — the grid decides everything else |

- **Intent** — unequal cells in one tight grid, each holding one fact; the right call
  for a board that must carry five or six unrelated facts at once.
- **Palette treatment** — quiet ground, cells in `surface`, exactly **one** cell
  promoted to an `accent-primary` fill as the focal point. Semantic colour inside a
  cell (a status dot) is fine; a second accent-filled cell is not.
- **Shape language** — radius `16` on every cell, one `20` gutter, spans of 1–3 on the
  six-column grid above.
- **Material / depth** — a `1`-unit hairline in `dim`. No shadow, no gradient. One
  device for every cell, never both.
- **Type treatment** — two steps per cell: a `23` label at `600` and one `44+` value at
  `700`. Sentence case for labels; a literal value takes the mono stack.
- **Motion character** — the grid is static. One cell moves at a time: a status dot
  pulsing, a bar filling. Stagger with negative delays so at most one cell reads as
  live at any moment.
- **SVG recipes** — `reference/styles/bento-grid.md`: the six-column arithmetic, the
  focal cell, the staggered per-cell pulse.
- **Relaxations** — none. `bento-grid` runs on every default gate; the hairline the
  UI-contrast gate is checking for is exactly what makes a cell visible.
- **Never** — varying gutters or radius, a second accent-filled cell, a cell with three
  lines of body text, cells off the grid, every cell animating at once, or a grid so
  uniform it may as well be a table.

### Catalog swatches

`docs/assets/styles.svg` is a contact sheet whose subject *is* the style catalog, so
each tile has to show its own style's palette character — those colours are the
content, not the chrome. They are declared here as named roles so nothing enters a
visual as an untraceable hex, and they are scoped to that one asset. No other visual
in this repo uses them.

The sheet is also the one asset in this repo gated **without** `--style`. Every
structural, seam, legibility, contrast, palette and byte gate still applies to it;
only the `bento-grid` *form* invariants are lifted, because a plate showing
skeuomorphic bevels and neo-brutalist zero-radius blocks cannot honour one radius and
one material. Its own frame, gutters and labels are still bento. This exemption covers
exactly one file and is stated in the run report.

**Because it is gated without `--style`, the sheet gets no per-style relaxations
either** — the global `filter_depth: 1` applies to every tile, including the ones
whose catalog entries declare floors of 3 or 5. That is the constraint, not a
loophole, and two conventions satisfy it:

- **Grain is turbulence read through a `<mask>`.** One `<filter>` holds a single
  `feTurbulence`; a rect carrying that filter sits inside a `<mask>`, and a flat
  palette colour is drawn through it. Depth 1, monochrome, any hue, and the
  anisotropy still comes free from the `baseFrequency` ratio — `#nmetal` at
  `1.6 0.006`, `#nwood` at `0.006 0.055`, `#ntooth` at `0.55`.
- **Hand-drawn tiles are wobbled by hand, not by a filter.** A roughen chain is
  turbulence *plus* displacement, which is two primitives. At 264×152 the tile's
  path coordinates are simply drawn off-true instead.

Depth-3-and-up looks — impasto relief, a chained bevel — are *suggested* with
gradients and offset geometry, exactly as this sheet has always suggested
skeuomorphic with `url(#skeu)`. A tile shows a style's character at cell scale; it is
not a reproduction of what that style produces on a full board.

The sheet's height is the other stated exception. At 31 tiles it runs
**1200 × 2816**, well past the 320–760 range in `viz-production.md`. Three columns is
forced by the longest slug: `.slug` carries no `data-role`, so it sits on the 18 px
label floor, and `holographic-projection` needs about 237 user units at that size
against the 217 a four-column cell would give it.

**Eight accepted graphic-contrast warnings, and why each one stays.** The sheet gates
at **0 errors**. It also prints eight `WARN`s of the form *"graphic contrast N:1 on
&lt;shape&gt; stroke is under 3:1 — fine for decoration, not for a load-bearing
border"*, and the warning is correct in every case: these are the tiles whose subject
*is* a deliberately faint mark. Raising them would misrepresent the style, so they
stay, enumerated here rather than left for a reader to rediscover.

| Warn | Where | Why it is right |
| --- | --- | --- |
| 1.48:1 | the `#hatch` pattern line in `<defs>` | Measured against the root background because it lives in `defs`; on the vellum it actually paints, `sw-irongall` on `sw-vellum` is **6.30:1** |
| 1.55:1 | ide-dark pane divider | `#30363d` on `#0d1117` is the real hairline of a dark editor; a visible border is the wrong picture |
| 2.62:1 ×3 | lofi-wireframe ghost paths | Placeholder squiggles and the image X. The spec requires these be *shapes*, never `<text>`, precisely so their faintness carries no meaning |
| 1.91:1 | pencil-lined-paper margin rule | A legal pad's margin line is a pale red print, not an outline |
| 2.53:1 ×2 | wood-grain grain lines | Grain is a figure in the timber; at 3:1 it reads as drawn-on stripes |

No text anywhere on the sheet is below 4.5:1 — every tile that carries a label was
recoloured until it cleared the floor, including the wood-grain burn, which sits on a
sanded `sw-timbersand` field for exactly that reason.

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
| sw-steel        | `#7e888f` | brushed-metal ground |
| sw-steelface    | `#c3cbd2` | brushed-metal plate face |
| sw-steeldark    | `#3c4349` | engraved cut, plate edge |
| sw-vellum       | `#e5d8b8` | codex aged rag |
| sw-irongall     | `#5a4632` | codex ink |
| sw-conorange    | `#ff9c00` | console-elbow frame |
| sw-conrose      | `#cc6666` | console-elbow block |
| sw-conperi      | `#9999ff` | console-elbow block |
| sw-rain         | `#00ff41` | digital-rain phosphor |
| sw-rainhead     | `#9cffb0` | digital-rain head glyph |
| sw-graphite     | `#3a414d` | draughtsman and pencil lead |
| sw-void         | `#01070c` | holographic and hud ground |
| sw-holo         | `#4fd8ff` | holographic body |
| sw-holoedge     | `#bef3ff` | holographic bright edge |
| sw-hudcyan      | `#00e5ff` | hud instrument hue |
| sw-idepane      | `#161b22` | ide-dark pane surface |
| sw-idediv       | `#30363d` | ide-dark hairline divider |
| sw-idblue       | `#58a6ff` | ide-dark identifier — 6.85:1 on the pane, where `sw-blue2` is only 3.73:1 |
| sw-isotop       | `#6f67d6` | isometric top face |
| sw-isolft       | `#5b54b0` | isometric left face |
| sw-isorgt       | `#474189` | isometric right face |
| sw-wiregrey     | `#4a4a4a` | lofi-wireframe line work |
| sw-wireghost    | `#9a9a9a` | lofi-wireframe placeholder — shapes only, never text |
| sw-oilground    | `#1e1810` | oil-impasto ground |
| sw-oilblue      | `#2f4b8f` | oil-impasto pigment |
| sw-ruled        | `#afc6db` | lined-paper printed rules |
| sw-margin       | `#e3a6a6` | lined-paper margin line |
| sw-roughblue    | `#1971c2` | rough-sketch stroke |
| sw-roughfill    | `#a5d8ff` | rough-sketch hachure |
| sw-wcblue       | `#5a6ba8` | watercolour wash |
| sw-wcrose       | `#c4738c` | watercolour wash |
| sw-wcochre      | `#d2a24c` | watercolour wash |
| sw-timber       | `#8a5c31` | wood-grain ground |
| sw-timberlt     | `#a97438` | wood-grain figure |
| sw-timberdk     | `#3b2410` | wood-grain burn |
| sw-timbersand   | `#c9a678` | wood-grain sanded label field — `#3b2410` on it is 6.37:1, on raw timber only 2.53:1 |

## Visual inventory

| Asset | Doc | Depicts | Tier | Source facts |
| --- | --- | --- | --- | --- |
| hero | README.md | a hand-authored SVG passes the bundled checker and is committed as-is — no render step in the path | animated-hero | SKILL.md preflight + phase 6; reference/viz-production.md; scripts/svg_check.py |
| lazy-rerender | README.md | the facts/src/design hash triad decides RE-RENDER vs REUSE; a prose edit re-authors nothing | animated-flagship | reference/embedding.md → Lazy re-render decision |
| styles | README.md | the 31 catalog styles in alphabetical order, each rendered in its own idiom | animated-flagship | reference/styles.md; reference/styles/*.md; scripts/styles.json |
