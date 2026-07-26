# skeuomorphic

**Primary axis:** material · **Aliases:** `realist`, `textured`

<div align="center">
<img src="../../docs/samples/skeuomorphic.svg" alt="The skeuomorphic specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">
</div>


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

Up to three chained filter primitives per element, which is why this style relaxes
the filter depth gate further than any other in the digital family. Four devices do
almost all the work, and they compose:

- **The four-stop bevel with a hard tonal break at 50%.** Two stops at the same
  offset is what produces a *machined* edge instead of a soft ramp; a smooth
  gradient reads as plastic, and this one reads as metal.
- **Brushed grain** — `feTurbulence baseFrequency="0.9 0.02"` → `feColorMatrix
  saturate 0` → `feComponentTransfer slope 0.10`, blended over the face. Three
  primitives, and the reason the floor is 3.
- **The gloss `<path>`** — a single closed path across the upper third of the panel,
  white at `0.10`–`0.16`, its lower edge a shallow curve. Not a gradient: a real
  reflection has an edge.
- **A lamp `radialGradient`** for any lit indicator, so the glow falls off from the
  element rather than sitting behind it as a blur.

Use `<linearGradient>` for the face; use a filter only where a gradient can't reach.

## Type treatment

System sans, `600`–`700` for labels. **Engraved labels are always two copies of the
same string** — the lower copy offset one unit in the highlight colour at low
opacity, the sharp glyph on top at full contrast — never one filtered `<text>`, which
smears the letterforms. Give the offset copy `aria-hidden="true"`, or every label is
announced twice. Small caps with `+1` tracking reads correctly on a device panel.

## Motion character

Mechanical and short. A meter needle sweeping, an LED breathing, a knob rotating
through a limited arc. Real devices don't drift, so nothing floats — motion has a
start position it returns to.

A **sagging cable** is the on-idiom connector: a quadratic whose control point sits
below the chord, with the packet travelling it. Straight connectors belong to
`schematic`; a cable has weight.

## SVG recipes

A bevelled panel with a top-lit face and an inset well:

```svg
<defs>
  <!-- four stops, hard tonal break at 0.5: a machined edge, not a ramp -->
  <linearGradient id="face" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0"   stop-color="#5a606a"/><stop offset="0.5" stop-color="#4a4f57"/>
    <stop offset="0.5" stop-color="#3a3f46"/><stop offset="1"   stop-color="#31353b"/>
  </linearGradient>
  <radialGradient id="lamp" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0"   stop-color="#f0b429" stop-opacity="1"/>
    <stop offset="0.55" stop-color="#f0b429" stop-opacity=".45"/>
    <stop offset="1"   stop-color="#f0b429" stop-opacity="0"/>
  </radialGradient>
  <filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.9 0.02" numOctaves="2" seed="5"/>
    <feColorMatrix type="saturate" values="0"/>
    <feComponentTransfer><feFuncA type="linear" slope="0.10"/></feComponentTransfer>
  </filter>
  <filter id="bevel" x="-15%" y="-15%" width="130%" height="130%">
    <feDropShadow dx="0" dy="2" stdDeviation="2" flood-opacity="0.55"/>
    <feDropShadow dx="0" dy="-1" stdDeviation="0" flood-color="#6d747e" flood-opacity="0.9"/>
  </filter>
</defs>
<style>
  svg { --background:#22262b; --surface:#3a3f46; --ink:#f2f4f6; --accent:#f0b429;
        --shade:#1b1e22; --hi:#6d747e; }
  .panel { fill: url(#face); filter: url(#bevel); }
  .grain { fill: var(--surface); filter: url(#grain); mix-blend-mode: overlay; }
  .gloss { fill: #ffffff; opacity: .13; }
  .well  { fill: var(--shade); stroke: #565c65; stroke-width: 1; }
  .cable { stroke: var(--shade); stroke-width: 4; fill: none; stroke-linecap: round; }
  .led   { fill: url(#lamp); animation: breathe 4s ease-in-out infinite; }
  .eng-lo{ fill: var(--hi); font-size: 22px; font-weight: 700; letter-spacing: 1px; }
  .eng   { fill: var(--ink); font-size: 22px; font-weight: 700; letter-spacing: 1px; }
  @keyframes breathe { 0%,100% { opacity: .45 } 50% { opacity: 1 } }
  @media (prefers-reduced-motion: reduce) { .led { animation: none; opacity: 1 } }
</style>

<!-- a reflection has an edge: the gloss is a path, not a gradient -->
<path class="gloss" d="M120 120 H520 V178 Q320 206 120 182 Z"/>

<!-- the cable sags: control point below the chord -->
<path class="cable" d="M520 240 Q640 296 760 240"/>

<text class="eng-lo" x="141" y="309" aria-hidden="true">GAIN</text>
<text class="eng"    x="140" y="308">GAIN</text>
```

Two `feDropShadow` primitives in one filter is the old relaxation; the brushed-grain
chain is three and is why the floor moved.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| filter depth | 1 → **3** chained primitives per element |

Three is exactly the brushed-grain chain — turbulence, desaturate, alpha. Nothing
else relaxes. The contrast floor still applies to every label, so keep engraved text
legible rather than authentically murky.

## Never

Light from two directions, more than three filter primitives on one element, a single
filtered `<text>` for engraving, an engraving copy without `aria-hidden`, a smooth
two-stop gradient where the bevel needs its hard break, a gloss built as a gradient
instead of a path, photographic texture (there is no remote image to load), a bevel
on text that drops it below contrast, straight connectors where a cable should sag,
"leather stitching" pastiche that carries no information.
