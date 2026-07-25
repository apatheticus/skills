# neumorphism

**Primary axis:** material · **Aliases:** `soft-ui`, `soft`

<img src="../../docs/samples/neumorphism.svg" alt="The neumorphism specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">


## Intent

Everything extruded from one continuous surface: no borders, no color fields, just a
light shadow and a dark shadow on the same background color. Choose it for consumer
apps and dashboards with a calm register. Its defining low contrast is also its
accessibility problem — read the Relaxes section before committing.

## Palette treatment

**One surface color for nearly everything.** The card and the canvas are the *same*
hex; the shape is legible only from its shadows. Derive a light (+8% lightness) and a
dark (−10%) from that color and use them exclusively for shadows. The accent appears
only in text, icons, and the one active state — never as a card fill.

## Shape language

Generously rounded: radius `16–28`, never less than `16`. Soft, wide shapes; no thin
elements, because a 1-unit line has nowhere to put a shadow. Pills for controls,
circles for toggles.

## Material / depth

The dual shadow is the entire style. Raised elements get light-from-top-left; pressed
elements invert the same pair.

**Two ways to build it, and they are not equivalent.**

- **The filter pair** — two `feDropShadow` primitives in one filter, one dark at
  `+7,+7` and one white at `−7,−7`. This is the authentic version, because the
  shadows are *blurred*, and neumorphism without blur is not neumorphism. It is why
  this style declares a filter depth of 2.
- **The geometry pair** — two offset copies of the shape behind the face, no filter
  at all. Byte-cheap and sharper, and the right call at small rendered scale or when
  the byte budget is tight, but the edges are hard and the material reads as paper
  rather than moulded.

Use the filter pair by default; fall back to geometry deliberately, not by accident.

**SVG filters cannot be inset**, so a pressed state is not an inner shadow: it is a
second copy of the element cross-faded on top, carrying the same pair at **halved
offset, halved blur and halved opacity**. Halving all three is what reads as pressed;
halving only the offset reads as a smaller raised element.

A recessed track — a slider groove, a progress channel — is a `<linearGradient>` from
the dark shadow tone to the light one along the short axis. That gradient is the one
place colour differs from the surface.

## Type treatment

System sans, `600` for labels. **Keep type contrast high even though the surfaces are
low-contrast** — that is the discipline this style needs. Put the softness in the
surfaces, not in the text. Sentence case, normal tracking.

## Motion character

Slow and breathing. Elements press in and release, shadows soften and firm. Nothing
travels far; `4–8` units of movement is plenty. Long easing —
`cubic-bezier(.4,0,.4,1)` over `4s` or `6s`.

## SVG recipes

The filter pair, the pressed pair, and the groove:

```svg
<defs>
  <filter id="raise" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="7"  dy="7"  stdDeviation="9" flood-color="#b9c2ce" flood-opacity=".9"/>
    <feDropShadow dx="-7" dy="-7" stdDeviation="9" flood-color="#ffffff" flood-opacity=".9"/>
  </filter>
  <!-- pressed: offset, blur AND opacity all halved -->
  <filter id="press" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="3.5"  dy="3.5"  stdDeviation="4.5" flood-color="#b9c2ce" flood-opacity=".45"/>
    <feDropShadow dx="-3.5" dy="-3.5" stdDeviation="4.5" flood-color="#ffffff" flood-opacity=".45"/>
  </filter>
  <linearGradient id="chan" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#b9c2ce"/><stop offset="1" stop-color="#ffffff"/>
  </linearGradient>
</defs>
<style>
  svg { --background:#e8ecf2; --surface:#e8ecf2; --ink:#4a4e63;
        --lite:#ffffff; --dark:#b9c2ce; --accent:#5b7cfa; }
  .bg     { fill: var(--background); }
  .raised { fill: var(--surface); filter: url(#raise); }
  .pressed{ fill: var(--surface); filter: url(#press); }
  .groove { fill: url(#chan); }
  .t      { fill: var(--ink); font-weight: 600; }
  .sink   { animation: sink 6s cubic-bezier(.4,0,.4,1) infinite; }
  @keyframes sink { 0%,100% { opacity: 1 } 50% { opacity: 0 } }
  @media (prefers-reduced-motion: reduce) { .sink { animation: none; opacity: 1 } }
</style>

<rect class="pressed"      x="100" y="100" width="320" height="140" rx="22"/>
<rect class="raised sink"  x="100" y="100" width="320" height="140" rx="22"/>
<rect class="groove"       x="140" y="280" width="240" height="16" rx="8"/>
```

The byte-cheap alternative, when the filter pair is too expensive:

```svg
<!-- raised card: dark copy down-right, light copy up-left, face on top -->
<rect class="sh-d" x="106" y="106" width="320" height="140" rx="22"/>
<rect class="sh-l" x="94"  y="94"  width="320" height="140" rx="22"/>
<rect class="face" x="100" y="100" width="320" height="140" rx="22"/>
```

Cross-fading the raised copy over the pressed one (`.sink`) is the canonical
neumorphic motion, and it costs nothing beyond one keyframe.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| text contrast | 4.5:1 → **3.0:1** |
| UI / graphic contrast | 3.0:1 → **2.0:1** |
| filter depth | 1 → **2** chained primitives per element |

The two contrast relaxations exist because the style's shapes are *defined* by
near-background shadows; holding them to 3:1 would erase the style. The filter depth
of 2 is the raised/pressed shadow pair and nothing more.

**The cost is real:** labels at 3:1 will be unreadable for some low-vision readers.
So keep every label as far above 3.0 as the look allows — `#4A4E63` on `#E6E9EF` is
**6.74:1** and is the right default, not the murky grey the aesthetic implies —
spend the relaxation on the shadow shapes rather than the text, and rely on the
works-without-images gate to carry the meaning outside the picture.

## Never

An accent-filled card, a visible border, thin strokes, a pressed state built as a
true inner shadow (SVG has none), a pressed state that halves only the offset, dark
mode with the same shadow pair (recompute both from the dark surface), radius under
`16`, more than two primitives in one filter, or spending the text relaxation just
because it's available.
