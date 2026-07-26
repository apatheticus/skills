# y2k-retrofuturist

**Primary axis:** era · **Aliases:** `y2k`, `retrofuture`, `chrome`

<div align="center">
<img src="../../docs/samples/y2k-retrofuturist.svg" alt="The y2k-retrofuturist specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">
</div>


## Intent

The turn-of-the-millennium future: chrome gradients, translucent plastic, wide
letter-spacing, lens flares implied rather than drawn, and an optimism about
technology that hadn't been complicated yet. Choose it for nostalgic, playful, and
media projects.

## Palette treatment

Cool metallics plus one hot accent. Silver-blue gradients carry the chrome; the repo's
brightest accent becomes the "active" color — a hot pink, cyan, or acid green.
`background` is either near-black (space) or a pale blue-white (plastic). Two-stop
gradients only; three-stop for chrome specifically.

## Shape language

Capsules and lozenges — radius equal to half the height, so everything is a pill.
Ellipses, swooshes, and one long tapering curve as a compositional spine. Stroke
weight `1.5`–`2`, and the on-idiom stroke is an **iridescent gradient** rather than a
flat tint: a multi-stop `<linearGradient>` running cyan → violet → hot pink along the
element. It is the era's signature edge treatment and costs four stops.

The **perspective grid** — a floor of horizontal rules converging on a vanishing point
with verticals fanning from it — is the other era cue worth having. Draw it once, at
low opacity, behind everything, and let it establish the horizon the composition sits
on.

## Material / depth

Chrome is a vertical gradient with a hard light band across the upper third: light →
mid → *bright* → dark. That band is what makes it read as metal rather than a plain
gradient. **Break to a dark stop at the bottom**, not to mid-grey: the abrupt jump to
near-black at the base is what reads as a reflected horizon, and a chrome ramp that
fades out evenly just looks like a grey gradient.

Plastic is a fill at `70–85%` opacity with a small bright ellipse for the specular
highlight.

A **soft-band scanline sweep** is the on-idiom overlay: a wide, low-opacity horizontal
band travelling down the board, its edges feathered by a gradient rather than hard.
Keep it under 3 Hz — WCAG 2.3 — which at these canvas heights means `6s` or `12s`,
never a fast flicker.

## Type treatment

System sans, `600`–`700`, **wide tracking** (`+2` to `+4`) on titles — the single
most recognisable cue of the era. Uppercase titles, sentence-case body. Mono for
anything that should look like telemetry. A thin outline around display text is
on-idiom; keep the fill at full contrast.

## Motion character

Sweeping and glossy. A specular highlight travelling across chrome, a slow rotation of
an orbital element, a pill sliding along its spine. Long easing, `4s` or `6s`, nothing
abrupt. One "scan" pass is the signature move.

## SVG recipes

Chrome with a travelling specular sweep:

```svg
<defs>
  <linearGradient id="chrome" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0"   stop-color="#dfe9f5"/>
    <stop offset="0.34" stop-color="#8fa6c4"/>
    <stop offset="0.40" stop-color="#ffffff"/>
    <stop offset="0.62" stop-color="#5b7196"/>
    <stop offset="1"   stop-color="#2b3a52"/>
  </linearGradient>
  <linearGradient id="irid" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0"   stop-color="#4bf0ff"/>
    <stop offset="0.5" stop-color="#7b2fff"/>
    <stop offset="1"   stop-color="#ff3fb4"/>
  </linearGradient>
  <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0"   stop-color="#4bf0ff" stop-opacity="0"/>
    <stop offset="0.5" stop-color="#4bf0ff" stop-opacity=".22"/>
    <stop offset="1"   stop-color="#4bf0ff" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="pill"><rect x="120" y="140" width="420" height="96" rx="48"/></clipPath>
</defs>
<style>
  svg { --background:#070b18; --ink:#eaf2ff; --accent:#ff3fb4; --accent-2:#4bf0ff; }
  .bg    { fill: var(--background); }
  .metal { fill: url(#chrome); }
  .edge  { stroke: url(#irid); stroke-width: 2; fill: none; }
  .t     { fill: var(--ink); font-weight: 700; letter-spacing: 3px; }
  .glint { fill: var(--ink); opacity: .5; animation: sweep 6s ease-in-out infinite; }
  /* one pass per 12s: 0.083 Hz, far under the 3 Hz ceiling */
  .band  { fill: url(#scan); animation: band 12s linear infinite; }
  @keyframes sweep {
    0%   { transform: translateX(-160px) }
    100% { transform: translateX(620px) }
  }
  @keyframes band { from { transform: translateY(-120px) } to { transform: translateY(640px) } }
  @media (prefers-reduced-motion: reduce) { .glint, .band { display: none } }
</style>

<rect class="metal" x="120" y="140" width="420" height="96" rx="48"/>
<rect class="edge"  x="120" y="140" width="420" height="96" rx="48"/>
<g clip-path="url(#pill)">
  <rect class="glint" x="0" y="140" width="70" height="96" transform="skewX(-18)"/>
</g>
<rect class="band" x="0" y="0" width="1200" height="120"/>
```

The glint starts and ends fully outside the clip, so `t=0` and `t=6s` look identical
and the `6s` cycle runs twice per `12s` loop cleanly. Reduced motion hides it
outright — the chrome still reads without the sweep.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| filter depth | 1 → **2** chained primitives per element |

Two covers a glow built as blur plus merge on the one active element. **Contrast is
not relaxed**, and this style's failure mode is specific: a chrome ramp is not one
ground, it is four, and a label crossing it is measured against the worst of them.
Light ink `#EAF2FF` sits at **10.19:1** over the ramp's dark base, **2.21:1** over
its mid-tone, and **1.13:1** over the bright band — the same text, legible at one end
of the pill and invisible at the other. Wide-tracked light text on a dark ground
clears the floor easily; text on chrome cannot. Put it on a solid pill.

## Never

Text sitting directly on a chrome gradient (the light band destroys contrast — put it
on a solid pill instead), a corner radius that isn't half the height, more than one
sweep per board, a chrome gradient without the hard light band or without the dark
break at the base (it just looks grey), a scanline above 3 Hz, a flat stroke where the
iridescent gradient belongs, skeuomorphic bevels on top of the plastic, or lens-flare
bitmaps — there is no remote image to load.
