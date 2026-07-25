# human-voice — visual design system

One frozen system; all repo visuals derive from it. Facts come from the repo
(SKILL.md, reference/), never invented. Frozen for this run.

## Story extraction

Audience:     writers and engineers shipping prose that a reader did not ask for
Value:        rewrites text so it reads as human-authored, in the register the document actually calls for
Proof:        33 catalogued patterns, of which 22 apply everywhere and 11 change or switch off by register
First action: hand it a draft and let it name the register before it edits a word
Theme:        a proof pass on a page — the register is chosen in the margin before a single mark is made

## Frozen system

This skill ships no logo, brand tokens, or style guide, so the resolved style's
palette treatment fills the gap (`design-system.md` → "when a repo has no identity at
all, the style's palette treatment fills the gap"). `editorial` asks for paper and ink
with a single accent, which is what the table below is.

### Palette

| Role | Hex | Notes |
| --- | --- | --- |
| background       | `#fbf9f4` | warm off-white paper |
| surface          | `#f4efe3` | a slightly deeper paper for a bounded plate; used sparingly |
| ink              | `#1a1a18` | soft black — print black has warmth, `#000` does not |
| muted            | `#6b6862` | captions and secondary body; 5.27:1 on paper |
| accent-primary   | `#8c2f1f` | rust — the proof rule, and nothing else |
| rule             | `#d8d3c8` | the decorative hairline under a headline; never bounds content |
| keyline          | `#8f8a7e` | bounds a figure; clears the 3:1 graphic floor because the box is load-bearing |

Two neutrals, not one, and the split is deliberate. `editorial`'s instinct is a single
pale hairline, but a box that separates one item of content from another has to be
visible — so `rule` stays faint where it is pure typography and `keyline` is dark
enough to pass the graphic-contrast gate where it carries meaning.

### Typography

| Role | Stack |
| --- | --- |
| display | `Georgia, 'Iowan Old Style', serif` |
| body    | `Georgia, 'Iowan Old Style', serif` |
| mono    | `ui-monospace, SFMono-Regular, Menlo, monospace` |

System stacks only — never a remote font, which an SVG cannot fetch on GitHub. A serif
carries the headline and the body here, which is correct for this style and wrong for
most others. Mono is reserved for literals: a skill name, a flag, a pattern number.

### Shape language

Rules and columns. Radius `0`. Three weights: a `3`-unit rust rule opens a plate, a
`1`-unit `rule` hairline separates headline from body, and a `1.5`-unit `keyline`
bounds a figure. No filled panels beyond the one bounded plate. Outer margin `80`
units, never less.

### Motif

The **proof rule**: a rust stroke that behaves like a copy editor's mark. It opens a
plate as a heavy rule, bounds the one selected item as a keyline, and strikes through a
banned phrase where a pattern is being demonstrated. Derived from what the product does
— it marks up prose — and it is the only place the accent appears.

### Composition rules

Sparse-editorial. Left-aligned, ragged right, generous leading, one idea per plate.
A wide outer margin is structural, not decoration: it is where the type scale gets its
authority. Important content clear of the edges; legible at rendered width (1200 units
in an 820 px embed).

### Motion rules

- Seamless ambient loops, `data-loop-s="12"` on every animated plate; every animation
  duration divides 12 exactly.
- **Almost none, and slow.** A rule drawing itself across the page over `6s`; a
  strikethrough arriving over a phrase. If a reader would not notice the motion on a
  first pass, it is correctly tuned.
- Ease `ease-in-out`. Nothing linear, nothing bouncing, nothing that repeats fast
  enough to read as a blink.
- Every animated visual carries a `prefers-reduced-motion` block that stops all motion
  and leaves a legible still — for a drawn rule that means fully drawn, not absent.

## Style

| Field | Value |
| --- | --- |
| Slug | `editorial` |
| Source | catalog (`--style editorial`) |
| Primary axis | composition — print hierarchy decides the layout before anything else |

- **Intent** — print hierarchy carried into a diagram: a headline, a lede, a hairline
  rule, a wide outer margin, a figure that behaves like a plate in a magazine. The
  right call for repos whose docs are read rather than skimmed.
- **Palette treatment** — paper and ink. One accent, used for the rule and the callout
  only. Colour never fills a large area.
- **Shape language** — radius `0–2`; a `3` rule opens, a `0.75`–`1` hairline separates,
  a thin keyline bounds a figure instead of a shadowed card.
- **Material / depth** — none. This is paper. Depth comes from the margin and the type
  scale, not from shadow, gradient, or bevel.
- **Type treatment** — four steps with real contrast between them: headline `64+`/`700`
  at `-1.5` tracking, standfirst `28`/`400`, body `20`/`400`, caption `16`/`500` at
  `+0.8` tracking, uppercase. Left-aligned, ragged right.
- **Motion character** — almost none, and slow: a rule drawing itself over `6s`, a
  strikethrough arriving over a phrase.
- **SVG recipes** — `reference/styles/editorial.md`: the self-drawing rule whose `t=0`
  and `t=D` are both "no rule visible", the four-step scale, the hairline.
- **Relaxations** — none. The muted caption colour still has to clear 4.5:1, which is
  why `muted` above is darker than print instinct suggests.
- **Never** — centred body text, a second accent, a shadowed card, margins under `80`
  units, all-caps headlines, a type scale with less than a `1.4` ratio between steps,
  or motion loud enough to notice twice.

## Visual inventory

| Asset | Doc | Depicts | Tier | Source facts |
| --- | --- | --- | --- | --- |
| hero | README.md | the register is selected before any pattern is read, and Professional is the default when the genre is unclear | animated-hero | SKILL.md → Step 1; reference/registers.md |
| pattern-gates | README.md | the 33-pattern catalog splits into 22 that apply in every register and 11 that change or switch off | animated-flagship | SKILL.md → Step 3; reference/patterns.md |
