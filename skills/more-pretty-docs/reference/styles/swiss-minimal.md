# swiss-minimal

**Primary axis:** composition · **Aliases:** `swiss`, `international`, `grid`

## Intent

The International Typographic Style: a strict grid, hairline rules, asymmetric
balance, and type carrying the whole message. Choose it when the content is the
point and any finish would be noise — libraries, tooling, standards, protocol docs.
It is also the safest default, because it passes every gate without relaxation.

## Palette treatment

Three colors do almost all the work: `ink` on `background`, plus one **muted** grey
(around `#8A8A8A`) carrying secondary type — kickers, folios, endpoint labels. That
third role is what lets the style build hierarchy without a second weight or a second
accent. One accent, used **once** per board — a single rule, a single filled counter,
a single moving dash. Never a gradient. Greys are structural, never decorative.

## Shape language

Rectangles and straight lines only. Corner radius `0–2`. Stroke weights come from a
two-step scale: `1` for grid and rules, `2.5` for the one emphasized path. Circles
are allowed only as data points or numbered markers.

**`1` is the floor, not a suggestion.** A `0.5` hairline is authentic to print and
wrong here: at the rendered scale of a README image it either disappears or aliases
into a grey smear, and it fails the graphic-contrast check for a load-bearing rule.

## Material / depth

None. Flat, no shadow, no bevel, no gradient. Depth is expressed by position and
whitespace, not by lighting.

## Type treatment

System sans, two weights (`400` regular, `700` for the one title). Tight tracking on
display sizes (`-0.5` to `-1`), normal on body. Sentence case. Mono only for
literal identifiers — paths, commands, env vars. Left-aligned, ragged right, never
centered except a single title.

Three devices carry almost all the hierarchy, and they are worth using by name:

- **The kicker** — one short uppercase line above the title in the muted grey at
  `+2.4` tracking. It is the only uppercase on the board and the only place tracking
  goes positive.
- **The folio** — a right-aligned muted line on the same baseline as the title,
  holding the section number or subject. Right alignment against a left-aligned
  title is the asymmetric balance the style is named for.
- **The bottom rule with endpoint labels** — one full-width `1` rule with a muted
  label at each end. It reads as a scale or a span for free, and replaces the axis
  labels a chart would otherwise need.

## Motion character

Minimal and linear. One flow dash along one path; at most one counter or state
change. Nothing eases dramatically — `linear` or a shallow `cubic-bezier(.4,0,.6,1)`.
If you can remove a motion and lose no information, remove it.

## SVG recipes

The token block and a marching rule:

```svg
<style>
  svg { --background:#faf9f7; --ink:#111111; --muted:#8a8a8a;
        --rule:#c9c7c2; --accent:#d6452b; }
  .bg    { fill: var(--background); }
  .t     { fill: var(--ink); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
  .kick  { fill: var(--muted); font-size: 18px; letter-spacing: 2.4px;
           text-transform: uppercase; }
  .folio { fill: var(--muted); font-size: 18px; text-anchor: end; }
  .grid  { stroke: var(--rule); stroke-width: 1; fill: none; }
  .lead  { stroke: var(--accent); stroke-width: 2.5; fill: none;
           stroke-dasharray: 18 260; animation: march 4s linear infinite; }
  @keyframes march { from { stroke-dashoffset: 278 } to { stroke-dashoffset: 0 } }
  @media (prefers-reduced-motion: reduce) { .lead { animation: none } }
</style>

<text class="t kick"  x="64"   y="96">pipeline</text>
<text class="t"       x="64"   y="152" font-size="44" font-weight="700">Ingest</text>
<text class="t folio" x="1136" y="152">02</text>

<line class="grid" x1="64" y1="520" x2="1136" y2="520"/>
<text class="t kick"  x="64"   y="552">source</text>
<text class="t folio" x="1136" y="552">warehouse</text>
```

A modular grid you can actually place against — 12 columns on a 1200 canvas means a
column every `100`, gutters at `24`, content starting at `x=64`.

## Relaxes

Nothing. This style is the reference case for every default gate. Check the muted
grey against your own background before using it: `#8A8A8A` on `#FAF9F7` measures
**3.28:1**, which clears the graphic floor but **not** the 4.5:1 text floor, so on a
light ground the muted role needs to go darker (`#6E6E6E` or below) for type.

## Never

Gradients, shadows, glows, rounded cards, centered body text, more than one accent
per board, a `0.5` hairline, tracking above `0` anywhere but the kicker, decorative
dot grids or "tech" texture, icons where a word is clearer.
