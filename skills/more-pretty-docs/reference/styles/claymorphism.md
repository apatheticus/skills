# claymorphism

**Primary axis:** material · **Aliases:** `clay`, `3d-soft`

## Intent

Fat, rounded, pastel volumes that look pressed out of modelling clay — inflated
shapes with a soft inner light and a wide diffuse shadow. Choose it for onboarding,
education, and anything with a friendly consumer register.

## Palette treatment

Pastel and light. Take the repo's accents and use them at high lightness / moderate
saturation as *fills* — clay objects are colored objects. `background` is a very
light tint of the primary accent rather than neutral white. `ink` stays dark enough
to pass contrast on those pastel fills, which usually means near-black, not gray.

## Shape language

The roundest style in the catalog: radius `24–40`, and shapes wider than they are
tall. Nothing sharp, nothing thin. Circles and superellipse-ish rounded rects only.
Elements overlap slightly, like objects on a table.

## Material / depth

Two cues, one primitive each: a wide soft shadow below, and an inner top highlight
that reads as light catching a curved surface. Build the highlight as a lighter
rounded rect clipped to the top third of the shape — cheaper and cleaner than a
filter, and it keeps you inside the default filter depth of 1.

## Type treatment

System sans, `700`, generous size. Sentence case, slightly loose tracking (`+0.3`).
Type sits *on* clay objects, so it needs to be big and dark. No thin weights, no
all-caps micro-labels.

## Motion character

Squash-and-stretch, gentle. Objects breathe, tilt a few degrees, or bob a few units —
but only where the bob means something (arrival, selection, activity). Long, soft
easing over `4s` or `6s`. Never fast.

## SVG recipes

An inflated clay card with a clipped inner highlight:

```svg
<defs>
  <filter id="soft" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#8f7bd6" flood-opacity="0.35"/>
  </filter>
  <clipPath id="c1"><rect x="100" y="100" width="300" height="180" rx="34"/></clipPath>
</defs>
<style>
  svg { --background:#f4f0ff; --surface:#c9b8ff; --ink:#1d1533;
        --accent:#ff9ec4; --accent-2:#8ce0d0; --lite:#e2d9ff; }
  .clay  { fill: var(--surface); filter: url(#soft); }
  .gloss { fill: var(--lite); clip-path: url(#c1); }
  .t     { fill: var(--ink); font-weight: 700; }
  .bob   { transform-box: fill-box; transform-origin: center;
           animation: bob 4s ease-in-out infinite; }
  @keyframes bob {
    0%,100% { transform: translateY(0) scale(1) }
    50%     { transform: translateY(-6px) scale(1.02) }
  }
  @media (prefers-reduced-motion: reduce) { .bob { animation: none } }
</style>

<rect class="clay" x="100" y="100" width="300" height="180" rx="34"/>
<rect class="gloss" x="100" y="100" width="300" height="70" rx="34" opacity="0.5"/>
```

Symmetric keyframes return to the start on their own, so `4s` in a `12s` loop is
seam-exact with no extra work.

## Relaxes

Nothing. The pastel fills still have to carry `ink` at 4.5:1 — that is what forces
near-black text instead of the mid-gray the style is often drawn with.

## Never

Sharp corners, thin strokes, dark backgrounds, gray text on pastel (it fails
contrast), more than three clay colors in one board, a bob on something that isn't
changing state.
