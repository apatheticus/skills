# watercolor

**Primary axis:** material · **Aliases:** `watercolour`, `wash`, `aquarelle`

<div align="center">
<img src="../../docs/samples/watercolor.svg" alt="The watercolor specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">
</div>


## Intent

Pigment in water on cold-press paper: soft-edged washes that darken where they pool
at an edge, overlaps that multiply into a third colour, and a fine ink line laid over
the top. Choose it for narrative and editorial pieces, essays, community and
onboarding material — visuals whose job is warmth rather than precision.

**Compare `oil-impasto`:** both are painted, but watercolour is *transparent* —
overlaps multiply, the paper shows through, and nothing is raised. Impasto is opaque
and lit. If the medium should feel light, pick this.

## Contrast — read this before choosing it

**Watercolour puts mid-tone pigment on a mid-tone ground, and label contrast fails
4.5:1 on its native palette. The floor is not relaxed.** A compliant watercolour
visual therefore needs one of two moves on every `<text>`: a solid backing shape in
the paper tone under the label, or an ink far darker than any wash on the board
(a near-black `#2A2622` reads correctly as the pen line over the wash). Both are
authentic to the medium — a watercolourist reserves white paper for the ink work.

Declared honestly: this is a **decorative style**, and it also **reads as
provisional** the way the hand-drawn family does. Use it where labels carry no load
and the alt text does the work; if the diagram's meaning lives in its labels, pick
something else.

## Palette treatment

Warm paper (`#FBF7EE`) and three transparent pigments from the repo's palette pushed
soft: a slate blue (`#5A6BA8`), a rose (`#C4738C`), and an ochre (`#D2A24C`), each
laid at `0.45`–`0.6` opacity with `mix-blend-mode: multiply`. **Overlaps are the
palette**: two washes crossing make the fourth colour, and you should compose so at
least one overlap happens. No opaque fills, no white paint — white is the paper.

## Shape language

Soft masses, not shapes. Every wash is a `<path>` with irregular edges, displaced at
`scale="17"` through a low-frequency turbulence and blurred *after* displacement —
that ordering is what gives the soft edge; blurring first gives mush. Radius is
meaningless. The one crisp element is the ink line, at `1.2`–`1.6`, drawn last and
deliberately not registered exactly to the wash beneath it.

## Material / depth

Transparency and edge darkening. Depth is **how many washes have crossed**, nothing
else — no shadow, no gradient doing lighting, no blur used as a shadow. Edge
darkening (the pooling at a wash boundary) is the tell: a second, slightly smaller
copy of the wash path at higher opacity, offset a unit or two.

Paper tooth is a second, isotropic turbulence at `0.5` over the full frame,
`multiply` blend, low alpha. See the grain-ratio axis in `styles.md` — paper sits at
the isotropic end, with canvas.

## Type treatment

A script or calligraphic face — Gabriola, Segoe Script, with Caveat behind them — at
`24`–`28`, one `40+` title, **never filtered and never washed**. It sits at full
opacity on its reserved paper or in the dark ink. The contrast between a controlled
pen line and an uncontrolled wash is the composition; making the lettering soft too
turns the whole thing to fog.

These faces are named with system fallbacks and are never fetched, so the chain often
lands on Segoe Script or Comic Sans MS. Say so rather than promising Gabriola; a
remote font `href` or `@import` is a hard gate failure.

## SVG recipes

The wash filter — displace, *then* blur — plus edge darkening and paper tooth:

```svg
<defs>
  <filter id="wash" x="-12%" y="-12%" width="124%" height="124%">
    <feTurbulence type="fractalNoise" baseFrequency="0.014" numOctaves="3" seed="21" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="17"
                       xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feGaussianBlur in="d" stdDeviation="2.6"/>
  </filter>
  <filter id="tooth" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.5" numOctaves="1" seed="3"/>
    <feColorMatrix type="saturate" values="0"/>
    <feComponentTransfer><feFuncA type="linear" slope="0.11"/></feComponentTransfer>
  </filter>
</defs>
<style>
  svg { --paper:#fbf7ee; --blue:#5a6ba8; --rose:#c4738c; --ochre:#d2a24c;
        --pen:#2a2622; }
  .paper { fill: var(--paper); }
  .wash  { filter: url(#wash); mix-blend-mode: multiply; opacity: .52; }
  .pool  { filter: url(#wash); mix-blend-mode: multiply; opacity: .30; }
  .pen   { stroke: var(--pen); stroke-width: 1.4; fill: none; }
  .cal   { fill: var(--pen); font-size: 26px;
           font-family: Gabriola, 'Segoe Script', Caveat, cursive; }
  .tooth { fill: var(--pen); filter: url(#tooth); mix-blend-mode: multiply; }
</style>

<rect class="paper" x="0" y="0" width="1200" height="620"/>
<path class="wash" fill="var(--blue)"  d="M140 160 h300 v150 h-300 Z"/>
<path class="pool"         fill="var(--blue)"  d="M148 168 h284 v134 h-284 Z"/>
<path class="wash"         fill="var(--ochre)" d="M380 210 h280 v150 h-280 Z"/>
<path class="pen" d="M142 158 h304 v154 h-304 Z"/>
<rect class="tooth" x="0" y="0" width="1200" height="620"/>
```

## Relaxes

| Gate | Default → floor |
| --- | --- |
| filter depth | 1 → **3** chained primitives per element |

Three is the wash chain — turbulence, displacement, blur. **Contrast is not
relaxed**; see the section above, which is why the reserved-paper or dark-ink rule is
mandatory rather than advisory.

## Never

A label without reserved paper or dark ink, a filtered or washed `<text>`, an opaque
fill, white paint, blur applied before displacement, a drop shadow, a board with no
overlap (that's flat colour with soft edges, not watercolour), a bloom-in entrance,
or use for a diagram whose meaning lives in its labels.
