---
name: reflect
description: Generate a comprehensive, evidence-backed reflection report on how the user uses Claude Code — what works, what needs improvement, and the highest-leverage changes to their setup — by mining past session transcripts in ~/.claude/projects/ with sub-agents, clustering signals across sessions, and consolidating with /insights data. Produces a polished, self-contained, interactive HTML report. Trigger when the user asks to reflect on their Claude Code usage, audit their sessions, find setup improvements, or runs /reflect.
argument-hint: "[window: 30d|90d|all] [focus: free text, e.g. a project or theme]"
user-invocable: true
license: MIT
version: 1.1.2
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

## Arguments

Parse from the invocation args (both optional, in any order):

- **Window** — `30d` (default), `Nd`, or `all`. Sessions whose transcript
  mtime falls inside the window are in scope.
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

### Phase 4 — Report

Read `reference/report-guide.md` for structure, interactivity, motion, and
the self-containment rules, and `reference/design-system/` — a bundled copy of
the **SaaS Pro** design system: `DESIGN.md` and `MOTION.md` (the standards),
`tokens/*.css` (four token files), `components.css` (the `sp-*` class layer),
and `charts/` (chart geometry references, read-only — see its README).
Requirements in brief:

- Single self-contained HTML file at `REPORT`. No external requests: vendor
  GSAP inline (curl the minified build and embed); include three.js only if
  a WebGL scene is genuinely used; fonts inline as base64 woff2 subsets or
  fall back to the system stack. It must open from `file://`, offline,
  years from now.
- Ranked assessment, most leverage first; drill-down from executive summary
  to per-cluster evidence (verbatim quotes, session IDs, project paths).
- Custom inline SVG graphics throughout (spec in report-guide.md): hand-built
  charts for all data, explanatory diagrams where they make a finding land
  faster, and decorative SVG layers for aesthetic polish — no chart
  libraries, no raster images.
- Embed the machine-readable summary block
  (`<script type="application/json" id="cc-reflection-data">`) per the spec
  in report-guide.md — future runs depend on it.

### Phase 5 — Deliver

SendUserFile the report (display: render) with a caption naming the top
finding. In the final message: TL;DR of the top 3–5 recommendations with
their verdicts and session counts, plus anything the run had to skip
(insights stale, unreadable transcripts) — no silent gaps.

## Guardrails

- Diagnosis only. The only writes allowed: `OUT_DIR`, the report file, and
  scratchpad temp files.
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
