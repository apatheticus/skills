# Flowchart

Decision logic with branches — the shape a reader follows to find out which path their
own case takes. Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery); see `THIRD_PARTY.md`.

**Aliases:** `decision-tree`, `decision-flow`, `branch` · **Unit counted:** step

**Best for:** decision logic, algorithms, user-facing branching flows ("Should I…?"),
onboarding routing, support-triage trees.

When the thing to explain is *why two similar requests ended differently*, read
`reference/diagram-patterns.md` §4 first. Flowchart is that pattern's nearest type, and
the pattern owns its own primitives and a tighter budget than this file's.

## Layout conventions

Shape carries the kind. Colour never does — the accent role is editorial, and a fill that
means "decision" is a second signalling system arguing with the first.

| Kind | Geometry |
| --- | --- |
| Start / end | stadium, `152×56`, `rx=28` — half the height, so the ends are true semicircles |
| Step / action | the shared node box, `152×80`, `rx=8` |
| Decision | diamond on a `180×120` bounding box, vertices at the four edge midpoints |
| Merge point | filled `ink` dot, `r=8`, where branches rejoin |

Those are the upstream shapes rescaled to the 1200-unit board by `diagram-grammar.md` §3:
the `120×64` step becomes `152×80`, the `rx=20` terminator becomes `rx=28`, and the `r=4`
merge dot becomes `r=8` — at the arithmetic value of `5` it is a speck, and `8` is the
nearest value on the 4-unit grid that still reads as a junction.

Flow runs top → down. From a diamond the conventional exits are Yes to the right and No
below, and every outgoing arrow is labelled regardless. Each exit leaves from its own
vertex — right, bottom, left — which is why three is the exit ceiling: there is no fourth
vertex that is not the entry.

The accent role goes on the happy path *or* on the single most consequential decision,
never on every decision. Two focal marks is the ceiling and one is usually the right
answer.

Elbows, label plates, attach fanning and the arc hop for an unavoidable crossing are the
shared grammar's job — `diagram-grammar.md` §4, checked by `svg_check.py`.

## Budget

From `scripts/diagrams.json`: **9 steps, 12 edges, 2 focal, 3 zones** — the catalog
defaults, with no per-type override. Diamonds and merge dots are steps and count.

A tree that exceeds this is two diagrams: an overview that ends at the branch, and a
detail that starts there. Shrinking the boxes is not the alternative, because the type
ramp is a contrast floor rather than a preference. Whatever the split leaves out is
recorded in `budget_cuts[]` in the visual's `viz.json`.

## Motion

A flowchart is a static claim about routing, so the honest loop is one that traces a path
already fully drawn: a dash marching along the happy path, or an ordered emphasis that
lifts one step's opacity at a time in traversal order and returns to the resting frame.
8–14s on `data-loop-s`, seam-exact, every duration dividing it.

What may not move is geometry — `diagram-grammar.md` §11. A diamond that swells to look
"active", a branch that slides in, an arrow that redraws itself: each makes the committed
coordinates true in one frame and false in another, and the geometry checks measure the
committed ones. Branch labels stay put, because a reader who pauses the loop anywhere
must still be able to read both exits.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| Fill colour signalling node type | Shape already says it, so the colour then says nothing |
| A decision with four or more exits | Nest two diamonds; a four-way diamond has no exit vertex left |
| An unlabelled branch | The reader cannot tell which case is theirs — the one failure a flowchart does not survive |
| Two exits leaving one vertex | Fan them; merged strokes near the box are untraceable |
| The accent role on every decision | Then nothing is focal and the eye has no entry point |
| A merge dot standing in for a step | It rejoins branches; it does not do anything |
| A loop drawn as an upward diagonal back to the top | Route it as an orthogonal return down the outside margin |

## Specimen

`docs/samples/types/flowchart.svg`.
