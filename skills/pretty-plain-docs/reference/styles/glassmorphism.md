# glassmorphism

**Primary axis:** material · **Aliases:** `glass`, `frosted`, `aero`

<div align="center">
<img src="../../docs/samples/glassmorphism.svg" alt="The glassmorphism specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">
</div>


## Intent

Frosted glass panels floating over a field of coloured light, lit by a single
key light. Choose it for media projects, overlay-heavy UIs, and showcase
repos where the visual is partly the product. It costs the most bytes of any style
here except `maximalist`; read the whole recipe before committing.

**The illusion depends on one idea: the glass samples what is actually behind it.**
Every shortcut that fakes that — a flat white overlay, a baked blur texture, a
static gradient standing in for the backdrop — reads as plastic. If you change
nothing else from this document, keep the real backdrop sample.

Photorealism here comes from stacking eight cheap passes, not from one clever
filter. Omitting any single pass is survivable; omitting three is not.

## Palette treatment

The **ground** carries the colour: four or five large orbs, each a
`<radialGradient>` from a saturated hue at `0.7–0.95` down to the same hue at `0`,
the whole group blurred at `stdDeviation="38"`. Spread them to the canvas edges and
let them bleed off — a contained orb looks like a sticker. Six orbs starts to read
as mud once blurred.

Hues that work: magenta `#FF2D8A`, cyan `#22D3EE`, amber `#FFB020`,
violet `#7C5CFF`, green `#34D399`.

Under them, a **base wash**: a full-bleed rect with a diagonal `<linearGradient>`,
three stops of deep desaturated colour (`#150A2C → #2B0F4C → #0A1032`). This is the
darkness the glass tints toward, and keeping it dark and desaturated is what makes
the contrast strategy below work.

`ink` is near-solid — text is the one thing that is never translucent.

## Shape language

Radius `12–24` on panels. Large soft orbs behind, crisp rounded rectangles in front.

**The rim stroke is an asymmetric gradient, and a uniform one is the single most
common tell of a fake.** Real glass edges are never evenly bright: hot where the key
light strikes, cool along the shaded edges, with a weaker bounce highlight at the
far corner. Run a diagonal `<linearGradient>` at `.90 → .16 → .06 → .48`. A flat
`0.45` stroke reads as an outlined rectangle.

Then a second, **inner rim**: `0.8`px white at `opacity:.11`, inset `1.4`px with the
radius reduced by the same amount. That is what reads as glass *wall thickness*.

## Material / depth

Here is the constraint that shapes everything: **SVG has no `backdrop-filter`.** A
panel cannot blur what is behind it. The workaround is to draw the background once
as `<g id="scene">` and then `<use>` it again, filtered, clipped to each surface.

That duplication is geometry, not decoration, and it is why this style gets a raised
byte ceiling and a raised filter-depth ceiling.

### The layer stack

Order is load-bearing. Build bottom to top exactly as listed.

**Once, at the bottom** — `<g id="scene">`: base wash rect, then the blurred orb
group. It must be addressable, because every glass surface references it.

**Contact shadow, before any glass** — one blurred dark rect per surface, inset
horizontally and offset down from the panel, `fill` the wash's darkest stop at
`opacity:.5`, blurred at `stdDeviation="16"`. Without this the panels sit *in* the
background rather than above it.

**Per surface, inside its `clipPath`:**

| Pass | Element | Purpose |
| --- | --- | --- |
| 1 | `<use href="#scene">` with `filter:url(#frost)` | the real backdrop blur |
| 2 | scrim rect, the wash's darkest stop at `.58` | darkens the sample — **this is what makes white text legible** |
| 3 | tint rect, `<linearGradient>` white `.20 → .05` on a `0,0 → .35,1` axis | surface tint, brighter on the key-light side |
| 4 | `<use href="#pool">` | the specular highlight — see The light pool |
| 5 | grain rect, `filter:url(#grain)`, `opacity:.14`, `mix-blend-mode:overlay` | frost micro-texture; skip it and the glass reads as plastic |
| 6 | top-edge highlight, `2.5`px white rect at `opacity:.30` | light catching the top bevel |

**Per surface, outside its `clipPath`:** the rim stroke, then the inner rim.

### Cap it

**At most three glass panels per board**, plus thin connectors and one footer strip.
Beyond that, split into two visuals. Each filtered `<use href="#scene">` re-renders
and re-filters the entire background, so cost scales with surface count. Past about
six surfaces, restructure: put every surface sharing a filter into **one**
`clipPath` with multiple children (the clip is their union) and draw **one** filtered
`<use>` clipped to it. Per-surface scrim and tint rects stay separate.

### `frost` vs `refract`

Two filters, and using the wrong one is visible.

- **`frost`** — a plain `feGaussianBlur` — on large flat surfaces. The eye reads them
  as flat panes, and displacement over a large area looks like a smear.
- **`refract`** — blur, then `feTurbulence` displaced through `feDisplacementMap` —
  on small or curved elements: thin connector bars, spheres, anything that should
  behave as a lens. **The displacement is what makes a curved surface read as solid
  glass rather than a hole**, and it is the pass whose absence makes a board read as
  a flat frost. The gate requires it.

**Tuning `stdDeviation` on `frost`.** Below about `8` the background stays legible
through the panel and competes with the text. Above about `22` the panel goes
uniformly grey, the backdrop sample stops being visible as *this* background, and
the effect dies. `12–17` is the usable band; the specimen uses `14`.

## Type treatment

System sans, `400`–`500`. Never thin. Text sits on glass, which is a low-contrast
ground, so pick the scrim alpha *after* measuring — see Relaxes.

Every label group also carries **`filter:url(#inkShadow)`**, a `1`px-offset dark drop
shadow at `stdDeviation="1.6"`. It is the second of the two contrast mechanisms and
it is not optional.

## The light pool

There is no motion here, but there is still **one light**, and it is a *material*
pass rather than a motion one — a glass surface with no specular highlight reads as
matte, not as glass.

The most common failure is one highlight per panel, which reads as three separate
gleams rather than a light source. Use **one pool, referenced everywhere**, parked
off-centre with a `transform` attribute on each `<use>` so the key light is
asymmetric and agrees with the rim gradient:

```svg
<radialGradient id="sheen">
  <stop offset="0"   stop-color="#fff" stop-opacity=".20"/>
  <stop offset=".22" stop-color="#fff" stop-opacity=".16"/>
  <stop offset=".42" stop-color="#fff" stop-opacity=".10"/>
  <stop offset=".62" stop-color="#fff" stop-opacity=".05"/>
  <stop offset=".82" stop-color="#fff" stop-opacity=".015"/>
  <stop offset="1"   stop-color="#fff" stop-opacity="0"/>
</radialGradient>
<g id="pool">
  <ellipse cx="600" cy="222" rx="140" ry="230" fill="url(#sheen)"
           transform="rotate(-20 600 222)"/>
</g>
```

Then inside every clip group, including the connector bars:
`<use href="#pool" xlink:href="#pool" transform="translate(-170,0)"/>`

The gradient must fall to exactly `stop-opacity="0"` at offset `1`, or the ellipse
boundary is visible as a hard edge across the glass.

**Direction, not travel.** A static diagram still has to say which way data flows.
A chevron on each connector does it; a dot does not, because a stationary dot on a
bar is ambiguous about whether it is moving and which way.

**One thing a static loses, and it is worth knowing.** Moving colour behind the
panels is the strongest evidence that the blur is a live backdrop sample rather
than a baked texture — a still frame cannot distinguish the two. The static
compensates with refraction: the connector bars visibly distort what is behind
them, which no baked texture reproduces. That is another reason `refract` is a
required primitive here rather than a nicety.

## SVG recipes

The filters. Copy them verbatim — filter regions must be generous, because a blur
clipped by its own region produces a hard rectangular edge that is very hard to
diagnose later.

```svg
<filter id="oblur"   x="-60%" y="-60%" width="220%" height="220%">
  <feGaussianBlur stdDeviation="38"/>
</filter>
<filter id="frost"   x="-40%" y="-40%" width="180%" height="180%">
  <feGaussianBlur stdDeviation="14"/>
</filter>
<filter id="refract" x="-60%" y="-60%" width="220%" height="220%">
  <feGaussianBlur stdDeviation="4" result="b"/>
  <feTurbulence type="fractalNoise" baseFrequency=".018" numOctaves="2" seed="5" result="t"/>
  <feDisplacementMap in="b" in2="t" scale="18" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="4" stitchTiles="stitch"/>
  <feColorMatrix type="saturate" values="0"/>
</filter>
<filter id="inkShadow" x="-30%" y="-40%" width="160%" height="180%">
  <feDropShadow dx="0" dy="1" stdDeviation="1.6" flood-color="#0A1032" flood-opacity=".8"/>
</filter>
<filter id="cast" x="-60%" y="-60%" width="220%" height="220%">
  <feGaussianBlur stdDeviation="16"/>
</filter>
```

One surface, whole stack:

```svg
<g id="scene">
  <rect x="0" y="0" width="1200" height="460" fill="url(#base)"/>
  <g filter="url(#oblur)">
    <circle cx="200" cy="500" r="200" fill="url(#oA)"/>
    <!-- three or four more, bleeding off the edges -->
  </g>
</g>

<!-- contact shadow first -->
<rect x="94" y="206" width="272" height="134" rx="22"
      fill="var(--wash-c)" opacity=".5" filter="url(#cast)"/>

<g clip-path="url(#n1)">
  <use href="#scene" xlink:href="#scene" filter="url(#frost)"/>   <!-- 1 real backdrop -->
  <rect class="scrim" x="80" y="180" width="300" height="150"/>   <!-- 2 -->
  <rect class="tint"  x="80" y="180" width="300" height="150"/>   <!-- 3 -->
  <use  href="#pool" xlink:href="#pool" transform="translate(-170,0)"/>  <!-- 4 -->
  <rect class="grain" x="80" y="180" width="300" height="150"/>   <!-- 5 -->
  <rect class="bevel" x="80" y="180" width="300" height="2.5"/>   <!-- 6 -->
</g>
<rect class="rim"  x="80"   y="180"   width="300"   height="150"   rx="20"/>
<rect class="rim2" x="81.4" y="181.4" width="297.2" height="147.2" rx="18.6"/>
```

`<use href="#scene">` is what keeps the duplication cheap — the orb geometry is
declared once and filtered as many times as there are surfaces.

### XML and rendering traps

Every one of these produced a silently broken file during the original build.

1. **An XML comment cannot contain `--`**, which makes a comment documenting CSS
   custom properties unparseable by definition. Put the parameter block inside the
   `<style>` element as a CSS comment.
2. **`<` inside a CSS comment still parses as markup.** Writing a tag name in angle
   brackets opens an element that never closes. Wrap the whole style content in
   `/* <![CDATA[ */ … /* ]]> */`, which makes it immune to both traps at once.
3. **A CSS `transform` overrides the `transform` presentation attribute** — they do
   not compose. This style parks the light pool with an attribute, so never also
   set `transform` on `.sweep` in CSS.
4. **`scale()` on an SVG group** pivots at `0,0` in any renderer that ignores
   `transform-box`. Set `transform-origin` in explicit user units rather than
   relying on `transform-box: fill-box`.
5. **Always emit both `href` and `xlink:href`** on `<use>`, and declare
   `xmlns:xlink`. Costs nothing, covers older renderers.
6. **`mix-blend-mode` is dropped by librsvg and older Inkscape.** It works in
   browsers and in the `<img src>` embedding this skill targets. If the file will be
   rasterised server-side, swap the grain layer to plain opacity.
7. **Never rely on default `fill`.** SVG defaults to black; a connector path without
   `fill="none"` renders as a filled blob.

### Adapting to other content

The style is independent of the diagram. Keep the layer stack per surface and change
only the rect and `clipPath` coordinates; every surface needs its own `clipPath`.

**Light direction is one decision applied in four places** — the rim gradient axis,
the tint gradient axis, the top-edge highlight, and the contact-shadow offset must
all agree on a single key light. The specimen lights from the upper left, so shadows
fall down and right. Changing the light means changing all four together, and not
doing so is the most common inconsistency in derivative work.

Above about `rx="24"` on a `150`px-tall panel the inner-rim inset needs recomputing
or the two strokes visibly diverge at the corners. Orb hues change freely — but the
base wash stays dark and desaturated, because **a light background inverts the whole
contrast strategy** and needs a light scrim with dark ink throughout.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| byte cap | 150 KB → **200 KB** |
| filter-chain depth | 1 → **3** |

The byte relaxation is granted because the backdrop duplicates are load-bearing
geometry, not ornament. It is not a licence for more panels — three, then split.

The depth relaxation exists for `refract` specifically, which is three primitives by
construction. It is paired with a **fidelity floor, not just a ceiling**: the style
requires `feGaussianBlur`, `feTurbulence` **and** `feDisplacementMap`, at a deepest
chain of at least `3`. A board with a plain blur and nothing else is a flat frost,
and before this floor existed it gated clean. The grain pass is prose-mandated rather
than machine-checked, because `feColorMatrix` is too generic a primitive to require
without over-fitting the gate.

**Contrast is not relaxed, and this is the style most likely to fail it.** Two
mechanisms fix it and both are required: the **scrim goes down before the tint**, so
the panel reads as smoked glass rather than white-on-white, and `inkShadow` sits on
every label group.

**Verify, do not assume.** The background varies across the canvas, so the ratio is
not a number, it is a range. Measure each label against the **lightest** blurred
region behind it — under every orb it overlaps, not the average:

```bash
# Chrome headless is required — cairosvg and librsvg do not implement
# feDisplacementMap or feTurbulence faithfully enough to measure against.
chrome-headless-shell --headless --disable-gpu --force-device-scale-factor=1 \
    --screenshot=probe.png --window-size=1200,460 "file://$PWD/probe.svg"
```

Render with the label layer hidden, take the maximum relative luminance inside each
label's box, and require
`(L_text + 0.05) / (L_bg_max + 0.05) ≥ 4.5`. **Report the measured ratio per label.**
"Looks fine" is not a result.

That measured worst case is also what `data-bg` must point at. Declare it as a
palette role — the specimen's `--panel: #5D546F` is not a colour anyone chose, it is
the composite of scrim over the lightest backdrop under any label. Declaring the
role as the flat scrim colour would report a ratio the render never achieves.

Worked numbers from the specimen: a `.58` scrim over the same wash and orbs, with
the pool's centre stop at `.20`, measures a worst case of **5.93:1** across all
twelve label boxes — the worst being the `02` marker on the centre panel, where the
parked pool and the violet orb overlap. Heavier scrim is not a free fix: past about
`.66` the frost stops being visible and the panel is just a dark rectangle.

## Never

More than three panels per board, translucent text, a `backdrop-filter` (it does
nothing), a plain blur standing in for refraction on a small or curved surface,
frosting the panel harder than the field, a flat or uniform rim stroke, a light pool
per panel instead of one shared, a non-zero final stop on the sheen gradient, a
panel tint that drops its label below 4.5:1 over any orb it overlaps, a bare dot
standing in for flow direction, or duplicating the scene geometry instead of
`<use>`-ing it.
