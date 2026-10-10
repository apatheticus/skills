---
name: reflect
description: Generate a comprehensive, evidence-backed reflection report on how the user uses Claude Code — what works, what needs improvement, and the highest-leverage changes to their setup — by mining past session transcripts in ~/.claude/projects/ with sub-agents, clustering signals across sessions, and consolidating with /insights data. Produces a polished, self-contained, interactive HTML report. Trigger when the user asks to reflect on their Claude Code usage, audit their sessions, find setup improvements, or runs /reflect.
argument-hint: "[window: 30d|90d|all] [limit=N, default 15] [out=PATH, default ./Reflections] [focus: free text, e.g. a project or theme]"
user-invocable: true
license: MIT
version: 1.9.0
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

**Needs:** Claude Code with the Workflow tool (Phase 3) and `python3`,
standard library only (Phase 4). No Workflow tool: say so and stop before
Phase 0.

## Guardrails

- Diagnosis only. The only writes allowed: `OUT_DIR` (the output folder,
  Phase 0), the report file, and scratchpad temp files. A `PRIOR_DIR` outside
  `OUT_DIR` is read, never written, moved or deleted.
- `OUT_DIR/reflect-status.json` is the user's record, not yours.
  `scripts/render_report.py` is its only writer: it merges, never resets a
  `state` or `note` the user set, never drops an item because this edition
  did not surface it, and writes nothing if a merge would. Never write or
  edit the file by hand.
- Every recommendation cites ≥1 session ID with a verbatim evidence quote;
  skill proposals cite ≥3 distinct sessions.
- Only propose a skill for something that actually recurs — recurrence beats
  cleverness.
- Transcripts contain private data. It stays in the local report; never send
  transcript content to external services. A new `OUT_DIR` gets its
  `.gitignore` (Phase 0 step 1) so a commit cannot carry it off either.
- If the window yields >400 sessions (e.g. `all`), tell the user the scale,
  then proceed with triage-weighted sampling: deep-read all high-priority
  sessions, sample the clean remainder, and say so in the report's
  methodology section.

## Contents

Needs and Guardrails sit above this list; they hold for every phase.
Sections, in run order:

- **Run checklist** — copy it into your response and tick each gate.
- **Step 0 — read the format sources** — hard gate before anything is
  generated; your response opens with the `[format sources read]` line.
- **Arguments** — window (`30d` default, `Nd`, `all`), `limit=N` (15 default,
  `all` for no cap), `out=PATH` (`./Reflections/` default), and an optional
  focus.
- **Pipeline**
  - **Phase 0 — Scope the corpus** — `OUT_DIR`/`REPORT`, `corpus.py` for the
    in-window transcripts and their counts, the prior report, the ledger.
  - **Phase 1 — /insights freshness gate** — gate on recency, never coverage.
  - **Phase 2 — Triage** — batch by the priority `corpus.py` scored; no agents.
  - **Phase 3 — Extraction** — Workflow fan-out: extract, cluster (reusing
    prior ids), decide, consolidate.
  - **Phase 4 — Report** — `assemble.py` builds and ranks the data,
    `verify_quotes.py` checks every quote, `render_report.py` fills
    `assets/template.html`.
  - **Step 0b — verify before publishing** — the script's checks, ending in
    `headings match: yes`.
  - **Phase 5 — Deliver** — send the report, TL;DR, skipped items, how the
    loop closes.

### Reference files — bundled, one level deep, read each in full

- `reference/report-guide.md` — the report's spec and the data schema. Read
  in Step 0 and again in Phase 4; Phase 0 uses its § The status ledger.
  Sections: The bundled template · Structure (top to bottom) · The status
  ledger · Per-finding handoff · The Usage panorama — dashboard spec · Custom
  SVG graphics · Interactivity & motion · Embedded data block.
- `assets/template.html` — the report itself: CSS, fonts, GSAP and renderer
  inline, with sample data. About 340KB: **never Read it**; `head -40` shows
  its header comment, which is all a run needs.
- `scripts/corpus.py` — Phases 0 and 2. Scopes the transcripts, excludes this
  session and its forks, counts the panorama, scores triage priority.
- `scripts/workflow_result.py` — reads a Workflow output file's `result` and
  undoes the harness's `<\` and `Assistant\:` escaping; `assemble.py` uses it.
- `scripts/assemble.py` — Phase 4. Builds `report-data.json`: thresholds,
  ledger `wontdo`, streak, trend, adopted, rank.
- `scripts/verify_quotes.py` — Phase 4. Keeps only verbatim evidence,
  re-ranks.
- `scripts/render_report.py` — Phase 4. Validates the data, merges the
  status ledger, fills the template, writes both, and checks them (Step 0b).
- `reference/extraction-guide.md` — read in Phase 3, before authoring the
  workflow script. Sections: Transcript anatomy · Signal families · Extractor
  output schema · Batching · Clustering & decision stage.

### External inputs — not bundled

- `~/.claude/projects/**/*.jsonl` — the transcripts (Phases 0 and 3).
- `OUT_DIR/reflect-status.json` — the user's status ledger; read in Phase 0
  (from `PRIOR_DIR`, which is `OUT_DIR` unless an old report is migrating),
  merged and written to `OUT_DIR` by `render_report.py` in Phase 4.
- `~/.claude/usage-data/` — `/insights` facets, session-meta, and report
  (Phases 1–3).

## Run checklist

Copy this into your response, after the `[format sources read]` line, and tick
each box as the gate passes:

```
- [ ] Step 0   guide read, template header read; opening line printed
- [ ] Phase 0  OUT_DIR resolved; corpus.py ran, this session excluded; prior report + ledger found
- [ ] Phase 1  /insights gate passed, or the user chose to proceed
- [ ] Phase 2  batches built from corpus.json priorities
- [ ] Phase 3  workflow run: extract → cluster → decide → consolidate
- [ ] Phase 4  assemble.py + verify_quotes.py ran, rebuilt quotes read; report rendered; ledger merged by the script
- [ ] Step 0b  headings match: yes
- [ ] Phase 5  report sent; TL;DR and skipped items stated
```

## Step 0 — read the format sources (non-negotiable)

Before generating anything, read BOTH of these and quote their first line back in your
response. If either read fails, STOP and report it — do not fall back to memory or to a
previous report's shape.

1. Style/format spec — `reference/report-guide.md`, resolved against this
   skill's own directory. Read it in full.
2. The template's header comment — `head -40 assets/template.html`, same
   directory. Only those 40 lines: the rest of the file is vendored CSS, fonts
   and GSAP, and must never be Read into context.

Open your response with, verbatim:

    [format sources read] <guide path> | <template path>

Section names, order, and the dashboard come from the template, which the guide
specifies — never invented, never carried over from an earlier run. If the guide
and the template's header disagree, stop and ask which is authoritative; do not
pick one.

## Arguments

Parse from the invocation args (all optional, in any order):

- **Window** — `30d` (default), `Nd`, or `all`. Sessions whose transcript
  mtime falls inside the window are in scope.
- **Limit** — `limit=N`, where N is a positive integer; `limit=all` lifts the
  cap. Default 15. The report renders the N highest-impact findings. Any other
  value after `limit=` is an error: say so and stop, never guess.
- **Output** — `out=PATH`, the folder the report and its ledger go to.
  Default `Reflections/` in the launch folder: the session's primary working
  directory, where Claude Code was started, never wherever the shell has
  since `cd`'d to. A relative PATH resolves against that same launch folder;
  `~` expands; quote a PATH with spaces (`out="My Reports"`). An empty
  `out=` is an error: say so and stop.
- **Focus** — any remaining free text (e.g. a project name, `permissions`,
  `report styling`). Scope stays global, but extractors are told to dig deeper
  on matching sessions/themes and the report gives the focus a dedicated
  section.

## Pipeline

### Phase 0 — Scope the corpus

1. Resolve `OUT_DIR` from `out=` (see Arguments; default
   `<launch folder>/Reflections/`) and
   `REPORT = OUT_DIR/cc-reflection-$(date +%Y%m%d).html`. If `OUT_DIR` is
   missing, create it and write `OUT_DIR/.gitignore` holding the single line
   `*`: the report quotes private transcripts, and a launch folder is often a
   repo root, so git must never see the folder. Write that file only into a
   folder this run created. A folder that already existed is left alone,
   because `out=` may name one the user keeps in git on purpose, and a user
   who deleted the file wants the reports tracked. Set
   `PRIOR_DIR = OUT_DIR`, with one exception for reports made
   before 1.8.0, which wrote to `<launch folder>/Outputs/Reflections/`: when
   `out=` was not given, `OUT_DIR` holds no `cc-reflection-*.html` and no
   `reflect-status.json`, and that old folder holds either, set `PRIOR_DIR`
   to the old folder. It is read-only; this run still writes only to
   `OUT_DIR`, and Phase 5 says so.
2. Scope and count the corpus in one call, into `WORK`, a new folder in the
   scratchpad:

   ```bash
   python3 <skill dir>/scripts/corpus.py --window <window> \
     --self ${CLAUDE_SESSION_ID} --out WORK/corpus.json
   ```

   Claude Code fills in `${CLAUDE_SESSION_ID}` with this run's id when it loads
   the skill. The script drops that session and every transcript that
   continues into it (a fork or resume carries this conversation's history),
   then records each in-window transcript's path, project, size, counts and
   triage priority, and builds the Usage panorama. If it stops because
   `--self` was not filled in, pass the id from this session's own transcript
   file name. `corpus.json` is the corpus for every later phase.
3. Find the prior report: the most recent `PRIOR_DIR/cc-reflection-*.html`
   older than today. Read its embedded `cc-reflection-data` block for the
   recommendation ids and titles the cluster stage reuses (Phase 3 step 5);
   `assemble.py` reads the same file for Trend in Phase 4. No prior report
   means no Trend.
4. Read the status ledger `PRIOR_DIR/reflect-status.json` — what the user has
   already checked off. Read only, for two things: items marked `wontdo` are
   dropped from the ranked list, and items marked `done` that still recur in
   this window are the report's most important rows, their note saying what
   was already tried. The merge happens in Phase 4, in the script. Full
   contract in `reference/report-guide.md` § The status ledger. Missing
   file → every item is `open`.

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

`corpus.py` already scored every session from its counts and the /insights
facets: `priority` is `high` (friction, an unfinished outcome, many errors,
interruptions, very long), `low` (short, clean, `fully_achieved`), `medium`
(everything else, including no facet), or `empty` (no turns in the window).
Raise sessions matching the focus to `high` and leave out `empty`. Every other
session gets read; priority sets batch depth (high-priority sessions get
smaller batches and deeper reads, low-priority ones skim batches).

### Phase 3 — Extraction (Workflow fan-out)

Orchestrate with the **Workflow tool** (the user opted into multi-agent
orchestration by invoking this skill). Read
`reference/extraction-guide.md` for the signal taxonomy, extractor prompt
template, JSON schemas, and batching rules, then author the workflow script.
It returns exactly the object in § Workflow return value, which `assemble.py`
reads in Phase 4. Shape:

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
5. **Reuse ids** — give the cluster stage the prior edition's recommendation
   ids and titles: a cluster that is the same issue keeps the prior `id`, or
   Trend reads it as adopted and new at once. `assemble.py` computes streak,
   trend and adopted from those ids in Phase 4.
6. **Rank and cap** — `assemble.py` ranks in code in Phase 4, never an agent:
   `leverage` descending, then `effort` ascending, then distinct sessions
   descending, then `id`. The cap is display-only: Trend, the status ledger
   and the embedded data block all see the full ranked list, and the report
   renders only the top `limit`. Cut earlier and finding #16 reads as adopted
   this week and new the next.

### Phase 4 — Report

The report is `assets/template.html` filled with this run's data. You write
JSON; `scripts/render_report.py` writes the HTML. The template already carries
the Neumorphic Fresh design system, fonts, GSAP, every chart, the ledger
controls, the handoff bar and the motion, so there is nothing to style, vendor
or fetch. **Never Read or hand-edit the template or the report**: both are
~340KB, and a hand edit is exactly the drift the template exists to stop.

1. Re-read `reference/report-guide.md` § Embedded data block: it is the full
   schema, and the script enforces it.
2. Write `WORK/narrative.json`, the prose only this run can write: `hero`
   (the one-line verdict and the paragraph), `focus` when one was given, and
   `methodology` (triage, sampled, pipeline, limitations), shaped as
   `assemble.py`'s docstring shows. Then build the data and check its quotes:

   ```bash
   python3 <skill dir>/scripts/assemble.py --workflow <the workflow's output file> \
     --corpus WORK/corpus.json --narrative WORK/narrative.json \
     --prior-report <Phase 0 step 3's report, if any> \
     --status PRIOR_DIR/reflect-status.json --limit <limit> \
     --out WORK/report-data.json
   python3 <skill dir>/scripts/verify_quotes.py \
     --data WORK/report-data.json --corpus WORK/corpus.json
   ```

   `assemble.py` joins clusters to decisions, applies the verdict thresholds,
   drops findings the ledger marks `wontdo`, sets streak, trend and adopted,
   ranks the **full** list, and copies in the corpus counts and panorama.
   `verify_quotes.py` keeps only evidence found verbatim in the session it
   cites and prints a line for every quote it rebuilt or dropped. Read each
   `rebuilt` line: a rebuilt quote can keep a real but off-topic fragment. Fix
   a problem at its source (`narrative.json`, or a rerun workflow stage) and
   rerun both scripts.
3. Render:

   ```bash
   python3 <skill dir>/scripts/render_report.py \
     --data WORK/report-data.json \
     --prior-status PRIOR_DIR/reflect-status.json \
     --status OUT_DIR/reflect-status.json --out REPORT
   ```

   The script reads the prior ledger (missing means empty), keeps every
   item's `state`, `note`, `marked` and `first_seen`, adds each new
   actionable finding as `open`, drops nothing, and writes the result to
   `OUT_DIR` before the report, so the file exists even if the user never
   clicks Save. A data problem prints one line per missing or invalid field
   and writes nothing. Fix the JSON and rerun; never work around the script.
   A bad ledger is the user's to fix: say so and stop.

### Step 0b — verify before publishing

The script's own output is the gate. It must print `ledger: K kept, A added,
0 changed`, `data blocks: round-trip ok`, `headings match: yes`, `external
requests: none`, `block ids: each exactly once`, and AA contrast in both
themes, and exit 0. Any other line means fix the
data (or, for a template defect, stop and say so), never the claim.

### Phase 5 — Deliver

Send the report with SendUserFile (display: render), captioned with the top
finding, if that tool exists; otherwise print REPORT as an absolute path and
offer to open it. In the final message: TL;DR of the top 3–5 recommendations in rank
order, with their verdicts and session counts, plus anything the run had to
skip (insights stale, unreadable transcripts, findings past the `limit` as
`showing N of M`) — no silent gaps.

Tell the user in one line how the loop closes: tick items off in the report as
they address them, click **Save status**, and save over
`OUT_DIR/reflect-status.json`, written as the real path. If the previous
edition's ledger had anything marked done that came back this week, lead with
that — it is the strongest signal in the report. If `PRIOR_DIR` was the old
`Outputs/Reflections/`, say in one line that its history now carries on in
`OUT_DIR` and the old folder can go once the user has checked the new report.
