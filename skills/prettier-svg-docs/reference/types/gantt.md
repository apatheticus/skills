# Gantt

Tasks and phases as bars on a shared time axis. Ported from
[`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery); see `THIRD_PARTY.md`.

**Best for:** project plans and roadmaps where tasks have explicit start and end dates
grouped into phases, and the reader needs temporal overlap, parallel tracks and
milestone sequencing in one look.

**It is one of the five chart types, so `reference/charts.md` governs it.** A bar's
start and end are plotted numbers, and a plotted number is a claim: draw it only if the
next run can **recompute** it from the repository's source — a milestone file, dated
release tags, a roadmap doc with real dates. A committed snapshot of somebody's plan is
not recomputable, and a bar drawn from memory is a fabrication with a ruler under it.

## Layout conventions

| Part | Value |
| --- | --- |
| `viewBox` | `0 0 1200 H`, with `H = 96 + rows × 56 + 40` |
| Label column | `x=40` → `x=268` (228 units) |
| Timeline area | `x=268` → `x=1160` (892 units) |
| Axis labels | `y=72`, mono, `data-role="metadata"` |
| Axis separator | hairline in `rule` at `y=80` |
| Row | 56 units tall; the bar is 32 units, 12 units of padding above and below |
| Bar radius | 6 |

Time runs left to right. Pitch is `892 / total_periods`, and a bar's width is
`(end_period − start_period) × pitch` — the one place a non-grid number is unavoidable,
because the axis is data. Snap the *rows* to the grid, not the bars.

Phases are `data-zone` washes behind their rows, at 2% ink with a `rule` hairline, with
the phase name as a mono eyebrow in the left margin. One focal bar carries the accent
role — the critical-path task or the key deliverable — and every other bar is `muted`
fill at 0.15 with a `muted` stroke. A "today" or milestone marker is an optional dashed
vertical in `muted`.

## Budget

From `scripts/diagrams.json`: **12 tasks, 0 edges, 2 focal, 3 zones.**

The zero edge budget is the mechanical form of upstream's rule against dependency
arrows: a dependency drawn between two bars is a checker error here, not a matter of
taste. When a dependency genuinely carries the meaning, the diagram is a `flowchart` or
a `process`, and the Gantt is the wrong type for it.

Past twelve tasks, or past five parallel tracks in one phase, split into a phase-level
overview and one detail chart per phase.

## Primitives

```svg
<!-- an ordinary task -->
<g data-node="true">
  <rect x="X_START" y="ROW_Y" width="BAR_W" height="32" rx="6"
        fill="var(--muted)" fill-opacity="0.15"
        stroke="var(--muted)" stroke-width="1"/>
  <text x="X_START+12" y="ROW_Y+21" data-role="label" data-bg="surface">Task name</text>
</g>

<!-- the focal task: one per board -->
<g data-node="true" data-focal="true">
  <rect x="X_START" y="ROW_Y" width="BAR_W" height="32" rx="6"
        fill="var(--accent)" fill-opacity="0.12"
        stroke="var(--accent)" stroke-width="1"/>
  <text x="X_START+12" y="ROW_Y+21" data-role="label" data-bg="surface"
        fill="var(--accent)">Key deliverable</text>
</g>
```

Task names sit in the left column at the `label` floor of 18 units; the bar's own text
is the short form. Axis periods and phase eyebrows are mono at the `metadata` floor of
16. A bar narrower than its label gets the label to its right, outside the bar, not a
smaller type size.

## Motion

A Gantt is a plan, and a plan holds still. The bars carry measured widths, so nothing
may grow, slide or re-time — a bar animating from zero width shows a false duration in
every frame but the last, and the type ramp exists to be readable at all of them.

What may loop, at 12s: the "today" marker as a slow opacity pulse, or an ordered
emphasis walking the phases in sequence — each phase zone lifting from 2% to 4% ink and
settling. Both leave every coordinate on the board untouched.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| Bars whose dates cannot be recomputed from the repo | A plotted number is a claim; see `reference/charts.md` |
| Dependency arrows between bars | Zero edge budget — and a dependency graph is a different type |
| More than five parallel tracks in a phase | The overlap stops being legible |
| Start and end dates written into the bar label | The axis already says it; the label repeats it worse |
| Equal weight on every bar | Without a focal task the reader has no entry point |
| A bar shortened so its label fits | The width is the datum; move the label out instead |

## Specimen

`docs/samples/types/gantt.svg`.
