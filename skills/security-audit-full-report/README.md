<div align="center">

# security-audit-full-report

**A Claude Code skill that audits a codebase over and over until a cycle stops finding anything new, then merges every run into one interactive HTML report.**

<!-- pd:badges start -->
[![License: MIT](https://img.shields.io/badge/License-MIT-5B5FEF.svg)](../../LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-skill-23265E)](SKILL.md)
[![Orchestrates](https://img.shields.io/badge/orchestrates-security--audit-EF4458)](https://github.com/cloudflare/security-audit-skill)
[![Loop](https://img.shields.io/badge/loop-until_convergence-23265E)](#how-it-works)
[![Output](https://img.shields.io/badge/output-one_HTML_report-2ECC9A)](assets/template.html)
<!-- pd:badges end -->

<!-- pd:viz name="hero" src=".prettydocs/src/hero/" facts-hash="6c3c781c20090054ed7edc1e353af6ab896b8877461d034522c05cabc3afe7fd" src-hash="9a09abc21dcb1ee37a81ace7a53eb02896729f1d340db0fd112ec788f0e096b6" -->
<div align="center">
<img src="docs/assets/hero.svg" alt="An animated board showing one engagement. Four cycle cards run left to right, one security-audit run each, lit in turn. Run 1 and run 2 each add more than zero new medium-or-higher findings, so the convergence counter resets to zero both times. Run 3 adds none and the counter reaches one; run 4 adds none and the counter reaches two. A dark stop card on the right states the rule the ledger applies: stop when the counter reaches two consecutive zero-new cycles, or when the run number reaches max_cycles. Either way the loop ends and one consolidated report is written once, at the stop — every run merged into a single HTML file that stays filterable by run, with every claim traced back to that run's findings.json and the page built from the bundled assets/template.html." width="820" />
</div>
<!-- pd:viz end -->

</div>

## What this is

`security-audit-full-report` is an agent skill for Claude Code. It runs a **repeated** security assessment against a codebase and produces one shareable HTML report. Ask for "an iterative security audit", "keep auditing until it's clean", or invoke `/security-audit-full-report`, and it drives the underlying [`security-audit`](https://github.com/cloudflare/security-audit-skill) skill once per cycle — each cycle targeting the gaps the earlier ones left — until findings converge or a cycle budget is reached, then merges every run into a single consolidated report.

The skill is an **orchestrator**: it does not re-implement the hunting or the report rendering. `security-audit` does the actual vulnerability discovery; the report step is a folded-in copy of the `generate-cf-secaudit-report` workflow, with that skill's `template.html` bundled here so the whole thing stays self-contained and portable across teams.

It is also **stateful and resumable**. All finding data lives on disk under the engagement directory (`run-N/`, `ledger.md`), never only in context, so an engagement survives compaction and can be picked up after an interruption.

## The context contract

The session you invoke this from holds **the ledger and nothing else**.

That is a deliberate design, not a side effect. `security-audit` fans out 8–12 hunters, a validator per attack surface, and a verifier per finding — but by its own written design *"subagents do NOT write files — they return results to you"*. Run it inline and you absorb every one of those returns, on top of roughly 67 KB of skill text per cycle before a single agent reports. Five cycles of that fills any context window.

So every heavy step runs in a delegated agent with a cold context and a fixed return contract:

| Step | Runs in | Comes back as |
| --- | --- | --- |
| One audit cycle | agent briefed by `reference/cycle-agent.md` | 5 fields |
| Counting and cross-run dedup | `scripts/audit_state.py` | 9 fields |
| Building the report | agent briefed by `reference/report-agent.md` | 6 fields |
| Verifying the rendered report | agent briefed by `reference/verify-agent.md` | 6 fields |

The brief files are passed **by path** and never read by the orchestrator — the brief is for the agent. Same for every `findings.json`, every `REPORT.md`, and the report template.

This works because nested fan-out works: a subagent can spawn its own concurrent sub-agents and can invoke a skill, so a cycle agent runs `security-audit` and lets it fan out normally. Cycle agents must be spawned as `general-purpose` — `Explore` and `Plan` are declared without the `Agent` tool, and an audit inside one collapses to serial single-context hunting.

There is no `/loop`, deliberately. `/loop` re-injects this skill body and the whole `security-audit` stack on every firing and keeps every cycle in one accumulating context. Cycles are driven directly instead — spawn, commit, decide — and `ledger.md` supplies the resumability `/loop` was carrying.

> [!IMPORTANT]
> The [`security-audit`](https://github.com/cloudflare/security-audit-skill) skill must be installed — it is the engine this skill drives. On the first run, if it is missing, the skill offers to install it and then stops so you can reload skills. Nothing is audited until it is present.

## How it works

The skill has a **two-mode contract**, decided by whether today's engagement directory already exists:

<!-- pd:viz name="two-mode" src=".prettydocs/src/two-mode/" facts-hash="52bc908ecea92b9cd870f686591323368d9ae6cf1d8373de4cd5cf4d2f6080e2" src-hash="7c5695f5f664ef7821a6a1f184a9b8e2cf5ff4f0877b2245405c427be0bfe048" -->
<div align="center">
<img src="docs/assets/two-mode.svg" alt="Two mode cards side by side. Every invocation reads ledger.md first and picks its mode from what it finds. With no ledger, the skill enters preflight mode, which runs once with the user present and covers sections 1 to 3: check that the security-audit skill is installed, offer to add .audit/ to .gitignore, create the engagement directory and write ledger.md, then state the cycle budget and begin. With a ledger whose status is running, it enters cycle mode, which never asks a question because the user may be away, and covers sections 4 and 5: spawn a cold agent that runs one full security-audit into run-N, commit that run so the state script counts and dedups it and returns a decision, continue to the next cycle or stop, and at the stop build the report and verify it against the live page — each of those four steps rippling in turn because cycle mode is the half that repeats. A band underneath carries the ledger's own status values: running, then converged or max-cycles-reached, then done." width="820" />
</div>
<!-- pd:viz end -->

- **Preflight** is the only mode allowed to ask questions. It verifies `security-audit` is installed, offers to add `.audit/` to `.gitignore`, creates the dated engagement directory, writes `ledger.md`, states the cycle budget, and begins.
- **Cycle mode** runs unattended. It spawns one cold agent to run a single audit into `run-N/`, commits that run through `audit_state.py` — which counts how many confirmed medium-or-higher findings are genuinely new and updates the convergence counter — and decides whether to continue.
- **Convergence** is reached when two consecutive cycles add zero new medium-or-higher findings, or when `max_cycles` is hit — whichever comes first. Either way the final report is generated once, at the stop.

Because questions are confined to preflight, no cycle can ever block on a prompt. Any decision that could stall a cycle must be answered during the first, human-present invocation.

## Cross-run deduplication

Each confirmed finding is keyed by the set of sink `file::scope` pairs in its `trace`, and checked against `findings-index.json`. A finding counts as **new** only if that sink is not already recorded. This is the correctness backbone: even when a cycle re-hunts ground an earlier cycle covered, the overlap is absorbed here and the convergence counter still advances soundly. Overlap between runs is expected, not exceptional.

The key is **structural and deterministic** — it comes from trace data the audit's own Phase 6 verifies against source, not from `root_cause` and `title` prose whose wording drifts between runs. No model judgment is involved, so nothing can bias the loop toward declaring a convergence it has not earned. Line numbers are excluded on purpose: they move whenever unrelated code above them changes.

The residual error runs one way by design. One bug reachable through two different sinks counts as two findings, which resets the counter and buys another cycle; `max_cycles` bounds that cost. Nothing would bound the cost of erring in the opposite direction.

## Usage

Inside Claude Code:

```text
/security-audit-full-report
/security-audit-full-report ./services/api
/security-audit-full-report ./services/api 8
run the security vuln report and keep auditing until it converges
```

The invocation accepts three positional arguments, all optional:

| Argument | Meaning | Default |
| --- | --- | --- |
| `target-dir` | The codebase to audit | current working directory |
| `max-cycles` | Hard cap on audit cycles before stopping | `5` |
| `design-system-dir` | A design system whose tokens style the report | bundled **SaaS Pro** |

## The report

The consolidated report is one interactive HTML file built from [`assets/template.html`](assets/template.html). It is **data-driven** — severity counts, KPIs, the donut, and every filter count are computed from a `F[]` findings array at runtime, so the numbers stay internally consistent no matter how many runs are merged.

| Element | What it shows |
| --- | --- |
| KPI hero | Total confirmed findings and severity breakdown, numbers first |
| Severity donut | High / Medium / Low proportions across all runs |
| Run filter | One button per run, labeled by its scope; view all runs or one alone |
| Finding cards | Attacker, broken trust boundary, description, fix, key file/symbol refs |
| Verified-clean grid | Areas checked and found sound |

Every claim traces to a run's `findings.json` (the source of truth) or `REPORT.md`; only `confirmed` findings appear. The report is verified against the live rendered page — cards expanded, severity filters clicked, console checked — before handoff, never certified from a green build alone.

## Engagement layout

State for one engagement lives under the target repo:

```
<target>/.audit/<YYYYMMDD>/
├── ledger.md                        durable source of truth (status, counter, findings)
├── run-1/
│   ├── findings.json                authoritative findings for the run
│   ├── REPORT.md                    exec summary, themes, recommendations
│   ├── FINDINGS-DETAIL.md
│   └── architecture.md
├── run-2/ …                         one dir per cycle
└── security-audit-<YYYYMMDD>.html   the consolidated report
```

The date stamps the *engagement*, not each run, so a loop that crosses midnight stays in one directory. On any invocation the skill re-reads `ledger.md` first and trusts it over context: `running` continues from the next cycle, `done` offers to reopen the report or start fresh.

## Requirements

- **Claude Code** with the [`security-audit`](https://github.com/cloudflare/security-audit-skill) skill installed (the skill offers to install it on first run).
- **`python3`** — runs `scripts/audit_state.py` and serves the report locally for the verification pass. Standard library only; no third-party packages.
- A browser tool for that verification pass.

No third-party Python packages; the report template has no external dependencies.

## Project structure

```
skills/security-audit-full-report/
├── SKILL.md              the orchestrator contract — the only file the primary session loads
├── README.md             this file
├── reference/            agent briefs, passed by path and never read by the orchestrator
│   ├── cycle-agent.md    run one security-audit cycle, return 5 fields
│   ├── report-agent.md   merge every run into the HTML report, return 6 fields
│   └── verify-agent.md   drive the rendered report, return 6 fields
├── scripts/
│   └── audit_state.py    ledger, structural dedup, convergence decision (stdlib only)
├── assets/
│   └── template.html     the consolidated report template (SaaS Pro, data-driven)
└── docs/assets/
    ├── hero.svg          the cycle, the stop rule, and the one report
    ├── two-mode.svg      preflight versus cycle mode
    └── src/              the frozen design system, and a manifest per visual
```

## Related skills

- [`security-audit`](https://github.com/cloudflare/security-audit-skill) — the single-run vulnerability hunter this skill loops. Use it directly for a one-shot audit.
- `generate-cf-secaudit-report` — turns an existing audit directory into a styled report. Its workflow is folded into this skill's §5 and its template is bundled in `assets/`. That copy can drift from the source; [SKILL.md](SKILL.md) records the sync point.

This skill is the end-to-end orchestrator of both.

## Testing

The convergence logic has a runnable self-check — the part where a silent bug would be least visible, because a wrong counter just ends the engagement early and looks like success:

```bash
python3 scripts/audit_state.py selfcheck
```

It asserts the whole decision path against synthetic runs: rejected findings excluded, duplicate sinks collapsed within a run, the same bug reworded across runs counted as known, a missing or malformed `findings.json` treated as a valid zero-new cycle rather than a crash, a genuinely new sink resetting the counter, and both stop conditions (`converged` and `max-cycles-reached`) firing where they should.

Everything above that line rests on two guarantees rather than tests: the structural cross-run dedup (so the convergence decision is sound even when runs overlap), and the mandatory verification pass over the rendered report — hero, KPIs, donut, an expanded card, a live severity filter, and the console — before any handoff.

## Documentation

- [SKILL.md](SKILL.md) — the full agent-facing contract: the two-mode workflow, preflight steps, cycle logic, convergence rule, and the folded-in report workflow.
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — how to propose a change to this collection.

## License

Released under the [MIT License](../../LICENSE) of the repository that ships it.

<!-- pd:footer start -->
<div align="center">
<br/>

**Copyright © 2026 Zerø Effort. Released under the MIT license.**

</div>
<!-- pd:footer end -->
