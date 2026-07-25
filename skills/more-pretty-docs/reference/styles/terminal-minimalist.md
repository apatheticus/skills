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

## Material / depth

None whatsoever. No shadow, no gradient, no blur. Panes are separated by rules and
background tint (`surface` a few percent lighter than `background`), exactly as a
terminal multiplexer does it.

## Type treatment

**Monospace only** — the checker enforces this for this style. One stack:
`ui-monospace, SFMono-Regular, Menlo, monospace`. Weights `400` and `700` only. All
text on the cell grid. Sentence case in prose; lowercase for commands, because that is
how they're typed. A `$` or `❯` prompt glyph is on-idiom.

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
  .t    { fill: var(--ink); font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
          font-size: 20px; }
  .ok   { fill: var(--ok); }
  .id   { fill: var(--id); }

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
```

`steps(8, end)` on a `4s` bar gives eight visible increments — a progress bar that
redraws rather than glides. `2s` and `4s` both divide `12s`.

## Relaxes

Nothing. A shell palette on near-black clears contrast comfortably; that is why good
terminal themes look the way they do.

## Never

Any non-mono font (a checker error for this style), rounded corners, shadows,
gradients, ASCII/box-drawing characters standing in for real strokes, smooth easing,
color used decoratively rather than semantically, or content placed off the cell grid.
