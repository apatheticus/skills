# y2k-retrofuturist

**Primary axis:** era · **Aliases:** `y2k`, `retrofuture`, `chrome`

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
weight `1.5`–`2`, often a lighter tint of the fill rather than `ink`.

## Material / depth

Chrome is a vertical gradient with a hard light band across the upper third: light →
mid → *bright* → dark. That band is what makes it read as metal rather than a plain
gradient. Plastic is a fill at `70–85%` opacity with a small bright ellipse for the
specular highlight.

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
  <clipPath id="pill"><rect x="120" y="140" width="420" height="96" rx="48"/></clipPath>
</defs>
<style>
  svg { --background:#070b18; --ink:#eaf2ff; --accent:#ff3fb4; --accent-2:#4bf0ff; }
  .bg    { fill: var(--background); }
  .metal { fill: url(#chrome); }
  .t     { fill: var(--ink); font-weight: 700; letter-spacing: 3px; }
  .glint { fill: var(--ink); opacity: .5; animation: sweep 6s ease-in-out infinite; }
  @keyframes sweep {
    0%   { transform: translateX(-160px) }
    100% { transform: translateX(620px) }
  }
  @media (prefers-reduced-motion: reduce) { .glint { display: none } }
</style>

<rect class="metal" x="120" y="140" width="420" height="96" rx="48"/>
<g clip-path="url(#pill)">
  <rect class="glint" x="0" y="140" width="70" height="96" transform="skewX(-18)"/>
</g>
```

The glint starts and ends fully outside the clip, so `t=0` and `t=6s` look identical
and the `6s` cycle runs twice per `12s` loop cleanly. Reduced motion hides it
outright — the chrome still reads without the sweep.

## Relaxes

Nothing. Wide-tracked light text on a dark ground clears contrast easily; the chrome
gradient is decorative and carries no labels.

## Never

Text sitting directly on a chrome gradient (the light band destroys contrast — put it
on a solid pill instead), more than one sweep per board, a chrome gradient without the
hard light band (it just looks gray), skeuomorphic bevels on top of the plastic, or
lens-flare bitmaps — there is no remote image to load.
