# swiss-minimal

**Primary axis:** composition · **Aliases:** `swiss`, `international`, `grid`

## Intent

The International Typographic Style: a strict grid, hairline rules, asymmetric
balance, and type carrying the whole message. Choose it when the content is the
point and any finish would be noise — libraries, tooling, standards, protocol docs.
It is also the safest default, because it passes every gate without relaxation.

## Palette treatment

Two colors do almost all the work: `ink` on `background`. One accent, used once per
board — a single rule, a single filled counter, a single moving dash. Never a
gradient. Grays are structural, never decorative.

## Shape language

Rectangles and straight lines only. Corner radius `0–2`. Stroke weights come from a
two-step scale: `1` for grid and rules, `2.5` for the one emphasized path. Circles
are allowed only as data points or numbered markers.

## Material / depth

None. Flat, no shadow, no bevel, no gradient. Depth is expressed by position and
whitespace, not by lighting.

## Type treatment

System sans, two weights (`400` regular, `700` for the one title). Tight tracking on
display sizes (`-0.5` to `-1`), normal on body. Sentence case. Mono only for
literal identifiers — paths, commands, env vars. Left-aligned, ragged right, never
centered except a single title.

## Motion character

Minimal and linear. One flow dash along one path; at most one counter or state
change. Nothing eases dramatically — `linear` or a shallow `cubic-bezier(.4,0,.6,1)`.
If you can remove a motion and lose no information, remove it.

## SVG recipes

The token block and a marching rule:

```svg
<style>
  svg { --background:#faf9f7; --ink:#111111; --rule:#c9c7c2; --accent:#d6452b; }
  .bg    { fill: var(--background); }
  .t     { fill: var(--ink); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
  .grid  { stroke: var(--rule); stroke-width: 1; fill: none; }
  .lead  { stroke: var(--accent); stroke-width: 2.5; fill: none;
           stroke-dasharray: 18 260; animation: march 4s linear infinite; }
  @keyframes march { from { stroke-dashoffset: 278 } to { stroke-dashoffset: 0 } }
  @media (prefers-reduced-motion: reduce) { .lead { animation: none } }
</style>
```

A modular grid you can actually place against — 12 columns on a 1200 canvas means a
column every `100`, gutters at `24`, content starting at `x=64`.

## Relaxes

Nothing. This style is the reference case for every default gate.

## Never

Gradients, shadows, glows, rounded cards, centered body text, more than one accent
per board, decorative dot grids or "tech" texture, icons where a word is clearer.
