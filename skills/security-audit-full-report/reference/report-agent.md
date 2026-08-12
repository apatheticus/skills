# Report-builder brief

You build the **one** consolidated HTML report for a finished engagement. You were
spawned with a cold context so that reading every run's findings and filling a
27 KB template happens here and not in the orchestrating session.

That session gets back the JSON object at the bottom of this file. It will not read
the findings, the template, or the report. Everything else stays with you.

> **Provenance.** This brief is a deliberate in-lined copy of the
> `generate-cf-secaudit-report` workflow, and `assets/template.html` is a copy of
> that skill's template. This keeps the parent skill self-contained and portable —
> it works on a machine that has never installed the report skill, which matters
> because the skill is shared across teams. The cost is drift: if the source
> skill's workflow or template improves, this copy goes stale silently. Synced as
> of **2026-07-15**. If that skill's `template.html` or workflow has changed since,
> re-sync both this file and `assets/template.html` from it rather than editing
> them in isolation.

## Your inputs

| Name | Meaning |
|---|---|
| `ENGAGEMENT` | absolute path of `<target>/.audit/<YYYYMMDD>/` |
| `SKILL_DIR` | absolute path of this skill, so you can find `assets/template.html` |
| `DESIGN_SYSTEM` | a design-system dir, or the string `bundled SaaS Pro` |
| `STOP_REASON` | `converged`, `max-cycles-reached`, or `halted-by-operator` |

Accuracy outranks polish throughout. A security reader must be able to trust every
number and every path.

**The report file is a deliverable, so write it.** A guard against agents writing
unsolicited report/summary `.md`/`.html` files may sit in front of the copy in §4.
It has a deliverable exception, and this page is the declared output contract of
the skill that spawned you — not a write-up of your own work — so the exception
applies. A cycle agent in one engagement read that guard as a wall and discarded
its run report; do not repeat it here, where nothing else carries the output.

## 1. Inventory, then fan out

List `ENGAGEMENT` and every `run-N/`. Each run has `findings.json` (source of
truth), `REPORT.md` (exec summary, themes, verified-clean notes, recommendations),
`FINDINGS-DETAIL.md` and `architecture.md`.

**Do not read them all yourself.** Spawn **one `general-purpose` agent per run**,
all in a single message so they run concurrently. Give each agent one run
directory and §2's extraction rules, and have it return that run's findings as a
JSON array — nothing else. You assemble; they extract.

A run whose `findings.json` is missing or malformed contributes zero findings. Note
it and carry on; it is already recorded in `ledger.md`'s per-cycle log, and it must
appear as a caveat in the final report rather than silently reducing the count.

## 2. Extraction rules — put these in every per-run agent's prompt

Trace every claim to `findings.json` / `REPORT.md`. Do not invent or shift
severities, attackers, paths, or counts. If the two disagree, prefer
`findings.json` and note the discrepancy.

Include **only** `verdict: "confirmed"` findings. Count the `rejected` ones and
return the count separately — a report that says how many candidate findings were
killed is more trustworthy, not less.

For each confirmed finding return:

| Field | From |
|---|---|
| `run` | the run number |
| `id` | preserve the original id where one exists |
| `sev` | `severity.overall_severity`, lowercase, verbatim — one of `critical`, `high`, `medium`, `low`, `informational`. Never fold a tier into a neighbour |
| `title` | `title` |
| `attacker` | `execution.attacker_perspective` |
| `boundary` | the trust boundary or invariant broken — from `root_cause` / `intended_behavior` |
| `desc` | a faithful 2–4 sentence condensation. Condense; never paste raw JSON |
| `fix` | `remediation.strategy` |
| `files` | array of key `file` / `scope` refs from `trace` |

## 3. The one rule that matters most — include every run

An engagement with several runs is **one** report, not several. Each run
deliberately covered ground the others did not; merging them is the only complete
picture. Combine severity counts across runs, tag each finding with its run of
origin, and expose a run filter so a reader can still view one run alone. Never
drop a run, and never emit one file per run.

Cross-run duplicates are already resolved on disk: `findings-index.json` holds one
record per distinct finding, keyed structurally by the entrypoint and sink
`file::scope` pairs of its attack path. Use it to
decide which findings are the *same* finding seen twice — show such a finding once,
tagged with every run that found it, rather than as N separate cards.

## 3a. Completeness — the report must not overstate its own coverage

**`converged` is the only stop reason that is evidence of coverage.** Every other
one means the engagement stopped for a reason unrelated to the codebase being
clean, and a reader who misses that will read a floor as a ceiling.

| `STOP_REASON` | What it means | What it is not |
|---|---|---|
| `converged` | two consecutive adjudicated cycles added no new medium-or-higher findings | still not a proof of absence |
| `max-cycles-reached` | the cycle budget ran out, with the loop still finding new ground | not evidence the loop was finished |
| `halted-by-operator` | a human stopped the engagement before either condition | says nothing at all about coverage |

Then check the ledger yourself rather than trusting the value you were handed —
`ENGAGEMENT/ledger.md` is short, and its per-cycle log is the primary record. Two
things there make an engagement **incomplete** independently of why it stopped:

- a log line beginning `run N: UNVALIDATED` — that cycle's hunters ran but nothing
  adjudicated their candidates, so its findings are absent rather than zero;
- a `run-N/` directory holding candidate files but no parsable `findings.json`.

**Whenever the stop reason is not `converged`, or any run is incomplete, the page
carries a completeness banner** — at the top of the executive summary, before any
count, in the report's own voice and not a footnote:

> This assessment stopped at N of M planned cycles because *&lt;reason&gt;*. Run K's
> candidate findings were never validated. **The findings below are a floor, not a
> total** — the assessment was still surfacing new medium-or-higher issues when it
> stopped, and unexamined areas remain.

Fill in the real numbers, drop the sentences that do not apply, and drop the
"still surfacing" clause if the last adjudicated cycle genuinely added nothing.
Never soften it to "the assessment is ongoing". Also add one entry to `caveats`
per incomplete run, so the orchestrator can repeat it in the handoff.

## 4. Fill the template

Copy `SKILL_DIR/assets/template.html` to
`ENGAGEMENT/security-audit-<YYYYMMDD>.html`, then populate it. The template is
**data-driven** — severity counts, KPIs, the donut and every filter count compute
from the `F[]` array at runtime, so you never hand-count anything. That is what
keeps a multi-run report internally consistent.

Populate:

- **`F[]`** — one object per confirmed finding, ordered critical→informational
  then by run.
- **`{{PLACEHOLDER}}` tokens** — project name, target slug, report date, scope
  blurb, the seven `{{KPI_*_SUB}}` sub-labels, `{{CLEAN_COUNT}}`,
  executive-summary HTML, theme cards,
  run-filter buttons, verified-clean items, recommendations, footer.
- **Run filter** — one `<button data-run="N">` per run, labelled by scope (e.g.
  "Run 1 · Web/API"). With only one run, delete the whole `data-group="run"`
  toolbar group; the template already hides per-card run tags in that case.
- **Severity tiers — touch nothing.** The template ships all five tiers
  `report-schema.json` permits, wired through one `SEV` table that drives the KPI
  tiles, the donut, the legend, the card badges and the filter bar together. A
  tier with no findings hides its own tile and filter button, so the visible tiles
  always sum to the stated total. **Do not add, delete or restyle a tier by hand**
  — that is what this replaced. A real report was published with tiles summing to
  49 against a stated 50 because a hand-added tier reached four of those five
  surfaces and missed the KPI row.
- **Stop reason** — state it in the executive summary, with §3a's completeness
  banner above it whenever the reason is not `converged` or any run is incomplete.

Delete the template-notes HTML comment and any example `F[]` entries.

**Design-system fidelity.** The template's `:root` is the bundled **SaaS Pro**
system, self-contained, needing no external directory. Only if `DESIGN_SYSTEM`
names a real directory, re-derive the `:root` block from its `tokens/*.css` and
adjust component colours per its `DESIGN.md` — never invent token values.
Otherwise use the bundled tokens as they are.

Keep the house rules: numbers-first KPIs as the hero; two card worlds (white light
cards for KPIs, summary and findings; dark navy cards for the donut and the
verified-clean grid — no third style); semantic colour is status only
(High→danger, Medium→warning, Low→info; gradients are identity, not status; never
pure grey or black); soft-physics shadows and radii; honour
`prefers-reduced-motion`, which is already wired.

## 5. Return

Do not verify the rendered page — a separate agent does that. Return **exactly**:

```json
{
  "report_path": "/abs/path/.audit/20260811/security-audit-20260811.html",
  "runs": 4,
  "findings_total": 17,
  "by_severity": {"critical": 0, "high": 4, "medium": 9, "low": 4},
  "rejected_count": 11,
  "caveats": []
}
```

`caveats` lists anything a reader must know that the page cannot state itself — a
run with no parsable findings, a `REPORT.md` that disagreed with its
`findings.json`. Empty array when there are none.
