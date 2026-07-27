# blueprint

**Primary axis:** material (the medium) · **Aliases:** `cyanotype`, `drafting`

<div align="center">
<img src="../../docs/samples/blueprint.svg" alt="The blueprint specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">
</div>


## Intent

A cyanotype print: white line work on a deep blue ground, with the apparatus of
drafting — a fine grid, dimension arrows, leader lines, revision marks, and a title
block in one corner. Choose it for architecture docs, systems design, and protocol
specifications. Cheap in bytes and passes every gate.

**Compare `schematic`:** blueprint is the *medium* — it should look drawn, on paper,
by hand, with tools. `schematic` is the *notation* — it should look specified. If your
visual wants dimension lines and a title block, you're here.

## Palette treatment

The ground is the identity: a deep desaturated blue (`#1b3a5c`-ish, or the repo's
darkest brand blue). Line work is white or a very pale blue-white at two opacities —
`0.9` for primary geometry, `0.35` for the underlying grid. One warm accent (amber or
rust) for the single thing being called out, used once. Nothing else has color.

## Shape language

Radius `0`. Two stroke weights and a dashed third: `1.6` for primary outlines, `0.8`
for dimension and leader lines, `0.8 dashed` for hidden or planned edges — the standard
drafting convention, and it is genuinely useful for marking simulated or future
components. Corner ticks rather than rounded joins.

## Material / depth

Ink on paper. No shadow, no gradient, no fill except at very low opacity to indicate a
region. Depth is conveyed by line weight, exactly as in real drafting: heavier lines
read as nearer.

## Type treatment

A condensed or plain system sans in uppercase at `+1` tracking, plus mono for
dimensions and part numbers. Small — `18`–`20` for annotations, `16` for the title
block, one `40+` sheet title. Labels sit at the end of leader lines, never on top of
geometry.

## SVG recipes

The grid, drafting line weights, and a self-drawing dimension:

```svg
<defs>
  <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
    <path d="M24 0 L0 0 0 24" fill="none" stroke="#9fc4e8" stroke-width="0.6" opacity="0.3"/>
  </pattern>
  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0,1 L9,5 L0,9 z" fill="#e8f2fb"/>
  </marker>
</defs>
<style>
  svg { --background:#12324f; --ink:#e8f2fb; --dim:#9fc4e8; --accent:#e0a33e; }
  .bg    { fill: var(--background); }
  .grid  { fill: url(#grid); }
  .main  { stroke: var(--ink); stroke-width: 1.6; fill: none; }
  .thin  { stroke: var(--dim); stroke-width: 0.8; fill: none; }
  .hidden{ stroke: var(--dim); stroke-width: 0.8; fill: none; stroke-dasharray: 6 5; }
  .t     { fill: var(--ink); font-size: 19px; letter-spacing: 1px; text-transform: uppercase; }
  .num   { fill: var(--dim); font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
           font-size: 17px; }
  .draw  { stroke-dasharray: 600; }
</style>

<line class="thin" x1="200" y1="330" x2="520" y2="330"
      marker-start="url(#arrow)" marker-end="url(#arrow)"/>
```

The title block belongs bottom-right: a `thin`-stroked rectangle holding the repo name,
the visual's subject, and a mono revision-style label. Never a date or version — the
no-volatile-facts rule applies inside visuals.

## Relaxes

Nothing. White on deep blue is a high-contrast pairing; the `0.35`-opacity grid is
decorative and carries no text.

## Never

Filled color regions at full opacity, shadows, gradients, rounded corners, labels
overlapping geometry, dimension lines without arrowheads, a date or version in the
title block, or more than one warm accent callout per board.
