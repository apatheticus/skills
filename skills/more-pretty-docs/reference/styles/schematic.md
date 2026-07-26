# schematic

**Primary axis:** composition (the notation) · **Aliases:** `technical-drawing`,

<img src="../../docs/samples/schematic.svg" alt="The schematic specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">

`circuit`, `netlist`

## Intent

A specification diagram: a consistent symbol alphabet, orthogonal routing, net labels
where a drawn wire would clutter, and no shading or perspective anywhere. Choose it for
hardware, compilers, data pipelines, and anything whose structure is genuinely a graph
with typed nodes.

**Compare `blueprint`:** blueprint is the medium and should look *drawn* — blue ground,
dimension arrows, a title block. Schematic is the notation and should look *specified* —
light ground, symbols, net labels. If two components of the same kind must be
instantly recognisable as the same kind, you're here.

## Palette treatment

Light ground, near-black line work — a printed spec sheet. `background` is white or a
faint warm gray; `ink` carries every line and symbol outline. Color is **typed**: one
hue per signal or data class (control, data, error), applied only to connections and
their net labels. Nodes themselves are uncolored outlines.

## Shape language

Radius `0`. **Orthogonal routing only** — every connection runs horizontal or vertical
with `90°` corners, never a diagonal or a curve. Junctions get a filled dot; crossings
without a junction get a small hop or simply cross unmarked (pick one and hold it).
Stroke `1.5` for connections, `2` for symbol outlines.

## Material / depth

None, absolutely. No shadow, no gradient, no fill beyond flat white inside symbols. A
schematic has no light source because it depicts topology, not objects.

## Type treatment

Mono for every identifier — part designators, net names, pin numbers — because they are
literal strings. System sans for the sheet title and any prose annotation. Uppercase
designators (`U1`, `CLK`, `DATA_OUT`), `18`–`20` units. Net labels sit on the wire in a
small white-filled box so they don't collide with the line.

## Symbol alphabet

Define it once per repo, in `DESIGN.md`, and reuse via `<defs>` + `<use>`. Give each
node *kind* one shape and never reuse a shape for two kinds:

| Kind | Symbol |
| --- | --- |
| Process / transform | rectangle |
| Store / persistence | rectangle with doubled left edge |
| External boundary | rectangle with clipped top-right corner |
| Decision / branch | diamond |
| Terminal / IO | rectangle with rounded ends *(the one radius exception)* |

## Motion character

Signal propagation. A pulse travelling along the orthogonal routes, arriving at each
node in sequence; a junction dot brightening as the signal passes. Everything stepped or
linear — a signal has no easing. `4s` or `6s`.

## SVG recipes

A reused symbol, orthogonal routing, and a propagating pulse:

```svg
<defs>
  <g id="proc"><rect x="0" y="0" width="150" height="76" fill="#ffffff"
                     stroke="#14181d" stroke-width="2"/></g>
  <path id="net1" d="M250,138 H420 V262 H590"/>
</defs>
<style>
  svg { --background:#f7f7f5; --ink:#14181d; --data:#1f6feb; --ctrl:#8957e5; --err:#cf222e; }
  .bg    { fill: var(--background); }
  .wire  { stroke: var(--data); stroke-width: 1.5; fill: none; }
  .junc  { fill: var(--data); }
  .t     { fill: var(--ink); font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
           font-size: 19px; }
  .netbg { fill: var(--background); }
  .pulse { fill: var(--data); }
  @media (prefers-reduced-motion: reduce) { .pulse { display: none } }
</style>

<use href="#proc" x="100" y="100"/>
<use href="#proc" x="590" y="224"/>
<path class="wire" d="M250,138 H420 V262 H590"/>

<!-- travel along the routed net: the one place SMIL is allowed -->
<circle class="pulse" r="6">
  <animateMotion dur="6s" repeatCount="indefinite"><mpath href="#net1"/></animateMotion>
</circle>
```

Note the pulse references the **same** path the wire draws, so they can never drift.
And note `display: none` in the reduced-motion block — CSS cannot stop SMIL, so hiding
is the only way, and the checker requires it. The routed wire still shows the topology
with the pulse gone.

## Relaxes

Nothing. Near-black on white is the highest-contrast pairing available.

## Never

Diagonal or curved connections, two node kinds sharing a symbol, shading or gradients,
a net label sitting on a line without its white backing box, a signal that eases, or
color used decoratively instead of by signal class.
