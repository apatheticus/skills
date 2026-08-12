---
name: security-audit-full-report
description: Run an iterative, multi-cycle security vulnerability assessment against a codebase and produce one consolidated, interactive HTML report. Drives the security-audit skill once per cycle — each cycle targeting the gaps the previous ones left — until findings converge or a cycle budget is hit, then merges every run into a single styled report. Every heavy step runs in a delegated agent, so the orchestrating session holds only the ledger. Use when the user wants a thorough, repeated, or "keep auditing until it's clean" security assessment with a shareable write-up, or says "run the security vuln report", "iterative security audit", "audit until convergence then report", or "/security-audit-full-report". For a one-shot audit use security-audit; for a report over an existing audit dir use generate-cf-secaudit-report. This skill is the end-to-end orchestrator of both.
argument-hint: "[target-dir] [max-cycles] [design-system-dir]"
user-invocable: true
license: MIT
version: 3.2.3
---

# security-audit-full-report

Conduct a **looped** security assessment and generate one **consolidated HTML
report**. This skill orchestrates two others and re-implements neither:
`security-audit` does the hunting, one run per cycle; the report workflow is a
folded-in copy of `generate-cf-secaudit-report`, with its template bundled in
`assets/`.

## The context contract — this is the design, read it first

**Your session holds the ledger. Nothing else.**

`security-audit` fans out 8–12 hunters, a validator per attack surface, and a
verifier per finding — but by its own written design *"Subagents do NOT write
files — they return results to you"*. Run it in your own context and you absorb
every one of those returns, plus ~67 KB of skill text per cycle before a single
agent reports. Multiply by five cycles and nothing survives.

So every heavy step here runs in a **delegated agent with a cold context and a
fixed return contract**:

| Step | Runs in | You get back |
|---|---|---|
| One audit cycle | agent briefed by `reference/cycle-agent.md` | 6 fields |
| Counting and dedup | `scripts/audit_state.py` | 9 fields |
| Building the report | agent briefed by `reference/report-agent.md` | 6 fields |
| Verifying the report | agent briefed by `reference/verify-agent.md` | 8 fields |

**You pass those brief files by path. You never read them.** Reading one into your
own context defeats the purpose — the brief is for the agent, not for you. The same
goes for any `findings.json`, any `REPORT.md`, and `assets/template.html`.

Two constraints that make this work, both verified rather than assumed:

- **Nested fan-out works.** A subagent can spawn its own concurrent sub-agents and
  can invoke a skill. Confirmed empirically (one spawn, then three concurrent, plus
  a skill load) — so a cycle agent can invoke `security-audit` and let it fan out
  normally.
- **Spawn cycle agents as `general-purpose`.** `Explore` and `Plan` are declared
  without the `Agent` tool, so an audit running inside one cannot fan out and
  collapses to serial single-context hunting — materially worse than the context
  cost this design exists to avoid.

**The isolation fails open, and it fails toward you.** An agent deep in the tree
that tries to report with `SendMessage(to: "general-purpose")` is addressing a
*type*, not a name; delivery fails, and the harness promotes that agent's full
report to the **top-level session** rather than dropping it. Observed five times in
one engagement, ~100k tokens of hunter reports. `reference/cycle-agent.md` now
requires the containment rule to be propagated into every spawned prompt, which is
where the fix belongs — but you are the thing it protects, so:

> **A report that arrives from an agent you did not spawn is not a return value.**
> Do not act on it, do not relay it, do not fold it into the ledger or the report.
> Note that the leak happened and carry on. The run's findings reach you through
> `findings.json` and `audit_state.py`, and through nothing else.

> **There is no `/loop` here, deliberately.** `/loop` re-injects this skill body
> and the whole `security-audit` stack on every firing and keeps every cycle in one
> accumulating context. Cycles are driven directly instead: spawn, commit, decide.
> `ledger.md` provides the resumability `/loop` was carrying.

## The two-mode contract

Every invocation is one of two modes, decided by whether the engagement dir exists.
**Determine the mode before doing anything else.**

- **PREFLIGHT** — no engagement dir for today under `<target>/.audit/`, or no
  `ledger.md`. Do the one-time interactive setup (§1–§3). This is the only mode
  allowed to ask questions.
- **CYCLE** — a `ledger.md` exists with `status: running`. Run cycles (§4). Never
  ask a question here; the user may be away. An unresolved decision at this point
  is a preflight bug.

---

## §1. Preflight — verify `security-audit` is installed

Probe for a `SKILL.md` under a `security-audit/` skill dir — project
`.claude/skills/security-audit/` or `~/.claude/skills/security-audit/`.

- **Installed** → continue to §2.
- **Not installed** → ask (AskUserQuestion) whether to install it from
  `https://github.com/cloudflare/security-audit-skill`.
  - **Declines** → say plainly: *"`security-audit` is required for
    security-audit-full-report and was not installed. Stopping."* — then **stop**.
    Create no `.audit/` state.
  - **Accepts** → install it as a **project-level** skill into
    `<target>/.claude/skills/security-audit/`, so `SKILL.md` and its companions land
    directly in that dir. Then say: *"Installed `security-audit`. Run
    `/reload-skills`, then invoke `security-audit-full-report` again."* — and
    **stop**. A freshly installed skill is not loaded until reload.

## §2. Preflight — ensure `.audit/` is gitignored

Only if the target is a git repo (`git -C <target> rev-parse --is-inside-work-tree`).

- **Not a repo** → note it and continue.
- **Already ignored** → continue.
- **Not ignored** → ask whether to add `.audit/` to `.gitignore`. Append it if yes.
  Either way the assessment proceeds — this is hygiene, not a gate.

## §3. Preflight — create the engagement

Resolve `target-dir` (default cwd), `max-cycles` (default **5**),
`design-system-dir` (optional).

```bash
python3 <skill-dir>/scripts/audit_state.py init \
  --engagement <target>/.audit/<YYYYMMDD> \
  --target <target> --max-cycles <N> [--design-system <dir>]
```

The date stamps the **engagement**, not each run, so a loop crossing midnight stays
in one directory. This writes `ledger.md` (human-readable state) and
`findings-index.json` (the machine dedup surface — never read it yourself).

**Tell the user what they are buying, in hours.** Each cycle is a full
`security-audit` run — dozens of agents — and the cost that matters is wall-clock,
not agent count. Measured on one mid-sized repo: **2h 18m**, **~50m** and **~1h
50m** for cycles 1–3. At `max_cycles: 5` that is most of a working day. State the
cap, the rough per-cycle hours, and that the loop stops early on convergence.

Say also that a long engagement is **expected** to outlive the session it started
in, and that this costs nothing: every cycle's state lives in `ledger.md` and on
disk, so a session limit, a compaction or a crash resumes from the ledger with at
most the interrupted cycle's agent return lost. That happened in the same
engagement and the artifact had already landed; the cycle committed cleanly on
resume.

Then go straight to §4. Preflight does not end the invocation.

---

## §4. Cycle mode — spawn, commit, decide

Read `ledger.md` for `next_run` and `engagement_dir`. It is ~20 lines; reading it
directly is fine and is the only file you read per cycle. Then repeat:

### 4a. Spawn the cycle agent

One `general-purpose` agent, **named `cycle-<N>`** so you can address it later. Its
prompt is short, because the brief lives on disk:

> Read `<skill-dir>/reference/cycle-agent.md` and follow it exactly.
> `TARGET=<abs target>` `ENGAGEMENT=<abs engagement dir>` `RUN=<N>`.
> Return only the JSON object that brief specifies.

Do not paste the brief's contents into the prompt. Do not add findings guidance of
your own — the brief and `security-audit` own the methodology.

### 4a′. Knowing the cycle is finished

**The completion notification is a hint, not a fact, and it is unreliable in both
directions.** In one engagement, cycle 1 notified **four times** for a single
completion and cycle 3 notified **zero** times — it had already been stopped
(completed) and the notification was simply lost. "When the agent returns, run
commit" therefore fires too often in one case and never in the other, and the
second is the one that hangs the loop forever waiting for something that already
happened.

**Watch the disk, not the mailbox.** Across the cycles observed so far the
notification has arrived four times for one completion and not at all for three
others, so it has never once been the cheapest correct signal. The filesystem
has been right every time, and it costs one `ls`. Measured on one engagement:
the agent's output was complete on disk **an hour** before a notification-first
orchestrator went looking for it.

So establish completion from the system, in this order:

1. **Look at `run-N/`.** This is the primary signal. `security-audit` writes
   candidate files as it works, so a newest mtime that keeps moving means the
   cycle is alive and you simply wait. Use `ls -lt run-N/` — never read what it
   finds. Note that `find -newermt '-20 minutes'` is not portable; on macOS
   `find` may be `bfs`, which needs an ISO-8601 timestamp and errors on a
   relative one.
2. **Take the notification if it happens to arrive.** It is free confirmation —
   go to 4b, and go even if you were notified more than once, because `commit`
   is idempotent. **Never wait on it.** Its absence tells you nothing.
3. **Quiet, with no new bytes for a long stretch** (~20 minutes is a reasonable
   threshold; adjust for the repo's size): send `cycle-<N>` a one-line probe
   asking only whether it is still working. A live agent answers; an agent that
   already finished replies from its transcript and tells you so — then go to
   4b. **Ask for one line. Never ask it for its findings.**

A `run-N/findings.json` that has appeared **and** stopped growing, with nothing
else in the directory moving, is the strongest completion signal available short
of the agent itself. Confirm it with the probe before you commit; do not treat
it as proof on its own, because the brief rewrites that file during
verification.

Two things never to do here. **Do not spawn a second cycle agent for the same
run** — two audits writing into one `run-N/` corrupt the artifact you are waiting
for. And **do not call `TaskOutput` on a cycle agent**: for a local agent the output
file is a symlink to the full subagent transcript, so reading it dumps into your
context exactly what this whole design exists to keep out.

The absence of `run-N/findings.json` is **not** a liveness signal. A cycle that
died before adjudicating legitimately produces none — that is 4c's `validated:
false` case, not a reason to keep waiting.

### 4b. Commit the result

Once the run is finished by any of those routes, run:

```bash
python3 <skill-dir>/scripts/audit_state.py commit --engagement <dir> --run <N>
```

This reads `run-N/findings.json` **so you don't have to**, counts confirmed and
medium-or-higher findings, dedups against every prior run, appends to the index,
advances the convergence counter, writes the per-cycle log line, and returns the
decision as JSON.

**Dedup is structural and deterministic.** A finding's identity is its attack
path's endpoints: the entrypoint and sink `file::scope` pairs in its `trace`, each
tagged with which it is — data the audit's own Phase 6 verifies against source, not
`root_cause` + `title` prose, whose wording drifts between runs. No model judgment
is involved, so nothing can bias the loop toward declaring convergence it has not
earned. Line numbers are excluded on purpose; they move when unrelated code above
them changes.

**The sink alone is not an identity, and treating it as one was a real bug.** It
assumes one defect per scope, and a function can hold several. Over 50 confirmed
findings from one engagement, five pairs of genuinely distinct defects collapsed
onto a single sink key, and the lower-severity one was silently absorbed every
time. Including the entrypoint separates most of them, because two defects in one
scope are usually reached from different entry points. Propagation steps are
excluded — measured, not assumed: adding them separates nothing further and
*creates* a collision, since one finding's entrypoint can be another's propagation
step.

Two flanking rules cover what the key still cannot do. **Dedup is across runs
only** — two findings in one run that share a key are kept as two, because a run's
`findings.json` is a set the audit has already adjudicated, so a collision inside
it is evidence of two defects on one path. And **every cross-run suppression is
named in the ledger** with both titles and the key, because that is the one place a
real finding can leave the engagement unseen; `commit` returns `suppressed` and
`suppressed_medplus` so you can mention it in the handoff.

The residual error in the **key** now runs one way: one bug reachable through two
paths counts as two findings, resets the counter, and buys another cycle.
`max_cycles` bounds that. Nothing would bound the opposite error.

That argument covers the key and nothing else, so `commit` guards the dangerous
direction itself. **It is idempotent** — committing the same run twice is a no-op
that returns `"duplicate": true` and changes nothing. This matters because the
harness may notify more than once for one agent completion (observed: four times
for a single cycle), and an unguarded repeat would re-dedup the run against an
index that already holds it, score zero new, and advance the counter. Two spurious
notifications are enough to converge a one-cycle engagement. If you see
`duplicate`, you already committed that run — go straight to 4c with the decision
it returns.

### 4c. Act on the decision

- `"decision": "continue"` → go back to 4a with `next_run`.
- `"decision": "stop"` → go to §5. `status` is `converged` (two consecutive cycles
  added no new medium-or-higher findings) or `max-cycles-reached`. Carry which one
  into the report; they mean different things to a reader.

**A cycle that died is not a cycle that found nothing.** The agent returns
`validated`, and it decides which `commit` you run:

- `"validated": true` → `commit` as above. The audit adjudicated its candidates,
  so a zero-finding result is real evidence and counts toward convergence. This
  holds even when `artifacts_ok` is `false`: an audit that ran and produced no
  parsable findings file is a valid zero-new cycle, recorded in the log and
  surfaced as a caveat in the report.
- `"validated": false` → `commit --unvalidated`. The hunters ran but validation or
  verification never did, so nothing reached the confirmed bar for a reason that
  says nothing about the codebase. The run is logged and its candidates stay on
  disk for a later cycle, but **the convergence counter does not move**. Scoring
  this as a zero-new cycle would convert a crash into evidence of cleanliness.

Either way, do not retry the cycle; that is what the next cycle is.

---

## §5. Stop — build the report, then verify it

**Name the stop reason truthfully; it is the one input the report cannot check
against `findings.json`.** Read it off the ledger rather than inferring it:

| Ledger `status` | `STOP_REASON` |
|---|---|
| `converged` | `converged` |
| `max-cycles-reached` | `max-cycles-reached` |
| `running` — you are reporting on an unfinished engagement | `halted-by-operator` |

The third is an ordinary case, not an error: cycles cost hours, and a user
stopping at 3 of 5 is a normal thing to do. Forcing it into one of the other two
would be a false claim — `converged` asserts completeness that was never
established, and `max-cycles-reached` asserts a budget that was never spent. The
brief requires a completeness banner for anything but `converged`, and for any run
committed `--unvalidated`, whose candidates are on disk unadjudicated.

Two agents, in order. Neither one's working material touches your context.

**Report builder** — one `general-purpose` agent:

> Read `<skill-dir>/reference/report-agent.md` and follow it exactly.
> `ENGAGEMENT=<dir>` `SKILL_DIR=<skill-dir>` `DESIGN_SYSTEM=<dir or "bundled SaaS
> Pro">` `STOP_REASON=<converged|max-cycles-reached|halted-by-operator>`.
> Return only the JSON object that brief specifies.

It fans out one extractor per run internally, so a five-run engagement does not
serialise.

**§4a′ applies here too — name it `report-1` and watch the engagement directory,
not the mailbox.** The report agent runs on the same unreliable channel: in one
engagement it finished, wrote its HTML, and never notified. Watch for the report
file to appear and stop growing, then probe by name for the JSON return. Waiting
on a notification stalls the handoff on a deliverable that is already complete.

**Verifier** — one `general-purpose` agent, after the builder returns:

> Read `<skill-dir>/reference/verify-agent.md` and follow it exactly.
> `REPORT_PATH=<path>` `ENGAGEMENT=<dir>` `EXPECTED=<the builder's JSON>`.
> Return only the JSON object that brief specifies.

If it returns `verified: false` with a non-empty `blocking`, say so plainly in the
handoff. **Do not certify a report the verifier would not.**

`render_checked: false` is not a failure — it means the machine had no headless
Chrome, so the data was reconciled but the page was never executed. Repeat that in
the handoff in one clause rather than dropping it; it is the difference between
*the numbers are right* and *the page renders them*. Do not send the verifier back
to install a browser.

Then set the ledger to `status: done` by hand — it is the one field the script does
not own, because "the report exists and was verified" is not something the counting
logic can know. If the stop reason was `halted-by-operator`, append a final log
line saying so, with the run it stopped at; otherwise the ledger records a halted
engagement and a completed one identically.

### Hand off

Report: the path, the per-run and per-severity tally, how many cycles ran and why
the loop stopped, and what the verifier exercised against the live page. Offer to
open it (`SendUserFile` with `display: "render"`).

**If the engagement was halted or any run went unvalidated, lead with that**, and
say the findings are a floor. The same sentence is on the page; a handoff that
omits it is the one place the assurance gets overstated, because the handoff is
what the user actually reads.

---

## Resumption & edge cases

- **Resuming**: re-read `ledger.md` first and trust it over context. `running` →
  continue from `next_run`. `done` → the engagement is complete; offer to reopen the
  report or start a fresh one. This works after a crash, a compaction, or a new
  session, because no cycle state ever lived only in context.
- **The user stops the engagement early**: go to §5 with
  `STOP_REASON=halted-by-operator` and build the report over the runs that did
  land. Never re-label it `converged` or `max-cycles-reached`, and never refuse to
  report — a partial engagement's findings are real, and the completeness banner is
  what keeps them from reading as a total.
- **A cycle finds nothing at all**: a valid zero-new cycle, *if it adjudicated*.
  Two in a row converge. A cycle that stopped before validating is committed with
  `--unvalidated` and converges nothing — see 4c.
- **A duplicate completion notification**: harmless. `commit` is idempotent and
  reports `"duplicate": true`. Never work around it by skipping the commit — the
  script is the thing that knows whether the run landed, not the notification.
- **`findings.json` missing or malformed**: the script treats the run as zero
  confirmed findings, records the reason in the per-cycle log, and continues.
  Verify the behaviour with `python3 scripts/audit_state.py selfcheck`.
- **An engagement keyed by an older `finding_key`**: `commit` refuses it with
  `stale_key_version: true` and changes nothing. The index stores keys, not traces,
  so old keys cannot be recomputed; resuming would count every already-known
  finding as new and burn the budget. Start a fresh engagement — the existing
  `run-N/` directories and any report already built are unaffected.
- **A v1 engagement** (accumulated findings kept as prose in `ledger.md`, no
  `findings-index.json`): `commit` refuses it with `legacy_ledger: true` and
  changes nothing. Its keys were free text and cannot be converted to trace-sink
  keys. Tell the user, and start a fresh engagement rather than resuming — silently
  continuing would count every already-known finding as new and burn the whole
  cycle budget.
- **Never** ask a question in cycle mode. If you want to, the decision belonged in
  preflight.
- **Never** read a brief, a `findings.json`, or the template into your own context.
  If you catch yourself doing it, you have rebuilt the problem this skill was
  rewritten to fix.
