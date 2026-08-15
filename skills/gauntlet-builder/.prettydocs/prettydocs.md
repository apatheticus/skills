# gauntlet-builder — visual design system

One frozen system; all project visuals derive from it. Facts come from the repo
(SKILL.md, reference/, assets/, scripts/), never invented. Frozen for this run.

## Story extraction

Audience:     someone about to build a thing whose shape is not settled yet
Value:        turns an interview into a binary answer key, then into a loop that builds against it
Proof:        two legal verdict forms, an enumerated ungradeable list, and a 20-rule linter that gates the bar before anything runs
First action: answer one question, then say how you would know that answer came out wrong
Theme:        a checker's terminal — the standard is printed, and the run either exits 0 or names one gap

## Frozen system

This skill ships no logo, brand tokens, or style guide, so the resolved style's palette
treatment fills the gap (`design-system.md` → "when a repo has no identity at all, the
style's palette treatment fills the gap"). `terminal-minimalist` asks for a shell theme,
which is what the table below is: a near-black field, one soft off-white, and four
colours that mean status and nothing else.

### Palette

| Role | Hex | Notes |
| --- | --- | --- |
| background | `#0d1117` | the terminal field; never pure black |
| surface    | `#161b22` | a pane, a few percent lighter — the multiplexer's own separation |
| ink        | `#c9d1d9` | soft off-white, never `#ffffff`; 12.26:1 on background |
| muted      | `#8b949e` | secondary text, sublabels, the default connector; 6.15:1 |
| rule       | `#30363d` | hairlines and pane edges only — never a load-bearing graphic |
| ok         | `#3fb950` | green, meaning pass; 7.45:1 either way against background |
| warn       | `#d29922` | amber, meaning undecided — the `CANNOT JUDGE` colour; 7.50:1 |
| err        | `#f85149` | red, meaning fail; 5.65:1 |
| id         | `#58a6ff` | blue, meaning identifier — a named thing, not an outcome; 7.49:1 |

**`rule` is the one role that is not text-safe**, at 1.55:1, and that is deliberate: it
draws pane edges and the legend separator, which are chrome. Anything a reader has to
resolve — a node border, a connector — takes `muted` instead, which clears the 3:1
graphic floor at 6.15. A `SOFTENED` or graphic-contrast `WARN` on `rule` is expected and
is not a licence to darken content strokes.

**Nine roles, and four of them are the same decision.** `ok` / `warn` / `err` / `id` are a
shell theme's semantic set, not four accents. The style's rule — *colours mean status;
they are never decorative* — is what keeps them from being spent on emphasis, and it is
the rule most likely to be broken by a later run reaching for blue because a box looked
plain.

#### Grammar-role bindings

`reference/diagram-grammar.md` §2 names seven roles. They map onto the palette above and
never extend it:

| Grammar role | Bound to | Note |
| --- | --- | --- |
| `paper`   | `background` | the board ground, and the fill of every label mask |
| `surface` | `surface`    | node fill, pane fill |
| `ink`     | `ink`        | primary text |
| `muted`   | `muted`      | sublabels, node strokes, the default connector |
| `rule`    | `rule`       | hairlines, the legend separator — chrome only |
| `accent`  | `id`         | the focal mark, and nothing else |
| `link`    | `id`         | folded into `accent`; no board here draws an external call |

`accent` binds to `id` rather than to `ok` because the focal mark identifies *which* node
carries the weight, and green would read as a verdict on it. `link` folds into `accent`
on a single-accent palette, so the focal budget binds harder: one focal per board.

### Typography

| Role | Stack |
| --- | --- |
| display | `'JetBrains Mono', 'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace` |
| body    | the same stack |
| mono    | the same stack |

One stack, because `terminal-minimalist` declares `mono_only` and the checker enforces
it. Weights `400` and `700` only. System stacks and nothing fetched — a committed SVG may
not reference a remote font, and the chain resolves to whatever terminal face the reader
already has.

### Shape language

Radius `0`, always — `scripts/styles.json` declares `max_rx: 0` for this style and the
checker fails anything else. A character grid of `12 × 22` units at type size 20; text
baselines, rule endpoints and box edges all land on it. Rules are `1` unit, `2` for an
active pane border. A `4`-unit status rail runs down the left edge of a pane in that
pane's semantic colour — 4 rather than 3 because the same rail appears inside a
`data-node` group on the flowchart, where the 4-unit grid binds every rect the
checkers measure, and one width across both boards beats two.

**Connector elbows are square here, and that is a recorded divergence.**
`diagram-grammar.md` §4 makes a rounded quarter-arc bend mandatory at `r=10`; this style's
`Never` list forbids rounded corners of any size, and §6 gives radius to the style. So
connectors turn at hard right angles. Orthogonality — the part `svg_check.py` actually
measures — is unaffected.

### Motif

**The pre-printed verdict column.** Every board carries a fixed column of outcome glyphs
that exists before any work does — `✓` for a pass, `≠` for the one gap, `?` for something
nobody may grade. Derived from what the skill does: it writes the judgement column first
and the work is graded into it later. Repeat it lightly; it is a column, never wallpaper.

### Composition rules

Compact-technical. One pane per idea, bounded by real strokes rather than box-drawing
characters. Left-aligned throughout, because a terminal is. Content stays 48–80 units
clear of the edges. Legible at rendered width — 1200 units inside an 820 px embed.

### Motion rules

- Seamless ambient loops, `data-loop-s="12"` on every animated board; every duration
  divides 12 exactly.
- **Stepped, never tweened.** `steps()` easing throughout, because terminals redraw
  rather than glide. Smooth easing is on this style's `Never` list.
- Two motion ideas per board at most. A blinking block cursor and a scan stepping down
  the rows; a status rail advancing through a cycle and one dash marching a return path.
- Nothing faster than roughly 2 Hz, nothing under text, nothing moving geometry on a
  board that carries `data-diagram`.
- Every animated visual carries a `prefers-reduced-motion` block that stops all motion
  and leaves a legible still — for a scan that means parked on the opening row, not
  absent.

## Style

| Field | Value |
| --- | --- |
| Slug | `terminal-minimalist` |
| Source | catalog (`--style terminal-minimalist`, named by the user) |
| Primary axis | material — a shell rendered properly decides everything else |

- **Intent** — a terminal UI drawn with real strokes: monospace type on a dark field,
  box structure made of SVG rectangles and rules, a block cursor, and status colours
  borrowed from a good shell theme. The right call for a skill whose output is a bar and
  whose gate is a script that exits 0 or does not.
- **Palette treatment** — a shell theme. Colour means status. Green passes, amber is
  undecided, red fails, blue names a thing.
- **Shape language** — radius `0`, a `12 × 22` cell grid, `1`-unit rules meeting exactly
  at corners, a `2`-unit border on the active pane, a `4`-unit status rail.
- **Material / depth** — none. No shadow, no gradient, no blur; `styles.json` forbids all
  four primitives. Panes separate by rule and by a few percent of background tint.
- **Type treatment** — monospace only, weights `400` and `700`. Sentence case in prose,
  lowercase for commands. Semantic glyphs (`✓`, `≠`, `?`, `·`) carry status alongside
  colour so the boards survive greyscale.
- **Motion character** — a blinking block cursor, a stepped scan, a rail advancing one
  station per interval. All `steps()`.
- **SVG recipes** — `reference/styles/terminal-minimalist.md`: the blink, the stepped
  bar, the status rail, the reversed block strip.
- **Relaxations** — none. A shell palette on near-black clears contrast comfortably,
  which is why good terminal themes look the way they do.
- **Never** — a non-mono font (a checker error for this style), a rounded corner of any
  size, a shadow, a gradient, a Bézier connector, ASCII or box-drawing characters
  standing in for real strokes, smooth easing, colour used decoratively rather than
  semantically, or status carried by colour with no glyph.

## Visual inventory

| Asset | Doc | Depicts | Tier | Source facts |
| --- | --- | --- | --- | --- |
| hero | README.md | an answer key as it is emitted: binary rows, the two legal `judged by` forms, and an ungradeable Unknown below the rule | animated-hero | SKILL.md → Every answer produces a check; assets/ANSWER-KEY.template.md; scripts/check_answer_key.py |
| gauntlet-loop | README.md | contract → build → blind audit → verdict, with a win or tie passing and a loss returning exactly one gap | animated-flagship | reference/gauntlet.md; reference/critic-contract.md; assets/ANSWER-KEY.template.md |
