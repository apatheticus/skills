# Venn — set overlap

Two or three sets drawn as overlapping circles, where the overlap itself is the claim.

Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery), re-expressed for the 1200-unit board. See `THIRD_PARTY.md`.

**Best for:** the intersection of two or three domains, shared attributes across
categories, "where A meets B", and ikigai-style frames (desirable × feasible × viable).

## Layout conventions

- **Two or three circles.** `svg_check.py` caps `data-node` at 3. Four sets is a
  different diagram — see Anti-patterns.
- **Radii are equal only when the sets are.** Proportional radii when the sets differ
  meaningfully in size. Drawing a set the same size as one twice its weight is a claim
  the reader has no way to check and no reason to doubt.
- **Stroke is a 1-unit hairline**, `ink` or `muted` at reduced opacity. **Fill is a very
  low tint** — `ink` at 0.04 for the first set, `muted` at 0.05 for the second, `ink` at
  0.03 for the third — and the tints compound in the overlaps. That compounding *is* the
  drawing. Do not also paint the lens regions as separate filled paths: two tints plus an
  explicit lens fill disagree along every edge, and the seam shows.
- **Set labels sit outside their circle and never cross the stroke.** The name is `label`
  (18-unit floor), an optional technical sublabel is `metadata` (16). Anchor `end` on the
  left of the figure, `start` on the right, `middle` above or below.
- **Region labels sit inside the region they name**, centred, at the `label` floor. Where
  the region is too small for the word, put the label in clear canvas and run a leader to
  it.
- **A leader is not a connector.** It carries no `data-edge`, no arrowhead and no label
  mask — a hairline in `rule` from the region to the text, and nothing else. The
  connector rules in `diagram-grammar.md` §4 have no work to do on this type.
- `data-bg` on a region label names the composite **furthest from the text colour** — the darkest stack under
light-ground dark text, the lightest under dark-ground light text. Stating it as
"darkest" is correct only on a light palette and silently overstates contrast on
a dark one, which is the same trap in mirror image that this repo already records
for glassmorphism: paper plus
  every tint that overlaps there, not paper alone.
- Centres and radii sit on the 4-unit grid.

A three-set layout that works on a 1200-unit board, `viewBox="0 0 1200 960"`:

```
r = 200,  centres A(480,440)  B(720,440)  C(600,648)
```

Centres 240 apart give lens regions wide enough for a short word at the `label` floor.
The triple region in the middle holds **one** short word; anything longer takes a leader.

```svg
<g data-node="true">
  <circle cx="480" cy="440" r="200" fill="var(--ink)" fill-opacity="0.04"
          stroke="var(--ink)" stroke-opacity="0.35" stroke-width="1"/>
  <text x="256" y="404" data-role="label" data-bg="paper"
        text-anchor="end" class="setname">Desirable</text>
  <text x="256" y="432" data-role="metadata" data-bg="paper"
        text-anchor="end" class="sub">users ask for it</text>
</g>

<!-- the sweet spot: one accented region, clipped to the intersection -->
<g data-focal="true">
  <path d="…" fill="var(--accent)" fill-opacity="0.10"/>
  <text x="600" y="512" data-role="label" data-bg="accent"
        text-anchor="middle" class="region">Ship</text>
</g>
```

## Budget

From `scripts/diagrams.json`: **3 sets, 0 edges**, and the inherited defaults of **2
focal, 3 zones**. Two focal is the ceiling; **one** is the answer this type usually
wants, because the whole figure exists to point at a single sweet spot.

Over budget there is no split that keeps the type — four sets is not a denser Venn, it
is an unreadable one. Take a `quadrant` if two of the four are really axes, or a
`dp-security-matrix` if the question is which combinations hold. Record the change in
`budget_cuts[]`.

## Motion

One thing moves: the focal region's tint, breathing between two opacities on a duration
that divides `data-loop-s`. Everything else holds.

`cx`, `cy` and `r` may not animate. The overlap geometry is the entire content of the
type, so a Venn whose circles drift is making a different claim at every frame — and the
grid and radius checks measure the committed values, which the moving frames no longer
match. Set labels do not move either: a label that crosses its own stroke halfway through
the loop is the exact failure the layout rules exist to prevent.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| An unlabelled region | The reader cannot tell which set is which, and the overlap is the point |
| Circles that do not actually overlap | Then the sets are disjoint and this is a list |
| Equal radii for obviously unequal sets | Dishonest, and invisible to the reader |
| The accent role on more than one region | The sweet-spot signal dies the moment there are two |
| A label sitting on a circle stroke | Illegible; the stroke runs through the letterforms |
| Four or more circles | Unreadable at any size — use a matrix or a quadrant |
| Lens regions painted as explicit fills over the compounded tints | The two disagree at the edges |

## Specimen

`docs/samples/types/venn.svg`.
