# ER / data model

Entities, the fields inside them, and the cardinality of the relationships between them.
Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery). See `THIRD_PARTY.md`.

**Best for:** database schemas, API resource relationships, domain models — anywhere the
reader needs the field list and not only the box name.

## Layout conventions

An entity is a two-section box, and it is the one node in this skill whose height is
driven by content rather than declared:

| Part | Geometry at `viewBox` width 1200 |
| --- | --- |
| Box width | `240` — wide enough for `# customer_id  uuid` in mono at the `metadata` floor |
| Header band | `48` tall, filled `surface`, hairline in `rule` along its lower edge |
| Type tag | the grammar's own tag rect (§6): `40×20`, `rx 4`, text at `metadata` |
| Entity name | `label`, sans, centred on the band |
| Field row pitch | `28`, mono at `metadata`, left inset `20` |
| Body padding | `12` below the last field |

Height is therefore `60 + 28 × n_fields`, which lands on the 4-unit grid for every field
count. Radius `8` on the outer box.

Fields carry their key role as a mono prefix: `#` for a primary key, `→` for a foreign
key, nothing for a plain column. The prefix is what lets a reader find the join without a
legend entry per key.

Relationships are ordinary connectors under `reference/diagram-grammar.md` §4 — rounded
right-angle elbows, side ports for horizontal runs, top and bottom ports for vertical
ones. Lay the entities out so most relationships are straight single-segment lines; a
model that needs six elbows is usually clustered wrong rather than routed wrong.

The accent role goes on the aggregate root, or on the one entity every other entity
eventually reaches. If the model has no such entity, it has no focal, and that is a
legitimate answer.

## Budget

From `scripts/diagrams.json`: **8 entities** (`max_nodes`), **12 relationships**
(`max_edges`), **2 focal**, **3 zones**. The unit the budget counts is the entity, not
the field — a nine-field entity is one node.

Past eight entities, split into an overview naming the clusters and a detail per cluster.
Shrinking the box to fit a ninth entity puts the field text under the `metadata` floor,
which the checker catches, and makes the schema unreadable, which it does not.

## Primitives

**Cardinality glyphs.** `1`, `N`, `0..1`, `1..*` in mono at the `metadata` floor, one at
each end of the relationship, sitting `12`–`16` units out from the entity edge and `8`
units off the stroke. These are short enough to read against open canvas, so they take no
mask and no `data-label` — the checker's plate geometry applies to the relationship verb,
not to these.

**Relationship verb.** Optional, one per line, centred on the longest straight segment:
a `data-label` mask in `paper` with the 6–10 unit gap the grammar requires. Use it when
the direction is not obvious from the cardinality — "belongs to", "fulfils" — and skip it
when it is.

## Motion

Nothing structural moves: field rows, cardinality glyphs and box heights are the content,
and the grammar's geometry rule (§11) forbids animating them. What can carry an 8–14s
seamless loop is an ordered emphasis walking the relationships in read order — stroke
opacity from muted to full and back, one relationship at a time — which shows the reader
the traversal order of the model without changing what the model says at any instant. A
slow accent breath on the aggregate root is the other honest option. Pick one.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| An arrow for every foreign key on a model with dozens | Draw the clusters instead; the tangle is not information |
| Cardinality notation that differs between the two ends of one relationship | The reader cannot tell whether the mismatch is a mistake or a fact |
| Fields padded so every box is the same height | Natural height by content is the point of a two-section box |
| Every column listed | Show the keys and the fields the relationships turn on; the schema file holds the rest |
| The accent role on each of the "important" entities | Two at most, and usually one |

## Specimen

`docs/samples/types/er.svg`.
