<div align="center">

# reflect

**A Claude Code skill that reads your past sessions and hands back a ranked, evidence-backed diagnosis of your setup — as a single interactive HTML report.**

<!-- pd:badges start -->
[![License: MIT](https://img.shields.io/badge/License-MIT-4A4AE8.svg)](../../LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-skill-12142B)](SKILL.md)
[![Invoke](https://img.shields.io/badge/invoke-%2Freflect-3B36D6)](#usage)
[![Output](https://img.shields.io/badge/output-interactive_HTML-12142B)](#what-you-get)
[![Data](https://img.shields.io/badge/data-100%25_local-15714F)](#privacy-and-guardrails)
<!-- pd:badges end -->

<!-- pd:viz name="hero" src=".prettydocs/src/hero/" facts-hash="5ebfafd6760d4ed6f86744530184d0cbaa15df53f892ab06555d4f41416b0330" src-hash="8c61f07068b9fed44f4283ad2265b6be4dd97ea40bf8a4533c34d96dc696082d" -->
<div align="center">
<img src="docs/assets/hero.svg" alt="An animated board: two frosted glass panes over a slowly drifting field of indigo and blue, the same look as the report the skill produces. The upper pane carries the wordmark and the promise. The lower one frames the raw material — the session transcripts already under ~/.claude/projects that fall inside the window, with the session running the pass excluded from its own corpus, and every one of them scored by triage from cheap metadata before any agent runs, so effort goes where the friction is. Below the panes, three cards are marked in turn, left to right. The first, extract, pulls signals in four families — friction and failure, repetition and missed automation, wins and effective patterns, environment gaps — every one cited with a session ID and a verbatim quote. The second, cluster, merges and dedupes those signals across sessions. The third is dark rather than light, because it is the card that states numbers: a cluster only earns a verdict when enough distinct sessions back it, three for a new skill and two for an automation or a fix." width="820" />
</div>
<!-- pd:viz end -->

</div>

> [!IMPORTANT]
> `reflect` is **diagnosis only** and **fully local**. It reads your transcripts, writes one HTML report, and changes nothing else — no skills, hooks, or config are created on your behalf. Your session data never leaves your machine.

## What this is

`reflect` mines the Claude Code session transcripts already on your disk (`~/.claude/projects/`) and produces a ranked read on how you actually work with Claude Code: what's paying off, what keeps going wrong, and which changes to your setup would help most.

It runs the raw sessions through parallel sub-agents that pull out concrete signals — every one tied to a session ID and a verbatim quote — clusters those signals across sessions, and turns each recurring cluster into a decision: build a skill, add an automation, change a habit, or keep doing what works. The result is one self-contained HTML file you can open offline, today or years from now.

Recommending the changes **is** the deliverable. `reflect` never implements what it suggests — it diagnoses, ranks, and cites the evidence, and leaves the acting to you.

## What you get

A single interactive HTML report at `<cwd>/Outputs/Reflections/cc-reflection-<date>.html`:

- A ranked assessment, highest leverage first, that drills down from an executive summary to per-cluster evidence — verbatim quotes, session IDs, and project paths.
- Custom inline SVG graphics throughout — hand-built charts for every number, explanatory diagrams, and decorative polish. No chart libraries, no raster images, no external requests.
- An embedded machine-readable summary block, so the next run can diff against this one and show what you adopted, what still recurs, and what's new.
- A dedicated section for your `focus`, when you pass one.

The report is styled with the bundled **SaaS Pro** design system (see [reference/design-system/](reference/design-system/)) and opens straight from `file://`.

## How it works

`reflect` runs six phases, numbered 0 through 5. The heavy extraction stage fans out across many sub-agents through the Workflow tool; everything a session touches stays local.

<!-- pd:viz name="pipeline" src=".prettydocs/src/pipeline/" facts-hash="8862876d778e86f3577ab83da43ae01334086acdd480d717ba6628520f14e7e3" src-hash="e4fb539ecb169c18b1ae7853bc02f931010123d23e2ecc525c5f773dda13b77b" -->
<div align="center">
<img src="docs/assets/pipeline.svg" alt="A frosted glass pane over a slowly drifting field of indigo and blue carries the heading; below it six cards, read left to right and top to bottom, each marked in turn as the pass moves through them. Phase 0 scopes the corpus: enumerate the in-window transcripts and load the prior report so this run can be diffed against it. Phase 1 is the insights gate, and it gates on recency rather than coverage, because /insights samples a few hundred recent sessions instead of the whole corpus. Phase 2 triages, scoring every session from cheap metadata before any agent is spent. Phase 3 extracts: fan out over batched transcripts, cluster the signals, decide a verdict per cluster, then corroborate against the /insights data. Phase 4 renders one self-contained HTML file with inline SVG and no external requests, drawn as a small dark thumbnail because the report states its own numbers on dark data cards. Phase 5 delivers that file with a summary of the top findings and anything the run had to skip. Nothing leaves the machine, and nothing is built — recommending the change is the deliverable." width="820" />
</div>
<!-- pd:viz end -->

| Phase | What happens |
| --- | --- |
| 0 · Scope | Enumerate in-window transcripts (the current session is excluded), and load the most recent prior report for trend diffing. |
| 1 · Insights gate | Check that `/insights` data is fresh enough to corroborate; if it's stale, pause and ask before proceeding. |
| 2 · Triage | Score every in-window session from cheap metadata so agent effort goes where the friction is. |
| 3 · Extraction | Fan out over batched transcripts, extract schema-enforced signals, cluster them, decide a verdict per cluster, then cross-check against `/insights`. |
| 4 · Report | Render the single self-contained HTML file with inline SVG charts and the embedded summary block. |
| 5 · Deliver | Surface the report and a TL;DR of the top recommendations, naming anything the run had to skip. |

## What it looks for

Every extractor reads its transcripts through four signal families:

| Signal family | What it captures |
| --- | --- |
| Friction & failure | Errors, retries, interruptions, and dead ends. |
| Repetition & missed automation | The same manual thing done over and over. |
| Wins & effective patterns | What worked and is worth repeating. |
| Environment gaps | Missing skills, permissions, or configuration. |

Each cluster then earns a verdict, gated on how many distinct sessions back it — recurrence beats cleverness:

| Verdict | Meaning | Evidence bar |
| --- | --- | --- |
| `new-skill` | A recurring pattern worth turning into a skill. | ≥ 3 distinct sessions |
| `automation` | A hook, setting, or cron that removes the toil. | ≥ 2 sessions |
| `fix` | A config, prompt, or habit change. | ≥ 2 sessions |
| `keep-doing` | A win worth codifying so it sticks. | a cited win |
| observation | Noted, but below the action threshold. | under threshold |

## Usage

Invoke the skill from any project directory — the report lands under that directory's `Outputs/`.

```text
/reflect [window] [focus]
```

Both arguments are optional and order-independent:

| Argument | Values | Default | Effect |
| --- | --- | --- | --- |
| Window | `30d`, `Nd`, `all` | `30d` | Sessions whose transcript falls inside the window are in scope. |
| Focus | any free text | none | Extractors dig deeper on matching sessions, and the report gives the focus its own section. |

### Examples

```text
/reflect
/reflect 90d
/reflect all permissions
/reflect 30d report styling
```

## Getting started

### Prerequisites

- **Claude Code**, with multi-agent orchestration (the Workflow tool) available — the extraction phase depends on it.
- Some existing session history under `~/.claude/projects/`. A fresh install has nothing to reflect on yet.
- **Recommended:** run `/insights` in another session first. `reflect` uses its data to corroborate findings, and will pause to ask if that data is stale or missing.

### Install

```bash
npx skills add apatheticus/skills --skill reflect
```

Or as part of the Claude Code plugin bundle:

```
/plugin marketplace add apatheticus/skills
/plugin install apatheticus-skills@apatheticus
```

Or copy the folder straight into a skill directory:

```bash
cp -R skills/reflect ~/.claude/skills/reflect
```

However it arrives, the skill is then available as `/reflect`.

## Project structure

```text
skills/reflect/
├── SKILL.md                         Pipeline definition and guardrails (the skill itself)
├── README.md                        This file
├── .prettydocs/                     This README's own design system, and a manifest per visual
├── docs/
│   └── assets/
│       ├── hero.svg                 Sessions become signals, clusters, then verdicts
│       └── pipeline.svg             The six phases, 0 through 5
└── reference/
    ├── extraction-guide.md          Signal taxonomy, extractor prompts, JSON schemas, batching
    ├── report-guide.md              Report structure, interactivity, self-containment rules
    └── design-system/               Bundled "SaaS Pro" design system, for the report
        ├── DESIGN.md                Colour, type, space, elevation, component rules
        ├── MOTION.md                Durations, easings, patterns, reduced motion
        ├── tokens/                  colors, typography, spacing, motion
        ├── components.css           The sp-* class layer
        └── charts/                  Chart geometry references (read-only)
```

## Privacy and guardrails

- **Diagnosis only.** The only writes are the output directory, the report file, and scratch temp files. `reflect` never builds or edits what it recommends.
- **Local by design.** Transcripts hold private data; it stays in the local report and is never sent to an external service.
- **Evidence or it doesn't ship.** Every recommendation cites at least one session ID with a verbatim quote; a `new-skill` proposal cites at least three distinct sessions.
- **No silent gaps.** If a run skips sessions (stale insights, an oversized `all` window, unreadable transcripts), it says so in the report and the closing summary.

## Documentation

- [SKILL.md](SKILL.md) — the full pipeline, arguments, and guardrails.
- [reference/extraction-guide.md](reference/extraction-guide.md) — signal taxonomy, extractor prompt template, and JSON schemas.
- [reference/report-guide.md](reference/report-guide.md) — report structure, motion, and the self-containment rules.
- [reference/design-system/DESIGN.md](reference/design-system/DESIGN.md) — the SaaS Pro design system used for the report.
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — how to propose a change to this collection.

## License

Released under the [MIT License](../../LICENSE) of the repository that ships it.

<!-- pd:footer start -->
<div align="center">
<br/>

**Copyright © 2026 Zerø Effort. Released under the MIT license.**

</div>
<!-- pd:footer end -->
