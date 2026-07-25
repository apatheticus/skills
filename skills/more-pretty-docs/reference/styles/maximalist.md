# maximalist

**Primary axis:** composition · **Aliases:** `max`, `dense`, `more`

## Intent

Density as the message: layered panels, multiple simultaneous type scales, color
everywhere, a board that rewards a second look. Choose it for showcase repos and
expressive projects that want the docs to be part of the personality. It is the most
expensive style here and the easiest to get wrong.

## Palette treatment

Every role in the palette, used, plus derived tints. Large color fields adjacent to
each other without neutral separation. The discipline is not restraint in *count* but
restraint in *area*: one color dominates roughly half the board, the rest are accents
against it. Random color is noise; a dominant plus five supports is maximalism.

## Shape language

Mixed on purpose — hard rectangles, circles, diagonal bands, and one organic blob in a
single composition. Radius varies by element family (`0` for bands, `20` for cards),
which in any other style would be a mistake. Stroke weights from `1` to `6`.

## Material / depth

Layering, not lighting. Overlap and z-order create depth; elements sit partly on top
of each other with visible offset. Keep filters to the default single primitive — the
bytes are already going elsewhere.

## Type treatment

Three type scales visible at once, with real contrast between them: a very large
display line (`72+`, weight `900`), a mid label set (`24`, weight `600`), and mono
metadata (`18`). Mixed case, mixed alignment, rotated text is allowed once per board.

**Density comes from splitting boards, never from shrinking type.** Every label still
meets its legibility floor. If it doesn't fit, that is a second visual.

## Motion character

Several things move, at different rates, all seam-exact. Three or four motion ideas
running on `2s`, `3s`, `4s`, and `6s` cycles inside a `12s` loop reads as busy-but-
composed because every one of them lands on the seam. This is where the arithmetic
earns its keep.

## SVG recipes

Multi-rate motion that all resolves at `t=12s`:

```svg
<style>
  svg { --background:#12071f; --ink:#fdf7ff; --accent:#ff2e88;
        --accent-2:#00e5c0; --accent-3:#ffd23f; --accent-4:#5b3df5; }
  .bg    { fill: var(--background); }
  .band  { fill: var(--accent-4); }
  .card  { fill: var(--accent); }
  .disc  { fill: var(--accent-2); }
  .t     { fill: var(--ink); }
  .disp  { fill: var(--ink); font-size: 76px; font-weight: 900; letter-spacing: -2px; }
  .meta  { fill: var(--accent-3); font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
           font-size: 18px; }

  .r2 { animation: spin 2s linear infinite; transform-box: fill-box; transform-origin: center }
  .r3 { animation: pulse 3s ease-in-out infinite }
  .r4 { animation: slide 4s linear infinite }
  .r6 { animation: sweep 6s ease-in-out infinite }

  @keyframes spin  { to { transform: rotate(360deg) } }
  @keyframes pulse { 0%,100% { opacity: .5 } 50% { opacity: 1 } }
  @keyframes slide { 0% { transform: translateX(0); opacity: 0 }
                     12% { opacity: 1 } 88% { opacity: 1 }
                     100% { transform: translateX(240px); opacity: 0 } }
  @keyframes sweep { 0%,100% { transform: translateY(0) } 50% { transform: translateY(-18px) } }

  @media (prefers-reduced-motion: reduce) {
    .r2, .r3, .r4, .r6 { animation: none; opacity: 1 }
  }
</style>
```

`2`, `3`, `4`, and `6` all divide `12` — six, four, three, and two cycles
respectively, every one of them home at the seam.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| byte cap | 150 KB → **250 KB** |

Granted because density is the point. It is not a licence to skip `<defs>` + `<use>`
for repeated geometry, and it is not a licence to shrink type — the legibility floors
and the contrast gate are unchanged.

## Never

Type below its floor, more than four simultaneous motion rates, a cycle that doesn't
divide the loop, overlap that occludes a label at any phase, or "more elements"
standing in for a composition. Read the filmstrip carefully — this is the style where
phase-dependent occlusion actually happens.
