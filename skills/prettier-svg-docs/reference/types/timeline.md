# Timeline

Events positioned in time along one honest axis. Ported from
[`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery); see `THIRD_PARTY.md`.

**Best for:** release history, project milestones, incident reconstructions, roadmaps,
changelog visualisations — anything whose meaning is *when*, and whose spacing is
therefore data rather than layout.

## Layout conventions

A horizontal hairline baseline across the middle, in `rule`, and everything else hung
off it. The working geometry on a 1200-unit board:

| Part | Value |
| --- | --- |
| `viewBox` | `0 0 1200 520` |
| Baseline | `y=260`, from `x=80` to `x=1120` |
| Tick mark | vertical hairline, `y=252` → `y=268`, at each time boundary |
| Tick date label | `y=292`, mono, `data-role="metadata"` |
| Event dot | `r=6` on the baseline |
| Milestone dot | `r=8`, the accent role |
| Leader, above | `y=252` → `y=180`; name at `y=148`, sublabel at `y=168` |
| Leader, below | `y=268` → `y=348`; name at `y=364`, sublabel at `y=384` |

Labels alternate above and below the axis so adjacent events never collide, each joined
to its dot by a 1-unit hairline drop. The drop shares an x with its dot, so it is a
plain `<line>` and legal under the orthogonality rule. It is not a `data-edge`: it joins
a dot to its own label rather than one event to another, and a timeline usually declares
no edges at all.

**The spacing is the claim.** If the intervals are unequal, the dots are unequally
spaced. Faking a linear rhythm because it looks tidier makes the picture say something
the data does not. When one region is too dense to draw at true scale, break the axis
visibly — a gap with a marked discontinuity — rather than compressing it quietly.

Every date label names its unit. A tick reading `Q3` with no year, or `12` with no
month, is the failure this type produces most often.

## Budget

From `scripts/diagrams.json`: the defaults apply unchanged — **9 events, 12 edges,
2 focal, 3 zones**, on the 4-unit grid. The unit is the *event*, not the tick: an axis
may carry twelve month ticks and still be at three of nine.

Past nine events, split into an overview timeline (phases, or years) and a detail
timeline for the one span that carries the argument. Do not shrink the type ramp to fit
a tenth dot in.

## Primitives

```svg
<!-- the baseline carries no data-edge — it is the axis, not a connection -->
<line x1="80" y1="260" x2="1120" y2="260" stroke="var(--rule)" stroke-width="1"/>

<!-- an ordinary event, label above -->
<g data-node="true">
  <line x1="440" y1="252" x2="440" y2="180" stroke="var(--rule)" stroke-width="1"/>
  <circle cx="440" cy="260" r="6" fill="var(--muted)"/>
  <text x="440" y="148" data-role="label" data-bg="background"
        text-anchor="middle">v2.0</text>
  <text x="440" y="168" data-role="metadata" data-bg="background"
        text-anchor="middle" class="sub">schema rewrite</text>
</g>

<!-- a milestone: the accent role, larger dot, one or two per board -->
<g data-node="true" data-focal="true">
  <circle cx="760" cy="260" r="8" fill="var(--accent)"/>
</g>
```

Dates are mono; names are sans. Both are `data-role` floors from
`reference/diagram-grammar.md` §3 — 18 units for a name, 16 for a date or sublabel.

## Motion

The axis is fixed, so nothing on it may move. What can loop is a **read head**: a soft
vertical band or a brightening pass that sweeps left to right along the baseline once
per cycle, at 12s, seam-exact because it re-enters at `x=80` exactly where it started.
An ordered emphasis works too — each event's dot rising in opacity in date order, then
resting.

Motion never moves geometry. A dot that drifts is a date that changed; a leader whose
length animates is an event that moved. Neither the dots, the leaders, the ticks nor
any text may be animated in `cx`, `cy`, `r`, `x`, `y` or a transform.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| Equal spacing for unequal intervals | The axis stops being data and becomes decoration |
| No unit on the axis | "Q3" of what? The reader cannot place a single event |
| Labels all on one side | They collide, and the alternation is what buys the density |
| A label with no leader | At any density above four events the reader guesses which dot it belongs to |
| A milestone for every event | The accent role is one or two editorial marks |
| A silently compressed dense region | Break the axis visibly or split the diagram |

## Specimen

`docs/samples/types/timeline.svg`.
