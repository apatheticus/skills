# Report guide — structure, design, motion, self-containment

The report is the user's permanent record and playbook. It must be
highly polished, easy to skim, and reward drilling down. One HTML file,
opens from `file://`, offline, indefinitely.

A run no longer writes HTML. It writes JSON, and `scripts/render_report.py`
pours that JSON into `assets/template.html`. Everything below the first section
is the spec the template implements, so read it to know what the data has to
carry and what the reader will see, not as instructions for hand-authoring.

## Contents

- **The bundled template** — what is inside, the vendored versions, contrast,
  editing it, and re-vendoring when the user updates Neumorphic Fresh.
  - The five brand rules — one tonal base, fresh accent, rounding, motion, copy.
  - Token groups — for edits to the report layer.
- **Structure (top to bottom)** — the section order; the checker reads its
  headings from this list.
  - "Since last report" — layout spec.
- **The status ledger** — `reflect-status.json`: schema, reading it in Phase 0,
  rendering and saving it in the report.
- **Per-finding handoff** — `#card-<id>` permalink, Copy link, Copy agent brief
  (with the brief's Markdown shape).
- **The Usage panorama — dashboard spec** — KPI strip and charts as one dense dashboard.
- **Custom SVG graphics** — data charts and decoration; no chart libraries, no raster.
- **Interactivity & motion** — nav, filters, search, expand/collapse, animation.
- **Embedded data block** — the full `cc-reflection-data` schema, the ledger
  block, and the meta block; future runs depend on them.

## The bundled template

`assets/template.html` is the whole report: CSS, fonts, icons, GSAP, the page
skeleton and the renderer, all inline, with synthetic sample data in its JSON
blocks. Open it in a browser and it shows a complete sample report.

**Never Read `template.html` or a rendered report into context.** Each is about
340KB, almost all of it base64 fonts and minified GSAP. Its first 40 lines are a
header comment that says what is inside; `head -40` is the whole of what a run
needs from it.

**What is inside, in order.** Every block carries an id, and the checker fails
if any id appears more than once.

| Block | Contents |
| --- | --- |
| `style#nf-tokens` | Neumorphic Fresh `colors_and_type.css`, verbatim, minus the two Google Fonts `<link>` lines in its header comment |
| `style#nf-patch` | The dark values the design system's `prefers-color-scheme` fallback leaves out: `--el-float`, `--glow-*`, `--accent-press`, every `*-wash` |
| `style#nf-components` | Neumorphic Fresh `components.css`, verbatim |
| `style#nf-fonts` | Sora and Plus Jakarta Sans (weights 400–800) and JetBrains Mono (400–600), latin variable subsets as base64 woff2, OFL 1.1 notice inline |
| `style#report` | The report layout layer: tokens only, no literal colours, contrast patches included |
| svg sprite | Lucide icons (ISC licence noted): sun, moon, chevron, link, check |
| skeleton | Sticky nav, hero, and the seven section `<h2>`s from § Structure, with empty mount points |
| `script#cc-reflection-data` / `-status` / `-meta` | The three JSON blocks; `render_report.py` replaces them |
| `script#vendor-gsap` | GSAP 3.15.0 core, minified, licence banner kept |
| `script#renderer` | Vanilla JS that reads the JSON and builds every section, chart and control |

**Vendored versions.** Neumorphic Fresh as of the user's copy dated
2026-07-07. GSAP 3.15.0 core only: ScrollTrigger is deliberately absent, because
reveals are driven by `IntersectionObserver` (§ Interactivity & motion). The
layout layer and the interaction code were lifted from the 2026-10-05 edition,
rules and code only, with no content.

**Why it is bundled.** The design system used to be read at run time from the
user's own copy so it stayed current. That copy moved, the path broke, and every
run re-authored ~720KB of HTML from prose, so the shape drifted edition to
edition. Bundling freezes the design system; re-vendoring (below) is how it moves.

### The five brand rules (obey them in any edit to the report layer)

1. **One tonal base per theme.** Surfaces are the *same colour* as the page and
   are raised by paired light/dark shadows (`--el-1/2/3`, `--inset-1/2`). **Never
   give a card a different fill colour.** There is no dark card, no navy card, no
   inverted chart panel — a chart sits on the same ground as the prose around it.
2. **Fresh accent.** The mint→teal→cyan gradient (`--grad-fresh`) on primary
   actions, with a soft `--glow-accent` bloom. Lively, not grey.
3. **Generous, pillowy rounding** and airy spacing.
4. **Springy motion** — hover lifts, press sinks (`--ease-spring`).
5. **Sentence case, warm calm copy, no emoji** in chrome.

### Theming

Light and dark are both fully defined. `script#theme-boot` in `<head>` sets
`data-theme` on `<html>` before first paint, from `localStorage` (`ccr-theme`)
or, failing that, `prefers-color-scheme`; the nav toggle flips it and persists
it. Every colour is a token, so the toggle works only while nothing is
hard-coded: a literal hex in the report layer or in a chart is a defect.

### Contrast

Everything the reader must *read* clears WCAG AA (4.5:1) in both themes; chart
furniture (gridlines, hairlines, track fills, axis ticks) is exempt. The
design system's raw semantic hues fail on their own washes, so the report layer
mixes badge text toward `--fg1` (`color-mix(in srgb, <hue> 34–40%, var(--fg1))`),
and lifts `--fg3` to a `--meta` token for meta lines. `render_report.py`
re-measures every one of those pairs from the vendored tokens on each run and
fails below 4.5:1. **If you change a `color-mix` percentage in the report layer,
change the matching pair in `check_contrast()` in the same edit**, or the
checker measures a colour the page no longer uses. Never encode meaning in
colour alone: pair a series colour with a direct label, a dot, or an icon.

### Token groups (for edits to the report layer)

| Group | Tokens |
| --- | --- |
| Ground | `--bg` `--bg-2` `--surface` `--surface-2` `--surface-inset` |
| Elevation | `--el-1` `--el-2` `--el-3` `--el-float` `--inset-1` `--inset-2` |
| Text | `--fg1` (body) `--fg2` (secondary) `--meta` (meta lines, report layer) `--fg3` (chart furniture only) `--fg-on-accent` |
| Accent | `--accent` `--accent-press` `--accent-wash` `--grad-fresh` `--glow-accent` |
| Semantic | `--success` `--warning` `--danger` `--info` + each `--*-wash` |
| Chart series | `--c-1` … `--c-6`, in order, for every multi-series chart |
| Lines | `--line` `--line-strong` `--c-track` |
| Type | `--font-display` (Sora) `--font-body` (Plus Jakarta Sans) `--font-mono` (JetBrains Mono), `--fs-*`, `--weight-*` |
| Shape and motion | `--r-*`, `--dur-*`, `--ease-*` |

The `nf-*` classes the report uses come from `components.css`: `nf-badge`,
`nf-btn`, `nf-chip`, `nf-input`, `nf-segment`, `nf-code`. Anything else (exec
row, card, tile, KPI) is built from tokens in `style#report`.

### Editing the template

Edit it in place with targeted edits: `grep -n` for the block or rule, change
it, never load the file whole. Then run

```bash
python3 scripts/render_report.py --sample --out <scratchpad>/sample.html
```

and open the sample in both themes at desktop and phone width. The script's
checks are necessary, not sufficient: they cannot see a broken layout.

### Re-vendoring when the user updates Neumorphic Fresh

```bash
python3 scripts/render_report.py --vendor "<path to Neumorphic Fresh Design System>"
python3 scripts/render_report.py --sample --out <scratchpad>/sample.html
```

`--vendor` replaces only `style#nf-tokens` and `style#nf-components`, stripping
any `<link>` line, and says whether each changed. `nf-patch`, the fonts and the
report layer stay. The `--sample` run then re-measures contrast against the new
tokens. If a pair fails, fix the mix in `style#report` (and its pair in
`check_contrast()`), not the vendored file. If the update renamed or removed a
token the report layer uses, the page will show it as a missing colour, so look
before shipping. Fonts and GSAP are pinned and change only on purpose.

## Structure (top to bottom)

The order below is a **spec, not a suggestion**. The template's static headings
are these names verbatim, and `render_report.py` compares them against this
list on every run, printing `headings match: yes/no`. Item 1 is the hero, whose
heading is the free-text `<h1>`; every other bold name is an `<h2>`, in order.
Rename one here and the template must change with it.

1. **Hero** — title, date, analysis window, session/project counts, and a
   one-paragraph verdict of the period. The `<h1>` verdict line is the one piece
   of free text in the whole report. Subtle ambient motion; a KPI stat row under it.
2. **Executive summary** — the ranked recommendation list in impact order
   (SKILL.md Phase 3 step 6), most impactful first, capped at `limit` rows.
   Each row: rank, verdict badge (new-skill / automation / fix /
   keep-doing / observation), title, leverage score, effort, session count.
   Clicking a row opens and scrolls to its detail card. Filter chips by
   **verdict *and* family**, plus a text search across all clusters. Filters
   and search hide rows; they never reorder them. When the cap cut anything,
   a muted footer line reads `Showing 15 of 27 · rerun with limit=all`.
3. **Since last report** (only when a prior report existed) — see the layout
   spec below. Three columns: **Adopted / Still recurring / New**.
4. **Focus** (only when a focus argument was given) — deep dive on the focused
   project/theme: a summary, a row per named finding, and the full card of any
   finding ranked past the cap. Not capped by `limit`: the user asked for this
   theme by name.
5. **Wins & playbook** — effective patterns worth keeping, same evidence
   treatment as a detail card. Impact order, drawn from the capped list.
6. **Usage panorama** — the dashboard. See its own spec below.
7. **Findings & recommendations** — detail cards, one per shown finding, in
   impact order and capped at `limit`, **collapsed by default** to summary +
   verdict; expand to reveal the handoff bar (see
   § Per-finding handoff), rationale, the concrete example (in a copyable `<pre>`
   block — the exact prompt / skill description / settings line), and the
   evidence: verbatim quotes with session ID, project, and date. Actionable
   cards come first; observations follow under their own sub-heading.
   Corroborated-by-/insights findings get a marker.
8. **Methodology appendix** — window, counts, triage rules, sampling (if
   any), sessions skipped as unreadable, /insights coverage %, the `limit`
   in force with `showing N of M`, and limitations.

A section with nothing to show (no prior report, no focus) is hidden along with
its nav link; its heading stays in the template.

Findings sit **after** the panorama deliberately: the summary ranks them up top
for the skimmer, the panorama gives the reader the shape of the week, and the
long evidence cards are the reference material you drill into last.

### "Since last report" — layout spec

Three equal columns on one row (`repeat(3, 1fr)`, collapsing to one column under
~1000px), each a card on `var(--surface)` with `var(--el-2)`. This section is
read at a glance, so the formatting rules are tight:

- **Column header**: an `nf-badge` in the bucket's semantic colour
  (Adopted → success, Still recurring → warning, New → info) with the count
  beside it. Not a bare `<h3>`.
- **One item per row**, and a row is **exactly two lines**: the recommendation
  title (600 weight, `--fg1`, `--fs-sm`), and one meta line beneath it in
  `--font-mono` / `--fs-2xs` / `--meta`. Never wrap a paragraph of rationale
  into this section — it belongs in the detail card.
- **The meta line carries the bucket's own fact, not a generic one**: Adopted →
  the report it was first raised in; Still recurring → `streak ×N` plus the
  session count; New → the family and the session count.
  When the status ledger has something to say about a row, that wins the meta
  line: `tried 6 Sep — came back`, `you marked this done 6 Sep`, `set aside
  6 Sep`. See § The status ledger.
- **Long titles truncate, never reflow the grid.** Two-line clamp
  (`-webkit-line-clamp: 2`), `overflow-wrap: anywhere`, and `min-width: 0` on
  every flex/grid child — without that last one a single long `code` token
  blows the column out and the three-column grid stops being three columns.
- **Each column is in impact order**, with one exception: in Still recurring,
  rows the reader marked done that came back lead the column (each group in
  impact order), because a fix that failed is the strongest signal in the
  report. Adopted rows use the prior edition's leverage, since they have none
  this week.
- **A row links to its detail card** (same behaviour as an exec-summary row).
- **The `limit` cap does not apply here.** This section is a delta, not the
  ranked list. A row ranked past the cap keeps its place, with no card link and
  its meta line *leading* with `ranked #N, past limit` so the ellipsis cannot
  cut it off.
- **An empty bucket renders an empty state**, not an empty card: one muted line
  saying what emptiness means ("nothing was adopted since 24 Aug").

## The status ledger — check off what you've addressed

The report is a worklist, not a bulletin. The reader marks what they have acted
on, and the next run reads those marks back. Without this, the same finding is
re-derived from scratch every week, and a fix that was tried and failed looks
exactly like one that was never tried.

**The file.** `OUT_DIR/reflect-status.json`, keyed by recommendation id — the
same content-derived slug used for `id="card-<id>"`. That is why those ids must
stay stable across editions: never renumber them, never make them positional.

```json
{ "schema": 1, "updated": "2026-09-06", "edition": "20260906",
  "items": {
    "zsh-glob-guard-false-positives": {
      "state": "done",
      "note": "added setopt no_nomatch to .zshenv — guard still fires on URLs",
      "marked": "2026-09-06",
      "title": "zsh-glob-guard blocks correct commands…",
      "first_seen": "20260830", "last_seen": "20260906"
    }
  } }
```

`state` is one of `open`, `done`, `wontdo`. Nothing else; the script rejects
anything else.

**Reading it (Phase 0).** Load the file if present. Merge, never overwrite:
every item already in it keeps its `state`, `note`, `marked` and `first_seen`;
every recommendation in this edition that is missing from it is added as `open`
with `first_seen` set to this edition. Write the merged file back beside the
report, and pass that same file to `render_report.py --status`. Track actionable
verdicts only — a `keep-doing` habit is not something the reader addresses, so
it gets no ledger entry and no control.

**What the prior states mean for this edition:**

| Prior state | Recurs this window? | Do this |
|---|---|---|
| `done` | no | **Adopted**. Meta line: `you marked this done <date>`. |
| `done` | yes | **Still recurring**, meta line leading with `tried <date> — came back`. The card quotes the reader's own `note` verbatim above the rationale. This is the most valuable row in the report: say plainly that the attempted fix did not hold, and make the new recommendation *different* from the one that failed. |
| `wontdo` | either | Drop it from the ranked list. It shows once in **Still recurring** as a muted line — `set aside <date>` plus the note — so it stays visible without nagging. Never re-rank it, never re-argue it. |
| `open` | yes | Ordinary recurring item, streak +1. |
| `open` | no | Ordinary adopted/resolved item. |

None of this adds a fourth column. The three buckets stay. The renderer derives
every one of those meta lines from the ledger block and each finding's `trend`;
the data does not spell them out.

**Rendering it** (the template does all of this). Every tracked card carries a
`.stbar` as the first child of its `.fbody`: a three-button segmented control
(`Open` / `Done` / `Won't do`) plus a one-line note input, `maxlength="180"`.
Live state lives in `localStorage` under `ccr-status`. The exec-summary row and
the card summary each carry a read-only `.stpill` showing `Done` or `Won't do`,
`hidden` while open. The top bar carries a live count and a `Save status`
button; the exec controls carry a `Hide checked off` toggle.

Four things that are easy to get wrong, all found the hard way, all handled in
the template — keep them that way in any edit:

- **The controls go in `.fbody`, never in `<summary>`.** A button inside a
  `<summary>` toggles the `<details>` on every click.
- **Do not add a grid cell to `.exec-row` for the pill.** It sits inline inside
  the row's existing `<small>`. The row is a fixed-column grid; a seventh child
  silently breaks the alignment of every row at once.
- **`Hide checked off` is a toggle, not a filter chip.** It is excluded from the
  verdict/family chip query (`#filters .nf-chip:not(.st-toggle)`) and hides via
  its own class (`.st-hidden`), so it composes with search and filters.
- **Repaint must not clobber a focused note input.** The value write is guarded
  with `document.activeElement !== input`, or every keystroke resets the caret.

**Saving it back.** `Save status` writes the merged ledger out. It tries
`showSaveFilePicker()` first so the reader can drop the file straight into
`Outputs/Reflections/`, and falls back to an `<a download>` Blob when it is
absent or throws — the picker is unavailable from a `file://` origin in some
browsers, and a silent failure there loses the reader's work. `AbortError` (the
reader cancelled) is swallowed; anything else falls back.

## Per-finding handoff — a link and a brief

Every finding has to be addressable and portable on its own. The reader's next
move after reading a card is usually to hand that one finding to an agent to
evaluate and, if it holds up, implement. Each card carries a **handoff bar**: a
durable link to the finding, and a one-click brief that is self-contained enough
to paste into a fresh session.

**The anchor is the contract.** Every card has `id="card-<id>"`, using the same
content-derived slug as the status ledger. That id is the permalink: it must
stay stable across editions, never be renumbered, never be positional. A link
handed to an agent in October has to still resolve in a report generated in
December.

**Deep links open what they point at.** Cards are `<details>` collapsed by
default, so on load, on the `load` event (after fonts shift the layout), and on
`hashchange`, the renderer reads `location.hash`; if it names a card it clears
any filter hiding it, forces it open, jumps it into view (an instant jump: a
smooth scroll started during load is cut short) and flashes it. Clicking an
exec-summary row or a "Since last report" row updates the hash via
`history.replaceState`, so the address bar always holds a link to whatever the
reader is looking at.

**The handoff bar** sits in `.fbody`, directly under the `.stbar` (or first, on a
card with no ledger entry). It holds the anchor as a real `<a href="#card-<id>">`,
**Copy link** (`location.href.split('#')[0] + '#card-<id>'`, correct from
`file://` or HTTP), and **Copy agent brief**.

**The brief** is built at click time from the embedded data block, the single
copy of every finding's text. Shape:

````markdown
# <title>

Source: <absolute url>#card-<id>
Finding: <id> · <report filename> · window <from> → <to>
Verdict: <verdict> · effort <effort> · leverage <n>/10 · <n> sessions · streak ×<n>
Family: <family> · Projects: <a, b, c>

## Already tried            (only when the reader marked it done and it came back)
Marked done <date>, and it came back. Reader's note: "<note>"

## What it costs
<rationale>

## Proposed change
```<example_lang>
<example, verbatim>
```

## Evidence
1. session <id> (<project>, severity <sev>, <date>)
   <summary>
   > <verbatim quote>
...

## Task
This is a diagnosis mined from Claude Code transcripts, not a verified plan.
Confirm the problem still exists before changing anything, then either apply the
change above or propose a better one and say why.
````

That closing **Task** paragraph is not optional. A brief without it reads as an
instruction to go and edit, and the findings are exactly the kind of claim that
has been wrong before — the report's own recurring `verify-against-source-before-publishing`
cluster is the reason it is there.

**Every finding gets the bar**, including `keep-doing` wins and observations. A
win is the most useful thing to hand an agent that is about to do similar work.

Both buttons fall back to a hidden `<textarea>` plus `document.execCommand('copy')`
when `navigator.clipboard` is absent or throws, and confirm in the button label
(`Copied`, or `Copy failed`) for about 1.4s. A silent failure looks identical to
a successful copy.

## The Usage panorama — dashboard spec

This section is a **reporting dashboard**, not a stack of charts. It is judged
against real analytics products: dense, aligned, scannable, no wasted space, no
chart bigger than the question it answers. The template draws it from
`panorama` in the data block; a missing key drops its tile, it never breaks the
grid.

**Layout.** One 12-column CSS grid, `gap: 18px`. Every tile declares its span. A
tile is a card on `var(--surface)` with `var(--el-2)`, `--r-lg`, 20–24px padding.

| Band | Content | Data | Spans |
| --- | --- | --- | --- |
| KPI strip | Up to 6 stat tiles: overline label, big display number, sub-line, sparkline. | `panorama.kpis[]` | `2` each |
| Trend | The wide time-series: one stacked area per series, direct-labelled. | `panorama.trend` | `8` |
| Composition | The donut it pairs with, legend inline to the right. | `panorama.mix` | `4` |
| Detail row | Two or three ranked-bar tiles: top tools, failures by kind. | `panorama.detail[]` | `6`/`6`, or `4`/`4`/`4` |
| Token row | Stacked column per day (cache read / cache write / output / input), and tokens by project. | `panorama.tokens_daily`, `panorama.tokens_by_project` | `7` / `5` |
| Distribution | Activity heatmap, rows × 24 hours. | `panorama.heatmap` | `12` |
| Placement | **"Where each recommendation sits"** — leverage × effort for the shown findings only, each point linking to its card. | the recommendations | `12` |

When a pair is missing one half, the other widens to `12`.

**Sizing.** Each SVG is authored at its true rendered width — a `6`-span tile is
`viewBox="0 0 503 h"`, a `12`-span tile `1068` — never drawn small and scaled
up. At phone width a chart 600 units or wider keeps a 600px minimum and scrolls
sideways inside its tile, rather than shrinking to a thumbnail.

**Axes.** The axis maximum rounds to a clean step — `1/2/2.5/5 × 10ⁿ` over five
ticks — so the reader sees `0 / 200 / 400 / 600 / 800 / 1k`, never
`0 / 138 / 276 / 414`. Values above four digits abbreviate (`1.2k`, `4.8M`).

**Equal-height rows.** Tiles in a grid row stretch to the same height; each is a
flex column whose sub-copy takes `margin-bottom: auto`, so charts bottom-align.

**A data table is not a chart.** The methodology table sits in its own
`overflow-x: auto` wrapper with a `min-width`, so it never pushes a horizontal
scrollbar onto the page at phone width.

**Density rules.** Direct-label a series wherever it fits and drop the legend.
One number per tile gets the display face; everything else is `--font-mono` at
`--fs-xs`. If a chart needs a paragraph to explain it, it is the wrong chart.

**Token usage is required when the data is available.** Claude Code transcripts
carry `message.usage` on every assistant record — `input_tokens`,
`cache_creation_input_tokens`, `cache_read_input_tokens`, `output_tokens`.
Dedupe by `message.id` before summing: streaming writes the same usage block on
every partial, and naive counting inflates the total several-fold. Report the
four components separately — the cache-read share is the interesting number. If
a corpus predates the field, say so in the methodology limitations rather than
omitting the tile silently.

## Custom SVG graphics

Every chart is hand-built inline SVG drawn by the renderer — no chart library,
no raster — with `role="img"`, an `aria-label`, and `<title>` tooltips. All
fills and strokes reference tokens, so every chart survives the theme toggle;
series colours come from `--c-1` … `--c-6`, in order; gradient ids are derived
from the chart's own name, never random.

What the template draws, and the rules each keeps:

- **Area:** the area closes back along its baseline under a gradient; the top
  edge is a separate drawn line; labels sit in a gutter right of the plot with a
  greedy vertical de-collision pass.
- **Donut:** SVG arcs with the total in the hub; legend rows are
  `swatch · label · mono value`.
- **Ranked bars:** a track plus a bar per row, value at the end.
- **Stacked columns:** segments stacked per day; per-day totals labelled only
  when there are 10 days or fewer.
- **Heatmap:** opacity scaled by the square root of the cell's share of the peak;
  empty cells on `--c-track`.
- **Quadrant:** a beeswarm (points sharing a cell spread across the column), a
  label lane to the right with leader lines and de-collision, labels clipped to
  what the lane holds, and the leverage axis cropped to one below the lowest
  score present.

Decoration — the hero's blurred mint/cyan/lime blobs — is `aria-hidden`, one
glow per region, and never displaces evidence.

## Interactivity & motion

- Sticky top nav with scrollspy and smooth-scroll anchors, the search box, the
  theme toggle, the live ledger count and `Save status`. At phone width the
  links scroll sideways in one row instead of wrapping.
- Expand/collapse detail cards (`<details>`), collapsed by default.
- Filter the summary by verdict **and** family; text search across clusters.
- Copy buttons on every `<pre>` example block.
- GSAP is the tweening engine; `IntersectionObserver` triggers each reveal
  (ScrollTrigger was tried and left 55 elements at opacity 0 after a full
  scroll). Fade-up entrances, count-up numbers (≤1.4s), bars growing from the
  baseline, lines drawing, donut arcs popping in, hero blobs drifting.
- **Fast chrome, slow data**: controls respond in ≤180ms; a chart may take up to
  1.3s to draw. Motion never delays reading.
- Under `prefers-reduced-motion: reduce`, nothing animates: counters and charts
  render their **final state immediately**.
- **The ticker gate.** Every reveal is a from-state, applied the instant it is
  created. If `requestAnimationFrame` never fires — a background tab, a
  low-power browser, an embedded preview — the tweens never advance and the
  report would render at `opacity: 0`, which is what the 27 July and 24 August
  editions did. So the renderer draws everything at its *final* state first, and
  only starts motion once a frame has ticked:

  ```js
  var ticked = false;
  requestAnimationFrame(function () { ticked = true; });
  setTimeout(function () { if (ticked) startMotion(); else settleAll(); }, 260);
  ```

  A safety sweep plays anything still hidden 2.5s after start, whenever
  scrolling settles, and when a hidden tab becomes visible again (a hidden tab
  runs neither the observer nor scroll events).

## Embedded data block (machine-readable — future runs depend on this)

The report carries three JSON blocks, each exactly once. `render_report.py`
writes all three; a run supplies the first two as files.

**`cc-reflection-data`** — everything the report shows. Trend (Phase 3 step 5)
reads only `recommendations[]` from the prior edition, so every addition here is
backward-compatible: older editions still parse.

```json
{
  "generated": "YYYY-MM-DD",
  "window": {"kind": "30d", "from": "YYYY-MM-DD", "to": "YYYY-MM-DD"},
  "focus": null,
  "design_system": "Neumorphic Fresh",
  "sessions_analyzed": 0,
  "projects": ["..."],
  "insights_coverage": 0.0,
  "tokens": {"input": 0, "cache_create": 0, "cache_read": 0, "output": 0},
  "limit": 15,
  "prior": {"edition": "YYYYMMDD", "date": "YYYY-MM-DD"},
  "notes": {"summary": "optional override of a section's sub-line"},
  "hero": {
    "verdict": "the <h1>: the period in one line",
    "summary": "one paragraph",
    "kpis": [{"label": "Sessions", "value": 27, "sub": "62 incl. sub-agent runs",
              "suffix": "", "dec": 0}]
  },
  "recommendations": [
    {
      "id": "kebab-case-stable-id",
      "rank": 1,
      "verdict": "new-skill|automation|fix|keep-doing|observation|nothing",
      "title": "...",
      "family": "friction|repetition|wins|environment",
      "leverage": 1,
      "effort": "minutes|hour|day",
      "session_ids": ["..."],
      "streak": 1,
      "trend": "new|recurring",
      "projects": ["..."],
      "rationale": "what it costs",
      "example": "the exact prompt / skill description / settings line",
      "example_lang": "json",
      "evidence": [{"quote": "verbatim", "summary": "optional one-liner",
                    "session_id": "...", "project": "...", "date": "YYYY-MM-DD",
                    "severity": "low|medium|high"}],
      "corroborated": true,
      "corroboration": "what /insights says, one sentence"
    }
  ],
  "adopted": [{"id": "...", "title": "...", "leverage": 8, "raised": "YYYY-MM-DD"}],
  "panorama": {
    "days": ["YYYY-MM-DD", "..."],
    "kpis": [{"label": "...", "value": 0, "sub": "...", "spark": [0, 1, 2]}],
    "trend": {"title": "...", "sub": "...", "series": [{"name": "project", "values": [0]}]},
    "mix": {"title": "...", "sub": "...", "unit": "turns", "items": [{"name": "...", "value": 0}]},
    "detail": [{"title": "...", "sub": "...", "items": [{"name": "...", "value": 0}]}],
    "tokens_daily": {"title": "...", "sub": "...", "series": [{"name": "cache read", "values": [0]}]},
    "tokens_by_project": {"title": "...", "sub": "...", "items": [{"name": "...", "value": 0}]},
    "heatmap": {"title": "...", "sub": "...", "unit": "events",
                "rows": [{"label": "Mon", "values": [0, "…24 hourly values"]}]},
    "quadrant": {"title": "...", "sub": "..."}
  },
  "methodology": {
    "corpus": [["Transcripts", "62 files, 178 MB"]],
    "triage": ["..."],
    "sampled": "none, every session was read",
    "unreadable": ["session ids skipped"],
    "pipeline": ["..."],
    "limitations": ["..."],
    "projects": [{"name": "...", "sessions": 0, "tokens": 0}]
  }
}
```

Field rules, all enforced by the script unless marked optional:

- `recommendations` holds the **full** ranked list, never just the rows the cap
  let through, or the next run reads every finding past the cap as adopted.
  `rank` is 1..N and must follow the Phase 3 sort exactly (leverage desc,
  effort asc, session count desc, id asc); the script recomputes it and fails
  on any difference. `limit` is the number in force, or `null` for `limit=all`.
- Keep `id` stable across runs for the same underlying issue (derive it from the
  cluster theme) so trend diffs, ledger entries and deep links all hold.
- `streak` counts consecutive reports in which the item appeared unresolved.
- Every finding needs `rationale`, `example` and at least one `evidence` entry
  with `quote`, `session_id`, `project` and `date`.
- `prior` is `null` when there was no prior edition; then `trend` and `adopted`
  are not required, and Since last report is hidden. When `prior` is set, every
  finding needs `trend`.
- `focus` is `null`, or `{term, summary, ids[]}` where every id is a finding.
- `panorama` is optional, key by key. Every `series.values` has one entry per
  `days` entry; every heatmap row has 24.
- `methodology` needs `triage`, `sampled`, `unreadable` and `limitations`. The
  renderer adds the window, counts, /insights coverage and the `limit` line
  (`showing N of M`) itself.
- Optional: `hero.kpis`, `projects` and `example_lang` on findings (projects
  default to the evidence's), `corroborated`/`corroboration`, `notes`.

**`cc-reflection-status`** — the merged ledger, exactly as in § The status
ledger.

**`cc-reflection-meta`** — written by the script, never by hand:
`{"file": "<report filename>", "from": "...", "to": "...", "generated": "..."}`.
The agent brief reads it for its `Finding:` line.

Inside each block `<` is written as `<`. JSON parsers read it back as `<`,
and it keeps `</script>` and `<!--` out of the block whatever a quote contains.
To read a prior edition's data, parse the block's text as JSON — no unescaping
needed.
