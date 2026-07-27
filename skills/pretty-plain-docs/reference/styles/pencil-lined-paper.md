# pencil-lined-paper

**Primary axis:** material · **Aliases:** `lined-paper`, `graphite-notes`, `legal-pad`

<div align="center">
<img src="../../docs/samples/pencil-lined-paper.svg" alt="The pencil-lined-paper specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">
</div>


## Intent

A page torn out of a notebook: printed blue rules, a red margin line down the left,
graphite handwriting sitting *on* the ruling, and the tooth of the paper visible
through it. Choose it for notes, changelog narratives, teaching material, and
retrospectives — anything that should read as something a person wrote down while
thinking.

**Compare `draughtsman-notebook`:** that one is *drafting* on notebook stock —
construction lines, dimensions, a straightedge. This one is *writing* — the ruling
governs the layout, the hand is loose, and there are no instruments. If the content
is prose and sketches, you're here; if it's a measured drawing, you're there.

**It reads as provisional**, like the rest of the paper family. Internal notes and
narrative pieces, not proposals.

## Palette treatment

Warm white stock (`#FCFBF6`), printed rules in a pale blue (`#AFC6DB`), one red-pink
margin line (`#E3A6A6`), and graphite (`#4A4A52`) for everything written. The repo's
accent appears once, as a highlighter pass or a circled term. Five values total.

## Shape language

**The ruling is the grid.** Every baseline sits on a rule, and every box aligns to a
rule boundary — that discipline is what separates this from generic hand-drawn.
Rules at a constant pitch (26–32 units), stroke `1`. Written line work at `1.6`,
loose, radius `0`–`6`. Boxes are drawn around content after the fact, so they
overshoot at the corners.

## Material / depth

Paper and graphite, nothing else. Depth is pressure: heavier graphite reads as
nearer. The one texture is graphite grain — full-frame `feTurbulence` at high
`baseFrequency` (`1.3`), desaturated, alpha cut to about `0.13`, blended `multiply`.
No shadows, no gradients, no blur.

## Type treatment

A loose handwriting face — Caveat, with Bradley Hand and Segoe Script behind it — at
`22`–`26` for written content, and one `40+` heading. Every baseline lands on a
printed rule.

**The named faces are never fetched.** On GitHub the chain lands on Bradley Hand,
Segoe Script or Comic Sans MS. Say so rather than promising the exemplar's look; a
remote font `href` or `@import` is a hard gate failure. Where fidelity matters,
subset the face and embed it as base64.

## SVG recipes

Ruling, margin, graphite grain and the roughened hand:

```svg
<defs>
  <pattern id="rules" width="1" height="30" patternUnits="userSpaceOnUse">
    <line x1="0" y1="30" x2="1" y2="30" stroke="#AFC6DB" stroke-width="1"/>
  </pattern>
  <filter id="rough" x="-8%" y="-8%" width="116%" height="116%">
    <feTurbulence type="fractalNoise" baseFrequency="0.032" numOctaves="2" seed="6" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="2"
                       xChannelSelector="R" yChannelSelector="G"/>
  </filter>
  <filter id="graphite" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="1.3" numOctaves="1" seed="9"/>
    <feColorMatrix type="saturate" values="0"/>
    <feComponentTransfer><feFuncA type="linear" slope="0.13"/></feComponentTransfer>
  </filter>
</defs>
<style>
  svg { --stock:#fcfbf6; --rule:#afc6db; --margin:#e3a6a6; --lead:#4a4a52; }
  .stock  { fill: var(--stock); }
  .ruling { fill: url(#rules); }
  .margin { stroke: var(--margin); stroke-width: 1.4; }
  .hand   { stroke: var(--lead); stroke-width: 1.6; fill: none; filter: url(#rough); }
  .write  { fill: var(--lead); font-size: 24px;
            font-family: Caveat, 'Bradley Hand', 'Segoe Script', 'Comic Sans MS', cursive; }
  .tooth  { fill: var(--lead); filter: url(#graphite); mix-blend-mode: multiply; }
</style>

<rect class="stock"  x="0" y="0" width="1200" height="620"/>
<rect class="ruling" x="0" y="0" width="1200" height="620"/>
<line class="margin" x1="120" y1="0" x2="120" y2="620"/>
<rect class="tooth"  x="0" y="0" width="1200" height="620"/>

<text class="write" x="152" y="180">source → transform → store</text>
```

Baselines must be multiples of the rule pitch offset by the pattern phase, or the
handwriting floats and the whole illusion collapses.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| filter depth | 1 → **3** chained primitives per element |

Three is the graphite-grain chain — turbulence, desaturate, alpha. Contrast is not
relaxed: `#4A4A52` on `#FCFBF6` is **8.47:1**. The pale blue ruling is decorative
and never carries text.

## Never

Text off the ruling, a shadow, a gradient, a blur, a filtered `<text>`, a remote
font, a draw-on entrance, a second accent, ruling used as a decorative texture rather
than the layout grid, or graphite grain applied to type.
