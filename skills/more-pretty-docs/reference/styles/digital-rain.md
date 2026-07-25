# digital-rain

**Primary axis:** era + material · **Aliases:** `matrix-rain`, `phosphor-crt`, `falling-glyphs`

<img src="../../docs/samples/digital-rain.svg" alt="The digital-rain specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">


## Intent

Columns of monospace glyphs falling down a black field, each column out of phase
with its neighbours, a bright head glyph leading a dimming tail. Structure emerges
where the rain is *withheld* — the diagram is the negative space. Choose it for
stream processing, log pipelines, event ingestion, and security tooling.

**Franchise guardrail.** Like `console-elbow` and `holographic-projection`, this is a
visual language, not a protected work. Emit geometry, palette, type class and motion
only. **Never** a fictional alphabet, a wordmark, a logo, or a recognisable object
from a source work, and decline to add one on request rather than treating it as a
customisation option. Glyphs are ASCII drawn from the repo's own vocabulary — status
codes, field names, hex — not an invented script.

## Palette treatment

**Two greens and one alert colour. Not five.** A dim tail (`#008F11`-ish), a bright
head (`#9CFFB0`), and the phosphor mid-tone between them (`#00FF41`) for readable
text. One alert hue — the repo's accent — appears on exactly the thing being called
out. The restraint is what makes it read as phosphor rather than generic sci-fi; a
third green collapses it. Ground is pure black.

## Shape language

Radius `0` everywhere — this is a character grid, and rounded corners have no
meaning in one. Panels are outlines at `1` in the dim green, snapped to the glyph
cell. Everything aligns to the monospace advance so columns never drift.

## Material / depth

A CRT, not a screen. Depth is **glyph brightness only**: nearer means brighter.
A `feGaussianBlur` fed back through `feMerge` gives the phosphor bloom on the head
glyph. No shadows, no gradients doing lighting work — a vertical `linearGradient`
used as an opacity fade on a rain column is the one permitted gradient.

## Type treatment

Monospace only, and the checker enforces it: Courier New, JetBrains Mono,
ui-monospace. Rain glyphs at `18`–`20`, readable labels at `20`–`24`, one `40+`
title. Labels sit inside a solid black plate cut out of the rain so they never
compete with a falling column — the rain is texture, the label is content, and they
must not share pixels.

## Motion character

Six or so columns falling **out of phase**, each on the same duration with a
different negative `animation-delay`, so the loop stays exact while the field looks
irregular. `linear`, `4s` or `6s`, translating by exactly one column height so the
seam is invisible. The head glyph blinks at a different rate. Keep every flash under
3 Hz — WCAG 2.3.

## SVG recipes

A phase-shifted column, the bloom, and the label plate:

```svg
<defs>
  <filter id="bloom" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="3" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#008F11" stop-opacity="0"/>
    <stop offset="1" stop-color="#008F11" stop-opacity="1"/>
  </linearGradient>
</defs>
<style>
  svg { --bg:#000000; --tail:#008F11; --phos:#00FF41; --head:#9CFFB0; }
  .g    { font-family: 'Courier New', ui-monospace, monospace; font-size: 19px;
          fill: var(--tail); }
  .head { fill: var(--head); filter: url(#bloom); }
  .lab  { font-family: 'Courier New', ui-monospace, monospace; font-size: 22px;
          fill: var(--phos); }
  .plate{ fill: var(--bg); }
  .fall { animation: fall 6s linear infinite; }
  .fall:nth-of-type(2) { animation-delay: -1s }
  .fall:nth-of-type(3) { animation-delay: -2.5s }
  .fall:nth-of-type(4) { animation-delay: -4s }
  /* travel is exactly one column height, so t=D matches t=0 */
  @keyframes fall { from { transform: translateY(-240px) } to { transform: translateY(0) } }
  @media (prefers-reduced-motion: reduce) { .fall { animation: none } .head { filter: none } }
</style>

<g class="fall"><g class="g">
  <text x="0" y="20">2 0 4</text><text x="0" y="44">t t l</text>
  <text class="head" x="0" y="68">a c k</text>
</g></g>

<rect class="plate" x="300" y="180" width="264" height="44"/>
<text class="lab"   x="316" y="210">ingest → index</text>
```

The travel distance must equal the repeating unit exactly — one column height, or an
exact multiple of the glyph advance — or the seam shows as a jump.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| filter depth | 1 → **2** chained primitives per element |

Two is the bloom: one blur merged back over the source. Contrast is not relaxed —
`#00FF41` on black is about 15:1, and the black label plate exists precisely so
every reader gets that ratio rather than text-over-rain.

## Never

A fictional alphabet, a wordmark, or a named object from a source work. A third
green, a light ground, rounded corners, a proportional face, text sitting directly
over falling glyphs, a flash above 3 Hz, eased falling motion, or travel that isn't
an exact multiple of the glyph advance.
