# terminal-minimalist

**Primary axis:** material · **Aliases:** `tui`, `cli`, `terminal`, `ascii-adjacent`

## Intent

A terminal UI rendered properly: monospace type on a dark field, box-drawing structure
made of real SVG strokes, a block cursor, and status colors borrowed from a good shell
theme. Choose it for CLIs, infrastructure, and devops repos. Along with `blueprint` it
is the cheapest style in the catalog — often under 8 KB.

**This is not ASCII art.** ASCII art is banned by house style. The difference: ASCII
art draws boxes out of `+`, `-`, and `|` characters inside a text block. This style
draws real strokes and real rectangles, and only uses mono *type* for the labels.

**Compare `ide-dark`:** the two get confused constantly, and they are opposites in
form. This one is a TUI — radius `0`, a character grid, monospace everywhere, stepped
redraws. `ide-dark` is the GUI: rounded panes, mixed proportional and mono type,
Bézier connectors, eased motion. If your reference image has rounded corners and a
sidebar, you want `ide-dark`, not a loosened terminal.

## Palette treatment

A shell theme. `background` is near-black (`#0d1117`-ish) or a deep warm black; `ink`
is a soft off-white, never pure `#fff`. Then the standard semantic set — one green for
success, one amber for pending, one red for failure, one blue or cyan for identifiers.
Colors mean status; they are never decorative.

## Shape language

Radius `0`, always. A single-cell grid: pick a cell size (say `12 × 22` units) and
place *everything* on it — text baselines, rule endpoints, box edges. Rules are `1`
unit, drawn cell-aligned so they meet exactly at corners. One `2`-unit rule for the
active pane border.

A **3-unit status rail** down the left edge of a pane, in the semantic colour for that
pane's state, is the cheapest status indicator in the catalog and stays inside the
radius-`0` rule. A full-width **block status strip** along the bottom — solid
semantic fill, mono text reversed out of it — is the other one.

## Material / depth

None whatsoever. No shadow, no gradient, no blur. Panes are separated by rules and
background tint (`surface` a few percent lighter than `background`), exactly as a
terminal multiplexer does it.

## Type treatment

**Monospace only** — the checker enforces this for this style. Name a real programming
face ahead of the generics so the glyphs are the ones the reader knows from their own
terminal: `'JetBrains Mono', 'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo,
Consolas, monospace`. Nothing is fetched; the chain resolves to whatever is installed.
Weights `400` and `700` only. All text on the cell grid. Sentence case in prose;
lowercase for commands, because that is how they're typed. A `$` or `❯` prompt glyph
is on-idiom.

**Semantic glyphs beat semantic colour alone.** `=` for unchanged and `≠` for changed,
`✓`/`✗`, `+`/`-` — a mono face has them all, they read at any size, and they survive
being printed in greyscale. Colour still means status; the glyph means it too.
An `exit 0` on the status strip is the on-idiom way to report a clean result.

## Motion character

A blinking block cursor, a spinner cycling through frames, a progress bar filling, a
log line appearing. All stepped — terminals redraw, they don't tween. `steps()`
easing throughout.

## SVG recipes

The blinking cursor and a stepped spinner:

```svg
<style>
  svg { --background:#0d1117; --surface:#161b22; --ink:#c9d1d9;
        --ok:#3fb950; --warn:#d29922; --err:#f85149; --id:#58a6ff; }
  .bg   { fill: var(--background); }
  .pane { fill: var(--surface); }
  .rule { stroke: #30363d; stroke-width: 1; fill: none; }
  .t    { fill: var(--ink); font-size: 20px;
          font-family: 'JetBrains Mono', 'IBM Plex Mono', ui-monospace,
                       SFMono-Regular, Menlo, Consolas, monospace; }
  .ok   { fill: var(--ok); }
  .id   { fill: var(--id); }
  .rail { fill: var(--ok); }              /* 3-unit status rail */
  .strip{ fill: var(--ok); }              /* block status strip */
  .ko   { fill: var(--background); }      /* text reversed out of the strip */

  .cursor { fill: var(--ink); animation: blink 2s steps(1, end) infinite; }
  @keyframes blink { 0%,49% { opacity: 1 } 50%,100% { opacity: 0 } }

  .bar { fill: var(--ok); animation: fill 4s steps(8, end) infinite;
         transform-box: fill-box; transform-origin: left center; }
  @keyframes fill { from { transform: scaleX(0) } to { transform: scaleX(1) } }

  @media (prefers-reduced-motion: reduce) {
    .cursor { animation: none; opacity: 1 }
    .bar    { animation: none; transform: scaleX(1) }
  }
</style>

<rect class="cursor" x="360" y="184" width="11" height="22"/>

<rect class="rail"  x="120" y="120" width="3" height="264"/>
<rect class="strip" x="120" y="560" width="960" height="26"/>
<text class="t ko"  x="132" y="580">exit 0  ·  12 checked  ·  0 ≠</text>
```

`steps(8, end)` on a `4s` bar gives eight visible increments — a progress bar that
redraws rather than glides. `2s` and `4s` both divide `12s`.

## Relaxes

Nothing. A shell palette on near-black clears contrast comfortably; that is why good
terminal themes look the way they do.

## Never

Any non-mono font (a checker error for this style), rounded corners of any size —
if the reference has them, the style you want is `ide-dark` — shadows, gradients,
Bézier connectors, ASCII/box-drawing characters standing in for real strokes, smooth
easing, colour used decoratively rather than semantically, status carried by colour
with no glyph, or content placed off the cell grid.
