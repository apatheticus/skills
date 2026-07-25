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

**`<pattern>` fills are the single cheapest way to get density**, and the most
under-used device in this style: dots, stripes and checks tile from a few bytes each,
add texture at every zoom level, and cost nothing in type size. Declare two or three
in `<defs>` and fill large fields with them instead of flat colour. Three patterns
over a dominant hue reads denser than six extra shapes ever will.

A pattern can also **move seam-exactly**: translate the filled element by an exact
multiple of the pattern tile over the loop, and the texture appears to scroll forever
with `t=D` identical to `t=0`. Translate by anything else and the seam shows.

## Type treatment

Three type scales visible at once, with real contrast between them: a very large
display line (`72+`, weight `900`), a mid label set (`24`, weight `600`), and mono
metadata (`18`). Mixed case, mixed alignment, rotated text is allowed once per board.

**Density comes from splitting boards, never from shrinking type.** Every label still
meets its legibility floor. If it doesn't fit, that is a second visual.

**The white label plate is the mechanism that makes the occlusion rule enforceable.**
On a board this busy, "don't let anything cover a label" is a hope; a solid
`background`-or-white rectangle sitting under every label, sized to the text, is a
guarantee. It also fixes contrast in one move, because the label is then measured
against a colour you chose rather than whatever pattern happens to be behind it at
that phase.

## Motion character

Several things move, at different rates, all seam-exact. Three or four motion ideas
running on `2s`, `3s`, `4s`, and `6s` cycles inside a `12s` loop reads as busy-but-
composed because every one of them lands on the seam. This is where the arithmetic
earns its keep.

## SVG recipes

Multi-rate motion that all resolves at `t=12s`:

```svg
<defs>
  <pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse">
    <circle cx="4" cy="4" r="2.6" fill="#ffd23f"/>
  </pattern>
  <pattern id="stripe" width="18" height="18" patternUnits="userSpaceOnUse"
           patternTransform="rotate(35)">
    <rect width="7" height="18" fill="#00e5c0"/>
  </pattern>
  <pattern id="check" width="24" height="24" patternUnits="userSpaceOnUse">
    <rect width="12" height="12" fill="#5b3df5"/>
    <rect x="12" y="12" width="12" height="12" fill="#5b3df5"/>
  </pattern>
</defs>
<style>
  svg { --background:#12071f; --ink:#fdf7ff; --accent:#ff2e88;
        --accent-2:#00e5c0; --accent-3:#ffd23f; --accent-4:#5b3df5; }
  .bg    { fill: var(--background); }
  .dots  { fill: url(#dots); }
  .strp  { fill: url(#stripe); }
  .plate { fill: var(--ink); }
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
  /* the stripe tile is 18 wide; 72 = 4 tiles, so the texture scrolls seamlessly */
  .rp { animation: tile 6s linear infinite }

  @keyframes tile  { from { transform: translateX(0) } to { transform: translateX(72px) } }
  @keyframes spin  { to { transform: rotate(360deg) } }
  @keyframes pulse { 0%,100% { opacity: .5 } 50% { opacity: 1 } }
  @keyframes slide { 0% { transform: translateX(0); opacity: 0 }
                     12% { opacity: 1 } 88% { opacity: 1 }
                     100% { transform: translateX(240px); opacity: 0 } }
  @keyframes sweep { 0%,100% { transform: translateY(0) } 50% { transform: translateY(-18px) } }

  @media (prefers-reduced-motion: reduce) {
    .r2, .r3, .r4, .r6, .rp { animation: none; opacity: 1 }
  }
</style>

<!-- every label rides a plate, so its contrast is a number you chose -->
<rect class="plate" x="96" y="352" width="228" height="34"/>
<text x="108" y="378" font-size="24" font-weight="600" fill="#12071f">throughput</text>
```

`2`, `3`, `4`, and `6` all divide `12` — six, four, three, and two cycles
respectively, every one of them home at the seam. Four rates is the cap: a fifth
stops reading as composed and starts reading as broken.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| byte cap | 150 KB → **250 KB** |

Granted because density is the point. It is not a licence to skip `<defs>` + `<use>`
for repeated geometry, and it is not a licence to shrink type — the legibility floors
and the contrast gate are unchanged.

## Never

Type below its floor, more than four simultaneous motion rates, a cycle that doesn't
divide the loop, a pattern translated by anything but an exact tile multiple, a label
without a plate, overlap that occludes a label at any phase, or "more elements"
standing in for a composition. Read the filmstrip carefully — this is the style where
phase-dependent occlusion actually happens.
