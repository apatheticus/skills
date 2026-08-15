# Icons

An 87-icon monochrome set lives in `assets/icons/` — one bare `<svg>` per icon, drawn in
`currentColor` against its own 24-unit `viewBox`. This file is the mechanism. It holds no
paths, and reading it loads no icon.

Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery). See `THIRD_PARTY.md`.

---

## When an icon earns its place

Rarely. A labelled box says what a thing is in words the reader already has; an icon says
it in a picture they decode, and the label has to say it anyway. The node box in
`diagram-grammar.md` §6 is the default and carries no icon. An icon needs a yes to one of:

- Is the diagram **scanned** rather than read — a stack map where the reader hunts for
  *the database* rather than reading each name?
- Is the thing a **product** whose logo is more recognisable than its name, and is naming
  the vendor part of the point?
- Does the same kind **repeat** enough that a shared mark beats re-reading six labels
  that differ by one word?

An icon that appears once is decoration. Use it for a whole class or not at all, and never
as the only thing separating two nodes — the label carries the meaning.

## Looking one up

`assets/icons/INDEX.md` is the lookup surface: one row per icon, grouped by category
(Compute, People, Network, Data, Kubernetes, Action, DevOps, Brand, Data stack, Language,
Statistical tools, File formats), with a one-line purpose and its upstream source. Read
the index, pick a name, then read `assets/icons/<name>.svg` — only the icons being drawn.

## Inlining it

A committed SVG references nothing remote, so the geometry is copied in. Two shapes, and
the choice is about repetition.

**A `<symbol>` in `<defs>`, referenced by `<use>`** — the default. Move the icon file's
root attributes onto the `<symbol>`, give it an `id`, paste its children unchanged. The
24-unit `viewBox` maps onto whatever box the `<use>` declares, so scaling needs no
transform, and a mark used eight times is stored once.

```svg
<defs>
  <symbol id="ic-database" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <!-- children of assets/icons/database.svg, verbatim -->
  </symbol>
</defs>
<use href="#ic-database" x="X" y="Y" width="24" height="24" color="var(--muted)"/>
```

**Pasting the paths into a `<g transform="translate(X,Y) scale(S/24)">`** is for a single
appearance whose paths need their own attributes. It costs one element per path against a
style's `min_elements` floor where `<use>` costs one; `svg_check.py` counts both as drawn.

Either way the icon lives inside the `<g data-node="true">` it belongs to. It is not a node, and
never takes `data-node`, `data-edge` or `data-focal`.

## Colour

Every icon is `currentColor` throughout, so it takes whatever the CSS `color` property
resolves to on the `<use>` or an ancestor — `color="var(--muted)"`. That is the whole
binding: no per-icon palette, and `svg_check.py`'s off-system-colour gate exempts
`currentColor` by name, so a correctly inlined icon declares nothing.

Icons take `muted` by default, `ink` when they should read at the weight of the node's own
strokes. `accent` belongs to the ≤2 focal elements and the focal rule owns it.

Generic icons are stroked, brand silhouettes filled. Mixing both in one diagram reads as
two icon sets.

## Size

The board is 1200 units and the grid is 4 (`diagram-grammar.md` §10), so the icon box is a
multiple of 4: **24 is the default**, 32 for a stack map where the mark is what gets
scanned, 40 at the very top. Above that it out-shouts type whose `label` floor is 18.

Two consequences of the 24-unit source box:

- **The stroke scales with the icon.** `stroke-width` 1.5 in icon space renders at
  `1.5 × S / 24` board units — 2 at S=32, 2.5 at S=40, against node strokes of 1.25–1.5.
  Hold a hairline by setting `stroke-width` to `1.5 × 24 / S` on the `<use>` or `<symbol>`.
- **Its interior geometry is exempt from the 4-unit grid**, as a pattern tile is. The grid
  binds the placement — the `<use>` `x`, `y`, `width`, `height` — not a 24-unit path.

Inside a node the icon takes the type-tag slot (§6, item 3) or the left padding column,
8–12 units from the name. It never overlaps text, and if the box must grow to fit one, the
node width moves to the next grid value rather than the type shrinking.

## Licence

Tabler Icons (MIT), Simple Icons (CC0), Devicon (MIT), log-z/logos (MIT) — all
redistributable, all recorded in `THIRD_PARTY.md`; per-icon provenance is `INDEX.md`'s
third column. Brand marks stay their owners' trademarks: fine in documentation, which a
diagram is; not fine redrawn, recoloured off-brand, or implying an endorsement.

Two files diverge from upstream deliberately: `dagster.svg` drops a hardcoded white
knock-out (an icon inheriting its colour cannot know its ground) and `hop.svg` drops an
Inkscape `<metadata>` block whose unbound `rdf:` prefixes made the file invalid XML.
