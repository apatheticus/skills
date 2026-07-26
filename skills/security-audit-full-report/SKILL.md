---
name: security-audit-full-report
description: Run an iterative, multi-cycle security vulnerability assessment against a codebase and produce one consolidated, interactive HTML report. Drives the security-audit skill in a /loop — each cycle targets the gaps the previous cycles left — until findings converge or a cycle budget is hit, then merges every run into a single styled report. Use when the user wants a thorough, repeated, or "keep auditing until it's clean" security assessment with a shareable write-up, or says "run the security vuln report", "iterative security audit", "audit until convergence then report", or "/security-audit-full-report". For a one-shot audit use security-audit; for a report over an existing audit dir use generate-cf-secaudit-report. This skill is the end-to-end orchestrator of both.
argument-hint: "[target-dir] [max-cycles] [design-system-dir]"
user-invocable: true
license: MIT
version: 1.0.0
---

# security-audit-full-report

Conduct a **looped** security assessment and generate a **consolidated HTML
report**. This skill orchestrates two other skills — it does not re-implement
either:

- **`security-audit`** does the actual hunting, one run per cycle.
- **`generate-cf-secaudit-report`**'s workflow (folded in below, with its
  `template.html` bundled in this skill's `assets/`) turns all runs into one
  report.

The skill is **stateful and self-terminating**: `/loop` re-invokes it each
cycle, and it reads `ledger.md` to decide whether to run another audit cycle or
finish and report. All raw finding data lives on disk (`run-N/`, `ledger.md`),
never only in context — so cycles survive compaction and the loop is resumable.

## The two-mode contract (read first)

Every invocation is one of two modes, decided by whether the engagement dir
already exists. **Determine the mode before doing anything else.**

- **PREFLIGHT mode** — no engagement dir for today under `<target>/.audit/`, or
  `ledger.md` is absent. Do the one-time interactive setup (§1–§3) and start the
  loop. This is the only mode allowed to ask the user questions.
- **CYCLE mode** — a `ledger.md` exists and its `status` is `running`. Run exactly
  one audit cycle and update state (§4). Non-interactive — the user is away
  while `/loop` fires. Never call `AskUserQuestion` in this mode; if a decision
  is unresolved, that is a preflight bug.

> **Why interactivity is confined to preflight:** `/loop` firings run
> unattended. Any question that could block a cycle (install? edit gitignore?
> which design system?) must be answered during the first, human-present
> invocation. Do not defer an interactive decision into a cycle.

---

## §1. Preflight — verify `security-audit` is installed

Check whether the `security-audit` skill is available (look for a `SKILL.md`
under a `security-audit/` skill dir — project `.claude/skills/security-audit/`
or the user's `~/.claude/skills/security-audit/`; a reliable probe is
`ls **/skills/security-audit/SKILL.md` from the target and home).

- **Installed** → continue to §2.
- **Not installed** → ask the user (AskUserQuestion) whether to install it from
  `https://github.com/cloudflare/security-audit-skill`.
  - **Declines** → tell them plainly: *"`security-audit` is required for
    security-audit-full-report and was not installed. Stopping."* — then
    **stop**. Do not proceed, do not create any `.audit/` state.
  - **Accepts** → install it as a **project-level** skill into
    `<target>/.claude/skills/security-audit/` (clone/copy the repo contents so
    `SKILL.md` and its companion files land directly in that dir). Then tell the
    user: *"Installed `security-audit`. Run `/reload-skills`, then invoke
    `security-audit-full-report` again to start the assessment."* — then
    **stop**. A freshly
    installed skill is not loaded until reload, so the loop cannot start this
    turn.

## §2. Preflight — ensure `.audit/` is gitignored

Only relevant if the target is a git repo (`git -C <target> rev-parse
--is-inside-work-tree`).

- **Not a git repo** → skip this step; note it ("target isn't a git repo, no
  gitignore change needed") and continue.
- **Git repo, `.audit/` already ignored** → continue.
- **Git repo, `.audit/` not ignored** → ask the user (AskUserQuestion) whether
  to add `.audit/` to `.gitignore`. If **yes**, append `.audit/` to
  `<target>/.gitignore` (create the file if absent). If **no**, continue without
  changing it. Either way the assessment proceeds — this is hygiene, not a gate.

## §3. Preflight — create the engagement and start the loop

Resolve arguments: `target-dir` (default: cwd), `max-cycles` (default: **5**),
`design-system-dir` (optional).

1. Create the **engagement dir**: `<target>/.audit/<YYYYMMDD>/` where the date
   is **today's start date**. All runs of this loop live here — the date stamps
   the *engagement*, not each run, so a loop crossing midnight does not fracture
   into two dirs.
2. Write `ledger.md` (the durable ledger — the source of truth, not context):

   ```markdown
   # security-audit-full-report engagement <YYYYMMDD>
   status: running          # running | converged | max-cycles-reached | done
   target: <abs target path>
   engagement_dir: <abs .audit/<YYYYMMDD> path>
   design_system_dir: <path or "bundled SaaS Pro">
   max_cycles: 5
   next_run: 1
   consecutive_zero_new_medplus: 0

   ## Accumulated confirmed findings (dedup keys: root_cause + title)
   <!-- one line per confirmed finding across all runs; med+ marked.
        This list is the PRIMARY cross-run dedup surface — see §4b. -->

   ## Per-cycle log
   <!-- run N: <total confirmed> confirmed, <new med+ this run> new med+, counter=<n> -->
   ```
3. Start the loop by invoking **`/loop security-audit-full-report <target>
   <max-cycles> <design-dir?>`** (self-paced — omit an interval; each cycle is heavy and
   should run to completion before the next). Tell the user the loop has started,
   where state lives, and that it will stop on its own at convergence or after
   `max_cycles`.

> After §3, this invocation is done. The next `/loop` firing enters CYCLE mode.

---

## §4. Cycle mode — run one audit, update state, decide

Triggered when `ledger.md` exists with `status: running`. Do exactly this:

### 4a. Run one `security-audit` cycle
Read `ledger.md` for `next_run` = N and `engagement_dir`. Invoke the
**`security-audit`** skill with:

- **Target**: the engagement's `target`.
- **Output directory**: `<engagement_dir>/run-N`.
- **Prior-runs pointer**: explicitly tell `security-audit` that prior runs live
  in `<engagement_dir>` (the sibling `run-1..run-(N-1)` dirs), and that this
  overrides the `~/security-audit-skill/<repo>/` path named in its own text — for
  both the output location AND the "read prior `findings.json`" step, propagated
  to the sub-agents it fans out. When honored, its *"skip known findings / target
  the gaps"* logic makes each cycle hunt new ground, so its `findings.json` is
  mostly *new* findings.

  Treat this redirect as best-effort, not guaranteed. `security-audit`'s written
  default is its own `~/security-audit-skill/<repo>/` path, and whether a passed-in
  pointer reliably reaches its sub-agents is not something this loop can enforce.
  So do **not** make convergence depend on the redirect being obeyed: if it is
  ignored and a cycle re-hunts covered ground, the cross-run dedup in §4b absorbs
  the overlap and the counter still advances correctly. The redirect is an
  efficiency optimization (avoid re-work); §4b is the correctness guarantee.

Let `security-audit` run its full six-phase methodology (it fans out its own
sub-agents; their output stays out of this context). It writes
`run-N/findings.json` (authoritative), `REPORT.md`, `FINDINGS-DETAIL.md`,
`architecture.md`.

### 4b. Count "new medium-or-higher" findings
This step is the correctness backbone of the loop: it is what makes convergence
sound *regardless of whether §4a's prior-runs redirect was honored*. Do not treat
dedup here as a rare edge case — treat overlap between runs as expected and let
this step absorb it.

From `run-N/findings.json`, take every object with `verdict: "confirmed"` and
`severity.overall_severity` in {`medium`, `high`, `critical`} (lowercase enum).
For each, form a dedup key from `root_cause` + `title`. A finding is **new** only
if its key is **not** already in the ledger's *Accumulated confirmed findings*
list. Because `root_cause` is free text and its wording can drift between runs,
don't rely on an exact string match alone: if a run's finding is clearly the same
underlying issue as one already accumulated (same sink/file and same defeated
boundary, differently worded), treat it as **known**, not new — under-merging
here would keep the counter from ever reaching convergence. Append all of this
run's confirmed findings to the accumulated list.

Let `new_medplus_count` = number of *new* med+ findings this run.

### 4c. Update the convergence counter and log
- If `new_medplus_count == 0` → `consecutive_zero_new_medplus += 1`.
- Else → reset `consecutive_zero_new_medplus = 0`.
- Set `next_run = N + 1`. Append a `## Per-cycle log` line. Write `ledger.md`.

### 4d. Decide: continue, or finish + report
Stop the loop when **either**:
- `consecutive_zero_new_medplus >= 2` → set `status: converged`, **or**
- `N >= max_cycles` → set `status: max-cycles-reached`.

Otherwise the loop continues (do nothing further; the next firing runs cycle
N+1).

**When stopping:** generate the consolidated report (§5), set `status: done`,
and **terminate the loop** — if `/loop` is self-paced via a scheduled wakeup,
stop it (ScheduleWakeup `stop: true`); otherwise state the loop is complete so
it is not re-fired. Do not schedule another cycle after `done`.

---

## §5. Generate the consolidated report (folded-in generate-cf-secaudit-report)

Runs once, at convergence/stop, over **all** runs in the engagement dir. This is
the `generate-cf-secaudit-report` workflow — follow it faithfully; accuracy
outranks polish because a security reader must trust every number and path.

> **Provenance (why this is folded-in, not a skill call):** §5 is a deliberate
> in-lined copy of `generate-cf-secaudit-report`'s workflow, and `assets/template.html`
> is a copy of that skill's template. This keeps `/security-audit-full-report` self-contained and
> portable — it works on a machine that has never installed the report skill, which
> matters because this skill is shared across teams. The cost is drift: if the
> source skill's workflow or template improves, this copy goes stale silently.
> Synced from `generate-cf-secaudit-report` as of **2026-07-15**. If that skill's
> `template.html` or §-numbered workflow has changed since, re-sync both this
> section and `assets/template.html` from it rather than editing them in isolation.

### 5.1 Inventory
List the engagement dir and every `run-N/`. For each run read `findings.json`
(source of truth for the finding list) and `REPORT.md` (exec summary, themes,
verified-clean notes, recommendations). Note each run's stated scope — it's what
justifies keeping runs distinct in the report.

### 5.2 The one rule that matters most — include every run
An engagement with several runs is **one** report, not several. Each run
deliberately covered ground the others didn't; merging them is the only complete
picture. Combine severity counts across runs, tag each finding with its run of
origin, and expose a run filter so a reader can still view one run alone. Never
drop a run or emit one file per run.

### 5.3 Extract findings faithfully
Trace every claim to `findings.json` / `REPORT.md`. Don't invent or shift
severities, attackers, paths, or counts. If reports disagree, prefer
`findings.json` and note the discrepancy. For each finding capture: `run`, `id`
(preserve original ids where present), `sev` (high/medium/low; map any
`critical` to its own tier only if present), `title`, `attacker`, `boundary`
(trust boundary / invariant broken), a faithful 2–4 sentence `desc`, the `fix`,
and a `files` array of key file/symbol refs. Condense — don't paste whole JSON —
but keep it true. Only include `verdict: "confirmed"` findings; `rejected` ones
are excluded (optionally note the count of rejected/false-positives).

### 5.4 Fill the template
Copy this skill's `assets/template.html` to
`<engagement_dir>/security-audit-<YYYYMMDD>.html`, then populate it. The template
is **data-driven** — severity counts, KPIs, donut, and filter counts all compute
from the `F[]` array, so you never hand-count them (this is what keeps a
multi-run report internally consistent).

Populate:
- The `F[]` array — one object per confirmed finding, ordered high→low then by
  run.
- `{{PLACEHOLDER}}` tokens: project name, target slug, report date, scope blurb,
  KPI sub-labels, `{{CLEAN_COUNT}}`, executive-summary HTML, theme cards,
  run-filter buttons, verified-clean items, recommendations, footer.
- **Run filter**: one `<button data-run="N">` per run, labeled by scope (e.g.
  "Run 1 · Web/API"). If there's only one run, delete the entire
  `data-group="run"` toolbar group (the template already hides per-card run tags
  when a single run is present).
- Delete the template-notes HTML comment and any example `F[]` entries.

**Design-system fidelity:** the template's `:root` is the bundled **SaaS Pro**
system, self-contained (no external dir needed). Only if the user passed a
`design-system-dir`, re-derive the `:root` block from its `tokens/*.css` and
adjust component colors per its `DESIGN.md` before filling content — don't invent
token values. Otherwise use the bundled tokens as-is. Keep the house rules:
numbers-first KPIs as the hero; two card worlds (white light cards for
KPIs/summary/findings, dark navy cards for the donut and verified-clean grid — no
third style); semantic color = status only (High→danger, Medium→warning,
Low→info; gradients are identity, not status; never pure gray/black); soft-physics
shadows and radii; honor `prefers-reduced-motion` (already wired).

### 5.5 Verify against the real pixels (do not skip)
Browsers block `file://`, so serve and drive it:
```
python3 -m http.server 8771 --directory "<engagement_dir>" &
# open http://localhost:8771/security-audit-<YYYYMMDD>.html in the browser tool
```
Screenshot the hero+KPIs+donut, scroll to findings, **expand one card**, and
**click a severity filter** — confirm the live count updates and the right cards
show. Read the console for errors. Kill the server (`lsof -ti:8771 | xargs
kill`). Fix anything off before handoff, and state which frames/interactions you
checked. (A green render is not proof — verify the real artifact.)

### 5.6 Hand off
Report: the report path, per-run and per-severity tally, how many cycles ran and
why the loop stopped (converged vs max-cycles), and what you verified against the
live page. Offer to open it (`SendUserFile` with `display: "render"`).

---

## Resumption & edge cases
- **Resuming an interrupted loop**: on any invocation, re-read `ledger.md` first
  and trust it over context. `status: running` → run the next cycle from
  `next_run`. `status: done` → the engagement is complete; don't re-run — offer
  to re-open or start a fresh engagement.
- **A cycle's `security-audit` finds nothing at all**: that's a valid zero-new
  cycle — increment the counter; two in a row still converges.
- **`findings.json` missing/malformed for a run**: treat that run as producing
  zero confirmed findings, note it in the per-cycle log, and continue — don't
  crash the loop. Flag it in the final report.
- **Never** ask a question in CYCLE mode. If you find yourself wanting to, the
  decision belonged in preflight.
