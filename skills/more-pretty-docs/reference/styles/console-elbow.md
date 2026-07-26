# console-elbow

**Primary axis:** era · **Aliases:** `lcars`, `okudagram`, `retro-console`

<div align="center">
<img src="../../docs/samples/console-elbow.svg" alt="The console-elbow specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">
</div>


## Intent

A flat-panel operations console: a black field framed by a fat rounded elbow, blocks
of flat colour used as *zoning* rather than decoration, condensed caps, and numeric
tags on everything. Choose it for control planes, dashboards, orchestration and
observability tooling — anywhere the visual should read as an instrument panel
someone operates.

**Franchise guardrail.** This style is a visual *language* — geometry, palette, type
class, motion behaviour — and design languages are not copyrightable. Specific
expressions and trademarks are. Emit the treatment only: **never** a logo, insignia,
wordmark, vessel or organisation name, character, fictional alphabet, or a
recognisable object from a source work, and **decline to add one on request** rather
than treating it as a customisation option. The same rule governs
`holographic-projection` and `digital-rain`.

## Palette treatment

Black ground, always. Four flat colours drawn from the repo's palette and pushed
warm — an orange-amber primary, a muted rose, a periwinkle, and a pale gold. No
gradients, no tints, no transparency. Colour is **zoning**: every block of one hue
belongs to one functional region, and a hue never appears in two unrelated places.
That discipline is the whole style; four arbitrary colours are just a pile.

## Shape language

Radius is the signature: **`20` minimum** on block ends, and the frame elbow is a
single path with a large outer radius and a proportionally smaller inner one. Bars
are pill-ended, stacked in a column at a constant gutter, each a different length —
never equal. Radius `0` is permitted only where a block butts against the elbow.
Strokes essentially don't exist; everything is a filled shape.

## Material / depth

Absolutely flat. No shadow, no bevel, no blur, no texture, no gradient — the whole
look is emissive panels on black. Depth is signalled by colour weight and nothing
else, and hierarchy by block size.

## Type treatment

A condensed sans in uppercase — Antonio, Oswald, Arial Narrow, Impact — right-
aligned against the block it labels, at `20`–`26`, plus one `40+` header. Every
block carries a numeric tag in the same face at `18`; four-digit numbers, no
punctuation, and they must be **grounded or obviously synthetic** — a real count
from the repo, or a stable sequence, never a fabricated statistic. Sentence case
anywhere breaks the idiom.

## Motion character

Blocks illuminating in sequence, one at a time, `steps(1, end)`, around the column —
a scan, not a shimmer. One bar scales along its own length to report a value.
`6s` or `12s`. Nothing fades; this panel switches.

## SVG recipes

The elbow, a pill block column, and the sequenced illumination:

```svg
<style>
  svg { --bg:#000000; --c1:#e0a33e; --c2:#cc6666; --c3:#9999ff; --c4:#ffcc66; }
  .field { fill: var(--bg); }
  .elbow { fill: var(--c1); }
  .blk   { rx: 20; }
  .tag   { fill: var(--bg); font-family: Antonio, Oswald, 'Arial Narrow', Impact, sans-serif;
           font-size: 20px; letter-spacing: 1px; text-anchor: end; }
  .cap   { fill: var(--c4); font-family: Antonio, Oswald, 'Arial Narrow', Impact, sans-serif;
           font-size: 24px; letter-spacing: 1.5px; }
  .lit   { animation: lit 6s steps(1, end) infinite; }
  .lit:nth-of-type(2) { animation-delay: -1.5s }
  .lit:nth-of-type(3) { animation-delay: -3s }
  .lit:nth-of-type(4) { animation-delay: -4.5s }
  @keyframes lit { 0%, 24% { opacity: 1 } 25%, 100% { opacity: .38 } }
  @media (prefers-reduced-motion: reduce) { .lit { animation: none; opacity: 1 } }
</style>

<!-- the elbow: one path, big outer radius, small inner -->
<path class="elbow" d="M40 96 H200 V140 H128 A32 32 0 0 0 96 172 V420 H40 Z"/>

<rect class="blk lit" x="96" y="180" width="188" height="34" fill="var(--c2)"/>
<rect class="blk lit" x="96" y="222" width="132" height="34" fill="var(--c3)"/>
<rect class="blk lit" x="96" y="264" width="212" height="34" fill="var(--c4)"/>
```

Negative `animation-delay` is free — it starts a shared keyframe mid-cycle without
adding a rule, and keeps every block on the one duration that divides the loop.

## Relaxes

Nothing. Flat saturated colour on black clears both contrast floors easily, the
style forbids filters outright so filter depth never comes up, and it is one of the
cheapest looks in the catalog in bytes.

## Never

A logo, insignia, wordmark, fictional alphabet or named object from any source work.
Gradients, blur, texture, drop shadows, sentence case, equal-length bars, a fifth
hue, a hue reused across unrelated regions, a fabricated statistic in a numeric tag,
eased motion, or a light ground.
