# Sequence

Time-ordered messages between actors — who called whom, in what order. Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery); see `THIRD_PARTY.md`.

**Aliases:** `sequence-diagram`, `message-flow`, `interaction` · **Unit counted:** lifeline

**Best for:** request/response flows, protocol exchanges, API call traces, incident
reconstruction, auth and token-refresh paths.

## Layout conventions

Actors are the shared `152×80` node box in one row at the top, each in a `data-node` group
that owns its lifeline. Time runs top → down and only top → down. Messages are horizontal
`data-edge` lines between lifeline centres, so they share a `y` and a plain `<line>` is
legal; the elbow rule (`diagram-grammar.md` §4) reaches only the self-message — a short U
`40` units right of its lifeline, labelled beside the loop.

Message levels sit **`44`** apart. Upstream's `24` rescales to `32`, and `32` is not merely tight — it is unsatisfiable: a §7 label plate is 22 tall and sits 8 above its own stroke, occupying `y−30 … y−8`, so the next message 32 below leaves its plate 2 units from the previous stroke and the checked gap floor of 6 errors. The arithmetic minimum is `8 + 22 + 6 = 36`, which rounds to 40 on the grid; 44 leaves room for a two-line guard. The accent role goes on the primary success response — one message,
occasionally two; an actor's focal stroke is a separate `data-focal` node.

| Kind | Stroke | Marker | When |
| --- | --- | --- | --- |
| Call (sync) | solid `muted`, `link` if it leaves the system | filled | Expects a reply |
| Return | dashed `muted` (`4,4`) | filled, never open | The reply — never solid |
| Async | dashed `muted` | open, never filled | Beacons, events, one-way notify |
| Headline success | solid `accent`, one or two | filled `accent` | The happy-path response |

## Budget

From `scripts/diagrams.json`: **5 lifelines, 12 messages, 2 focal** — five actors is what
fits across 1200 units at the `152` node width. Fragments carry the type's own caps
rather than the shared zone ceiling: **1 combined fragment** (a second
only when each is a single-region `opt` or `loop`), **2 `alt` regions**, **1 level of
nesting** — an `alt` inside an `alt` is two diagrams.

Over budget, split into an overview on the happy path and a detail on the failure path,
and record the cut in `budget_cuts[]`. `par`, `critical`, `break`, `ref`, participant
create/destroy and duration bars are all out of scope.

## Primitives

Three shapes are unique to this type. The **lifeline** is dashed, from the actor's
bottom edge to the message floor; the **activation bar** is the interval an actor holds
control — `16` wide (upstream `8`), because `12` at `x="CX-6"` puts every bar off the 4-unit
grid whenever `CX` is on it — use `x="CX-8"`, stacked for nested calls, always closed.

```svg
<line x1="CX" y1="TOP" x2="CX" y2="BOTTOM" stroke="var(--ink)" stroke-opacity="0.20"
      stroke-width="1" stroke-dasharray="4,4"/>
<rect x="CX-6" y="TOP" width="12" height="H"
      fill="var(--ink)" fill-opacity="0.06" stroke="var(--muted)" stroke-width="0.8"/>
```

The **combined fragment** is a `data-zone` frame spanning only the participating
lifelines, operator in a `48×20` tab at its top-left, mono and upper case.

```svg
<g data-zone="true">
  <rect x="X" y="Y" width="W" height="H" rx="4"
        fill="var(--ink)" fill-opacity="0.02" stroke="var(--rule)" stroke-width="1"/>
  <rect x="X" y="Y" width="48" height="20" rx="4"
        fill="var(--paper)" stroke="var(--rule)" stroke-width="1"/>
  <text x="X+24" y="Y+15" data-role="metadata" data-bg="paper" text-anchor="middle">ALT</text>
  <!-- guard, mono, at (X+16, Y+44); alt divider: a 4,4-dashed var(--rule) line, inset 12 -->
</g>
```

`opt` is one region under an `[if …]` guard, `alt` two regions split by that divider
(`[else]` on the second), `loop` one region under `[for each …]`. Geometry, upstream ×1.25
on the grid: frame inset `16` outside the outermost participating lifeline centre so
activation bars stay inside, guard `24` below the tab, first message `32` below the guard,
divider `20` clear of messages. Markers escape the rescale — `markerUnits` defaults to
`strokeWidth`, so their numbers are multiples of the stroke.

## Motion

Worth animating: the reading order — an ordered emphasis raising each message's opacity
top to bottom, settling on a resting frame where every message is visible. A marching dash
on one long call is the quieter alternative. 8–14s on `data-loop-s`, seam-exact. Nothing
moves geometry (`diagram-grammar.md` §11): bars do not grow, the frame does not expand to
reveal its region, and nothing travels upward, because time is the vertical axis.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| A message arrow pointing upward | Reverses time |
| An activation bar that never closes | Claims the actor still holds control |
| A label over another lifeline | Shift it into a gap, or shorten it |
| Lanes instead of lifelines | That is `swimlane`, a different grammar |
| `if`/`else` as loose arrow clusters | Nothing says they are alternatives |
| An `alt` nested in an `alt` | Two diagrams |
| The accent role on both `alt` branches | Both cannot be the headline |
| A frame over actors with no message in it | Overstates who participates |

## Specimen

`docs/samples/types/sequence.svg`.
