<div align="center">

# human-voice

**A Claude Code skill that rewrites prose so it reads as human-authored — in the register the document actually calls for.**

<!-- mpd:badges start -->
[![License: MIT](https://img.shields.io/badge/License-MIT-8c2f1f.svg)](../../LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-skill-1a1a18)](SKILL.md)
[![Registers](https://img.shields.io/badge/registers-4-1a1a18)](reference/registers.md)
[![Patterns](https://img.shields.io/badge/patterns-33-1a1a18)](reference/patterns.md)
<!-- mpd:badges end -->

<!-- mpd:viz name="hero" src="docs/assets/src/hero/" facts-hash="b26beb7f8d33557cc8587b7fd9b8e115ff8d8b75f0d876065917fd9d5328996b" src-hash="c8211a124b09c94319705a147a645ed0a049d9566ea33426054e90e8ad3e379b" -->
<img src="docs/assets/hero.svg" alt="An animated printed plate. A rust proof rule draws itself across the head of the page above the kicker, step one, choose the register; the folio reads plate one. Under the headline and a hairline, the standfirst says the skill rewrites prose so it reads as written by a person, that the register is chosen first and only then do its patterns apply, and that Professional is the default when the genre is unclear. Below, four columns divided by vertical hairlines name the registers with their genres — Editorial for essays, posts and marketing copy; Professional for memos, policies, reports and proposals; Technical for specs, runbooks, API docs and RFCs; Regulated for filings, compliance, clinical and safety material. A filled mark under Editorial reads voice on, and it is the only one: the other three read voice off, because neutral and plain is the human voice there. Professional alone is opened by the rust rule and marked default, since injecting voice into a document that did not want it is the most damaging thing this skill can do." width="820" />
<!-- mpd:viz end -->

</div>

> [!IMPORTANT]
> This is an editing pass over prose that already exists. It is not a drafting tool,
> and it is not a style guide for code, config, or commit messages. For anything a
> U.S. federal agency, evaluator, or auditor will read, the
> `federal-technical-writing` skill runs first and wins every collision.

## What this is

Machine-written prose has tells. Significance inflation, tidy triplets, "it's not just
X — it's Y", a closing paragraph that restates the opening. Strip them and the writing
stops being tiring to read.

The catch is that a travel essay and a system security plan both fail when they sound
generated, but they fail differently, and the fixes are not interchangeable. Injecting
personality into a policy document is its own kind of damage — and it is invisible to
the person who asked for the edit. So this skill picks a register before it reads a
single pattern, then applies only what that register wants.

It runs over blog posts, articles, memos, policies, reports, specs, runbooks, RFCs,
proposals, and filings. It answers "does this sound AI-generated?" and it is what you
reach for when a draft has to survive a detector.

## The four registers

Selected in step 1, before anything else, because every later decision depends on it.

| Register | Genres | Personality | Specificity currency |
| --- | --- | --- | --- |
| Editorial | blogs, essays, thought leadership, marketing | On | Lived experience, anecdote, scene |
| Professional | memos, policies, reports, proposals, briefs | Off | Institutional fact — dates, names, quantities |
| Technical | specs, architecture docs, runbooks, API docs, ADRs | Off | Reproducible artifact — error strings, config values |
| Regulated | federal, legal, clinical, safety, compliance | Off | Cited authority — statute, standard, control ID |

Professional is the default when the genre is unclear. Editorial never is. Full
profiles, opening and closing rules, and each register's characteristic failure mode
live in [`reference/registers.md`](reference/registers.md).

## How the pattern catalog is gated

<!-- mpd:viz name="pattern-gates" src="docs/assets/src/pattern-gates/" facts-hash="604da93f1fe8ce2b383e6ed84a44d92d1ed42f6af7b6225aa1dd8f2f0ca58680" src-hash="580c8cb0d3dbdd9cc41238290315cc195e77ab3d0aa7aa198054cef9ede8dddf" -->
<img src="docs/assets/pattern-gates.svg" alt="An animated printed plate setting the register gate table. A rust proof rule draws itself across the head above the kicker, step three, pattern gates; the folio reads plate two. The standfirst says that of the 33 catalogued patterns, 22 apply in every register, and that these eleven do not — applying them blind is how this skill breaks documents. Below, twelve rows are set in two stacks divided by a vertical hairline, each row a pattern and each of four columns a register: editorial, professional, technical, regulated. The em dash ban, signposting and diff-anchored writing are on almost everywhere; inline-header lists, title-case headings, hyphenated pairs and aphorism formulas switch off in technical and regulated; manufactured punchlines, rhetorical openers and voice injection are editorial-only. Emojis are limited in editorial and on elsewhere; excessive hedging is limited in technical and regulated, because calibrated uncertainty there is content rather than hedging; diff-anchored writing is elevated in technical, marked by the one ringed rust mark on the plate. A key sets the four states, and a closing line notes that a pattern with no tag for the selected register is off." width="820" />
<!-- mpd:viz end -->

Two gates are worth knowing before you trust the output, because getting them
backwards is expensive:

- **Hedging in Technical and Regulated writing.** "This may fail under load" is
  hedging and gets cut. "Throughput degrades above roughly 4k concurrent connections;
  we have not tested past 8k" is calibrated uncertainty and is often the most valuable
  sentence on the page. The test is whether the qualifier carries information.
- **Speculative gap-filling in Professional and Regulated writing** is treated as a
  blocker, not a style note. The same invented sentence that reads as vagueness in an
  essay is a fabricated claim attributed to your organisation in a filing.

All 33 patterns, each with a before and after plus its register tags, are in
[`reference/patterns.md`](reference/patterns.md), alongside the false-positive list —
a clean human writer trips several of these with no model involved.

## Technology stack

| Area | Choice |
| --- | --- |
| Format | Claude Code skill — Markdown with YAML frontmatter |
| Runtime | none; there is nothing to build, install, or execute |
| Tools used | `Read`, `Write`, `Edit`, `Grep`, `Glob`, `AskUserQuestion` |
| License | MIT, with attribution obligations — see [License](#license) |

## Project structure

```
human-voice/
├── SKILL.md                    the skill: register selection, the gates, self-check, delivery
├── reference/
│   ├── registers.md            the four register profiles, plus the plain-language floor
│   ├── patterns.md             all 33 patterns with before/after and register tags
│   ├── vocabulary.md           global and register-scoped word lists, with carve-outs
│   ├── examples.md             one full worked rewrite per register
│   └── attribution.md          provenance and license terms of the derived material
└── docs/assets/                this README's visuals, and the design system they derive from
```

## Getting started

### Prerequisites

None. No runtime, no dependencies, no network access.

### Install

```bash
npx skills add apatheticus/skills --skill human-voice
```

Or as part of the Claude Code plugin bundle:

```
/plugin marketplace add apatheticus/skills
/plugin install apatheticus-skills@apatheticus
```

Or copy the folder straight into a repo's skill directory:

```bash
cp -R skills/human-voice /path/to/repo/.claude/skills/human-voice
```

### Use

Point it at prose you already have:

```
Humanize the draft in docs/announcement.md
Does this section read as AI-generated?
```

It answers in a fixed order: the register it chose and why, the draft rewrite, an
honest list of what still reads as machine-written, then a final rewrite addressing
that list. A draft with nothing left to flag is almost always an unexamined draft, so
that third step is the one that matters.

If you supply your own earlier writing, it calibrates to your sentence lengths,
vocabulary, and habits rather than substituting generic "human" ones. That step is
skipped for Technical and Regulated work, where house style and cited authority set
the voice instead of a person.

## Testing

There is no automated test suite — the output is prose, judged by reading it. The
repository's `npm run validate` checks this skill's frontmatter and its entries in
both distribution manifests. See
[CONTRIBUTING.md](../../CONTRIBUTING.md) for how changes are proposed and reviewed.

## Documentation

- [`SKILL.md`](SKILL.md) — the skill itself: the steps, the gates, the rules.
- [`reference/registers.md`](reference/registers.md) — the four registers in full.
- [`reference/patterns.md`](reference/patterns.md) — the 33 patterns, with false positives.
- [`reference/vocabulary.md`](reference/vocabulary.md) — the word and phrase lists.
- [`reference/examples.md`](reference/examples.md) — a worked rewrite per register.
- [`reference/attribution.md`](reference/attribution.md) — provenance of the derived material.
- [CONTRIBUTING.md](../../CONTRIBUTING.md) — how to propose a change to this collection.

## License

Released under the [MIT License](../../LICENSE) of the repository that ships it.

The pattern catalog derives from the MIT-licensed
[`humanizer`](https://github.com/blader/humanizer) skill (© 2025 Siqi Chen) and,
through it, from
[Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
(CC BY-SA 4.0), maintained by WikiProject AI Cleanup. Those terms travel with the
material: full provenance in
[`reference/attribution.md`](reference/attribution.md).

<!-- mpd:footer start -->
<div align="center">
<br/>

**Copyright © 2026 Zerø Effort. Released under the MIT license.**

</div>
<!-- mpd:footer end -->
