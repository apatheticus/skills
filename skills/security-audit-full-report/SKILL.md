---
name: security-audit-full-report
description: Run an iterative, multi-cycle security vulnerability assessment against a codebase and produce one consolidated, interactive HTML report. Drives the security-audit skill once per cycle — each cycle targeting the gaps the previous ones left — until findings converge or a cycle budget is hit, then merges every run into a single styled report. Every heavy step runs in a delegated agent, so the orchestrating session holds only the ledger. Use when the user wants a thorough, repeated, or "keep auditing until it's clean" security assessment with a shareable write-up, or says "run the security vuln report", "iterative security audit", "audit until convergence then report", or "/security-audit-full-report". For a one-shot audit use security-audit; for a report over an existing audit dir use generate-cf-secaudit-report. This skill is the end-to-end orchestrator of both.
argument-hint: "[target-dir] [max-cycles] [design-system-dir]"
user-invocable: true
license: MIT
version: 2.0.0
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
| One audit cycle | agent briefed by `reference/cycle-agent.md` | 5 fields |
| Counting and dedup | `scripts/audit_state.py` | 9 fields |
| Building the report | agent briefed by `reference/report-agent.md` | 6 fields |
| Verifying the report | agent briefed by `reference/verify-agent.md` | 6 fields |

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

**Tell the user what they are buying before you start.** Each cycle is a full
`security-audit` run: dozens of agents, and real wall-clock. At `max_cycles: 5`
that is up to five of them. State the cap and that the loop stops early on
convergence.

Then go straight to §4. Preflight does not end the invocation.

---

## §4. Cycle mode — spawn, commit, decide

Read `ledger.md` for `next_run` and `engagement_dir`. It is ~20 lines; reading it
directly is fine and is the only file you read per cycle. Then repeat:

### 4a. Spawn the cycle agent

One `general-purpose` agent. Its prompt is short, because the brief lives on disk:

> Read `<skill-dir>/reference/cycle-agent.md` and follow it exactly.
> `TARGET=<abs target>` `ENGAGEMENT=<abs engagement dir>` `RUN=<N>`.
> Return only the JSON object that brief specifies.

Do not paste the brief's contents into the prompt. Do not add findings guidance of
your own — the brief and `security-audit` own the methodology.

### 4b. Commit the result

When the agent returns, run:

```bash
python3 <skill-dir>/scripts/audit_state.py commit --engagement <dir> --run <N>
```

This reads `run-N/findings.json` **so you don't have to**, counts confirmed and
medium-or-higher findings, dedups against every prior run, appends to the index,
advances the convergence counter, writes the per-cycle log line, and returns the
decision as JSON.

**Dedup is structural and deterministic.** A finding's identity is the set of sink
`file::scope` pairs in its `trace` — data the audit's own Phase 6 verifies against
source — not `root_cause` + `title` prose, whose wording drifts between runs. No
model judgment is involved, so nothing can bias the loop toward declaring
convergence it has not earned. Line numbers are excluded on purpose; they move when
unrelated code above them changes.

The residual error runs one way by design: one bug reachable through two sinks
counts as two findings, resets the counter, and buys another cycle. `max_cycles`
bounds that. Nothing would bound the opposite error.

### 4c. Act on the decision

- `"decision": "continue"` → go back to 4a with `next_run`.
- `"decision": "stop"` → go to §5. `status` is `converged` (two consecutive cycles
  added no new medium-or-higher findings) or `max-cycles-reached`. Carry which one
  into the report; they mean different things to a reader.

If a cycle agent returns `artifacts_ok: false`, commit it anyway — a run with no
parsable findings is a valid zero-new cycle, is recorded in the log, and surfaces
as a caveat in the report. Do not retry the cycle; that is what the next cycle is.

---

## §5. Stop — build the report, then verify it

Two agents, in order. Neither one's working material touches your context.

**Report builder** — one `general-purpose` agent:

> Read `<skill-dir>/reference/report-agent.md` and follow it exactly.
> `ENGAGEMENT=<dir>` `SKILL_DIR=<skill-dir>` `DESIGN_SYSTEM=<dir or "bundled SaaS
> Pro">` `STOP_REASON=<converged|max-cycles-reached>`.
> Return only the JSON object that brief specifies.

It fans out one extractor per run internally, so a five-run engagement does not
serialise.

**Verifier** — one `general-purpose` agent, after the builder returns:

> Read `<skill-dir>/reference/verify-agent.md` and follow it exactly.
> `REPORT_PATH=<path>` `ENGAGEMENT=<dir>` `EXPECTED=<the builder's JSON>`.
> Return only the JSON object that brief specifies.

If it returns `verified: false` with a non-empty `blocking`, say so plainly in the
handoff. **Do not certify a report the verifier would not.**

Then set the ledger to `status: done` by hand — it is the one field the script does
not own, because "the report exists and was verified" is not something the counting
logic can know.

### Hand off

Report: the path, the per-run and per-severity tally, how many cycles ran and why
the loop stopped, and what the verifier exercised against the live page. Offer to
open it (`SendUserFile` with `display: "render"`).

---

## Resumption & edge cases

- **Resuming**: re-read `ledger.md` first and trust it over context. `running` →
  continue from `next_run`. `done` → the engagement is complete; offer to reopen the
  report or start a fresh one. This works after a crash, a compaction, or a new
  session, because no cycle state ever lived only in context.
- **A cycle finds nothing at all**: a valid zero-new cycle. Two in a row converge.
- **`findings.json` missing or malformed**: the script treats the run as zero
  confirmed findings, records the reason in the per-cycle log, and continues.
  Verify the behaviour with `python3 scripts/audit_state.py selfcheck`.
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
