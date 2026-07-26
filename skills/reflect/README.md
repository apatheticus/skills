<div align="center">

<img src="./docs/assets/hero.svg" width="100%" alt="reflect — a Claude Code skill that turns your session history into a ranked, evidence-backed diagnosis of your setup as one interactive HTML report" />

# reflect

**A Claude Code skill that reads your past sessions and hands back a ranked, evidence-backed diagnosis of your setup — as a single interactive HTML report.**

<!-- update-docs:badges start -->
[![Type: Claude Code skill](https://img.shields.io/badge/type-Claude_Code_skill-11d3a3)](SKILL.md)
[![Invoke: /reflect](https://img.shields.io/badge/invoke-%2Freflect-12b5c9)](#usage)
[![Output: interactive HTML](https://img.shields.io/badge/output-interactive_HTML-28c8e8)](#what-you-get)
[![Engine: multi-agent Workflow](https://img.shields.io/badge/engine-multi--agent_Workflow-0bb98d)](#how-it-works)
[![Data: 100% local](https://img.shields.io/badge/data-100%25_local-2fc97a)](#privacy-and-guardrails)
[![License: MIT](https://img.shields.io/badge/License-MIT-11d3a3.svg)](../../LICENSE)
<!-- update-docs:badges end -->

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

The report is styled with the bundled **Neumorphic Fresh** design system (see [reference/design-system/](reference/design-system/)) and opens straight from `file://`.

## How it works

`reflect` runs a five-phase pipeline. The heavy extraction stage fans out across many sub-agents through the Workflow tool; everything a session touches stays local.

```mermaid
flowchart LR
  subgraph scope["Corpus (local only)"]
    T["Session transcripts<br/>~/.claude/projects"]
    I["/insights data<br/>~/.claude/usage-data"]
  end

  T --> TR["Triage<br/>score every session"]
  I --> TR
  TR --> EX["Extract signals<br/>parallel sub-agents"]
  EX --> CL["Cluster<br/>merge across sessions"]
  CL --> DE["Decide<br/>a verdict per cluster"]
  DE --> RP["Ranked interactive<br/>HTML report"]
  I -. "corroborate" .-> DE
  RP -. "diff vs prior run" .-> RP
```

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
├── docs/
│   └── assets/
│       └── hero.svg                 README hero graphic
└── reference/
    ├── extraction-guide.md          Signal taxonomy, extractor prompts, JSON schemas, batching
    ├── report-guide.md              Report structure, interactivity, self-containment rules
    └── design-system/               Bundled "Neumorphic Fresh" tokens and components
        ├── DESIGN.md
        ├── colors_and_type.css
        └── components.css
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
- [reference/design-system/DESIGN.md](reference/design-system/DESIGN.md) — the Neumorphic Fresh design system used for the report.
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — how to propose a change to this collection.

## License

Released under the [MIT License](../../LICENSE) of the repository that ships it.

<div align="center">
<br/>

**A Claude Code skill · diagnosis only · your transcripts never leave your machine.**

</div>
