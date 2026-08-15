# DP integration

The integration topology of a data platform — which sources plug in, which consumer
surfaces plug out, and what protocol each wire speaks. Ported from
`cathrynlavery/diagram-design` (MIT © 2025 Cathryn Lavery); see `THIRD_PARTY.md`.

**Best for:** the question *what surfaces does this platform expose, and over what wire?*
How data moves through phases is `high-level`; the landscape it replaces is `it-state`.

Mechanics are in `reference/diagram-grammar.md`: elbows §4, zones §8, node box §6,
connector labels §7, legend §9.

## Layout conventions

**Hub and spoke, in one explicit platform zone.** Sources in a left column, consumers in a
right column, the platform's components in a labelled zone between them. No phase axis and
no chevron banner — those belong to `high-level` and imply a time ordering this type is
not claiming.

**Every wire carries its protocol** — `JDBC`, `SFTP`, `ODBC`, `REST`, `HTTPS`, `IMAP`, per
§7, and always the wire's name rather than a verb. An integration team reads the labels
first and the boxes second, so one unlabelled bus arrow from "sources" to "the platform"
says nothing a sentence would not.

**Identity connects to the layer, never to a component.** A directory, secrets store or
policy engine authenticates everything inside the zone, so it sits in a band below and
sends one dashed line to the zone's bottom edge, labelled `AUTH`. Wiring it to one tool
understates the trust scope by the number of tools it also protects. Any layer-wide
service is the same: its own band, its own line to that edge, 32 apart.

**Exactly two focal components: the storage hub and the federation engine.** Those two
surfaces are what distinguish a platform from a pile of tools, and two is also the type
ceiling, so the decision makes itself; everything else stays `ink` or `muted`. Every
serve-flow edge to a consumer therefore touches a focal node and is accent by topology,
not by choice. Read-back and federated queries take `link` with a `4,3` dash; scheduler
triggers `muted`, dashed, unlabelled.

### Geometry

Upstream already measures this type on a 1200-unit canvas, so its x-coordinates carry over
unchanged — the ×1.25 rescale the other ports need is an error here. Heights moved: §6's
node box is 80 tall and upstream's side-column node was 64, too short to seat an 18-unit
name over a 16-unit sublabel.

```
left_x = 40   left_w = 160     right_x = 1000  right_w = 160
col_top = 92  col_node_h = 80  col_gap = 24    # stride 104 → 92, 196, 300
zone_x = 260  zone_w = 696     zone_y = 72     zone_pad_x = 16
zone_h = max(336, n_side * 104 - 24)
row_h = 80    row_gap = 24     bar_h = 56      # 72 for a focal bar
band_y(k) = zone_y + zone_h + 52 + k * 76      # bands 64 tall, 12 apart
fan_stride = 16                                # upstream's 4 is under §4's floor of 12
```

Three components across a row divide the zone exactly: width 200 at `x = 276, 508, 740`
with 32-unit gaps, the last ending on `zone_x + zone_w - 16`. One band gives a 620-unit
height with §9's legend. Fanning out, stagger the exits down the engine's right edge and
give each vertical its own corridor.

## Budget

Nine systems, twelve connections, two focal, three zones — the defaults; `dp-integration`
declares no override in `scripts/diagrams.json`. This is the type where upstream spends 14–20 nodes and argues the count *is* the claim.
That exemption did not come across, so upstream's fallbacks are the primary path here —
worth knowing before drawing rather than halfway through. Collapse identical sources into
one node with a counted sublabel (four databases become one `Databases` reading
`4 × MariaDB`), and split by integration plane when the planes argue different things.

Three sources, three platform components and three consumers is nine; the platform zone
takes one of the three, leaving two bands — but a band is a drawn box, so it costs a
**node** as well as a zone, and at nine nodes there is none left. A board that wants a
cross-cutting band budgets 3 + 2 + 3 + 1, not 3 + 3 + 3 + 1. Every collapse and split goes in
`budget_cuts[]` — a collapsed node and an omitted one look identical to the next run.

## Motion

The wires are the subject. A dash offset marching the federated and read-back edges says
the query goes out and the answer comes back without asserting a rate, and both
directions read correctly at every frame because neither endpoint moves. The alternative,
not both on one board, is an ordered emphasis walking the serve-flow edges one at a time.
8–14s, seam-exact, nothing that moves geometry (§11) — the zone border especially, since
its extent is the trust claim.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| Sources or consumers collapsed to one box when the surfaces differ | Deletes the subject; `architecture` is where collapsing belongs |
| One unlabelled bus arrow into the platform | The protocols get read first |
| Identity or any band drawn inside the zone | It gates the layer from outside; inside misstates the trust |
| A band wired to one specific tool | True only if it protects that one tool |
| Scheduler triggers drawn solid and labelled | A trigger is not a data flow; its label competes with the protocols |

## Specimen

`docs/samples/types/dp-integration.svg`.
