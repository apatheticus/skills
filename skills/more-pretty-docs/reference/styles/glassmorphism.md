# glassmorphism

**Primary axis:** material · **Aliases:** `glass`, `frosted`, `aero`

## Intent

Frosted translucent panels floating over a colored, blurred ground — depth through
transparency. Choose it for media projects, overlay-heavy UIs, and showcase repos
where the visual is partly the product. It costs the most bytes of any style here
except `maximalist`; read the recipe before committing.

## Palette treatment

The **ground** carries the color: two or three large accent blobs at high saturation,
heavily blurred. Panels are near-white or near-black at `12–20%` opacity with a `1`px
`50%`-opacity light border. `ink` must be near-solid — text is the one thing that is
never translucent.

## Shape language

Radius `12–20` on panels. Large soft blobs behind, crisp rectangles in front. Panel
borders are the only strokes, always `1`, always a light tint at partial opacity.

## Material / depth

Here is the constraint that shapes everything: **SVG has no `backdrop-filter`.** A
panel cannot blur what is behind it. The workaround is to draw the blurred ground
**twice** — once as the page background, once as a copy clipped to the panel's
rectangle — so the panel appears to frost what it covers.

That duplication is geometry, not decoration, and it is why this style gets a raised
byte ceiling. Cap it: **at most three glass panels per board.** Beyond that, split
into two visuals.

## Type treatment

System sans, `500`–`600`. Never thin. Text sits on glass, which is a low-contrast
ground, so pick the panel tint *after* checking the label passes 4.5:1 against it —
usually that means a darker panel than the style is normally drawn with.

## Motion character

Slow drift. The ground blobs move; the panels stay put. `8s` or `12s` translations of
`20–40` units, `ease-in-out`. The frost effect means the panel content shimmers as
the ground passes behind it, which is the whole payoff and needs no extra motion.

## SVG recipes

The ground-duplicate trick, with the clip doing the frosting:

```svg
<defs>
  <filter id="blur"><feGaussianBlur stdDeviation="70"/></filter>
  <g id="ground">
    <circle cx="300" cy="140" r="200" fill="#7c3aed"/>
    <circle cx="900" cy="300" r="230" fill="#0ea5e9"/>
    <circle cx="620" cy="380" r="170" fill="#ec4899"/>
  </g>
  <clipPath id="panel1"><rect x="160" y="120" width="380" height="200" rx="16"/></clipPath>
</defs>
<style>
  svg { --background:#0b1020; --ink:#f8fafc; --edge:#ffffff; }
  .bg    { fill: var(--background); }
  .drift { animation: drift 12s ease-in-out infinite; }
  @keyframes drift {
    0%,100% { transform: translate(0,0) }
    50%     { transform: translate(-38px, 22px) }
  }
  .glass { fill: var(--edge); opacity: .14; }
  .edge  { stroke: var(--edge); stroke-width: 1; fill: none; opacity: .45; }
  .t     { fill: var(--ink); font-weight: 600; }
  @media (prefers-reduced-motion: reduce) { .drift { animation: none } }
</style>

<rect class="bg" x="0" y="0" width="1200" height="420"/>
<g class="drift" filter="url(#blur)"><use href="#ground"/></g>

<!-- the frosted copy: same ground, blurred harder, clipped to the panel -->
<g clip-path="url(#panel1)">
  <g class="drift" filter="url(#blur)" opacity="0.9"><use href="#ground"/></g>
  <rect class="glass" x="160" y="120" width="380" height="200" rx="16"/>
</g>
<rect class="edge" x="160" y="120" width="380" height="200" rx="16"/>
```

`<use href="#ground">` is what keeps the duplication cheap — the blob geometry is
declared once. Both copies carry the same `.drift` class so they never desynchronise.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| byte cap | 150 KB → **200 KB** |

Granted because the blurred ground duplicates are load-bearing geometry, not
ornament. It is not a licence for more panels — three per board, then split.

## Never

More than three panels per board, translucent text, a `backdrop-filter` (it does
nothing), a panel tint that drops its label below 4.5:1, ground blobs that move while
the panels also move, or duplicating the blob geometry instead of `<use>`-ing it.
