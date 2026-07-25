# whiteboard-marker

**Primary axis:** material · **Aliases:** `whiteboard`, `napkin`, `dry-erase`

## Intent

Thinking out loud: fat dry-erase strokes at partial opacity, boxes that overshoot at
the corners, arrows drawn faster than they were planned, and three marker colours
because that's what was on the tray. Choose it for brainstorm captures, incident
timelines, workshop output and explainers that want to say *this is one person's
current model, not the specification*.

**The loosest style in the catalog**, at the improvised end of the roughness dial —
and it declares that loudly. Right for internal review, wrong for anything a
customer reads.

**Compare `rough-sketch`:** that one is the tidy collaborative diagram — thin doubled
strokes, hachure fills, displacement 2.2. This one is displacement 4.5 and a 3.4-wide
round marker. If it should look agreed, pick that; if it should look in progress,
pick this.

## Palette treatment

Board white with a faint warm cast (`#F7F8F6`), a near-black marker (`#2B2B2B`) for
structure, and three tray colours — blue (`#2266CC`), red (`#D93A2B`), green
(`#2E9E4F`) — mapped onto the repo's palette. **Every stroke sits at about `0.88`
opacity**, because dry-erase ink is never fully opaque and the board shows through.
That single value does more for the illusion than the colours do.

## Shape language

Displacement `scale="4.5"` — the top of the roughness dial in `styles.md`, above the
"improvised" threshold. Stroke `3.4` with **round caps and round joins**; a square
cap instantly reads as a pen, not a marker. Radius `0`–`8`, but corners overshoot by
several units because a marker doesn't stop where the hand meant to. Fills, where
they exist at all, are loose scribbled hatch at low opacity — never solid.

## Material / depth

None whatsoever. No shadow, no gradient, no blur, no texture beyond the roughen
filter. A whiteboard is a flat surface with ink on it, and any material cue at all
contradicts the premise.

## Type treatment

A loose handwriting face — Caveat, with Bradley Hand and Comic Sans MS behind it —
at `24`–`28` for labels and one `44+` heading. Everything is written, nothing is
typeset. Labels go inside their shapes or right beside them; there are no leader
lines on a whiteboard.

**The named faces are never fetched.** On GitHub the chain lands on Bradley Hand,
Segoe Print or Comic Sans MS — degraded, but still hand-lettered. Say so rather than
promising Caveat; a remote font `href` or `@import` is a hard gate failure.

## Motion character

Almost none, and **steady-state — no draw-on entrance.** The temptation here is
enormous and it is wrong: animating the marker strokes into existence turns a
thinking aid into a screensaver, and it violates the loop contract anyway. What is
allowed: one circled term whose dash pattern creeps at `8s`, or one arrow's packet
travelling at `6s`, `ease-in-out`. That is the entire budget.

## SVG recipes

The roughen filter at whiteboard scale, plus the marker stroke:

```svg
<defs>
  <filter id="rough" x="-10%" y="-10%" width="120%" height="120%">
    <feTurbulence type="fractalNoise" baseFrequency="0.024" numOctaves="2" seed="17" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="4.5"
                       xChannelSelector="R" yChannelSelector="G"/>
  </filter>
</defs>
<style>
  svg { --board:#f7f8f6; --marker:#2b2b2b; --blue:#2266cc; --red:#d93a2b; --green:#2e9e4f; }
  .board { fill: var(--board); }
  .mk    { stroke-width: 3.4; stroke-linecap: round; stroke-linejoin: round;
           fill: none; opacity: .88; filter: url(#rough); }
  .write { fill: var(--marker); font-size: 26px; opacity: .88;
           font-family: Caveat, 'Bradley Hand', 'Segoe Print', 'Comic Sans MS', cursive; }
  .circ  { stroke: var(--red); stroke-width: 3.4; stroke-linecap: round; fill: none;
           opacity: .88; filter: url(#rough); stroke-dasharray: 14 8;
           animation: creep 8s linear infinite; }
  @keyframes creep { from { stroke-dashoffset: 22 } to { stroke-dashoffset: 0 } }
  @media (prefers-reduced-motion: reduce) { .circ { animation: none; stroke-dashoffset: 0 } }
</style>

<rect class="board" x="0" y="0" width="1200" height="620"/>
<!-- corners overshoot: the path closes past where it started -->
<path class="mk" stroke="var(--marker)"
      d="M120 150 H428 V282 H116 V144"/>
<text class="write" x="150" y="226">event stream</text>
<ellipse class="circ" cx="700" cy="300" rx="130" ry="62"/>
```

The overshoot is drawn, not filtered: end the path a few units past its origin. And
**never filter the text** — displacement at 4.5 obliterates letterforms; wobble the
shapes only and expand the filter region or displaced edges clip.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| filter depth | 1 → **2** chained primitives per element |

Two is the roughen chain: turbulence feeding one displacement. Contrast is not
relaxed — `#2B2B2B` at `0.88` on `#F7F8F6` composites to `#3D3D3D` and measures **10.20:1**, so the marker
colours must be checked individually against the board before use, not assumed.

## Never

A draw-on entrance, a square stroke cap, full opacity ink, a solid fill, a shadow,
gradient or blur, a leader line, typeset labels, a filtered `<text>`, a remote font,
displacement below 4 (that's `rough-sketch`), or use in a customer-facing document.
