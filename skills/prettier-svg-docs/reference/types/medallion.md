# Medallion

Storage tiers of one dataset side by side, with the promotion between them drawn over the
top. Ported from [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design)
(MIT © 2025 Cathryn Lavery). See `THIRD_PARTY.md`.

**Best for:** a lakehouse or bucket layout where each tier is a distinct quality and access
level of the same data — raw landing, anonymised, staging, aggregated, archive — and the
reader needs what each tier holds, who writes it, and how data is promoted onward. Prefer
`process` when role lanes carry the story, and `high-level` for the cluster itself.

## Layout conventions

Tiers are tall cards in a single row. On the 1200-unit board with 40-unit margins:

```
tier_gap  = 24     tier_h = 476     band_h = 100     tier_y = band_h
tier_w    = floor4((1120 - (n_tiers - 1) * 24) / n_tiers)
            # 3 tiers -> 356   4 -> 260   5 -> 204   6 -> 164
tier_x(i) = 40 + i * (tier_w + 24)          tier_cx(i) = tier_x(i) + tier_w / 2
viewBox_h = band_h + tier_h + (20 + 72 if path cards else 0) + 20
            # 5 tiers with two path cards -> 1200 x 688; without -> 1200 x 596
```

The band holds the promotion connectors and their labels, nothing else. Inside a card,
offsets are from `tier_y`:

| Element | Offset | Role |
| --- | --- | --- |
| Header band | `0`–`48`, plus a 12-unit tint extension below it | — |
| Tier name | `+32` | `label`, sans |
| Bucket name | `+80` | `metadata`, mono |
| Field label / value | `+124` / `+148`, `+176` / `+200`, `+224` / `+248` | `metadata` |
| Example heading | `+344` | `metadata`, under a hairline that makes it read as a heading |
| Example lines | `+372`, `+400` | `metadata` |

Field text is left-inset `20`, so the usable width is `tier_w − 40`; a value that does not
fit is split by hand into two `<tspan>` lines. Upstream wraps these in a `<foreignObject>`,
which is dropped here: GitHub renders a committed SVG inside an `<img>`, where foreign
content does not render and the value would simply be missing.

Card treatment uses the grammar's node-treatment table (§2) and adds no roles: the first
tier takes the input/actor treatment, ordinary tiers the service treatment, an archive tier
the optional/async treatment with its `4,3` dash, the focal tier accent fill and stroke.
The focal signal reaches the bucket name and example lines only; tool, format and writer
stay `muted`, or the card drowns.

## Primitives

**Promotion connectors.** One per adjacent pair, over the top of the cards, top-centre to
top-centre. Upstream draws these as cubic Béziers; here they are orthogonal, because
rounded right-angle elbows are mandatory under `reference/diagram-grammar.md` §4 and a
curve between two nodes fails that check:

```svg
<path data-edge="true" d="M CXi,100 V 54 Q CXi,44 CXi+10,44 H CXj-10 Q CXj,44 CXj,54 V 100"
      fill="none" stroke="var(--muted)" stroke-width="1.5" marker-end="url(#arrow)"/>
```

The label sits centred on the band run at `y = 32` in `metadata`, with a `data-label` mask
in `paper` — an 8-unit gap above the stroke, inside the 6–10 the grammar requires.
The connector *into* the focal tier takes the accent role and a matching marker; a lifecycle
promotion keeps the `4,3` dash. No promotion runs right to left — this type reads one
direction, and a write-back is a different diagram.

**Path cards.** Up to two, below the tier row at `y = 596`, `72` tall, `548` wide at
`x = 40` and `x = 612`. They describe *how* data is written between tiers — a SQL path, a
notebook path — not what any tier holds.

## Budget

From `scripts/diagrams.json`, the defaults apply: **9 nodes**, **12 edges**, **2 focal**,
**3 zones**. The unit is the tier, and path cards are nodes too, so five tiers plus two
path cards is seven of the nine. Promotions are `n_tiers − 1`, well inside twelve.

Three to six tiers is the working range; past six the cards are narrower than their own
field text. Split into an overview of the ladder and a detail per tier, recording the cut
in `budget_cuts[]`.

## Motion

The cards and their text are the content and hold still. What can loop at 8–14s is a token
travelling a promotion connector's fixed path, run in tier order so the reader sees the
sequence, or a dash offset on the lifecycle connector saying the archive step is continuous
rather than triggered. One or the other: two moving ideas across five cards reads as
traffic.

## Anti-patterns

| Anti-pattern | Why it fails |
| --- | --- |
| More than one focal tier | Focal marks the analytical surface the rest exists to feed |
| Archive treatment on a tier that is not an archive | The dash is a retention signal, and reuse spends it |
| Accent on a connector that does not land in the focal tier | Accent is the focal decision restated, not a second one |
| Path cards describing what a tier holds | That belongs in the tier's own fields |
| A tier with no concrete example payload | Without one the card is abstract and unearned |
| A promotion label over 14 characters | It stops fitting the band; shorten the verb |

## Specimen

`docs/samples/types/medallion.svg`.
