---
name: reflect
description: Generate a comprehensive, evidence-backed reflection report on how the user uses Claude Code — what works, what needs improvement, and the highest-leverage changes to their setup — by mining past session transcripts in ~/.claude/projects/ with sub-agents, clustering signals across sessions, and consolidating with /insights data. Produces a polished, self-contained, interactive HTML report. Trigger when the user asks to reflect on their Claude Code usage, audit their sessions, find setup improvements, or runs /reflect.
argument-hint: "[window: 30d|90d|all] [limit=N, default 15] [focus: free text, e.g. a project or theme]"
user-invocable: true
license: MIT
version: 1.5.0
disable-model-invocation: true
---

# reflect

Produce a ranked, evidence-backed diagnosis of the user's Claude Code usage:
what works, what recurs as friction, and which setup changes (skills,
automations, fixes, habits) have the highest leverage. The deliverable is a
single self-contained interactive HTML report. **This is diagnosis only** —
build or edit nothing except the report (and its output directory). Do not
create skills, hooks, or config changes the report recommends; recommending
them IS the deliverable.

## Contents

Sections, in run order:

- **Run checklist** — copy it into your response and tick each gate.
- **Step 0 — read the format sources** — hard gate before anything is
  generated; your response opens with the `[format sources read]` line.
- **Arguments** — window (`30d` default, `Nd`, `all`), `limit=N` (15 default,
  `all` for no cap), and an optional focus.
- **Pipeline**
  - **Phase 0 — Scope the corpus** — `OUT_DIR`/`REPORT`, in-window
    transcripts, the prior report's JSON, the status ledger.
  - **Phase 1 — /insights freshness gate** — gate on recency, never coverage.
  - **Phase 2 — Triage** — score every session from metadata; no agents.
  - **Phase 3 — Extraction** — Workflow fan-out: extract, cluster, decide,
    consolidate, trend, then rank by impact and cap at `limit`.
  - **Phase 4 — Report** — one self-contained HTML file in Neumorphic Fresh.
  - **Step 0b — verify before publishing** — print `headings match: yes/no`.
  - **Phase 5 — Deliver** — send the report, TL;DR, skipped items, how the
    loop closes.
- **Guardrails** — the write boundary, the ledger, evidence rules, privacy,
  scale.

### Reference files — bundled, one level deep, read each in full

- `reference/report-guide.md` — the report's style and format spec. Read in
  Step 0 and again in Phase 4; Phase 0 uses its § The status ledger.
  Sections: Design system — Neumorphic Fresh · Self-containment rules ·
  Structure (top to bottom) · The status ledger · Per-finding handoff · The
  Usage panorama — dashboard spec · Custom SVG graphics · Interactivity &
  motion · Embedded data block.
- `reference/extraction-guide.md` — read in Phase 3, before authoring the
  workflow script. Sections: Transcript anatomy · Signal families · Extractor
  output schema · Batching · Clustering & decision stage.

### External inputs — not bundled

- `~/.claude/projects/**/*.jsonl` — the transcripts (Phases 0 and 3).
- `OUT_DIR/cc-reflection-20260727.html` — the last known-good exemplar (Step 0).
- `OUT_DIR/reflect-status.json` — the user's status ledger; read in Phase 0,
  written back in Phase 4.
- `~/.claude/usage-data/` — `/insights` facets, session-meta, and report
  (Phases 1–3).
- `/Users/luke/scratch/Styles/Neumorphic Fresh Design System/` — the report's
  design system (Phase 4). Missing → stop and ask.

## Run checklist

Copy this into your response, after the `[format sources read]` line, and tick
each box as the gate passes:

```
- [ ] Step 0   both format sources read; opening line printed
- [ ] Phase 0  OUT_DIR resolved; transcripts listed; prior JSON + ledger loaded
- [ ] Phase 1  /insights gate passed, or the user chose to proceed
- [ ] Phase 2  triage list built
- [ ] Phase 3  workflow run: extract → cluster → decide → consolidate → trend → rank
- [ ] Phase 4  report written to REPORT; merged ledger written to OUT_DIR
- [ ] Step 0b  headings match: yes
- [ ] Phase 5  report sent; TL;DR and skipped items stated
```

## Step 0 — read the format sources (non-negotiable)

Before generating anything, cat BOTH of these and quote their first line back in your
response. If either read fails, STOP and report it — do not fall back to memory or to a
previous report's shape.

1. Style/format spec — `reference/report-guide.md`, resolved against this
   skill's own directory.
2. Last known-good exemplar — `cc-reflection-20260727.html` inside `OUT_DIR`
   (`<invocation cwd>/Outputs/Reflections/`). That edition is the reference
   implementation for the markup idiom; it is not simply the newest file there,
   so do not substitute a later report.

Open your response with, verbatim:

    [format sources read] <guide path> | <exemplar path>

Section names, order, and the dashboard come from the guide — never invented, never
carried over from an earlier run. If the guide and the exemplar disagree, stop and ask
which is authoritative; do not pick one.

## Arguments

Parse from the invocation args (all optional, in any order):

- **Window** — `30d` (default), `Nd`, or `all`. Sessions whose transcript
  mtime falls inside the window are in scope.
- **Limit** — `limit=N`, where N is a positive integer; `limit=all` lifts the
  cap. Default 15. The report renders the N highest-impact findings. Any other
  value after `limit=` is an error: say so and stop, never guess.
- **Focus** — any remaining free text (e.g. a project name, `permissions`,
  `report styling`). Scope stays global, but extractors are told to dig deeper
  on matching sessions/themes and the report gives the focus a dedicated
  section.

## Pipeline

### Phase 0 — Scope the corpus

1. Resolve `OUT_DIR = <invocation cwd>/Outputs/Reflections/` and
   `REPORT = OUT_DIR/cc-reflection-$(date +%Y%m%d).html`. Create `OUT_DIR` if
   missing.
2. Enumerate transcripts: `find ~/.claude/projects -name '*.jsonl'` filtered
   by mtime within the window. **Exclude the currently running session's own
   transcript** (its sessionId is in this conversation's context) and any
   `memory/` files. Record per file: project dir, session ID (basename), size,
   mtime.
3. Read prior reports: list `OUT_DIR/cc-reflection-*.html` older than today.
   From the most recent, extract the embedded JSON block
   (`<script type="application/json" id="cc-reflection-data">`) for the
   trend/delta stage. If no prior report or no JSON block, skip trending
   gracefully.
4. Read the status ledger `OUT_DIR/reflect-status.json` — what the user has
   already checked off. Merge, never overwrite. Items marked `wontdo` are
   dropped from the ranked list; items marked `done` that still recur in this
   window are the report's most important rows, and their note says what was
   already tried. Full contract in `reference/report-guide.md`
   § The status ledger. Missing file → every item is `open`.

### Phase 1 — /insights freshness gate

`/insights` output persists at `~/.claude/usage-data/`:
- `facets/<session-id>.json` — per-session goal, outcome, satisfaction,
  friction counts/detail, helpfulness, summary.
- `session-meta/<session-id>.json` — project path, duration, message/tool
  counts, tool errors, interruptions, tokens, first prompt.
- `report.html` — the rendered insights report.

**/insights samples** — it covers a few hundred recent sessions, not the
whole corpus, so never gate on coverage percentage. Gate on recency: if the
newest file under `~/.claude/usage-data/` is less than ~7 days old (or newer
than the window start, for windows shorter than that), proceed. If older or
missing, pause with AskUserQuestion: ask the user to run `/insights` in
another session now (option A: "done, continue"; option B: "proceed with
stale/partial data"). Either way, treat insights data as a corroborating
sample: compute the fraction of in-window session IDs that have a
`session-meta/` file, use it to weight (not veto) triage, and report it in
the methodology appendix.

### Phase 2 — Triage (cheap, no agents)

Use `session-meta` + `facets` JSON to score every in-window session before
spending agent tokens. High-priority markers: friction_counts non-empty,
outcome not `fully_achieved`, tool_errors high relative to message count,
user_interruptions > 0, very long sessions, sessions matching the focus.
Low-priority: short clean sessions with `fully_achieved` + satisfied. Sessions
with no meta/facet default to medium. Output a triage list: every session gets
read, but priority determines batch depth (high-priority sessions get smaller
batches / deeper reads; low-priority sessions get skim batches).

### Phase 3 — Extraction (Workflow fan-out)

Orchestrate with the **Workflow tool** (the user opted into multi-agent
orchestration by invoking this skill). Read
`reference/extraction-guide.md` for the signal taxonomy, extractor prompt
template, JSON schemas, and batching rules, then author the workflow script.
Shape:

1. **Extract** — `pipeline()` over transcript batches (group by project;
   ~5–15 sessions per batch by priority and size; pass file paths, not
   content). Each extractor agent reads its transcripts and returns
   schema-enforced JSON signals across all four families: friction & failure,
   repetition & missed automation, wins & effective patterns, environment
   gaps. Every signal cites session ID + verbatim evidence quote.
2. **Cluster** (barrier — needs all signals) — merge/dedupe signals into
   cross-session clusters. Plain code for grouping by key; an agent pass for
   semantic merging.
3. **Decide** — per cluster, one agent weighs recurrence against build cost
   and picks a verdict: `new-skill`, `automation` (hook/setting/cron),
   `fix` (config/prompt/habit change), `keep-doing` (a win to codify), or
   `nothing`. Thresholds: `new-skill` needs ≥3 distinct sessions;
   `automation`/`fix` need ≥2; anything below stays an observation. Every
   verdict must cite its session IDs and include a concrete example (the
   exact prompt to use, the skill description to write, the settings.json
   permission line, etc.).
4. **Consolidate** — cross-check clusters against the /insights facet data
   and `~/.claude/usage-data/report.html`: where they agree, mark the finding
   corroborated; where /insights surfaces something extraction missed, add it
   with its own evidence.
5. **Trend** — if a prior report's JSON was loaded, diff: recommendations
   adopted (signal gone), still recurring (flag streak count), new this
   report.
6. **Rank and cap** — in script code, never by an agent. Sort the full list
   by impact: `leverage` descending, then `effort` ascending (minutes < hour
   < day), then distinct session count descending, then `id` ascending so
   ties land the same every run. Number every item with its `rank`. The cap
   is display-only: Trend, the status ledger and the embedded data block all
   see the full ranked list, and the report renders only the top `limit`.
   Cut earlier and finding #16 reads as adopted this week and new the next.

### Phase 4 — Report

Read `reference/report-guide.md` for structure, interactivity, motion, and
the self-containment rules. The report is styled in the **Neumorphic Fresh**
design system, which is **not bundled here** — read it from the user's own
maintained copy at `/Users/luke/scratch/Styles/Neumorphic Fresh Design System/`
(`DESIGN.md`, `colors_and_type.css`, `components.css` for the `nf-*` layer, and
`ui_kits/dashboard/Widgets.jsx` as the chart geometry reference). If that
directory is missing, stop and ask — do not substitute another design system.
Requirements in brief:

- Single self-contained HTML file at `REPORT`. No external requests: vendor
  GSAP inline (curl the minified build and embed); include three.js only if
  a WebGL scene is genuinely used; fonts inline as base64 woff2 subsets or
  fall back to the system stack. It must open from `file://`, offline,
  years from now.
- Every list of findings in impact order (Phase 3 step 6), most impactful
  first; render only the top `limit` and state `showing N of M` whenever the
  cap cut anything. Drill-down from executive summary to per-cluster evidence
  (verbatim quotes, session IDs, project paths).
- Custom inline SVG graphics throughout (spec in report-guide.md): hand-built
  charts for all data, explanatory diagrams where they make a finding land
  faster, and decorative SVG layers for aesthetic polish — no chart
  libraries, no raster images.
- Embed the machine-readable summary block
  (`<script type="application/json" id="cc-reflection-data">`) per the spec
  in report-guide.md — future runs depend on it.
- Give every finding a handoff bar: the stable `#card-<id>` permalink, a
  **Copy link** button, and a **Copy agent brief** button that writes a
  self-contained Markdown brief the reader can paste straight into a fresh
  agent session. Deep links must open the card they name, on load and on
  `hashchange`. Spec in report-guide.md § Per-finding handoff.
- Render the status ledger: the merged ledger inlined as
  `<script type="application/json" id="cc-reflection-status">`, a check-off
  control on every actionable card, status pills on the summary rows, and a
  `Save status` button. Spec in report-guide.md § The status ledger. Write the
  merged ledger back to `OUT_DIR/reflect-status.json` as well, so the file
  exists even if the user never clicks Save.

### Step 0b — verify before publishing

After generating, diff your section headings against the guide's § Structure (top to
bottom) list and print `headings match: yes/no`. `no` means fix the output, not the
claim.

### Phase 5 — Deliver

SendUserFile the report (display: render) with a caption naming the top
finding. In the final message: TL;DR of the top 3–5 recommendations in rank
order, with their verdicts and session counts, plus anything the run had to
skip (insights stale, unreadable transcripts, findings past the `limit` as
`showing N of M`) — no silent gaps.

Tell the user in one line how the loop closes: tick items off in the report as
they address them, click **Save status**, and save over
`Outputs/Reflections/reflect-status.json`. If the previous edition's ledger had
anything marked done that came back this week, lead with that — it is the
strongest signal in the report.

## Guardrails

- Diagnosis only. The only writes allowed: `OUT_DIR`, the report file, and
  scratchpad temp files.
- `OUT_DIR/reflect-status.json` is the user's record, not yours. Merge into it;
  never reset a `state` or `note` the user set, and never drop an item just
  because this edition did not surface it.
- Every recommendation cites ≥1 session ID with a verbatim evidence quote;
  skill proposals cite ≥3 distinct sessions.
- Only propose a skill for something that actually recurs — recurrence beats
  cleverness.
- Transcripts contain private data. It stays in the local report; never send
  transcript content to external services.
- If the window yields >400 sessions (e.g. `all`), tell the user the scale,
  then proceed with triage-weighted sampling: deep-read all high-priority
  sessions, sample the clean remainder, and say so in the report's
  methodology section.
