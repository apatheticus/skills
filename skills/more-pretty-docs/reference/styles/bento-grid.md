# bento-grid

**Primary axis:** composition · **Aliases:** `bento`, `cards`, `dashboard`

<img src="../../docs/samples/bento-grid.svg" alt="The bento-grid specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">


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

A neutral-plus-one-indigo palette is the reference pairing: a cool grey ramp for
ground, surface and edge (`#F4F4F5` / `#FFFFFF` / `#E4E4E7`) with a single saturated
indigo (`#4F46E5`) as the accent. Map the repo's own palette onto that shape — a
near-neutral ramp and one confident hue — rather than distributing brand colours
across the cells.

## Shape language

Radius `12–20`, identical on every cell. **One gutter value everywhere** — `16` or `20`
units, never varied. Cells span whole grid units: spans of 1, 2, or 3 columns and
nothing in between.

Do the arithmetic before drawing anything. On a 1200 canvas with `40` outer margins and
a `20` gutter, six columns leaves `1200 − 80 − 5×20 = 1020`, so a column is `170`:

```
x = 40 + col × 190            col 0…5 → 40, 230, 420, 610, 800, 990
w = span × 170 + (span−1) × 20    span 1→170, 2→360, 3→550
```

The last cell ends at `990 + 170 = 1160`, exactly one margin from the edge. Sketch the
rectangles first, confirm they tile with no leftover slivers, then fill them.

## Material / depth

Barely any: a `1`-unit hairline border in a slightly lighter tint than the cell, or one
very soft shadow shared by every cell. Pick one and use it for all cells. Never both.

## Type treatment

Per-cell hierarchy, up to three steps:

| Role | Treatment |
| --- | --- |
| Eyebrow | `18`–`20`, weight `600`, tracking `+1.4`, uppercase, in the muted neutral |
| Label | `22`–`26`, weight `600` |
| Value | `44+`, weight `700` |

The **eyebrow** is what lets a cell name its category without spending the label line
on it — but it must clear the type floor and the contrast floor like anything else.
At the 9-px, pale-grey size the idiom is usually drawn at, it does neither; here it
is `18`+ in a neutral dark enough to measure 4.5:1 on the cell surface.

Units belong on the value, not in the label, as a smaller `<tspan>`:

```svg
<text class="val" x="72" y="196">128<tspan class="unit" dx="6">MB</tspan></text>
```

The focal cell may go larger. System sans throughout. Sentence case. Each cell gets
one label and at most one value — the moment a cell needs three lines of body text, it
should be two cells or a different style.

**One cell may hold a small diagram instead of a value** — three nodes and two
connectors, at the cell's own scale. It is the one place composition nests, and it
is what lets a bento board carry a process without leaving the idiom.

## Motion character

**One cell moves at a time.** A value counting, a sparkline drawing, a status dot
pulsing, a small bar filling. The grid itself is completely static — that stillness is
what makes the single moving cell read as live data. Stagger with negative delays so at
most one or two cells are mid-motion at any moment.

**Grow-then-hold, not grow-then-snap.** A bar that scales to full and holds for the
back half of its cycle reads as a measurement that settled; one that runs to full at
`100%` restarts visibly at the seam. Anchor the growth in **user units** —
`transform-box: view-box` with an explicit origin — rather than `fill-box` and
`left center`, so the bar grows from the gridline it is measured against instead of
from its own changing bounding box.

## SVG recipes

The grid, the focal cell, and a staggered per-cell pulse:

```svg
<style>
  svg { --background:#f4f5f7; --surface:#ffffff; --ink:#16181d;
        --muted:#6b7280; --accent:#3b5bdb; --edge:#e3e5ea; }
  .bg    { fill: var(--background); }
  .cell  { fill: var(--surface); stroke: var(--edge); stroke-width: 1; }
  .focal { fill: var(--accent); stroke: none; }
  .eye   { fill: var(--muted); font-size: 19px; font-weight: 600;
           letter-spacing: 1.4px; text-transform: uppercase; }
  .lab   { fill: var(--muted); font-size: 23px; font-weight: 600; }
  .val   { fill: var(--ink); font-size: 46px; font-weight: 700; }
  .unit  { fill: var(--muted); font-size: 24px; font-weight: 600; }
  .on-focal { fill: #ffffff; }

  .dot   { fill: var(--accent); animation: live 4s ease-in-out infinite; }
  .d1 { animation-delay: 0s }
  .d2 { animation-delay: -1.33s }
  .d3 { animation-delay: -2.67s }
  @keyframes live { 0%,100% { opacity: .35 } 50% { opacity: 1 } }

  /* grow, then hold: the second half is still, so the seam is invisible */
  .bar { fill: var(--accent); transform-box: view-box; transform-origin: 72px 0; }
  .grow{ animation: grow 6s cubic-bezier(.4,0,.2,1) infinite; }
  @keyframes grow { 0% { transform: scaleX(0) } 45%,100% { transform: scaleX(1) } }

  @media (prefers-reduced-motion: reduce) {
    .dot { animation: none; opacity: 1 }
    .grow{ animation: none; transform: scaleX(1) }
  }
</style>

<!-- 6-col grid: x = 40 + col*190, w = span*170 + (span-1)*20 -->
<rect class="cell"  x="40"  y="40" width="360" height="180" rx="16"/>  <!-- col 0, span 2 -->
<rect class="focal" x="420" y="40" width="170" height="180" rx="16"/>  <!-- col 2, span 1 -->

<text class="eye" x="72" y="88">throughput</text>
<text class="val" x="72" y="150">128<tspan class="unit" dx="6">MB</tspan></text>
<rect class="bar grow" x="72" y="176" width="290" height="12" rx="6"/>
```

The negative delays spread three dots across one `4s` cycle without changing any
duration, so the seam contract holds for free. `4s` and `6s` both divide `12s`.

## Relaxes

Nothing. White cells on a light ground need a hairline border to be visible at all,
which is exactly what the UI-contrast gate is checking for — so let it check.

Note the radius floor applies to **nested** shapes too, not just the cells: a chip or
inner panel at radius `10` inside a `16` cell is a checker error, and it reads wrong
anyway. Nested radii step *down* from the cell but stay at or above `12`.

## Never

Varying gutters, varying radius, a nested radius below the floor, more than one
accent-filled cell, no focal cell at all, a cell with three lines of body text, a
9-px pale eyebrow, cells that don't align to the grid, more than two cells animating
at once, a bar that snaps back at the seam, `fill-box` origins on a growing bar, or a
grid so uniform it may as well be a table — the *unequal* spans are the style.
