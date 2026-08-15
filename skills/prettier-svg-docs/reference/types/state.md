# State

States, transitions and the guards between them — what a thing can be, and what moves it.
Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery); see `THIRD_PARTY.md`.

**Aliases:** `state-machine`, `statechart`, `fsm` · **Unit counted:** state

**Best for:** finite state logic — order status, auth and session state, connection
lifecycle, a form wizard, job-queue status.

## Layout conventions

A state is the shared node box, `152×80` at `rx=8`, named in sans. Two pseudo-states
bracket the machine:

| Marker | Geometry |
| --- | --- |
| Start | filled `ink` dot, `r=8` |
| End | ring, outer `r=12` stroked in `ink`, inner filled `r=8` |

Both are the upstream `r=6` and `8`/`5` markers rescaled by `diagram-grammar.md` §3 and
rounded to the 4-unit grid — at their arithmetic values they read as stray punctuation
next to a `152`-wide box.

Orient along the dominant direction, left → right or top → down, and rearrange the states
before accepting a crossing. This is the type where rearranging usually works, because a
state machine has no natural reading order to protect.

**Transitions are orthogonal, not curved.** Upstream draws them as curves; the host
grammar's connector rule is that a path between nodes sharing neither `x` nor `y` is
elbowed with quarter-arc bends, and the host wins. The single exception is the self-loop,
which leaves and re-enters the same edge: an arc rising `40` units above the state's top
edge at radius `24`, label centred above it.

Transition labels are connector labels and obey `diagram-grammar.md` §7 — a masked plate,
≤14 characters, upper case, mono, `6`–`10` units off the stroke. The upstream form
`event [guard] / action` does not fit in fourteen characters, so the **event** takes the
plate and anything further moves to a legend row keyed by the event name. If three
transitions all need guards spelled out, the machine is really two machines.

The accent role goes on the state the reader should notice — usually the error state, or
the successful terminal state, never both, and never a colour code across all states.

A "from any state" transition is one annotation, not `n` arrows: a single line such as
`* → ERROR on timeout` in the legend strip. Drawing it from every state costs the whole
edge budget to say one thing.

## Budget

From `scripts/diagrams.json`: **9 states, 12 transitions, 2 focal, 3 zones** — the catalog
defaults, no override.

The edge budget binds before the classic heuristic does. Upstream's rule of thumb is that
more than `states × 2` transitions means two machines; here twelve edges is the ceiling
regardless, so from six states onward the arrow count is what forces the split first. Split
by lifecycle phase — a machine for the acquisition path, a machine for the failure and
retry path — and record the cut in `budget_cuts[]`.

## Motion

A state diagram already shows every state at once, so a loop that walks a token through
one representative path is honest and a loop that implies live status is not. Two forms
work: a dash marching along a single transition to show direction, or an ordered emphasis
raising state opacity in traversal order and returning to a resting frame in which every
state is fully drawn. 8–14s on `data-loop-s`, seam-exact.

Geometry never moves — `diagram-grammar.md` §11. In particular, a state does not swell to
mark itself current, and the self-loop arc is not redrawn stroke by stroke. A reader who
pauses the loop is looking at a complete machine, not a snapshot of one.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| An unlabelled transition | *What triggers this* is the entire content of the diagram |
| A "from any state" arrow drawn from every state | One annotation says it; `n` arrows spend the edge budget on it |
| More transitions than `states × 2` | Almost always two machines that share a vocabulary |
| A curved or diagonal transition between off-axis states | Elbows are mandatory; the self-loop is the only arc |
| Colour used to classify states | The accent role marks one state editorially, not a status taxonomy |
| A terminal state with an outgoing transition | It is not terminal; use the ring only where the machine stops |
| Start and end drawn as labelled boxes | The dot and the ring are the convention, and they cost no budget |

## Specimen

`docs/samples/types/state.svg`.
