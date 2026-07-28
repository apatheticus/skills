# pretty-plain-docs — visual design system

One frozen system; all repo visuals derive from it. Facts come from the repo
(SKILL.md, reference/, scripts/), never invented. Frozen for this run.

## Story extraction

Audience:     developers who want their repo docs generated, truthful, designed, and still
Value:        writes standard project docs and authors their key diagrams as static SVG, with nothing to install and nothing that moves
Proof:        every visual in this skill's own README was authored and gated by the skill itself
First action: copy the folder into `.claude/skills/` and run `/pretty-plain-docs`
Theme:        the specification sheet — a typed graph whose routing and verdicts are drawn, not performed

## Frozen system

No product brand tokens exist for this skill, so the palette below was filled from the
resolved style's palette treatment when the system was first derived. **It does not
change when the style changes.** Style owns form; the palette is the product's, even
when the product had nothing to say and a style had to speak for it (`styles.md` →
precedence). `schematic` asks for a light ground and near-black line work with colour
carried only by signal class, and the result is a printed spec sheet rather than the
dark board the sibling skills use.

### Palette

| Role | Hex | Notes |
| --- | --- | --- |
| background       | `#f7f7f5` | sheet ground, faint warm gray |
| surface          | `#ffffff` | inside a symbol outline, and net-label backing boxes |
| ink              | `#14181d` | every line, symbol outline, and identifier |
| dim              | `#5a616b` | sheet grid, annotations, metadata |
| accent-primary   | `#1a5fd0` | the `data` signal class |
| accent-control   | `#6639ba` | the `control` signal class |
| warn             | `#cf222e` | the `error` signal class; stale and failed states only |

Three signal classes and no more. Colour here is **typed**, never decorative: a hue
identifies what travels along a connection, so a node outline is never coloured and a
label is never tinted for emphasis.

Every one of the five foreground roles clears **4.5:1 against both grounds** — `dim` at
5.83:1 on the sheet, `accent-primary` at 5.45:1, `warn` at 4.99:1, `accent-control` at
6.85:1, `ink` at 16.62:1. That is deliberate rather than incidental: `schematic`
declares no relaxations, so a palette needing one would have to be fixed here instead.
The first `accent-primary` candidate, `#1f6feb`, measured 4.32:1 on the sheet ground and
was darkened until it passed on the ground as well as inside a `surface` box.

### Typography

| Role | Stack |
| --- | --- |
| display | `-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif` |
| body    | same as display |
| mono    | `ui-monospace, SFMono-Regular, Menlo, monospace` |

System stacks only — never a remote font, which an SVG cannot fetch on GitHub. Every
identifier is mono, because part designators, file names, net names and commands are
literal strings. The sheet title and any prose annotation take the display stack.
Uppercase designators at `19`–`20`; annotations at `18`.

### Shape language

Radius `0` everywhere. **Orthogonal routing only** — every connection runs horizontal
or vertical with `90°` corners, never a diagonal or a curve. Stroke `1.5` for
connections, `2` for symbol outlines; nothing thinner, which is also the style's
`min_stroke_width` gate. Junctions carry a filled `4`-unit dot; crossings without a
junction simply cross unmarked, held consistently.

Symbol alphabet, defined once and reused via `<defs>` + `<use>`. One shape per node
kind, never a shape reused for two kinds:

| Kind | Symbol |
| --- | --- |
| Process / transform | rectangle |
| Store / persistence | rectangle with a doubled left edge |
| External boundary | rectangle with a clipped top-right corner |
| Decision / branch | diamond |
| Terminal / IO | rectangle with rounded ends *(the one radius exception)* |

### Motif

The **verdict box**: every board carries exactly one terminal symbol that reports the
state of the thing the board describes — `0 errors`, `loop_s 0`, `re-render: none`.
Derived from what the product does (nothing ships until the bundled checker reports
zero errors), so it survives a change of style. In a static skill it also does the job
motion does elsewhere: it is the one element the eye is meant to land on last.

### Composition rules

One graph per board, read left to right, with the flow direction stated by arrowheads
rather than implied by position. Every net that carries meaning is labelled, and every
label that sits on a wire gets a `surface`-filled backing box. **Ordering is numbered
where a reader could get it wrong** — a still cannot demonstrate sequence, so it has
to assert it. Important content clear of the edges; legible at rendered width (1200
units in an 820 px embed).

### Stillness rules

- **`data-loop-s="0"` on every root `<svg>`.** It is the static marker shared with the
  sibling skills, and the only value this skill's checker accepts.
- **Nothing animates.** No `@keyframes`, no `animation:` declaration, no SMIL tag. The
  checker treats any of them as a structural error, not a style deviation.
- **No element exists only to be moved.** A marker parked at a start position, or an
  empty channel where a pulse would travel, is a composition authored for the wrong
  skill. Every drawn element must read at rest.
- **`schematic` has no material to fake**, which suits a still: depth here would mean
  `feGaussianBlur`, `feDropShadow` or a gradient element — all four *forbidden* by the
  style — so fidelity is carried entirely by draughtsmanship and drawn density.
- **Every structural visual carries its Mermaid source** in a collapsed `<details>`
  block after the closing marker. With no motion to hold surplus meaning, the graph the
  SVG draws and the graph Mermaid encodes are the same graph, and they must agree.

## Style

| Field | Value |
| --- | --- |
| Slug | `schematic` |
| Source | catalog (`--style schematic`) |
| Primary axis | composition — the notation decides everything else |

- **Intent** — a specification diagram: a consistent symbol alphabet, orthogonal
  routing, net labels where a drawn wire would clutter, and no shading anywhere. The
  right call for something whose structure is genuinely a graph with typed nodes,
  which is what a doc pipeline and a hash triad both are.
- **Palette treatment** — light ground, near-black line work, colour applied only to
  connections and their net labels by signal class. Node outlines stay uncoloured.
- **Shape language** — radius `0`, orthogonal routing, `1.5`/`2` strokes, filled
  junction dots; the symbol table above.
- **Material / depth** — none, absolutely. No shadow, no gradient, no fill beyond flat
  `surface` inside a symbol. A schematic has no light source because it depicts
  topology, not objects.
- **Type treatment** — mono for every identifier, display sans for the sheet title and
  annotations, uppercase designators at `19`–`20`.
- **SVG recipes** — `reference/styles/schematic.md`: the reused symbol, orthogonal
  routing, and the signal-class net.
- **Relaxations** — none. `schematic` runs on every default gate, which is why it was
  chosen for this skill's own visuals: a pass here proves the base gates rather than a
  softened set. Near-black on white is also the highest-contrast pairing available.
- **Never** — diagonal or curved connections, two node kinds sharing a symbol, shading
  or gradients, a net label on a line without its backing box, an unarrowed net whose
  direction a reader has to guess, or colour used decoratively instead of by signal
  class.

### Catalog swatches

`docs/assets/styles.svg` is a contact sheet whose subject *is* the style catalog, so
each tile has to show its own style's palette character — those colours are the
content, not the chrome. It is gated as the declared `catalog-sheet` style, with its
own entry in `scripts/styles.json`: `filter_depth: 5`, `bytes_fail: 300 KB`,
`min_elements: 620`. The declaration lives in the catalog where the checker reads it,
not in a paragraph here.

Two things follow from that:

- **Each tile is the style's own specimen, scaled.** `docs/samples/<slug>.svg` is built
  and gated at 1200 × 460 under `--style <slug>`, then composed into a 550 × 211 cell.
  The sheet therefore cannot be less faithful than the catalog it indexes, and it
  cannot drift from it either.
- **Filters carry `data-style="<slug>"`.** Each tile's chain is measured against the
  floor of the style it depicts rather than the file-wide ceiling, which is what lets
  `oil-impasto` keep its five-primitive lit relief on a sheet that also holds
  `swiss-minimal`.

Token names are namespaced per specimen (`--oil-impasto-ground`). `var()` inside a
`<defs>` filter resolves against the `<defs>` element, not the tile referencing it, so
32 sets of `--ground` and `--ink` on one root would collide. Each tile group also
carries `isolation: isolate`, or a specimen's `mix-blend-mode` overlay composites
against the whole sheet, and its own `data-bg`, or its captions are measured for
contrast against the sheet's dark background instead of the surface they sit on.

The sheet's height is the one stated exception: two columns of 16 rows runs
**1200 × 4458**, well past the 320–760 range in `viz-production.md`. That is the cost
of showing every idiom at a scale where its material is still visible, and the sheet is
an index meant to be scrolled.

**The sheet is the catalog converted, not redrawn.** Each tile is the same specimen the
sibling skill ships, with its motion folded away per `viz-production.md` → The
animation ban: the reduced-motion resting values moved onto the base rules, the
keyframes and reduce blocks deleted, `data-loop-s` flipped to `0`. Geometry, filter
chains, palettes and type are untouched, and the sheet gates to **the same verdict as
the animated original** — 0 errors, 27 warnings, 34 softened — which is the evidence
that nothing about a style's fidelity depended on it moving.

**Accepted graphic-contrast warnings.** The sheet gates at **0 errors**, and prints
`WARN`s of the form *"graphic contrast N:1 on &lt;shape&gt; stroke … is under 3:1 —
fine for decoration, not for a load-bearing border"*. Identical warnings are aggregated
with an `(xN)` count, so a hairline grid applied thirty-one times reads as one finding
rather than thirty-one.

Every one of them is correct, and every one is a mark whose subject *is* faintness: the
HUD's `#0b2a38` grid on `#04121a`, a dark editor's pane hairline, the pencil pad's pale
red margin rule, wood grain figured into the timber, a skeuomorphic bevel highlight.
Raising any of them to 3:1 would misrepresent the style. None is a border anything
depends on.

Two floors are **not** softened anywhere on the sheet:

- **No text is below 4.5:1.** Every specimen that carries a label clears the floor —
  `wood-grain` reverses to `#F4ECE0` on the plank (4.90:1), `oil-impasto` drops its
  ochre body a step, `isometric-3d` carries a dedicated on-face ink.
- **The one exemption is WCAG 1.4.3's**, for purely decorative text. `digital-rain`'s
  falling glyphs are texture, not reading matter; they are marked `aria-hidden="true"`,
  and the checker reports how many it exempted so the exemption cannot be used quietly
  to launder an unreadable label.

The sheet draws entirely from the per-specimen namespaced palettes above; the roles in
the Palette table govern `hero.svg` and `lazy-rerender.svg`.
