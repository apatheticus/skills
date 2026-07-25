# bento-grid

**Primary axis:** composition · **Aliases:** `bento`, `cards`, `dashboard`

## Intent

Unequal cells packed into one tight grid, each cell doing exactly one job — the layout
Apple's product pages made ubiquitous. Choose it for feature overviews, capability
matrices, and dashboards. It is the best style here for a visual that has to hold five
or six unrelated facts at once.

## Palette treatment

A quiet ground with cells in `surface`, plus **one** cell promoted to an accent fill as
the focal point. That single colored cell is what makes the grid read as composed rather
than uniform. Semantic color inside cells (a status dot, a small chart) is fine; whole
extra colored cells are not.

## Shape language

Radius `12–20`, identical on every cell. **One gutter value everywhere** — `16` or `20`
units, never varied. Cells span whole grid units: on a 1200 canvas, a 6-column grid at
`188` + `20` gutter gives spans of 1, 2, or 3 columns and nothing in between.

The grid is the discipline. Sketch the cell rectangles first, confirm they tile with no
leftover slivers, then fill them.

## Material / depth

Barely any: a `1`-unit hairline border in a slightly lighter tint than the cell, or one
very soft shadow shared by every cell. Pick one and use it for all cells. Never both.

## Type treatment

Per-cell hierarchy, two steps: a `22`–`26` label and one large `44+` value or a short
phrase. The focal cell may go larger. System sans, `600` for labels, `700` for values.
Sentence case. Each cell gets one label and at most one value — the moment a cell needs
three lines of body text, it should be two cells or a different style.

## Motion character

**One cell moves at a time.** A value counting, a sparkline drawing, a status dot
pulsing, a small bar filling. The grid itself is completely static — that stillness is
what makes the single moving cell read as live data. Stagger with negative delays so at
most one or two cells are mid-motion at any moment.

## SVG recipes

The grid, the focal cell, and a staggered per-cell pulse:

```svg
<style>
  svg { --background:#f4f5f7; --surface:#ffffff; --ink:#16181d;
        --muted:#6b7280; --accent:#3b5bdb; --edge:#e3e5ea; }
  .bg    { fill: var(--background); }
  .cell  { fill: var(--surface); stroke: var(--edge); stroke-width: 1; }
  .focal { fill: var(--accent); stroke: none; }
  .lab   { fill: var(--muted); font-size: 23px; font-weight: 600; }
  .val   { fill: var(--ink); font-size: 46px; font-weight: 700; }
  .on-focal { fill: #ffffff; }

  .dot   { fill: var(--accent); animation: live 4s ease-in-out infinite; }
  .d1 { animation-delay: 0s }
  .d2 { animation-delay: -1.33s }
  .d3 { animation-delay: -2.67s }
  @keyframes live { 0%,100% { opacity: .35 } 50% { opacity: 1 } }

  @media (prefers-reduced-motion: reduce) { .dot { animation: none; opacity: 1 } }
</style>

<!-- 6-col grid: x = 40 + col*208, w = span*188 + (span-1)*20 -->
<rect class="cell"  x="40"  y="40" width="396" height="180" rx="16"/>
<rect class="focal" x="456" y="40" width="188" height="180" rx="16"/>
```

The negative delays spread three dots across one `4s` cycle without changing any
duration, so the seam contract holds for free. `4s` divides `12s` three times.

## Relaxes

Nothing. White cells on a light ground need a hairline border to be visible at all,
which is exactly what the UI-contrast gate is checking for — so let it check.

## Never

Varying gutters, varying radius, more than one accent-filled cell, a cell with three
lines of body text, cells that don't align to the grid, all cells animating at once, or
a grid so uniform it may as well be a table — the *unequal* spans are the style.
