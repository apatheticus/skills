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

<!-- pd:viz name="hero" src=".prettydocs/src/hero/" facts-hash="06c60024da13fac9e6c9e181900ff9633cece6662580ed3051368e9d9d635ddb" src-hash="9a09abc21dcb1ee37a81ace7a53eb02896729f1d340db0fd112ec788f0e096b6" -->
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
| One audit cycle | agent briefed by `reference/cycle-agent.md` | 6 fields |
| Counting and cross-run dedup | `scripts/audit_state.py` | 9 fields |
| Building the report | agent briefed by `reference/report-agent.md` | 6 fields |
| Verifying the report | agent briefed by `reference/verify-agent.md` | 8 fields |

The brief files are passed **by path** and never read by the orchestrator — the brief is for the agent. Same for every `findings.json`, every `REPORT.md`, and the report template.

This works because nested fan-out works: a subagent can spawn its own concurrent sub-agents and can invoke a skill, so a cycle agent runs `security-audit` and lets it fan out normally. Cycle agents must be spawned as `general-purpose` — `Explore` and `Plan` are declared without the `Agent` tool, and an audit inside one collapses to serial single-context hunting.

**The boundary fails open, and it fails toward the session it protects.** An agent deep in the tree that reports with `SendMessage(to: "general-purpose")` is addressing a type rather than a name; delivery fails, and the harness promotes that agent's full report to the top-level session instead of dropping it — observed five times in one engagement, roughly 100k tokens of hunter reports. The containment rule is therefore carried in the prompt of every spawned agent, and propagated into the prompts `security-audit` writes for the agents it fans out, because a leak cannot be closed in a prompt you never wrote. Everything below reports by returning, never by messaging.

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

A cycle is finished when the *system* says so, not when a notification arrives. That channel is unreliable in both directions: in one engagement a single cycle notified four times, and another notified not at all — it had already completed and the notification was lost, which would hang a loop that treats the notification as the trigger. So the orchestrator falls back to the run directory's own activity, and then to a one-line probe of the cycle agent, which is named for exactly that reason. Duplicate notifications are harmless because committing is idempotent.
- **Convergence** is reached when two consecutive cycles add zero new medium-or-higher findings, or when `max_cycles` is hit — whichever comes first. Either way the final report is generated once, at the stop.

Because questions are confined to preflight, no cycle can ever block on a prompt. Any decision that could stall a cycle must be answered during the first, human-present invocation.

### What it costs, and stopping early

The unit of cost is wall-clock, not agents. Measured on one mid-sized repository, cycles 1–3 took **2h 18m**, **~50m** and **~1h 50m**; at the default `max_cycles: 5` that is most of a working day. Preflight states the estimate before anything starts, because it is the one moment a user can still decline.

A long engagement is therefore **expected** to outlive the session that started it, and that costs nothing: all cycle state lives in `ledger.md` and on disk, so a session limit, a compaction or a crash resumes from the ledger. In the same engagement a session limit killed a cycle mid-flight; its artifact had already landed, only the agent's return was lost, and the run committed cleanly on resume.

Stopping early is an ordinary thing to do at that price, so it has a name of its own. The report's stop reason is read off the ledger and is one of `converged`, `max-cycles-reached`, or **`halted-by-operator`** — never forced into one of the first two, because `converged` claims a completeness that was never established and `max-cycles-reached` claims a budget that was never spent. Anything but `converged`, or any cycle whose candidates were never adjudicated, puts a **completeness banner** above the findings saying they are a floor rather than a total. The same sentence leads the handoff, since that is what the user actually reads.

## Cross-run deduplication

Each confirmed finding is keyed by its attack path's endpoints — the entrypoint and sink `file::scope` pairs in its `trace`, each tagged with which it is — and checked against `findings-index.json`. A finding counts as **new** only if that path is not already recorded. This is the correctness backbone: even when a cycle re-hunts ground an earlier cycle covered, the overlap is absorbed here and the convergence counter still advances soundly. Overlap between runs is expected, not exceptional.

The key is **structural and deterministic** — it comes from trace data the audit's own Phase 6 verifies against source, not from `root_cause` and `title` prose whose wording drifts between runs. No model judgment is involved, so nothing can bias the loop toward declaring a convergence it has not earned. Line numbers are excluded on purpose: they move whenever unrelated code above them changes.

**The sink alone is not an identity, and treating it as one was a real bug.** Keying on the sink assumes one defect per scope, and a function can hold several. Across 50 confirmed findings from one engagement, five pairs of genuinely distinct defects — different root causes, different remediations — collapsed onto a single sink key, and the lower-severity one was silently absorbed every time. Including the entrypoint separates most of them, because two defects in one scope are usually reached from different entry points. Propagation steps stay out, and that is measured rather than assumed: adding them separates nothing further and *creates* a collision, because one finding's entrypoint can be another's propagation step.

Two flanking rules cover what no path-derived key can do, since two defects can share a path. Deduplication is **across runs only** — two findings in one run that share a key are kept as two, because a run's `findings.json` is a set the audit has already adjudicated. And **every cross-run suppression is named in the ledger**, with both titles and the key, because that is the one place a real finding can leave the engagement without anyone seeing it go.

The residual error in the key then runs one way. One bug reachable through two different paths counts as two findings, which resets the counter and buys another cycle; `max_cycles` bounds that cost. Nothing would bound the cost of erring in the opposite direction.

That argument covers the key alone, so two further guards cover the ways a counter could advance without a cycle earning it. **Committing a run is idempotent** — a repeat is a no-op that changes nothing — because the harness sometimes fires a completion notification more than once, and an unguarded repeat would score zero new against an index that already holds the run. And **a cycle that stopped before adjudicating is committed as unvalidated**, which records the run and leaves the counter alone. An audit that ran and found nothing is evidence toward convergence; an audit that died before validating anything is evidence of nothing, and scoring the second as the first turns a crash into a clean bill of health.

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
| Severity donut | Critical / High / Medium / Low / Informational proportions across all runs |
| Run filter | One button per run, labeled by its scope; view all runs or one alone |
| Finding cards | Attacker, broken trust boundary, description, fix, key file/symbol refs |
| Verified-clean grid | Areas checked and found sound |

It ships **all five severity tiers** `report-schema.json` permits, wired through one table that drives the KPI tiles, the donut, the legend, the card badges and the filter bar together, so a tier is never half-added. A tier with no findings hides its own tile and filter button rather than showing a zero, which keeps the visible tiles summing to the stated total. That is not a cosmetic choice: the template previously shipped three tiers, and a real report was published with tiles summing to 49 against a stated 50 because a hand-added tier reached four of those five surfaces and missed the KPI row.

Every claim traces to a run's `findings.json` (the source of truth) or `REPORT.md`; only `confirmed` findings appear.

### How the report is verified

**Verification targets what varies, which is the data and not the template.** The template's behaviour — the tier table, the donut, the filters, the badges — is fixed and was proved by rendering three fixtures: all five tiers, two tiers, and zero findings. Clicking a severity filter on every engagement re-tests code that cannot have changed since. What an agent transcribes fresh each time is the `F[]` array, so that is what gets reconciled: no unreplaced placeholders, every `sev` one of the five exactly, no `undefined`, and the array's own tally matched against the report builder's returned counts.

**Then the page is rendered exactly once, because static checks cannot prove the script ran.** A finding title containing `</script>` yields a file that parses fine and renders with no findings on it — a data defect the template cannot defend against and grep cannot see. One `chrome-headless-shell --dump-dom` on the `file://` URL returns the post-script DOM, and the rendered numbers, the visible-tile sum, the run coverage and the console all come off that single invocation. No Playwright, no MCP browser, no `chrome-for-testing` install, no local HTTP server.

**With no headless Chrome on the machine, the pass says so rather than failing or faking it** — `render_checked: false`, and the orchestrator repeats that caveat in the handoff. The data reconcile is still a real result; it just is not proof the page executes, and those are reported as two separate fields on purpose. Earlier versions assumed a browser stack that was not there, which verified nothing at all.

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
- **`python3`** — runs `scripts/audit_state.py`. Standard library only; no third-party packages.
- **Optional:** any headless Chrome already on the machine — `chrome-headless-shell`, a Playwright cache, or Google Chrome itself. The verification pass renders the report once through `--dump-dom` to prove the page executes. Without one it reconciles the data and says the render did not happen; it never installs a browser, and it needs neither Playwright nor a local HTTP server.

No third-party Python packages; the report template has no external dependencies.

## Project structure

```
skills/security-audit-full-report/
├── SKILL.md              the orchestrator contract — the only file the primary session loads
├── README.md             this file
├── reference/            agent briefs, passed by path and never read by the orchestrator
│   ├── cycle-agent.md    run one security-audit cycle, return 6 fields
│   ├── report-agent.md   merge every run into the HTML report, return 6 fields
│   └── verify-agent.md   reconcile the report's data, render it once, return 8 fields
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

It asserts the whole decision path against synthetic runs: rejected findings excluded, two findings sharing a sink but reached from different entrypoints counted as two, the same bug reworded across runs counted as known, a missing or malformed `findings.json` treated as a valid zero-new cycle rather than a crash, a genuinely new path resetting the counter, and both stop conditions (`converged` and `max-cycles-reached`) firing where they should. Four of its assertions guard the counter against advancing on something other than a cycle: committing the same run twice changes neither the counter nor the index, an unvalidated commit records the run while leaving the counter where it was, two findings sharing a path within one run are kept as two, and an index keyed by an older `finding_key` is refused rather than recounted from scratch.

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
