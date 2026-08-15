# patent-drawing

**Primary axis:** era · **Aliases:** `patent`, `uspto-figure`, `figure-drawing`

<div align="center">
<img src="../../docs/samples/patent-drawing.svg" alt="The patent-drawing specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">
</div>


## Intent

A formal disclosure figure: black line work on white, no colour, no shading, every
part carrying a numbered reference character on a leader line, and a `FIG. 1` caption
underneath. Choose it when the visual should read as a *claim* — a mechanism
described precisely enough that someone could build it — for protocol
specifications, algorithms and reference implementations.

**The one style here with a real external convention.** Reference characters are
conventionally even numbers, leader lines never cross, and colour and shading are not
accepted. If someone asks for a patent-style figure **for an actual filing**, point
them at 37 CFR 1.84 rather than treating this as an aesthetic — this spec produces
the look, not a compliant drawing.

## Palette treatment

Black (`#000000`) on white (`#FFFFFF`). That is the entire palette, and it is the
one style in the catalog that does **not** take the repo's brand colours: colour is
not permitted in a patent figure, and admitting one accent would break the only thing
the style is about. Tone is achieved with hatch density, never with grey.

## Shape language

Displacement `scale="0.7"` — the ruled end of the roughness dial in `styles.md`,
below `1`, so it reads as inked with instruments rather than sketched. Radius `0`–`2`.
Stroke `1.5`, **uniform**, with square caps: a patent figure has no line-weight
hierarchy, because every feature is equally disclosed. Section views use 45° hatching
at a single weight and pitch.

## Material / depth

None. No shadow, no gradient, no blur, no fill, no grey. Depth is hatching and
overlap only. Hidden edges are dashed at the same `1.5` weight.

## Type treatment

A geometric sans in caps — Century Gothic, Futura, Trebuchet MS — at `20`–`22` for
reference characters and the figure caption, one `40+` sheet title if the layout
wants one. Reference characters sit at the outer end of a leader line, never on the
geometry, and **never touch or cross another leader**. Prefer even numbers (`102`,
`104`, `106`) and keep them ordered around the figure.

## Motion character

The least motion of any style in the catalog, and steady-state. One leader line's
dash pattern creeps, or one reference character breathes between two opacities, at
`8s`, `linear`. That is the budget. **No draw-on entrance** — a disclosure figure is
a fixed document, and animating it into existence contradicts what it claims to be.

## SVG recipes

The roughen filter at patent scale, uniform stroke, hatching and a leader:

```svg
<defs>
  <filter id="rough" x="-8%" y="-8%" width="116%" height="116%">
    <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="1" seed="8" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="0.7"
                       xChannelSelector="R" yChannelSelector="G"/>
  </filter>
  <pattern id="sect" width="9" height="9" patternUnits="userSpaceOnUse"
           patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="9" stroke="#000" stroke-width="1"/>
  </pattern>
</defs>
<style>
  .sheet { fill: #ffffff; }
  .ln    { stroke: #000000; stroke-width: 1.5; stroke-linecap: square; fill: none;
           filter: url(#rough); }
  .hid   { stroke: #000000; stroke-width: 1.5; stroke-linecap: square; fill: none;
           stroke-dasharray: 7 5; filter: url(#rough); }
  .sect  { fill: url(#sect); filter: url(#rough); }
  .ref   { fill: #000000; font-size: 21px; letter-spacing: 1px;
           font-family: 'Century Gothic', Futura, 'Trebuchet MS', sans-serif; }
  .cap   { fill: #000000; font-size: 22px; letter-spacing: 2px;
           font-family: 'Century Gothic', Futura, 'Trebuchet MS', sans-serif; }
  .creep { animation: creep 8s linear infinite; }
  @keyframes creep { from { stroke-dashoffset: 12 } to { stroke-dashoffset: 0 } }
  @media (prefers-reduced-motion: reduce) { .creep { animation: none; stroke-dashoffset: 0 } }
</style>

<rect class="sheet" x="0" y="0" width="1200" height="620"/>
<rect class="ln"    x="200" y="160" width="240" height="140"/>
<line class="ln"    x1="440" y1="180" x2="512" y2="146"/>   <!-- leader, never crossing -->
<text class="ref"   x="520" y="152">102</text>
<text class="cap"   x="200" y="560">FIG. 1</text>
```

**Never filter the text.** Reference characters must be crisp; only shape groups go
through the roughen filter.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| filter depth | 1 → **2** chained primitives per element |

Two is the roughen chain: turbulence feeding one displacement. Black on white is the
highest contrast available, so nothing else needs relaxing — and nothing else may.

## Never

Colour of any kind, including the repo's accent. Grey fills, shading, gradients,
shadows, varying stroke weights, crossing leader lines, a reference character sitting
on the geometry, a filtered `<text>`, a draw-on entrance, or presenting the output as
suitable for an actual filing.
