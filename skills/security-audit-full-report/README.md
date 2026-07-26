<p align="center">
  <img src="docs/assets/hero.svg" width="100%" alt="security-audit-full-report — a Claude Code agent skill that loops a security audit until findings converge, then merges every run into one consolidated interactive HTML report">
</p>

<div align="center">

<!-- update-docs:badges start -->
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-agent_skill-5B5FEF)](SKILL.md)
[![Orchestrates security-audit](https://img.shields.io/badge/orchestrates-security--audit-EF4458)](SKILL.md)
[![Loop until convergence](https://img.shields.io/badge/loop-until_convergence-F9A03F)](SKILL.md)
[![Output: single HTML report](https://img.shields.io/badge/output-single_HTML_report-2ECC9A)](assets/template.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-5B5FEF.svg)](../../LICENSE)
<!-- update-docs:badges end -->

</div>

## What this is

`security-audit-full-report` is an agent skill for Claude Code. It runs a **repeated** security assessment against a codebase and produces one shareable HTML report. Ask for "an iterative security audit", "keep auditing until it's clean", or invoke `/security-audit-full-report`, and it drives the underlying [`security-audit`](SKILL.md) skill in a `/loop` — one audit per cycle, each targeting the gaps the earlier cycles left — until findings converge or a cycle budget is reached, then merges every run into a single consolidated report.

The skill is an **orchestrator**: it does not re-implement the hunting or the report rendering. `security-audit` does the actual vulnerability discovery; the report step is a folded-in copy of the `generate-cf-secaudit-report` workflow, with that skill's `template.html` bundled here so the whole thing stays self-contained and portable across teams.

It is also **stateful and resumable**. All finding data lives on disk under the engagement directory (`run-N/`, `ledger.md`), never only in context, so a loop survives compaction and can be picked up after an interruption.

> [!IMPORTANT]
> The [`security-audit`](https://github.com/cloudflare/security-audit-skill) skill must be installed — it is the engine this skill drives. On the first run, if it is missing, the skill offers to install it and then stops so you can reload skills. Nothing is audited until it is present.

## How it works

The skill has a **two-mode contract**, decided by whether today's engagement directory already exists:

```mermaid
flowchart TD
    Start(["/security-audit-full-report"]) --> Mode{"ledger.md exists,<br/>status: running?"}
    Mode -- "no" --> Pre["Preflight (interactive):<br/>check install, gitignore,<br/>create engagement, start loop"]
    Pre --> Loop["/loop re-invokes each cycle"]
    Mode -- "yes" --> Cycle["Cycle mode (unattended):<br/>run one security-audit,<br/>count new medium+ findings,<br/>update ledger.md"]
    Loop --> Cycle
    Cycle --> Decide{"converged or<br/>max cycles?"}
    Decide -- "no" --> Loop
    Decide -- "yes" --> Report["Merge all runs into one<br/>consolidated HTML report"]
    Report --> Done(["status: done"])
```

- **Preflight** is the only mode allowed to ask questions. It verifies `security-audit` is installed, offers to add `.audit/` to `.gitignore`, creates the dated engagement directory, writes `ledger.md`, and starts the self-paced loop.
- **Cycle mode** runs unattended each time `/loop` fires. It runs exactly one audit into `run-N/`, counts how many confirmed medium-or-higher findings are genuinely new, updates the convergence counter, and decides whether to continue.
- **Convergence** is reached when two consecutive cycles add zero new medium-or-higher findings, or when `max_cycles` is hit — whichever comes first. Either way the final report is generated once, at the stop.

Because questions are confined to preflight, no `/loop` firing can ever block on a prompt. Any decision that could stall a cycle must be answered during the first, human-present invocation.

## Cross-run deduplication

Each confirmed finding is keyed by its root cause plus title and checked against the accumulated list in `ledger.md`. A finding only counts as **new** if that issue is not already recorded. This is the correctness backbone: even if a cycle re-hunts ground a previous cycle already covered, the overlap is absorbed here and the convergence counter still advances soundly. Overlap between runs is treated as expected, not exceptional.

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
- **`python3`** — used only to serve the report locally for the visual-verification pass.
- A browser tool for that verification pass.

No third-party Python packages; the report template has no external dependencies.

## Project structure

```
skills/security-audit-full-report/
├── SKILL.md            the skill contract: two-mode workflow, loop, report steps
├── assets/
│   └── template.html   the consolidated report template (SaaS Pro, data-driven)
└── docs/assets/        README artwork (this page's hero)
```

## Related skills

- [`security-audit`](https://github.com/cloudflare/security-audit-skill) — the single-run vulnerability hunter this skill loops. Use it directly for a one-shot audit.
- `generate-cf-secaudit-report` — turns an existing audit directory into a styled report. Its workflow is folded into this skill's §5 and its template is bundled in `assets/`, kept in sync as of the date noted in [SKILL.md](SKILL.md).

This skill is the end-to-end orchestrator of both.

## Testing

There are no automated tests. Correctness rests on two other guarantees: the cross-run dedup keyed on root cause and title (so the convergence decision is sound even when runs overlap), and the mandatory visual-verification pass over the rendered report (hero, KPIs, donut, an expanded card, and a live severity filter) before any handoff.

## Documentation

- [SKILL.md](SKILL.md) — the full agent-facing contract: the two-mode workflow, preflight steps, cycle logic, convergence rule, and the folded-in report workflow.
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — how to propose a change to this collection.

## License

Released under the [MIT License](../../LICENSE) of the repository that ships it.

<!-- update-docs:footer start -->
<div align="center">
<br/>

**Copyright © 2026 Zerø Effort. Released under the MIT license.**

</div>
<!-- update-docs:footer end -->
