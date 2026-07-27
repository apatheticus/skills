# hud

**Primary axis:** composition · **Aliases:** `heads-up-display`, `targeting-hud`, `telemetry`

<div align="center">
<img src="../../docs/samples/hud.svg" alt="The hud specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">
</div>


## Intent

An instrument overlay: reticles, tick scales along the frame edges, corner brackets
instead of boxes, counter-rotating rings around the thing under observation, and
numeric telemetry everywhere. Choose it for monitoring, tracing, profiling,
benchmarking and anything whose subject is *measurement*.

**Compare `console-elbow`:** both are instrument idioms, but the elbow is a *panel*
you operate — blocks of flat colour, zoning, chrome around content. A HUD is an
*overlay* on something else — brackets, ticks and readouts floating on a dark field
with nothing behind them. If the visual has a subject being watched, pick this.

## Palette treatment

One instrument hue plus one alert hue, on a very dark blue-black ground (`#03121A`).
Cyan (`#00E5FF`) for all structure and telemetry, amber (`#FFB300`) for the single
alert or locked state, and nothing else. Opacity does the rest of the work: `1` for
primary readouts, `0.6` for structure, `0.28` for tick scales. A third hue turns a
HUD into a dashboard.

## Shape language

Radius `0`–`2`. **Corner brackets, not rectangles** — draw four short L-shaped paths
at the corners of a region rather than closing the box. Strokes at `1.4` for primary
structure, `0.8` for ticks. Reticles are concentric circles with gaps in their dash
arrays. Tick scales run the full length of an edge at an even pitch with every fifth
tick longer. Nothing is filled except readout plates at very low opacity.

## Material / depth

Flat emitted light. No shadow, no bevel, no texture. Depth is opacity and stroke
weight only. A soft glow (`feGaussianBlur` merged back under the source) is permitted
on the alert element and nowhere else — it must mean *this one thing*, not decorate
the board.

## Type treatment

A condensed sans for labels (Roboto Condensed, Bahnschrift, Arial Narrow) and
monospace for every number (Roboto Mono, ui-monospace). Uppercase, `+1.5` tracking,
`18`–`22` for telemetry, `20`–`24` for labels, one `40+` title. Numbers must be
**grounded** — real values from the repo — or plainly structural (axis ticks). The
no-volatile-facts rule applies inside visuals: no timestamps, no version strings, no
invented percentages.

## SVG recipes

Corner brackets, a tick scale, and counter-rotating reticle rings:

```svg
<style>
  svg { --void:#03121A; --inst:#00E5FF; --alert:#FFB300; }
  .void  { fill: var(--void); }
  .brk   { stroke: var(--inst); stroke-width: 1.4; fill: none; }
  .tick  { stroke: var(--inst); stroke-width: 0.8; opacity: .28; }
  .tick5 { stroke: var(--inst); stroke-width: 0.8; opacity: .6; }
  .ring  { stroke: var(--inst); stroke-width: 1.2; fill: none; opacity: .6;
           transform-box: fill-box; transform-origin: center; }
  .num   { fill: var(--inst); font-family: 'Roboto Mono', ui-monospace, monospace;
           font-size: 19px; letter-spacing: 1px; }
  .lab   { fill: var(--inst); font-family: 'Roboto Condensed', Bahnschrift,
           'Arial Narrow', sans-serif; font-size: 22px; letter-spacing: 1.5px; }
</style>

<!-- brackets, not a box -->
<path class="brk" d="M320 200 h-28 v28 M760 200 h28 v28
                     M320 420 h-28 v-28 M760 420 h28 v-28"/>

<circle class="ring"  cx="540" cy="310" r="86" stroke-dasharray="52 18"/>
<circle class="ring" cx="540" cy="310" r="62" stroke-dasharray="26 12"/>
<circle cx="540" cy="310" r="7"  fill="var(--alert)" stroke="none"/>

<line class="tick5" x1="320" y1="452" x2="320" y2="466"/>
<line class="tick"  x1="344" y1="452" x2="344" y2="462"/>
<text class="num"   x="316" y="486">0</text>
```

The two rings are offset so their dash gaps never line up — that misalignment is
what reads as two independent instruments rather than one doubled circle.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| filter depth | 1 → **2** chained primitives per element |

Two is the alert glow: one blur merged back over the source, used on one element.
Contrast is not relaxed. `#00E5FF` on `#03121A` is about 12:1 at full opacity — but
the `0.28` tick opacity is decorative structure and must never carry text.

## Never

A third hue, a filled region at high opacity, a drop shadow, a closed rectangle where
brackets belong, a light ground, glow on anything but the alert, a timestamp or
version string in a readout, an invented statistic, or two rings whose dash gaps
align.
