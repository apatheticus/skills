# codex-leonardo

**Primary axis:** era · **Aliases:** `codex`, `renaissance-study`, `iron-gall`

<div align="center">
<img src="../../docs/samples/codex-leonardo.svg" alt="The codex-leonardo specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">
</div>


## Intent

A Renaissance inventor's working page: brown iron-gall ink on aged rag paper,
cross-hatched shading, construction geometry left visible, and mirrored marginalia
crowding the edges. Choose it for research writeups, speculative or exploratory
design docs, and projects that want to read as *an investigation in progress* rather
than a finished specification.

**It reads as provisional, deliberately.** Like the rest of the hand-drawn family it
signals "study", not "deliverable" — which is right for an RFC and wrong for a
product landing page.

## Palette treatment

Two inks and a stain, no more. Aged ground (`#E5D8B8`), primary ink a warm brown
(`#5A4632`), a faint secondary ink (`#7A6248`) for hatching and annotation, and a
single stain tone (`#B99A62`) painted as two or three soft ellipses at low opacity.
The repo's accent is permitted once, desaturated toward the ink, as a rubrication —
a highlighted initial or one boxed term.

## Shape language

Nothing is true. Every shape runs through the roughen filter at displacement
`scale="2"` — the middle of the roughness dial documented in `styles.md`, between
`draughtsman-notebook`'s 1.6 and `lofi-wireframe`'s 2.4. Radius `0`–`4`. Stroke
`1.6` for primary contours, `0.8` for hatching and construction arcs. Leave the
construction geometry in: the circle a curve was struck from, the centreline, the
bisector. That visible working is the style.

## Material / depth

Depth is **cross-hatch**, never shadow. Layer two `<pattern>` hatches at unequal
angles and unequal weight — the codex convention, distinct from `rough-sketch`'s
single −41° hachure and drafting's 45°. Aged paper is low-frequency fractal noise
mapped to sepia through the fifth column of an `feColorMatrix`. No gradients, no
blur, no drop shadows anywhere.

## Type treatment

An old-style serif italic — Palatino, Iowan Old Style, Georgia — at `20`–`24` for
annotation and one `40+` page title. Mirrored marginalia is a
`<g transform="translate(x,y) scale(-1,1)">` wrapper.

**Mirrored text is decorative and must stay out of the meaning path.** It is normal
text in the DOM: a screen reader announces it unmirrored, in reading order, as if it
were ordinary prose. Never put a fact, a label, or anything the alt text depends on
inside a mirrored group, and give the group `aria-hidden="true"` when the string
would otherwise be read aloud.

## SVG recipes

Aged paper, the roughen filter at codex scale, and cross-hatch:

```svg
<defs>
  <filter id="rough" x="-8%" y="-8%" width="116%" height="116%">
    <feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="11" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="2"
                       xChannelSelector="R" yChannelSelector="G"/>
  </filter>
  <filter id="aged" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="3" seed="4"/>
    <feColorMatrix values="0 0 0 0 0.72  0 0 0 0 0.62  0 0 0 0 0.44  0 0 0 0.12 0"/>
  </filter>
  <pattern id="hatchA" width="8" height="8" patternUnits="userSpaceOnUse"
           patternTransform="rotate(38)">
    <line x1="0" y1="0" x2="0" y2="8" stroke="#5A4632" stroke-width="0.9"/>
  </pattern>
  <pattern id="hatchB" width="11" height="11" patternUnits="userSpaceOnUse"
           patternTransform="rotate(-24)">
    <line x1="0" y1="0" x2="0" y2="11" stroke="#7A6248" stroke-width="0.6"/>
  </pattern>
</defs>
<style>
  .ink   { stroke: var(--ink); stroke-width: 1.6; fill: none; filter: url(#rough); }
  .const { stroke: var(--faint); stroke-width: 0.8; fill: none; stroke-dasharray: 4 4;
           filter: url(#rough); }
  .note  { fill: var(--ink); font-family: Palatino, 'Iowan Old Style', Georgia, serif;
           font-size: 21px; font-style: italic; }
</style>

<g transform="translate(980,420) scale(-1,1)" aria-hidden="true">
  <text class="note" x="0" y="0">nota bene</text>
</g>
```

**Never filter the text.** Displacement destroys letterforms at these sizes; wobble
the shapes and let the italic serif carry the hand. Every hand-drawn style in this
catalog filters shape groups only.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| filter depth | 1 → **2** chained primitives per element |

Two is the roughen chain — turbulence feeding one displacement — and the aged-paper
chain, turbulence feeding one colour matrix. Contrast is not relaxed: `#5A4632` on
`#E5D8B8` is **6.30:1**, so codex has no contrast excuse.

## Never

Drop shadows or blur, solid fills where hatching belongs, a fact inside mirrored
text, filtering a `<text>` node, a third ink, hatching at equal angle and weight
(that reads as drafting), construction lines erased, or a draw-on entrance.
