# brushed-metal

**Primary axis:** material · **Aliases:** `brushed-steel`, `machined-panel`, `nameplate`

<img src="../../docs/samples/brushed-metal.svg" alt="The brushed-metal specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">


## Intent

A machined aluminium panel with an engraved nameplate: anisotropic grain running one
direction, a specular sheen that travels across it, and type cut *into* the surface
rather than printed on it. Choose it for firmware, embedded systems, industrial
tooling, hardware SDKs, and anything where the product is a physical object or talks
to one.

**Compare `skeuomorphic`:** skeuomorphic imitates a whole object — bezel, sheen,
lamp, cable. brushed-metal imitates one *material* and applies it flat across the
board. If you want a device, pick skeuomorphic; if you want the plate it's screwed
to, pick this.

## Palette treatment

Three tones of one neutral plus the repo's accent, and nothing else. A mid ground
(`#7E888F`-ish), a lighter face for raised panels (`#C3CBD2`), and two darker tones
for recesses and engraving (`#5C656C`, `#3C4349`). The accent appears exactly once,
as the lit indicator or the one active channel. Metal has no hue variety; adding a
second accent reads as painted, not machined.

## Shape language

Radius `2`–`6` — machined edges are broken, not sharp, and not rounded either.
Rectilinear throughout, aligned to a coarse grid. Strokes at `1` for panel seams and
`1.5` for the outer plate edge. Screw or rivet marks at the four corners of a plate
are the one permitted ornament; use them once, not on every element.

## Material / depth

The grain is the whole style. One `feTurbulence` at an extreme x:y frequency ratio
(`1.6 0.006`) desaturated and dropped to about `0.10` alpha, blended `overlay` over
the flat fill. Depth comes from a two-stop bevel with a hard break at the mid-point,
never from a blurred shadow. See the grain-ratio axis in `styles.md`: this is the
directional end of the same dial `wood-grain` and `watercolor` sit on.

## Type treatment

A neutral grotesque in uppercase with `+1.5` tracking — Helvetica Neue, Inter,
Arial. **Engraved type is always two copies of the same string**, never one filtered
text node: a lighter copy offset `+1,+1` underneath for the lit lower edge of the
cut, and the dark glyph on top. Filtering a single text node smears the letterforms
and fails legibility.

**The duplicate copy must carry `aria-hidden="true"`.** It is a highlight, not a
word, and without the attribute every engraved label is announced twice.

## Motion character

A specular band travelling along the grain — slow, linear, `8s` or `12s`, one pass
per loop, at low opacity. The plate itself never moves. An indicator may pulse at a
different rate. Two motions total; metal is heavy and reads wrong when it's busy.

## SVG recipes

The grain, the bevel, and an engraved label:

```svg
<defs>
  <filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="1.6 0.006" numOctaves="2" seed="7"/>
    <feColorMatrix type="saturate" values="0"/>
    <feComponentTransfer><feFuncA type="linear" slope="0.10"/></feComponentTransfer>
  </filter>
  <linearGradient id="bevel" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0"    stop-color="var(--face)"/>
    <stop offset="0.5"  stop-color="var(--face)"/>
    <stop offset="0.5"  stop-color="var(--recess)"/>
    <stop offset="1"    stop-color="var(--recess)"/>
  </linearGradient>
</defs>
<style>
  .plate { fill: url(#bevel); stroke: var(--edge); stroke-width: 1.5; }
  .grain { fill: var(--face); filter: url(#grain); mix-blend-mode: overlay; }
  .eng-lo{ fill: var(--face); font-size: 24px; letter-spacing: 1.5px; }
  .eng   { fill: var(--recess); font-size: 24px; letter-spacing: 1.5px; }
  .sheen { animation: sheen 12s linear infinite; }
  @keyframes sheen { from { transform: translateX(-200px) } to { transform: translateX(1400px) } }
  @media (prefers-reduced-motion: reduce) { .sheen { animation: none } }
</style>

<rect class="plate" x="120" y="180" width="420" height="120" rx="4"/>
<rect class="grain" x="120" y="180" width="420" height="120" rx="4"/>
<text class="eng-lo" x="153" y="249" aria-hidden="true">THROUGHPUT</text>
<text class="eng"    x="152" y="248">THROUGHPUT</text>
```

The sheen is a low-opacity white parallelogram inside a `clipPath` matching the
plate, skewed a few degrees so it reads as a light source rather than a wipe.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| filter depth | 1 → **3** chained primitives per element |

Three is exactly the grain chain — turbulence, desaturate, alpha — and nothing more.
Contrast is **not** relaxed: engraved type at `#3C4349` on `#C3CBD2` measures **6.12:1**, so there is no excuse for murky labels.

## Never

A single filtered `<text>` for engraving, an engraving copy without `aria-hidden`,
isotropic grain (that's canvas, not metal), a second accent hue, blurred drop
shadows, the sheen crossing a label at full opacity, rounded corners above `6`, or
grain applied to text.
