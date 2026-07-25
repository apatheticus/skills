# neo-brutalist

**Primary axis:** material · **Aliases:** `brutalist`, `neubrutalism`

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

System sans at heavy weights (`800`–`900`), large. Uppercase for titles with `+1` to
`+2` tracking; sentence case for anything longer than three words. Type may sit
inside a filled block with its own black outline. Mono for identifiers, also bold.

## Motion character

Snappy and stepped. Things jump between positions rather than gliding — use
`steps()` easing or keyframes that hold and then move. Shadows shift as if the object
was nudged. Nothing eases smoothly; that would contradict the whole style.

## SVG recipes

The offset shadow and a stepped nudge:

```svg
<style>
  svg { --background:#fdf6e3; --ink:#000000; --accent:#ff4d3d;
        --accent-2:#2b6eff; --accent-3:#ffd400; }
  .bg     { fill: var(--background); }
  .shadow { fill: var(--ink); }
  .block  { stroke: var(--ink); stroke-width: 4; }
  .f1     { fill: var(--accent); }
  .f2     { fill: var(--accent-2); }
  .t      { fill: var(--ink); font-weight: 800; letter-spacing: 1.5; }
  .nudge  { animation: nudge 3s steps(1, end) infinite; }
  @keyframes nudge {
    0%, 49%   { transform: translate(0, 0) }
    50%, 100% { transform: translate(4px, 4px) }
  }
  @media (prefers-reduced-motion: reduce) { .nudge { animation: none } }
</style>

<!-- shadow first, then the outlined block on top -->
<rect class="shadow" x="108" y="108" width="300" height="150"/>
<rect class="block f1 nudge" x="100" y="100" width="300" height="150"/>
```

`steps(1, end)` makes the nudge a hard switch rather than a glide, which is the
motion signature of the style. `3s` divides `12s` four times.

## Relaxes

Nothing, and it needs nothing — black on saturated color clears the contrast gate
comfortably.

## Never

**Any blur filter** (`feGaussianBlur`, `feDropShadow`) — the checker forbids both for
this style. Also never: rounded corners, gradients, thin strokes, pastel fills, smooth
easing, drop shadows built from filters instead of geometry, or a shape without an
outline.
