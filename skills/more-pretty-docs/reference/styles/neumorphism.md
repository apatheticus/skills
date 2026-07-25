# neumorphism

**Primary axis:** material · **Aliases:** `soft-ui`, `soft`

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
elements invert the same pair. One filter primitive suffices if you build the pair as
two offset copies of the shape rather than a filter chain — cheaper and sharper.

## Type treatment

System sans, `600` for labels. **Keep type contrast high even though the surfaces are
low-contrast** — that is the discipline this style needs. Put the softness in the
surfaces, not in the text. Sentence case, normal tracking.

## Motion character

Slow and breathing. Elements press in and release, shadows soften and firm. Nothing
travels far; `4–8` units of movement is plenty. Long easing —
`cubic-bezier(.4,0,.4,1)` over `4s` or `6s`.

## SVG recipes

The dual shadow, built as two offset copies rather than a filter chain:

```svg
<style>
  svg { --background:#e8ecf2; --surface:#e8ecf2; --ink:#2b3441;
        --lite:#ffffff; --dark:#b9c2ce; --accent:#5b7cfa; }
  .bg     { fill: var(--background); }
  .sh-d   { fill: var(--dark); }
  .sh-l   { fill: var(--lite); }
  .face   { fill: var(--surface); }
  .t      { fill: var(--ink); font-weight: 600; }
  .press  { animation: press 6s cubic-bezier(.4,0,.4,1) infinite; }
  @keyframes press { 0%,100% { opacity: 1 } 50% { opacity: 0 } }
  @media (prefers-reduced-motion: reduce) { .press { animation: none; opacity: 1 } }
</style>

<!-- raised card: dark copy down-right, light copy up-left, face on top -->
<rect class="sh-d" x="106" y="106" width="320" height="140" rx="22"/>
<rect class="sh-l" x="94"  y="94"  width="320" height="140" rx="22"/>
<rect class="face" x="100" y="100" width="320" height="140" rx="22"/>
```

Cross-fading the light copy (`.press`) between raised and pressed states is the
canonical neumorphic motion, and it costs nothing in bytes.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| text contrast | 4.5:1 → **3.0:1** |
| UI / graphic contrast | 3.0:1 → **2.0:1** |

Both exist because the style's shapes are *defined* by near-background shadows;
holding them to 3:1 would erase the style. **The cost is real:** labels at 3:1 will
be unreadable for some low-vision readers. So keep every label as far above 3.0 as
the look allows, spend the relaxation on the shadow shapes rather than the text, and
rely on the works-without-images gate to carry the meaning outside the picture.

## Never

An accent-filled card, a visible border, thin strokes, dark mode with the same
shadow pair (recompute both from the dark surface), radius under `16`, or spending
the text relaxation just because it's available.
