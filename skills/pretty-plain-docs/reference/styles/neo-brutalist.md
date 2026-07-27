# neo-brutalist

**Primary axis:** material · **Aliases:** `brutalist`, `neubrutalism`

<div align="center">
<img src="../../docs/samples/neo-brutalist.svg" alt="The neo-brutalist specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">
</div>


## Intent

Thick black rules, hard offset shadows with zero blur, flat saturated color, and
nothing apologising for itself. Choose it for opinionated developer tools and
projects with a strong voice. It is cheap in bytes and passes every gate, which makes
it the expressive option that costs nothing.

## Palette treatment

Flat and loud. The repo's accents run at full saturation as large fills; `ink` is
true black and every element is outlined in it. `background` is either bright or
off-white — never a mid tone, because the black outlines need maximum separation.
Three fills per board is plenty.

## Shape language

**Radius `0`.** Squares, rectangles, hard diagonals. Every filled shape carries a
`3`–`5` unit black outline. Stroke weights are heavy and consistent: `3` minimum,
`5` for emphasis. Nothing hairline.

## Material / depth

The offset shadow, and only the offset shadow: a solid black copy of the shape, moved
`6–10` units down-right, with **no blur**. No filters at all — the shadow is a real
rectangle underneath. That is why this style forbids blur primitives outright rather
than relaxing anything.

## Type treatment

A **display grotesque plus a typewriter mono**, both heavy — Archivo Black with Arial
Black behind it for display, Courier New for identifiers and metadata. The pairing is
part of the idiom: one face shouting, one face that looks typed. Weights `800`–`900`,
large. Uppercase for titles with `+1` to `+2` tracking; sentence case for anything
longer than three words.

A **knocked-out title block** is the on-idiom heading: a solid `ink` rectangle with
the title reversed out of it in `background`. It costs one rect and produces the
highest-contrast element on the board.

## SVG recipes

The offset shadow, a stepped packet, and the return-to-home nudge:

```svg
<style>
  svg { --background:#fdf6e3; --ink:#000000; --accent:#ff4d3d;
        --accent-2:#2b6eff; --accent-3:#ffd400; }
  .bg     { fill: var(--background); }
  .shadow { fill: var(--ink); }
  .block  { stroke: var(--ink); stroke-width: 4; }
  .f1     { fill: var(--accent); }
  .f2     { fill: var(--accent-2); }
  .t      { fill: var(--ink); font-weight: 900; letter-spacing: 1.5px;
            font-family: 'Archivo Black', 'Arial Black', Impact, sans-serif; }
  .id     { fill: var(--ink); font-weight: 700; font-size: 20px;
            font-family: 'Courier New', ui-monospace, monospace; }
  .ko     { fill: var(--background); font-weight: 900; letter-spacing: 1.5px;
            font-family: 'Archivo Black', 'Arial Black', Impact, sans-serif; }
  /* out, further, home — the third stop hides the seam */
</style>

<!-- shadow first, then the outlined block on top -->
<rect class="shadow" x="108" y="108" width="300" height="150"/>
<rect class="block f1" x="100" y="100" width="300" height="150"/>

<!-- knocked-out title block -->
<rect class="shadow" x="100" y="300" width="360" height="64"/>
<text class="ko" x="122" y="346" font-size="34">PIPELINE</text>
```

The offset shadow is geometry — a second filled rect, not a filter — which is what
keeps the edge hard at every size.

## Relaxes

Nothing, and it needs nothing — black on saturated color clears the contrast gate
comfortably.

## Never

**Any blur filter** (`feGaussianBlur`, `feDropShadow`) — the checker forbids both for
this style. Also never: rounded corners, gradients, thin strokes, pastel fills, drop
shadows built from filters instead of geometry, a single type family doing both display and identifier work, or
a shape without an outline.
