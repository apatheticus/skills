# Annotation callout — the editorial aside

The marginal note. A short italic remark in the margin that marks a detail without
competing with the diagram's own grammar — *"structure is the index"*, *"no imports, no
configuration"*. It is the one primitive in this skill that speaks in the author's
voice rather than the system's.

Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery), re-expressed for a hand-authored 1200-unit SVG. See
`THIRD_PARTY.md` at the repo root.

`reference/diagram-grammar.md` is the vocabulary underneath this; §3 gives the type
floor a callout has to clear, and §2 gives the roles.

---

## Grammar

Three parts: the text, a dashed leader, a landing dot. All three are optional to the
diagram and none of them is a node.

```svg
<g class="callout">
  <!-- 1. italic display stack, right-aligned into the margin -->
  <text x="1128" y="44" data-role="essential" data-bg="paper"
        class="aside" text-anchor="end">no imports, no configuration</text>
  <!-- 2. dashed Bézier leader — the one curved path on the board -->
  <path d="M 1024,56 Q 876,104 652,272" fill="none"
        stroke="var(--ink)" stroke-opacity="0.4"
        stroke-width="1" stroke-dasharray="4,3"/>
  <!-- 3. landing dot, on the thing being remarked on -->
  <circle cx="652" cy="272" r="4" fill="var(--ink)"/>
</g>
```

```css
.aside { font-family: var(--display); font-style: italic; font-size: 20px; }
```

Every coordinate above is the upstream figure scaled ×1.25 onto the 1200-unit
`viewBox` and rounded to the 4-unit grid, per the reconciliation in
`diagram-grammar.md` §3. The 14px text becomes 20 units, which is the `essential`
floor — the smallest a callout may be, not a starting point to trim from. The `4,3`
dash is the host's dash, the same one the grammar uses for optional nodes and transit
paths; it is not the upstream value left in place.

## The leader is not an edge

Do not put `data-edge` on the leader path. A callout is editorial, not a connection —
tagging it spends one of the type's connectors, and on the five chart types
(`max_edges: 0`) it turns a correct board into a checker error. Two consequences follow
and both are useful: the leader is exempt from the six connector rules in
`diagram-grammar.md` §4, which is why it is allowed to be the one curved path on a
board of rounded right angles, and it never carries an arrowhead, because an arrowhead
is what would make it read as flow.

The curve and the dash together are the whole distinction. A solid leader is a flow
arrow no matter what it is attached to.

## Type

Upstream reserves an italic serif face for this primitive, and the serif is load-bearing
there: serif against the diagram's sans body is what signals editorial voice. That
mechanism does not survive the port intact, because **there are no webfonts** — a
committed SVG may reference nothing remote, and `svg_check.py` fails on a remote `href`
or `@import`. What plays the part here is the resolved style's own `display` stack, in
italic, against the `body` stack the node names use.

So the register is carried by three cues rather than one, and how much each does depends
on the style:

- **Italic.** Never optional; it is the only cue guaranteed to survive every fallback
  chain.
- **The `display` stack.** Where the style names a display face distinct from its body
  face, this recovers most of the upstream contrast — several styles' display stacks are
  serif or hand-lettered already. Where display and body resolve to the same system
  stack, it recovers nothing, and that is fine.
- **The dashed leader and the margin position.** These do the remaining work, and they
  are the reason the primitive still reads when the type contrast is zero.

Two questions worth answering before drawing one: does this style's `display` stack
actually differ from its `body` stack, and if not, is the leader doing enough on its own
that a reader would not mistake the remark for a stray label? If the answer to the
second is no, the note belongs in the doc body.

## Roles

Upstream's three colour intents map onto the grammar roles in §2 with no new role added.

| Intent | Text | Leader and dot |
| --- | --- | --- |
| Neutral aside — the default | `ink` | `ink` at `0.40` |
| Focal | `accent` | `accent` at `0.50` |
| Tertiary | `muted` | `ink` at `0.30` |

The focal row spends focal budget. `accent` belongs to the one or two elements the
diagram is actually about, so an accent callout has to be pointing at one of them; a
callout in accent landing on a non-focal node gives the board three things claiming
attention and `max_focal` will not catch it, because the callout is not a `data-focal`
node. Neutral is the right answer nearly always.

## Budget

**At most two callouts per diagram**, on every type. No key in `scripts/diagrams.json`
counts them and no checker enforces it — this one is prose-owned, so it is a question
rather than a gate: is each of these two remarks something the diagram genuinely cannot
say through a label, and would a reader be worse off without it? Three callouts is
commentary, and commentary belongs in the paragraph beside the visual.

A callout does not count against `max_nodes`, and its `<g>` costs nothing against a
style's `min_elements` floor.

## Placement

- Margins only — top-right and bottom-left are the natural pair. Never inside the
  active diagram area.
- The leader crosses open canvas. It does not cross a connector, a lifeline, a zone
  border or another callout's leader; offset the callout until it doesn't.
- The landing dot sits on the element being remarked on, not near it. A dot floating in
  the gap beside a node is ambiguous about which node it means.
- Right-aligned text (`text-anchor="end"`) in a right margin, left-aligned in a left
  margin, so the ragged edge faces the diagram.

## Motion

`diagram-grammar.md` §11 applies: no animation may mutate `d`, the dot's `cx`/`cy`/`r`,
or a transform on the callout group, because the leader's geometry is a claim about
which element the remark belongs to. A leader that swings between two targets during
the loop is a diagram that says two different things depending on when it is read.

What is legitimate is an `opacity` pass on the whole group, in the ordered-emphasis
idiom — the callout resting low and coming up as the reader's attention reaches it,
seam-exact at the board's `data-loop-s`. A `stroke-dashoffset` march along the leader is
available and is usually the wrong choice: a marching dash reads as transport, which is
what the dash was chosen to *not* say.

Most boards get the honest answer, which is that the callout does not move.

## Anti-patterns

- A solid leader, or a leader with an arrowhead — both read as a flow arrow.
- Upright type. Italic is the primitive; without it this is a floating label.
- A leader crossing arrows, lifelines or zone borders.
- A callout labelling something the diagram should label directly. Put the label on the
  element; the callout is for the remark that has no element to sit on.
- A callout carrying a fact that is not in `facts[]`. It is drawn text making a claim,
  same as any other.
- Three or more on one board.

Upstream's sibling primitive `primitive-sketchy.md` is **not** ported as a mechanism:
this skill already carries a `rough-sketch` style whose doubled strokes and hachure
occupy the same ground, and a style and a primitive competing to roughen the same
drawing is how a board ends up wobbling twice — see `reference/styles/rough-sketch.md`.

## Specimen

The callout has no specimen of its own; it is a primitive, not a type. It appears in
context inside the type specimens under `docs/samples/types/`, wherever the type's own
layout file calls for one.
