# SVG animation — the motion vocabulary

Read this before authoring the first animated visual in a run. It holds the seam
contract, the CSS patterns worth having, the one place SMIL is allowed, and the
reduced-motion rules. `viz-production.md` owns the pipeline around it;
`design-system.md` owns how calm the motion should be.

## The technique, and why

**Declarative CSS `@keyframes` inside an inline `<style>` element.** That is the
whole mechanism. A committed `.svg` is served as `image/svg+xml` with its bytes
intact, and the browser animates it in an `<img>` the same way it animates a
document — as long as nothing in the file needs script.

This is the technique used in the wild by well-known animated README assets, and it
survives GitHub because it asks for nothing GitHub strips.

Two things do **not** work and must never be reached for:

- **`<script>`** — stripped in the `<img>` context, and a hard checker error.
- **JavaScript-driven timelines** of any kind. There is no runtime here.

## The seam contract

The visual replays forever with no visible jump. Every rule is load-bearing.

1. **State at t=D equals state at t=0.** `D` is declared once, as `data-loop-s` on
   the root `<svg>`. It is the single source of truth for the loop length, and the
   checker reads it.
2. **Every animation duration divides `D` evenly.** A `5s` pulse inside a `12s` loop
   completes 2.4 cycles and jumps at the seam. `4s` completes exactly 3. This is
   pure arithmetic, which is why the checker can prove it rather than guess.
3. **Every animation is `infinite`.** A finite `animation-iteration-count` stops
   mid-loop and the visual dies after one pass.
4. **No entrance animations.** The loop is steady-state. Anything that "arrives"
   replays its arrival forever. Start in the composed state.
5. **Yoyo motion needs an even half-cycle count** so the element is back at its
   start by `t=D`. A `0% → 50% → 100%` keyframe set that returns to its origin is
   the reliable form; `alternate` direction with an odd count is not.
6. **`animation-delay` is free, and negative delay is the good kind.** A negative
   delay phase-shifts an already-running animation without adding time to the loop,
   which is how you stagger a row of nodes without breaking rule 2. A *positive*
   delay makes the first cycle differ from the rest — use it only if the delay also
   divides `D`.

Durations run **8–14s** per the design-system motion rule. Longer reads as static;
shorter reads as busy.

### Picking `D`

Choose `D` so the cycle counts you want are integers. `12s` is the workhorse: it
divides by 1, 2, 3, 4, 6, and 12, so 2s / 3s / 4s / 6s sub-cycles all land. `10s`
only gives you 1, 2, 5, 10 — which forces 5s cycles and reads slow. Prefer `12s`
unless the content wants otherwise.

## The CSS patterns

### Flow along a line — `stroke-dashoffset`

The workhorse for showing direction through a diagram. One dash marching along a
path, no geometry duplication:

```css
.flow {
  stroke-dasharray: 14 200;
  animation: march 4s linear infinite;   /* 4 divides 12 */
}
@keyframes march {
  from { stroke-dashoffset: 214; }
  to   { stroke-dashoffset: 0; }
}
```

The `dasharray` sum (`14 + 200 = 214`) must equal the `dashoffset` travel, or the
dash pattern restarts visibly. Keep the sum ≥ the path length so only one dash is
in flight.

### Emphasis — opacity pulse

```css
.pulse { animation: pulse 6s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: .4 } 50% { opacity: 1 } }
```

Symmetric keyframes return to the start automatically, which satisfies rule 5.
Never pulse below `0.35` on anything carrying text — the legibility floor applies at
every phase of the loop, not just at `t=0`.

### Travel — `transform`

```css
.token { animation: slide 4s cubic-bezier(.4,0,.2,1) infinite; }
@keyframes slide {
  0%   { transform: translateX(0); opacity: 0; }
  15%  { opacity: 1; }
  85%  { opacity: 1; }
  100% { transform: translateX(320px); opacity: 0; }
}
```

Fading in and out at the ends is what lets a one-way travel loop seamlessly: the
element is invisible at both `0%` and `100%`, so the teleport back is unseen. This
is the standard way to avoid an entrance animation while still showing motion in one
direction.

Use `transform-box: fill-box; transform-origin: center;` when rotating or scaling a
shape about itself — SVG's default origin is the user-space origin, not the element.

### Sequencing — staggered negative delays

```css
.step:nth-of-type(1) { animation-delay: 0s; }
.step:nth-of-type(2) { animation-delay: -1s; }
.step:nth-of-type(3) { animation-delay: -2s; }
```

All three share one 3s animation; the negative delays spread them across the cycle
without changing any duration. This keeps rule 2 intact for free.

`nth-of-type` works, but naming classes explicitly (`.s1`, `.s2`) is easier to
check and easier to read six months later.

### What not to animate

- **No strobing or flicker.** Nothing faster than roughly 2 Hz, ever.
- **No idle bobbing.** Motion communicates flow direction or a state change or it
  doesn't exist.
- **Nothing under text.** A moving element that passes behind a label makes the
  label unreadable for part of every loop, and the filmstrip is how you catch it.
- **Not everything at once.** One or two motion ideas per visual. A board where
  every element moves reads as noise and costs bytes.

## SMIL — one allowed use

`<animateMotion>` with an `<mpath>` is the **only** SMIL this skill permits, and
only for genuine travel along a curved path where a CSS `transform` cannot express
the trajectory:

```svg
<path id="route" class="rule" d="M120,200 C400,60 800,340 1080,200"/>
<circle r="7" class="token">
  <animateMotion dur="6s" repeatCount="indefinite">
    <mpath href="#route"/>
  </animateMotion>
</circle>
```

Rules:

- `dur` obeys the seam contract exactly as a CSS duration does — it must divide
  `data-loop-s`.
- `repeatCount="indefinite"`, always.
- Reference the *same* `<path>` the diagram already draws. Duplicating the geometry
  is how the dot and the line drift apart.

For anything on a straight line, a chord, or a simple arc, use CSS `transform`
instead. SMIL is deprecated in the spec even though every current browser still
ships it, and it is invisible to the CSS cascade — which brings us to the wrinkle.

### The SMIL reduced-motion wrinkle

**CSS cannot stop SMIL.** `animation: none` has no effect on an `<animateMotion>`,
and there is no media-query mechanism inside SMIL. A reader with Reduce Motion on
would still see the dot fly.

So any SMIL-animated element must **also** be hidden by a CSS rule inside the
reduced-motion query:

```css
@media (prefers-reduced-motion: reduce) {
  .pulse, .flow, .token { animation: none; }
  .smil-token { display: none; }     /* the only way to stop SMIL */
}
```

`svg_check.py` enforces this: every element carrying a SMIL animation child must be
matched by a `display: none` (or `visibility: hidden`) rule inside the
reduced-motion block. The composition therefore has to still make sense with the
travelling dot gone — which is a good constraint. The path it travels stays visible
and carries the direction.

## The reduced-motion contract

Every animated visual carries this block. It is mandatory and never softens for any
style:

```css
@media (prefers-reduced-motion: reduce) {
  .pulse, .flow, .token { animation: none; }
  .smil-token { display: none; }
}
```

- Every animated class appears in it.
- Setting `animation: none` parks the element at its **base** state — the attribute
  values on the element itself, not the first keyframe. So the base state must be
  the legible, composed one. If a class relies on its keyframes for its resting
  opacity, restate that value in the reduced-motion rule (`opacity: 1`).
- The stopped frame must be a visual you would have been willing to ship as a
  static. That is the real test.

**One honest caveat:** whether GitHub's image rendering honours
`prefers-reduced-motion` from the reader's OS is not something this skill can
guarantee — it depends on the host's rendering context. The rule ships anyway,
because it works where the SVG is opened directly, in VS Code's preview, on GitLab,
and anywhere the file is embedded in a page. Don't claim GitHub respects it without
checking.
