# wood-grain

**Primary axis:** material · **Aliases:** `wood`, `timber`, `pyrography`

<div align="center">
<img src="../../docs/samples/wood-grain.svg" alt="The wood-grain specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">
</div>


## Intent

A finished timber panel: long wandering grain with visible figure, a varnish
highlight travelling across it, and labels burned into the surface. Choose it for
craft-adjacent projects, static-site and publishing tools, hobbyist hardware, and
anything whose identity is warm and made-by-hand rather than engineered.

**Compare `brushed-metal`:** the two are the same recipe at opposite ends of the
grain-ratio dial — metal at `1.6 0.006` (grain across), wood at `0.006 0.055`
(grain along, at much lower frequency, so it wanders). Metal is cool, machined and
uppercase; wood is warm, figured, and takes a slab serif.

## Palette treatment

Four browns and one accent. A mid timber ground (`#8A5C31`), a lighter figure
(`#A97438`), and two darker tones for grain lines and burned type (`#5A381A`,
`#3B2410`). The repo's accent appears once, at most, as an inlay or a brass fitting.
No greys, no blues — wood has a hue and everything on the panel shares it.

## Shape language

Radius `4`–`10`: timber edges are eased, not sharp and not rounded like a UI. Panels
butt together with a visible seam line at `1` in the darkest brown. Any joint should
be a real joint — a lap, a butt, a mitre — drawn honestly, because a floating panel
with no edge treatment reads as a photograph of wood, not as wood.

## Material / depth

The grain is a **ring-band `<pattern>`** displaced by low-frequency turbulence at
`scale="26"` — much larger than any other displacement in the catalog, which is what
makes the grain wander rather than jitter. The figure (the knot, the cathedral) is
where two ring bands converge; place one per panel, off-centre, and let the
displacement do the rest.

Depth is a subtle two-stop bevel on the panel edge, never a blurred shadow.

## Type treatment

A slab serif in caps — Rockwell, Bookman Old Style, Georgia — at `24`–`28`, one `44+`
title, tracked `+1`.

**Burned type is always two copies of the same string**, never one filtered text
node: a blurred dark copy underneath for the scorch halo, and a sharp dark glyph on
top. A single filtered `<text>` smears the letterforms and fails legibility.

**The underneath copy must carry `aria-hidden="true"`.** It is a scorch mark, not a
word, and without the attribute every burned label is announced twice.

## Motion character

Slow and material, like `brushed-metal`. A varnish highlight travelling along the
grain at `12s`, `linear`, low opacity, one pass per loop. A burned label may glow
between two opacities at `6s`. The panel never moves; wood is heavy.

## SVG recipes

The ring-band grain, the displacement, and burned type:

```svg
<defs>
  <pattern id="rings" width="240" height="18" patternUnits="userSpaceOnUse">
    <rect width="240" height="18" fill="#8a5c31"/>
    <rect width="240" height="5"  fill="#5a381a" opacity=".45"/>
    <rect width="240" height="2" y="11" fill="#a97438" opacity=".55"/>
  </pattern>
  <filter id="wander" x="-6%" y="-6%" width="112%" height="112%">
    <feTurbulence type="fractalNoise" baseFrequency="0.006 0.055" numOctaves="3"
                  seed="19" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="26"
                       xChannelSelector="R" yChannelSelector="G"/>
  </filter>
  <filter id="scorch" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="2.4"/>
  </filter>
</defs>
<style>
  svg { --timber:#8a5c31; --figure:#a97438; --grain:#5a381a; --burn:#3b2410; }
  .panel { fill: url(#rings); filter: url(#wander); }
  .seam  { stroke: var(--burn); stroke-width: 1; }
  .burn-lo { fill: var(--burn); opacity: .55; filter: url(#scorch);
             font-family: Rockwell, 'Bookman Old Style', Georgia, serif;
             font-size: 26px; letter-spacing: 1px; }
  .burn    { fill: var(--burn);
             font-family: Rockwell, 'Bookman Old Style', Georgia, serif;
             font-size: 26px; letter-spacing: 1px; }
  .varnish { animation: varnish 12s linear infinite; }
  @keyframes varnish { from { transform: translateX(-240px) } to { transform: translateX(1440px) } }
  @media (prefers-reduced-motion: reduce) { .varnish { animation: none } }
</style>

<rect class="panel" x="0" y="0" width="1200" height="620" rx="6"/>
<text class="burn-lo" x="120" y="300" aria-hidden="true">MILL</text>
<text class="burn"    x="120" y="300">MILL</text>
```

The varnish highlight is a low-opacity near-white parallelogram inside a `clipPath`
matching the panel, travelling **along** the grain direction — across it reads as a
wipe, not a finish.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| filter depth | 1 → **3** chained primitives per element |

Three covers a grain chain that desaturates or tints after displacing.

**Contrast is not relaxed, and burned type on raw timber does not clear it.**
`#3B2410` on `#8A5C31` measures **2.53:1**; on the lighter figure `#A97438` it is
still only **3.63:1**. Both look convincing and both fail. Two moves fix it, and one
of them has to be on the board:

- **Sand a lighter field for the label** — a pale timber tone around `#C9A678` under
  the text takes `#3B2410` to **6.37:1**, and reads exactly like a planed area
  waiting to be branded.
- **Reverse the label** — a near-white scorch-negative (`#F4ECE0`) on the mid timber
  measures **4.90:1** and passes.

Verify any substituted timber tone from the repo's own palette rather than assuming;
darkening the burn alone does not get you there, because the ground is the problem.

## Never

Burned type straight onto mid timber (measure it — it fails), a single filtered
`<text>` for burned type, a scorch copy without `aria-hidden`, grain running across
the panel's long axis, isotropic grain (that's canvas), a grey or blue anywhere, a
blurred drop shadow, a floating panel with no edge treatment, a second accent, or the
varnish crossing a label at full opacity.
