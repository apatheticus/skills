# Diagram grammar — the parts every type shares

`reference/diagrams.md` picks the type. `reference/types/<slug>.md` gives that type its
layout. This file is the vocabulary underneath both: how a node is built, how a
connector is routed, where a label sits, what the grid is, and how the grammar's
semantic roles bind to whatever this repo's palette happens to call things.

Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery), re-expressed for a hand-authored 1200-unit SVG. See
`THIRD_PARTY.md`.

Everything here is checked by `svg_check.py`'s `diagram` class, which fires only when
the root carries `data-diagram`.

---

## 1. Semantic attributes

The grammar is only machine-checkable because the drawing says what its parts *are*.
Six attributes, in this skill's existing `data-*` namespace:

| Attribute | Goes on | Means |
| --- | --- | --- |
| `data-diagram="<slug>"` | the root `<svg>` | this is a diagram of that type; turns the `diagram` class on |
| `data-node="true"` | the `<g>` wrapping one node | one unit of the type's budget |
| `data-edge="true"` | the `<path>` or `<line>` of one connector | one connection |
| `data-label="true"` | the connector label's mask `<rect>` | a label plate, checked for clipping and gap |
| `data-focal="true"` | the accented group | one of the ≤2 accented elements |
| `data-zone="true"` | the `<g>` wrapping a zone/lane/boundary | a grouping container |
| `data-legend="true"` | the `<g>` wrapping the legend strip | must sit below every node |

**Write `="true"`, not a bare attribute.** The checker only asks whether the attribute
is present, so any value works — but SVG is XML, and XML has no valueless attributes.
A bare `<g data-node>` makes the file not well-formed, and the only thing the checker
can tell you is `not well-formed (invalid token)` at a line and column, which names
neither the attribute nor the cause. This matches the existing `data-specimen="true"`.

Two facts make this free. `<g>` is not a drawn tag, so semantic wrappers cost nothing
against a style's `min_elements` floor. And these attributes make the geometry checks
*exact*: upstream has to guess that a node is a `<rect>` at least 60×40 and a label
plate is 20–120 × 8–14, and its own ADR-0005 concedes the guess needs revisiting per
type. Here nothing is guessed.

## 2. Roles, and how they bind to this repo

The grammar names roles. The repo's frozen design system names colours. They are joined
by the mapping table in `reference/design-system.md`, and **the grammar never adds a
required palette role** — a repo whose palette has six roles maps all of these onto
those six, and a repo with twenty maps more precisely. Mapping, not extending, is what
keeps `design_hash` still.

| Grammar role | What it is for |
| --- | --- |
| `paper` | the board ground, and the fill of every mask |
| `surface` | node fill, zone wash |
| `ink` | primary text and stroke |
| `muted` | secondary text, sublabels, the default connector |
| `rule` | hairlines, zone borders, the legend separator |
| `accent` | the 1–2 focal elements, and nothing else |
| `link` | connectors that leave the system — HTTP, API, third party |

**The focal rule is the one that gets broken.** `accent` on one or two elements. If four
things want it, the focal decision has not been made. `svg_check.py` errors above the
type's `max_focal`. `data-focal` usually goes on a node group, but not always — on a
`venn` the focal is an intersection *region* and not a set, so it goes on whatever group
carries the accent. The rule counts accented elements, not nodes.

**The snippets in this file name the grammar's roles. A committed SVG names the
repo's.** Both the `var(--role)` custom properties and every `data-bg` value must
resolve to a role the project's `.prettydocs/prettydocs.md` actually declares — so on a
palette that calls its ground `background`, the snippets' `paper` becomes `background`
in the file you commit. A `data-bg` that names no declared role is the checker's one
quiet failure: a `WARN` rather than an `ERROR`, and the contrast floor is then not
applied to that text at all. Treat it as a failure.

### Node treatment by kind

| Kind | Fill | Stroke |
| --- | --- | --- |
| Focal (1–2) | `accent` at low alpha | `accent` |
| Service / API / step | `paper` | `ink` |
| Store / state | `ink` at 0.05 | `muted` |
| External / third party | `ink` at 0.03 | `ink` at 0.30 |
| Input / actor | `muted` at 0.10 | `muted` |
| Optional / async | `ink` at 0.02 | `ink` at 0.20, dashed `4,3` |
| Security boundary | `accent` at 0.05 | `accent` at 0.50, dashed `4,4` |

Every value goes through a declared custom property. A raw hex in the markup is a
checker error, and the palette table in `.prettydocs/prettydocs.md` is where the hex
lives.

## 3. Type ramp

This is where the two systems genuinely disagree and the host wins, so read the number
rather than porting the source. Upstream measures its ramp in CSS pixels on a 960–1280
canvas: node name 12px, sublabel 9px, eyebrow 7px. On this skill's **1200-unit
`viewBox`** a 12px node name is about **15 units — below the `label` floor of 18**, and
those floors are contrast-tested rather than aesthetic.

So the ramp is re-expressed as `data-role` floors, and the whole 7/8/9px tier collapses
into one:

| Grammar element | `data-role` | Minimum units at `viewBox` width 1200 |
| --- | --- | --- |
| Diagram title | `title` | 40 |
| Editorial callout | `essential` | 20 |
| Node name | `label` | 18 |
| Node sublabel | `metadata` | 16 |
| Type tag / eyebrow | `metadata` | 16 |
| Connector label | `metadata` | 16 |
| Legend item | `metadata` | 16 |
| Zone eyebrow | `metadata` | 16 |

**A wider `viewBox` scales the floor with it** — the floors are relative, so a
1600-unit board multiplies them by 1600/1200.

Consequence worth stating, because it is where a ported layout goes wrong: the node box
grows too. Upstream's 120×64 node at 960 becomes **152×80** here, and every type
reference's coordinates are scaled the same way. A ported node box that still measures
120×64 has silently kept the old ramp and its text is under the floor.

Mono is for technical content — ports, commands, URLs, field types. Names are sans. The
font stacks are the repo's own system stacks; there is no webfont, ever, because a
committed SVG may not reference anything remote.

## 4. Connectors — the six rules

Non-negotiable. **Three of the six are checked and three are not**, and knowing which
is which is the point of saying so: rules 1, 2 and 6 fail loudly in `svg_check.py`'s
`diagram` class; rules 3, 4 and 5 are author-side, because each needs an ownership link
between a connector and a node that the drawing does not declare. Read them as the
hand checks they are.

**1. Rounded right-angle elbows are mandatory.** A diagonal `<line>` or a slanted path
between nodes that share neither x nor y is an automatic fail. A plain `<line>` is legal
only when the endpoints share a coordinate. Every bend is a quarter-arc, `r=10` at this
scale (`r=8` minimum in tight layouts).

```svg
<!-- right + down, from (x1,y1) to (x2,y2); mid = (x1+x2)/2 -->
<path data-edge="true" d="M x1,y1 H mid-10 Q mid,y1 mid,y1+10 V y2-10 Q mid,y2 mid+10,y2 H x2"
      fill="none" stroke="var(--muted)" stroke-width="1.5" marker-end="url(#arrow)"/>
```

Flip the vertical signs for right+up.

**Port selection.** When the destination is noticeably above or below the source, leave
the source's top or bottom edge and enter the destination's top or bottom edge, with a
single-bend L-path. Side ports are for connections that travel mainly horizontally —
entering a node from the side on a mostly-vertical path reads as the arrow puncturing
the node face rather than arriving from above.

```svg
<!-- entering a node from its bottom; destination above source -->
<path data-edge="true" d="M x1,y_src H x2-10 Q x2,y_src x2,y_src-10 V y_dst"
      fill="none" stroke="var(--muted)" stroke-width="1.5" marker-end="url(#arrow)"/>
```

**2. Label-to-connector gap: 6–10 units, always.** The label never sits on its arrow.
The mask keeps the stroke from bleeding through the text; the *visible gap* between the
mask edge and the stroke is what lets the reader keep tracing the line. Never let the
mask touch the stroke.

**3. No overlapping connectors.** Two connectors never share a stroke path or run on top
of each other for any segment. When two must cross, hop the less important one. When two
want to run parallel, offset them by ≥12 units for their whole length, not just at the
attach point. If you are stacking connectors, the layout is wrong or the diagram is over
budget.

```svg
<!-- horizontal hop over a vertical crossing at x = cx -->
<path data-edge="true" d="M x1,y H cx-10 a 10,10 0 0,1 20,0 H x2" fill="none" .../>
<!-- vertical hop over a horizontal: a 10,10 0 0,0 0,20 -->
```

Bridge the passive, secondary, write-back or dashed line. Never bridge both.

**4. A shared edge means fanned attach points.** No two connectors share a point on a
box. For N connectors on an edge of length L, attach point `k` sits at `L × k / (N+1)`
from the leading corner, and adjacent points are ≥12 units apart. Route each one
orthogonally from its own point — strokes never merge near the box.

**5. A connector does not pass behind a box that is not its endpoint.** Reroute by
default. The one exception is a cross-cutting node — a footer bar, a horizontal layer —
that physically sits on the only direct orthogonal path. In that case the stroke is
**dashed** (`4,3`) to say *transit, not interaction*, the label sits at the visible end,
and no arrowhead may land on the intervening box's edge.

**6. A label mask does not overlap a node drawn after it.** Rule 2 keeps the label off
its own connector; this keeps it off the boxes. Nodes paint after labels, so a mask
landing inside a node is covered by the node fill and the text renders as a fragment on
the border. Put the label on a stretch of connector that runs through open canvas. Two
cases are legal and the checker knows them both: a mask fully *inside* a node is a badge
chip, and a mask over a **zone** is fine because zones paint first.

**Dashed paths follow every rule above.** The dash carries semantic weight, not a
different routing grammar.

**Two rules about the arrowhead itself**, which routing does not cover:

- **A marker's body extends backwards along the path**, so a connector entering a
  node's top edge while travelling *upward* buries its own arrowhead under the node
  fill. Check the direction of travel, not only the edge.
- **The marker terminates on the destination's rectangle edge** — not at its centroid,
  which hides the head, and not short of it, which leaves the connector floating.

## 5. Paint order

```
background → zones → connectors → connector labels → nodes → legend
```

This is not a preference; rule 6 is a consequence of it. Arrows before boxes is what
puts the strokes behind the nodes.

## 6. Node box

```svg
<g data-node="true">
  <!-- 1. opaque mask, so a connector behind a translucent fill does not show -->
  <rect x="X" y="Y" width="152" height="80" rx="8" fill="var(--paper)"/>
  <!-- 2. the styled box -->
  <rect x="X" y="Y" width="152" height="80" rx="8"
        fill="var(--surface)" stroke="var(--ink)" stroke-width="1.25"/>
  <!-- 3. rectangular type tag — a rectangle, never a pill -->
  <rect x="X+8" y="Y+8" width="40" height="20" rx="4"
        fill="none" stroke="var(--ink)" stroke-opacity="0.4" stroke-width="1"/>
  <text x="X+28" y="Y+23" data-role="metadata" data-bg="surface"
        class="tag" text-anchor="middle">API</text>
  <!-- 4. node name — sans, human-readable -->
  <text x="CX" y="CY+2" data-role="label" data-bg="surface"
        class="name" text-anchor="middle">Node Name</text>
  <!-- 5. technical sublabel — mono -->
  <text x="CX" y="CY+24" data-role="metadata" data-bg="surface"
        class="sub" text-anchor="middle">svc:8080</text>
</g>
```

**Radius belongs to the style, not to this file.** 4, 6 or 8 units is the default, and
it is only a default: a resolved style that declares `min_rx` or `max_rx` in
`scripts/styles.json` overrides it, and the checker enforces the *style's* number.
`bento-grid` floors radius at 12 and `swiss-minimal` caps it at 2 — a node box drawn at
`rx="8"` is an error under both. Read the resolved style's spec before choosing, the
same way you would for its fills. Radius is material; the grammar owns structure.

No shadow — borders, not shadows — unless the resolved style is one whose material *is*
a shadow (`flat-material` requires `feDropShadow` on every filter), in which case the
style's spec wins and says so.

## 7. Connector labels

```svg
<!-- stroke sits at ARROW_Y; the mask bottom is 8 units above it -->
<rect data-label="true" x="MID-40" y="ARROW_Y-30" width="80" height="22" rx="4" fill="var(--paper)"/>
<text x="MID" y="ARROW_Y-14" data-role="metadata" data-bg="paper"
      class="edgelabel" text-anchor="middle">WRITE</text>
```

- ≤14 characters, upper case, centred on the segment midpoint. Where a type's own
  vocabulary cannot fit that — `state`'s `event [guard] / action` form is the case that
  bites — the plate carries the part that identifies the transition and the rest moves
  to a legend row. Two stacked lines on one plate are permitted only when the type
  reference says so; a plate that grows to hold prose is a diagram over budget.
- 6–10 units between the bottom of the mask and the stroke. Checked.
- For a vertical segment the label goes beside the line, with the same gap horizontally.
- Never `writing-mode: vertical`.

## 8. Zones

Drawn before connectors and nodes.

```svg
<g data-zone="true">
  <rect x="X" y="Y" width="W" height="H" rx="10"
        fill="var(--ink)" fill-opacity="0.02"
        stroke="var(--rule)" stroke-width="1"/>
  <rect x="LX" y="Y+8" width="LW" height="20" rx="4" fill="var(--paper)"/>
  <text x="LCX" y="Y+23" data-role="metadata" data-bg="paper"
        class="eyebrow" text-anchor="middle">EDGE</text>
</g>
```

- **Zone `y` is `first_node_top − 48`.** That is the one number; the others follow from
  it. The eyebrow plate sits at `Y+8` and is 20 tall, so its bottom is at `Y+28`,
  which leaves exactly the **≥20 units** of clear space the eyebrow needs above the
  first enclosed node. (An earlier draft said `− 40` *and* `≥20`, with an 18-tall plate
  at `Y+5`: that arithmetic yields 17, and the two rules could not both hold at any
  plate height at or above 15. If you change one of these three numbers, redo the sum.)
- The wash is 2% ink. Anything stronger competes with the node fills.
- Three zones is the default ceiling, and some types declare their own — `nested` gets
  6, `swimlane` 5, `high-level` 4, `sequence` 1. Past the ceiling with no override, it
  is a `swimlane`; use that type.

## 9. Legend

A horizontal strip **below every node**, never floating in the diagram area, with a
hairline separator above it. Expand the `viewBox` height by about 72 units to hold it.

```svg
<g data-legend="true">
  <line x1="40" y1="LY-10" x2="1160" y2="LY-10" stroke="var(--rule)" stroke-width="1"/>
  <text x="40" y="LY+10" data-role="metadata" data-bg="paper" class="eyebrow">LEGEND</text>
  <!-- items in a row, ~200 units apart -->
</g>
```

## 10. The 4-unit grid

Every font size, coordinate, width, height, gap and radius divisible by 4. Checked on
`[data-node]` geometry.

The width and height row below is a **menu, not an enumeration**. The rule is
divisibility by 4, which is what `svg_check.py` measures; a derived 188 or 260 that a
type's own arithmetic produces is legal. The list is there so a board does not end up
with nine slightly different box widths.

| Category | Values |
| --- | --- |
| Type sizes | 16, 20, 24, 28, 32, 40, 48 |
| Node width | 96, 120, 132, 152, 160, 180, 200, 240, 320 |
| Node height | 56, 64, 72, 80, 88, 96, 104, 120 |
| Coordinates | any multiple of 4 |
| Gap between nodes | 24, 32, 40, 48, 64 |
| Padding inside a box | 8, 12, 16, 20 |
| Radius | style-owned — 4, 6, 8 only where the style declares no `min_rx`/`max_rx` |

Exempt: **corner radius** (a style may require 12 or cap at 2, neither of which the
grid should override), stroke widths, opacities, a pattern tile's own geometry, marker
geometry
(`markerUnits` defaults to `strokeWidth`, so a marker's numbers are multiples of the
stroke and not board units) — and **plotted data coordinates**. A chart's *skeleton*
sits on the grid: axes, ticks, gridlines, the plot rectangle, the legend. Its *values*
do not, because forcing a measured number onto a 4-unit lattice would move the number.
`svg_check.py` reads only `[data-node]` rect geometry, so the exemption is already how
the checker behaves; it is stated here so nobody "fixes" a radar polygon onto the grid.

Quick check — a coordinate ending in 1, 2, 3, 5, 6, 7 or 9 is wrong.

**When a style's column grid and this grid disagree, this one wins for `[data-node]`
geometry — and only for that.** A style may prescribe its own columns, and those
columns need not land on multiples of 4. `bento-grid` is the worked case: its six
columns are `x = 40 + col × 190` with `w = span × 170 + (span − 1) × 20`, of which
`x ∈ {230, 610, 990}` and `w ∈ {170, 550}` are odd multiples of 2, so the only cell
shape a `data-node` may occupy is a **span-2 cell at an even column** — `x ∈ {40, 420,
800}`, `w = 360`. There is no rescue by moving the margin or the gutter: with margin
`4m` and gutter `4g`, a 4-divisible column requires `2m + 5g ≡ 0 (mod 6)`, and the
frozen 20-unit gutter fixes `g = 5`, leaving `2m ≡ 5 (mod 6)` — unsatisfiable for any
integer.

So a node that cannot take a legal cell is centred on the 4-grid instead, off the
style's columns, and everything that is *not* a `data-node` — zones, connectors,
labels, legend, decoration — keeps following the style. The style still owns the
board's rhythm; the grid owns the boxes the checker measures.

## 11. Motion

The seam contract in `reference/svg-animation.md` applies unchanged: `data-loop-s` on
the root, every duration divides it, every animation `infinite`, no entrance
animations, and a reduced-motion block.

One rule is specific to diagrams and it is the single rule imported from upstream's
motion model:

> **Motion never moves geometry.** No animation may mutate `d`, `x`, `y`, `cx`, `cy`,
> `r`, `width`, `height`, `viewBox`, or a `translate`/`scale` transform on a
> `[data-node]` or `[data-edge]`. Nor semantic text.

The reason is mechanical rather than aesthetic: every geometry check in this file
measures the committed coordinates, so a loop that moves a node is a diagram that
passes its gate in one frame and fails in another. What may move: a flow token along a
fixed path, a dash offset marching along a connector, an ordered emphasis that changes
opacity or stroke weight, a material pass belonging to the style. All of them explain a
diagram that is already complete and correct at every instant.
