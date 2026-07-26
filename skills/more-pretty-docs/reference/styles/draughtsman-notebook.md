# draughtsman-notebook

**Primary axis:** era · **Aliases:** `engineers-notebook`, `graphite-draft`

<div align="center">
<img src="../../docs/samples/draughtsman-notebook.svg" alt="The draughtsman-notebook specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">
</div>


## Intent

An engineer's bound notebook: a faint blue-grey grid printed on warm stock, graphite
line work that is precise but visibly human, construction lines left in, and
annotations in a neat hand. Choose it for design records, ADRs, systems analysis and
anything that should read as *considered working* — rigorous, but not yet typeset.

**Compare the three drafting neighbours.** `blueprint` is a medium (cyanotype,
reproduction). `schematic` is a notation (symbol alphabet, net labels).
`patent-drawing` is a *convention* (37 CFR 1.84, reference characters, no colour).
This one is a *hand*: the same rigour, drawn by a person, on their own paper. If the
visual should look reasoned-through rather than issued, you're here.

**It reads as provisional.** Right for an internal design record, wrong for a
customer-facing proposal.

## Palette treatment

Warm stock (`#F4F2EA`), graphite (`#3A414D`) for primary line work, a printed grid
in pale blue-grey (`#B9C4CE`), and a lighter graphite (`#6E7683`) for construction
lines and dimension annotation. The repo's accent appears once, as the single thing
being called out. Four values total; a fifth turns it into a poster.

## Shape language

Displacement `scale="1.6"` — near the ruled end of the roughness dial in `styles.md`,
between `patent-drawing`'s 0.7 and `codex-leonardo`'s 2.0. Just enough deviation to
read as drawn by hand with a straightedge. Radius `0`–`4`. Stroke `1.7` for
primary contours, `0.9` for construction and dimension lines, `0.9` dashed for
hidden edges. Corners overshoot slightly, as a pencil does.

## Material / depth

Graphite on paper. Depth is line weight and hachure, never shadow. The one texture
is graphite grain: full-frame `feTurbulence` at high `baseFrequency` (`1.3`),
desaturated, alpha cut to about `0.13`, composited `multiply`. Drafting hachure runs
at 45° at a single weight — distinct from `codex-leonardo`'s two unequal angles.
Absolutely no drop shadows, blur or gradients.

## Type treatment

A neat handwriting face in caps — Architects Daughter, with Segoe Print and Bradley
Hand behind it — at `20`–`24`, plus mono for dimensions and part numbers, plus one
`40+` sheet title.

**Say what the reader will actually see.** These faces are named with system
fallbacks and are never fetched, so on GitHub the chain usually lands on Segoe
Print, Bradley Hand or Comic Sans MS. That is degraded but still hand-lettered.
Don't promise the exemplar's exact face; if fidelity matters, subset the font and
embed it as base64 — a remote `@import` or font `href` is a hard gate failure.

## Motion character

Steady-state, quiet, mechanical. A dimension line's dash pattern creeps along its own
length; a construction arc breathes between two opacities; the accent callout pulses
once per long cycle. `8s` or `12s`, `linear` or `ease-in-out`. Two motions at most.
**No draw-on entrance** — the page is already drawn.

## SVG recipes

The roughen filter at notebook scale, the graphite grain, and the printed grid:

```svg
<defs>
  <filter id="rough" x="-8%" y="-8%" width="116%" height="116%">
    <feTurbulence type="fractalNoise" baseFrequency="0.028" numOctaves="2" seed="3" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="1.6"
                       xChannelSelector="R" yChannelSelector="G"/>
  </filter>
  <filter id="graphite" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="1.3" numOctaves="1" seed="9"/>
    <feColorMatrix type="saturate" values="0"/>
    <feComponentTransfer><feFuncA type="linear" slope="0.13"/></feComponentTransfer>
  </filter>
  <pattern id="rule" width="26" height="26" patternUnits="userSpaceOnUse">
    <path d="M26 0 L0 0 0 26" fill="none" stroke="#B9C4CE" stroke-width="0.7"/>
  </pattern>
</defs>
<style>
  .stock { fill: var(--stock); }
  .grid  { fill: url(#rule); }
  .main  { stroke: var(--graphite); stroke-width: 1.7; fill: none; filter: url(#rough); }
  .const { stroke: var(--light); stroke-width: 0.9; fill: none; stroke-dasharray: 5 4;
           filter: url(#rough); }
  .hand  { fill: var(--graphite); font-size: 22px; letter-spacing: 0.5px;
           font-family: 'Architects Daughter', 'Segoe Print', 'Bradley Hand',
                        'Comic Sans MS', cursive; }
  .tooth { fill: var(--graphite); filter: url(#graphite); mix-blend-mode: multiply; }
  .creep { animation: creep 8s linear infinite; }
  @keyframes creep { from { stroke-dashoffset: 18 } to { stroke-dashoffset: 0 } }
  @media (prefers-reduced-motion: reduce) { .creep { animation: none; stroke-dashoffset: 0 } }
</style>
```

**Never filter the text.** Displacement destroys letterforms; wobble the shapes and
let the handwriting face carry the hand. The filter region must be expanded
(`x="-8%" width="116%"`) or displaced edges clip.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| filter depth | 1 → **3** chained primitives per element |

Three is the graphite-grain chain — turbulence, desaturate, alpha. The roughen chain
only needs two. Contrast is not relaxed: `#3A414D` on `#F4F2EA` is **9.17:1**.

## Never

Colour beyond the four values plus one accent, drop shadows, gradients, blur, a
filtered `<text>`, a remote font, a draw-on entrance, erased construction lines,
hachure at two angles (that's codex), or displacement above `2` (that's sketched,
not drafted).
