# Loop

A reinforcing cycle: work advances clockwise around a ring of stations while every pass
writes state back to one shared hub. Ported from
[`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery); see `THIRD_PARTY.md`.

**Best for:** flywheels, feedback loops and operating loops — where the last step really
does feed the first and something in the middle accumulates. Choose `flowchart` when the
path ends, branches toward an outcome, or never returns to its first step. The dashed
write-back spokes are the signal: remove them and this is a circular process.

## Layout conventions

| Parameter | Value |
| --- | --- |
| `viewBox` · hub centre `C` · ring radius `R` | `0 0 1200 880` · `(600, 440)` · `300` |
| Station box · hub box | 200 × 80 · 240 × 128 |
| Outer margin · spoke gap at the hub | 80 · 8 |

The geometry is deterministic. Station `k` of `N`, zero-indexed clockwise from the top:

```text
theta_k   = -90deg + k × (360deg / N)
P_k       = C + R × (cos theta_k, sin theta_k)
station_x = P_k.x - 100   station_y = P_k.y - 40
```

Round the station rectangles to the 4-unit grid *after* computing the ideal centres,
paired stations symmetrically; keep circle-intersection points at three decimals so the
arcs stay on one circle. The `viewBox` holds `cx ± (R + 100 + margin)` and
`cy ± (R + 40 + margin)` — `200…1000` and `100…780`.

**Two connector primitives are type-specific exceptions to the grammar's rule 1**, and
the only ones; the rest of `reference/diagram-grammar.md` §4 applies unchanged:

- **Ring arcs.** `A R R 0 0 1` on the station circle — same centre, same radius,
  clockwise, large-arc flag `0` since adjacent gaps are under 180°. Each leaves the
  source box at the circle's clockwise exit and stops `1.5 / R` radians short of the
  destination's entry, the arrowhead covering that last 1.5 units.
- **Radial spokes.** True radii from a station's inner edge to the hub, dashed `6,4` in
  `muted`, stopping 8 units outside the hub stroke, touching only their own station and
  the hub, never each other.

## Budget

From `scripts/diagrams.json`: **9 nodes, 16 edges, 2 focal, 3 zones.** The hub is a
node, so nine nodes is eight stations plus the hub. `max_edges` is an override, not the
default — `loop` is one of the few types that carries one.

**The edge budget is why the override exists.** A station costs a ring arc *and* a
write-back spoke, so `N` stations cost `2N` edges. At the default 12 the type would cap
at six stations for arithmetic reasons rather than editorial ones; at 16 the ceiling is
the node budget instead, which is the honest constraint. Below five stations the ring
reads as a triangle rather than a cadence, so the working range is **five to eight
stations with a spoke each**.

Exactly one hub, at most one focal station. Past budget, split into an overview Loop
plus a detail per stage.

## Primitives

```svg
<!-- ring arc, station k to k+1 -->
<path data-edge="true" d="M QX_EXIT,QY_EXIT A 300 300 0 0 1 QX_END,QY_END"
      fill="none" stroke="var(--muted)" stroke-width="1.5" marker-end="url(#arrow)"/>

<!-- write-back spoke, station edge inward to the hub -->
<path data-edge="true" d="M SX,SY L HX,HY" fill="none" stroke="var(--muted)" stroke-width="1.25"
      stroke-opacity="0.55" stroke-dasharray="6,4" marker-end="url(#arrow-soft)"/>
```

Stations are the grammar's node box at 200 × 80; the hub is that box inverted — `ink`
fill, text at `data-bg="ink"` — and is the board's only inverted element. Paint order is
the grammar's, hub last: ground → arcs → spokes → labels → stations → hub → text, so the
boxes mask any microscopic arc overshoot.

The hub is not another stage. It is accumulated state — memory, standards, evidence, a
shared operating record — and holds one name plus a short sublabel. Label two or three
spokes rather than crowding six into the hub halo.

## Motion

This is the one type whose obvious animation is also the correct one. A **flow token
travelling the ring** — a dot on the circle the arcs sit on — is what the diagram already
claims is happening, and it is seam-natural by arithmetic: `rotate(0deg → 360deg)` about
`C` over 12s returns to its exact origin, no keyframe tuning and no `alternate`. A
dash-offset march along the spokes, one period per cycle, reads as the write-back.

It still may not move geometry. The token is a free element, not a `[data-node]` or a
`[data-edge]`; a rotating station, an animated arc `d` or a spinning group all move boxes
the checker measures once. The ring turns, the stations do not.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| Two hubs | Two accumulated states are two systems — draw two diagrams |
| Solid spokes | They read as primary flow; the write-back signal disappears |
| Mixed arc and orthogonal ring segments | The ring becomes a rounded rectangle |
| A connector across the hub | Flow gets confused with state; raise `R` |
| Uneven station angles for no reason | The ring stops reading as one cadence |
| The accent on more than one station | The editorial gate disappears |
| A cycle that never returns | That is a flowchart arranged in a circle |
| A spinning diagram | Turn the token, not the ring |

## Specimen

`docs/samples/types/loop.svg`.
