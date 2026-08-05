# Website security scan — visual design system

One frozen system; all project visuals derive from it. Facts come from the repo
(SKILL.md, scripts, references), never invented. Frozen for this run.

## Provenance

Derived from: `assets/report-template.html`
Derived on:   the run that first wrote this file
Mapping:      product tokens mapped with gap-fills, marked below

The report template carries the full SaaS Pro token block the skill's own HTML
output is styled with. Doc visuals reuse those tokens so the README and the
artifact the skill produces read as one thing.

Record the same source path and its hash as `design_source_path` /
`design_source_hash` in each visual's manifest.

## Story extraction

Audience:     Someone who owns a public website and the DNS zone its corporate mail authenticates from.
Value:        Runs a fixed catalog of external, read-only checks against a target's domains and renders the result as an HTML report that tracks what moved since the last run.
Proof:        `scripts/test_delta.py` — a runnable self-check proving a check that did not run cannot be reported as resolved.
First action: Copy `assets/targets/example.md` to a new slug, then `python3 scripts/scan.py --profile assets/targets/<slug>.md`.
Theme:        The check ledger — one row per check, each carrying its own execution state, so an unrun check and a clean result never look the same.

## Frozen system

### Palette

| Role | Hex | Notes |
| --- | --- | --- |
| background       | `#F4F6FE` | page canvas |
| surface          | `#FFFFFF` | cards / panels |
| ink              | `#12142B` | primary text |
| muted            | `#4C5273` | secondary type — kickers, folios, endpoint labels |
| rule             | `#6A7091` | structural lines; darker than the product's hairline so a load-bearing border clears the 3:1 graphic floor |
| accent-primary   | `#4A4AE8` | the one accent on a board |
| attention        | `#EF4458` | graphic only — 3.45:1 on background, below the text floor, so never used on `<text>` |

Mapped from the report template's token block:

| Product token | Value | Doc role |
| --- | --- | --- |
| `--surface-page` | `#F4F6FE` | background |
| `--surface-card` | `#FFFFFF` | surface |
| `--ink-900` | `#12142B` | ink |
| `--ink-600` | `#4C5273` | muted |
| `--ink-500` | `#6A7091` | rule *(gap-fill: the template's `--border-default` is a translucent rgba and too faint for a diagram line)* |
| `--brand-600` | `#4A4AE8` | accent-primary *(gap-fill: `--brand-500` measures 4.50:1 on the background, exactly at the floor)* |
| `--danger` | `#EF4458` | attention |

### Typography

| Role | Stack |
| --- | --- |
| display | `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` |
| body    | `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` |
| mono    | `ui-monospace, SFMono-Regular, Menlo, monospace` |

**Never load a remote font.** The report template names Plus Jakarta Sans and
JetBrains Mono, both remote faces. An SVG cannot fetch either on GitHub, so doc
visuals use system stacks and accept the divergence from the HTML report.

### Shape language

Rectangles and straight lines. Corner radius `0`. Stroke `1` for grid and rules,
`2.5` for the single emphasized path. Spacing unit `8`; a 12-column grid on the
1200 canvas puts a column every `100` with content starting at `x=64`.

### Motif

**The check tick** — short vertical marks standing on a horizontal baseline, one
per check. A filled tick is a check that completed; a hollow tick is one that did
not. It is the product's whole argument in one mark, so it appears once per board
and never as wallpaper.

### Composition rules

Compact-technical. One strong composition per visual, left-aligned against the
column grid with a right-aligned folio, content kept `64` from the edges.

### Motion rules

- Seamless ambient loops, 12s each; state at t=D equals state at t=0.
- `data-loop-s="12"` on the root; every duration divides it (2s, 3s, 4s, 6s).
- Ease character: `linear`, or `cubic-bezier(.4,0,.6,1)` where a dash needs to
  settle. Nothing dramatic.
- No strobing, no idle bobbing. Motion shows the direction a probe travels or a
  state changing, or it is removed.
- Every animated visual carries a `@media (prefers-reduced-motion: reduce)` block
  that stops all motion and leaves a legible still.

### Style

| Field | Value |
| --- | --- |
| Slug | `swiss-minimal` |
| Source | derived |
| Primary axis | composition |

- **Intent** — The International Typographic Style: strict grid, hairline rules,
  asymmetric balance, type carrying the message. The safest default, and it passes
  every gate without relaxation.
- **Palette treatment** — Ink on background, plus the muted grey carrying secondary
  type. One accent per board, used once: a single rule, a single filled counter, a
  single moving dash. Never a gradient. Greys are structural, never decorative.
- **Shape language** — Rectangles and straight lines only, radius `0–2`. Stroke
  weights from a two-step scale: `1` for grid and rules, `2.5` for the one
  emphasized path. Circles only as data points or numbered markers.
- **Material / depth** — None. Flat. Depth is position and whitespace.
- **Type treatment** — System sans, two weights (`400`, `700` for one title). Tight
  tracking on display sizes, normal on body. Sentence case. Mono only for literal
  identifiers — check IDs, paths, commands. Left-aligned, ragged right.
- **Motion character** — Minimal and linear. One flow dash along one path; at most
  one state change. Remove any motion that costs no information.
- **SVG recipes** — The kicker (one uppercase muted line at `+2.4` tracking above a
  title), the folio (a right-aligned muted line on the title's baseline), and the
  bottom rule with an endpoint label at each end.
- **Relaxations** — none. `swiss-minimal` relaxes no gate.
- **Never** — Gradients, shadows, glows, rounded cards, centered body text, more
  than one accent per board, a `0.5` hairline, positive tracking outside the
  kicker, decorative dot grids, icons where a word is clearer.

## Visual inventory

| Asset | Doc | Depicts | Tier | Source facts |
| --- | --- | --- | --- | --- |
| `run-pipeline` | README | Target profile → catalog checks + exploratory pass → evidence JSON → narrative → HTML report with a delta against the previous run | animated-hero | `SKILL.md` Workflow, `scripts/scan.py`, `scripts/render_report.py` |
| `boundary` | README | What the scan sends and what it never sends, plus the named coverage gaps | animated | `SKILL.md` "The boundary", `references/check-catalog.md` "Deliberate coverage gaps" |
| `two-assets` | README | One domain name fronts a website and a mail-authenticating DNS zone; email findings outrank website findings | static | `SKILL.md` intro, `references/check-catalog.md` `email.*` |
