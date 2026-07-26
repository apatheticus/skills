# editorial

**Primary axis:** composition · **Aliases:** `magazine`, `print`, `typographic`

<div align="center">
<img src="../../docs/samples/editorial.svg" alt="The editorial specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">
</div>


## Intent

Print hierarchy carried into a diagram: a headline, a lede, a hairline rule, a wide
outer margin, and a figure that behaves like a plate in a magazine. Choose it for
essays, specifications, research, and repos whose docs are read rather than skimmed.

## Palette treatment

Paper and ink. `background` is a warm off-white (or a deep near-black for a "night
edition"); `ink` is a soft black, not `#000` — print black has warmth. One accent,
used for the rule and the drop cap or callout only. Color never fills large areas.

## Shape language

Rules and columns. Radius `0–2`. A single hairline (`0.75`–`1`) separates the
headline from the body; a heavier rule (`3`) opens the piece. Figures sit in a bounded
plate with a thin keyline, not a shadowed card.

Two print devices worth using by name, because they build structure without adding
weight:

- **Vertical column hairlines** — one `1`-unit rule down each column gutter, in the
  pale neutral. It makes a multi-column figure read as a *page* rather than as boxes
  placed near each other, and costs one line per gutter.
- **Roman-numeral section marks** — `I`, `II`, `III` in the caption role at the head
  of each region. They carry ordering without numbering anything the reader might
  mistake for data.

## Material / depth

None. This is paper. No shadow, no gradient, no bevel. Depth comes from the margin
and the type scale.

## Type treatment

The style's whole substance. A real hierarchy, four steps, with contrast between them:

| Level | Treatment |
| --- | --- |
| Kicker | `16`, sans, weight `600`, tracking `+2.6`, uppercase, above the headline |
| Headline | `64+`, weight `700`, tracking `-1.5`, sentence case |
| Standfirst / lede | `28`, weight `400`, `1.4` line spacing, `65ch`-ish measure |
| Body / labels | `20`, weight `400` |
| Caption / folio | `16`, weight `500`, tracking `+0.8`, uppercase |

**Kicker and folio are separate roles, and separating them matters.** The kicker is a
sans line above the headline naming the section; the folio is a right-aligned mark on
the headline's own baseline carrying the number or subject. Collapsing them into one
"small uppercase grey text" role is how this style flattens into generic web design.

Left-aligned, ragged right. Generous leading. An initial capital or a hanging quote is
on-idiom. A serif system stack (`Georgia, "Iowan Old Style", serif`) for the headline
and body reads correctly here — it is one of the few styles where serif is right, and
the kicker is the one place a sans belongs.

## Motion character

Almost none, and slow. A rule drawing itself across the page over `6s`, a caption
fading between two states, a single word underlining. If a reader wouldn't notice the
motion on first pass, it is correctly tuned.

## SVG recipes

A rule that draws itself, and the four-step scale in use:

```svg
<style>
  svg { --background:#fbf9f4; --ink:#1a1a18; --muted:#6b6862; --accent:#8c2f1f; }
  .bg   { fill: var(--background); }
  .h    { fill: var(--ink); font-family: Georgia, "Iowan Old Style", serif;
          font-size: 64px; font-weight: 700; letter-spacing: -1.5px; }
  .lede { fill: var(--ink); font-family: Georgia, serif; font-size: 28px; }
  .cap  { fill: var(--muted); font-size: 16px; font-weight: 500; letter-spacing: .8px; }
  .rule { stroke: var(--accent); stroke-width: 3; fill: none;
          stroke-dasharray: 1000; animation: draw 6s ease-in-out infinite; }
  @keyframes draw {
    0%      { stroke-dashoffset: 1000 }
    45%,55% { stroke-dashoffset: 0 }
    100%    { stroke-dashoffset: -1000 }
  }
  .hair { stroke: #d8d3c8; stroke-width: 1; fill: none; }
  @media (prefers-reduced-motion: reduce) { .rule { animation: none; stroke-dashoffset: 0 } }
</style>
```

The rule enters, holds, and exits the other side — so `t=0` and `t=D` are both "no
rule visible", and the loop is seam-exact at `6s` inside `12s`.

## Relaxes

Nothing. The muted caption color still has to clear 4.5:1, which usually means a
darker gray than print instinct suggests.

Budget **two** neutrals, not one. `#d8d3c8` measures about 1.4:1 on paper — correct for
the hairline under a headline, and a graphic-contrast WARN the moment you use it to
bound a figure that separates one item of content from another. Keep the pale tint for
pure typography and declare a second, darker `keyline` role (around `#8f8a7e`, ~3.4:1)
for any box that carries meaning. One accent still means one accent; a second neutral
is not an accent.

**And a keyline neutral is not a text colour.** Setting a folio in the `#C9C0B2`-class
tint measures **1.70:1** on this paper — it looks like restraint and reads as a defect. Every
`<text>` on the board, kicker and folio and caption included, uses `ink` or the darker
muted role and clears 4.5:1. The pale tint draws lines; it never spells words.

## Never

Centered body text, more than one accent, a shadowed card, a keyline neutral used as
text, kicker and folio collapsed into one role, cramped margins (keep `80+` units of
outer margin), all-caps headlines, a type scale with less than a `1.4` ratio between
steps, or motion loud enough to notice twice.
