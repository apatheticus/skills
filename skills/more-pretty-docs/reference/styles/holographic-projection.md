# holographic-projection

**Primary axis:** material · **Aliases:** `hologram`, `holo`, `projection`

## Intent

Light projected into a dark volume: a cone rising from an emitter, geometry rendered
as glowing wireframe with visible scanlines, and an irregular flicker that reads as
an unstable signal. Choose it for simulation, 3D and spatial tooling, digital twins,
and anything that models something not physically present.

**Franchise guardrail.** A visual language, not a protected work — the same line
`console-elbow` and `digital-rain` hold. Geometry, palette, type class and motion
only. **Never** a logo, insignia, wordmark, fictional alphabet, character, or
recognisable object from a source work, and decline to add one on request rather
than treating it as a customisation option.

## Palette treatment

**One hue plus one alert colour.** A cyan family — a bright edge (`#BEF3FF`) and the
body tone (`#4FD8FF`) — on a near-black ground (`#01070C`), plus the repo's accent
used once for the single alerting element. A third accent collapses the style toward
generic sci-fi; the discipline is the whole effect. All fills are transparent; the
hue lives in strokes and glow.

## Shape language

Wireframe. Fills at `0.06`–`0.14` opacity if at all, strokes at `1.2`–`1.6`. Radius
`0`–`4`. The projection cone is two straight edges from a small emitter footprint up
to the geometry's base, at very low opacity, plus a bright elliptical footprint. Any
shape may be tilted; nothing is drawn as a solid object.

## Material / depth

Emitted light, so depth is **glow and altitude**, never shadow. The glow is a
`feGaussianBlur` merged back under the source. Scanlines are a horizontal-stripe
`<pattern>` at low opacity, drifting slowly upward. Nothing occludes anything —
overlapping wireframe stays visible, which is the point.

## Type treatment

A wide or squarish sans in uppercase at `+3` tracking — Eurostile, Bahnschrift,
Arial Narrow — at `20`–`26`, one `40+` title. Labels glow like everything else, but
**a label never sits on the flicker**: put it outside the flickering group, or on a
low-opacity backing plate, so the readable content holds a steady contrast ratio
while the decorative geometry stutters.

## Motion character

Two signatures, both steady-state. Scanlines drift upward at a constant rate, over
an exact multiple of the stripe pitch so the seam is invisible. Geometry flickers on
`steps()` with an *irregular* keyframe distribution — evenly spaced steps read as a
metronome, not instability. `6s` or `12s`. Keep every flicker under 3 Hz per
WCAG 2.3, and keep the amplitude small (`0.72` → `1`, not `0` → `1`).

## SVG recipes

The glow, the scanline drift, and an irregular flicker:

```svg
<defs>
  <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
    <feGaussianBlur stdDeviation="4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <pattern id="scan" width="6" height="6" patternUnits="userSpaceOnUse">
    <rect x="0" y="0" width="6" height="2.4" fill="#4FD8FF" opacity="0.10"/>
  </pattern>
</defs>
<style>
  svg { --void:#01070C; --holo:#4FD8FF; --edge:#BEF3FF; }
  .void  { fill: var(--void); }
  .wire  { stroke: var(--holo); stroke-width: 1.4; fill: var(--holo); fill-opacity: .08;
           filter: url(#glow); }
  .cone  { fill: var(--holo); fill-opacity: .07; }
  .cap   { fill: var(--edge); font-family: Eurostile, Bahnschrift, 'Arial Narrow', sans-serif;
           font-size: 23px; letter-spacing: 3px; }
  /* drift is exactly one stripe pitch, so t=D matches t=0 */
  .scan  { animation: scan 6s linear infinite; }
  @keyframes scan { from { transform: translateY(0) } to { transform: translateY(-6px) } }
  /* irregular steps: instability, not a metronome */
  .flick { animation: flick 6s steps(1, end) infinite; }
  @keyframes flick {
    0%, 17%  { opacity: 1 }
    18%, 21% { opacity: .72 }
    22%, 63% { opacity: 1 }
    64%, 66% { opacity: .78 }
    67%, 100%{ opacity: 1 }
  }
  @media (prefers-reduced-motion: reduce) {
    .scan, .flick { animation: none; opacity: 1 }
  }
</style>

<rect class="void" x="0" y="0" width="1200" height="620"/>
<path class="cone" d="M560 560 L360 240 L840 240 L640 560 Z"/>
<ellipse cx="600" cy="560" rx="66" ry="18" fill="var(--edge)" fill-opacity=".22"/>
<g class="flick"><rect class="wire" x="400" y="260" width="400" height="180"/></g>
<rect x="0" y="0" width="1200" height="620" fill="url(#scan)" class="scan"/>
```

## Relaxes

| Gate | Default → floor |
| --- | --- |
| filter depth | 1 → **2** chained primitives per element |

Two is the glow: one blur merged back over the source. Contrast is not relaxed —
`#BEF3FF` on `#01070C` is around 17:1, so labels have no excuse, and the rule about
keeping them off the flicker exists so the measured ratio is the delivered one.

## Never

A logo, insignia, wordmark, fictional alphabet or named object from a source work. A
third hue, an opaque fill, a drop shadow, a light ground, a label inside a flickering
group, evenly spaced flicker steps, a flash above 3 Hz, opacity dropping to zero, or
scanline drift that isn't an exact multiple of the stripe pitch.
