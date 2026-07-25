# skeuomorphic

**Primary axis:** material · **Aliases:** `realist`, `textured`

## Intent

Controls that look like physical objects: bevelled edges, a top-lit sheen, inset
wells, visible material. Choose it for audio tools, hardware projects, samplers,
anything whose real-world analogue is a device with knobs. It is the most expensive
style in this catalog — budget for it.

## Palette treatment

The palette becomes *material*. Each role gets a light and dark variant derived from
it (roughly ±12% lightness) to serve as the bevel highlight and shade. One consistent
light source: **top-left**, always. Highlights on top and left edges, shade on
bottom and right, never both ways in one board.

## Shape language

Radius `6–12` on panels, `4` on inset wells. Everything has an edge — a 1px light
line above and a 1px dark line below. Circles for knobs and indicators. Nothing is
edge-to-edge; panels sit inside a frame with visible margin.

## Material / depth

Two chained filter primitives per element, which is why this style relaxes the filter
depth gate. The idiom is a soft outer shadow plus an inner highlight, or a bevel
built from a gradient pair. Use `<linearGradient>` for the face; use a filter only
where a gradient can't reach.

## Type treatment

System sans, `600`–`700` for labels. Engraved or embossed labels are on-idiom: the
same text twice, offset one unit, the lower copy in the shade color at low opacity.
Keep the top copy at full contrast so the label still passes the contrast gate.
Small caps with `+1` tracking reads correctly on a device panel.

## Motion character

Mechanical and short. A meter needle sweeping, an LED breathing, a knob rotating
through a limited arc. Real devices don't drift, so nothing floats — motion has a
start position it returns to.

## SVG recipes

A bevelled panel with a top-lit face and an inset well:

```svg
<defs>
  <linearGradient id="face" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#4a4f57"/><stop offset="1" stop-color="#31353b"/>
  </linearGradient>
  <filter id="bevel" x="-15%" y="-15%" width="130%" height="130%">
    <feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity="0.55"/>
    <feDropShadow dx="0" dy="-1" stdDeviation="0" flood-color="#6d747e" flood-opacity="0.9"/>
  </filter>
</defs>
<style>
  svg { --background:#22262b; --surface:#3a3f46; --ink:#f2f4f6; --accent:#f0b429; --shade:#1b1e22; }
  .panel { fill: url(#face); filter: url(#bevel); }
  .well  { fill: var(--shade); stroke: #565c65; stroke-width: 1; }
  .led   { fill: var(--accent); animation: breathe 4s ease-in-out infinite; }
  @keyframes breathe { 0%,100% { opacity: .45 } 50% { opacity: 1 } }
  @media (prefers-reduced-motion: reduce) { .led { animation: none; opacity: 1 } }
</style>
```

Two `feDropShadow` primitives in one filter is the relaxation being used — one for
the cast shadow, one for the top highlight.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| filter depth | 1 → **2** chained primitives per element |

Nothing else. The contrast floor still applies to every label, so keep engraved text
legible rather than authentically murky.

## Never

Light from two directions, more than two filter primitives on one element, photographic
texture (there is no remote image to load), a bevel on text that drops it below
contrast, "leather stitching" pastiche that carries no information.
