<div align="center">

# skills

**Agent skills published by Zerø Effort, installable from one source tree through two managed channels.**

<!-- mpd:badges start -->
[![install: npx skills](https://img.shields.io/badge/install-npx%20skills-E2E6FB)](https://skills.sh) [![validate](https://github.com/apatheticus/skills/actions/workflows/validate.yml/badge.svg)](https://github.com/apatheticus/skills/actions/workflows/validate.yml) [![license: MIT](https://img.shields.io/badge/license-MIT-E2E6FB)](./LICENSE) [![contributing](https://img.shields.io/badge/contributing-guidelines-0B0F1A)](./CONTRIBUTING.md)
<!-- mpd:badges end -->

<!-- mpd:viz name="hero" src="docs/assets/src/hero/" facts-hash="e80dc438d0637e7a65b534b879dc1fda6ebe72ee145886a7496cff6b72fb3185" src-hash="3df42bbf22933406f74a4f54ed46c893ab3699f186aa38837952cfe9950317a6" -->
<img src="docs/assets/hero.webp" width="860" alt="One source tree feeding two install channels. On the left, a skill directory: skills/&lt;name&gt;/ holding SKILL.md plus optional reference/, scripts/, and assets/ folders. Two paths lead right from it. The first is skills.sh — running npx skills add apatheticus/skills writes editable copies into your own project. The second is the Claude Code plugin — adding the marketplace and installing apatheticus-skills@apatheticus gives you a managed bundle that updates when the repo does. Both channels read the same skills/ directory." />
<!-- mpd:viz end -->

</div>

<br/>

## What this is

A public repository of agent skills. A skill is a folder with a `SKILL.md` in it: some
frontmatter telling an agent when to load it, and a body telling the agent what to do
once it has. Agents that support the [Agent Skills](https://agentskills.io) convention
read them directly.

Everything ships from one `skills/` directory, and there are two managed ways to get it,
plus a manual copy. `npx skills` takes one skill or all of them, writes editable files
into your project, and leaves you to pull updates yourself. The Claude Code plugin
installs the whole set as managed files that update when this repo does. Take the first
if you want to pick and choose or expect to edit what you get, the second if you would
rather not think about it.

Nothing here is published to npm. `package.json` is `private` and exists only to hold the
validation scripts.

<br/>

## Install

Three ways in. Pick one.

### `npx skills` — works with Claude Code, Codex, Cursor, Copilot, Gemini CLI, and other [Agent Skills](https://agentskills.io) hosts

```bash
npx skills add apatheticus/skills
```

That asks which skills and which agents you want, then writes editable copies into your
project. Nothing here is all-or-nothing — to skip the prompt and name what you want, pass
`-s` once per skill:

```bash
npx skills add apatheticus/skills -s human-voice                       # one skill
npx skills add apatheticus/skills -s human-voice -s more-pretty-docs   # two
npx skills add apatheticus/skills --all                                # every skill, every agent
```

Repeat the flag; `-s a,b` is not a list and matches nothing. The [Skills](#skills) table
below carries the exact command for each one.

Other useful variants:

```bash
npx skills add apatheticus/skills -l              # list what's in the repo, install nothing
npx skills add apatheticus/skills -g              # install globally, not per-project
npx skills add apatheticus/skills -a claude-code  # target one agent
npx skills update <skill-name>                    # pull later changes
```

<br/>

### Claude Code plugin — managed bundle, updates when this repo does

From inside Claude Code:

```
/plugin marketplace add apatheticus/skills
/plugin install apatheticus-skills@apatheticus
```

Or from a shell:

```bash
claude plugin marketplace add apatheticus/skills
claude plugin install apatheticus-skills@apatheticus
```

This channel is the whole set or none of it: the marketplace lists one plugin sourced from
the repo root, so every skill under `skills/` arrives together under one version. Unused
skills cost a session only their `description` line, not their body — but if you want a
subset, use `npx skills` above.

<br/>

### Manual — a single skill, no tooling

```bash
git clone https://github.com/apatheticus/skills.git
cp -R skills/<skill-name> ~/.claude/skills/<skill-name>
```

<br/>

### Removing

`npx skills` and manual copies are yours to delete: remove the skill directory
the install wrote. The plugin comes out through Claude Code:

```bash
claude plugin uninstall apatheticus-skills@apatheticus
claude plugin marketplace remove apatheticus
```

Restart Claude Code afterward. The skill list is read at session start, so a
removed skill stays visible until the next session.

<br/>

## Skills

<!-- skills:table start -->
| Skill | What it does | Install just this one |
| --- | --- | --- |
| [`human-voice`](./skills/human-voice) | Strip signs of AI-generated writing and rewrite prose so it reads as human-authored. Picks a register first (editorial, professional, technical, or regulated) so a spec never gets an essay's voice. Yields to a compliance skill for federal work. | `npx skills add apatheticus/skills -s human-voice` |
| [`make-pretty-docs`](./skills/make-pretty-docs) | Write a repo's standard docs against the truth of the code, then render their key diagrams as seamless-loop animated WebPs via HyperFrames. Re-renders only what changed. | `npx skills add apatheticus/skills -s make-pretty-docs` |
| [`more-pretty-docs`](./skills/more-pretty-docs) | The same docs engine, but the diagrams are seamless-loop animated SVG written directly — no renderer, no ffmpeg, nothing to install. Ships a 31-style catalog, from Swiss minimal to oil impasto, each with a gated full-width specimen, and a bundled checker that proves the loop is seam-exact before anything is committed. | `npx skills add apatheticus/skills -s more-pretty-docs` |
| [`security-audit-full-report`](./skills/security-audit-full-report) | Loop a security audit over a codebase until it stops finding anything new — each cycle hunts the ground the last one missed — then merge every run into one interactive HTML report. State lives on disk, so a run survives compaction and resumes where it stopped. Drives Cloudflare's `security-audit` skill; it does not re-implement the hunting. | `npx skills add apatheticus/skills -s security-audit-full-report` |
| [`reflect`](./skills/reflect) | Mine your own Claude Code session transcripts for what keeps going wrong, what quietly works, and which setup changes would pay off most — then hand back one self-contained interactive HTML report. Every recommendation cites a session ID and a verbatim quote; a proposed skill needs three separate sessions behind it. Diagnosis only, and nothing leaves the machine. | `npx skills add apatheticus/skills -s reflect` |
<!-- skills:table end -->

Add `-g` to any of those to install globally instead of into the current project. Stack
`-s` flags to take several at once.

<!-- `npm run validate` enforces this table: one row per skills/<name>, a link to the skill
     directory, a non-empty description you write yourself, and the exact install command.
     Row order is not checked, so curate it. -->

<br/>

## What a skill looks like

A skill is read in stages, and only the first stage sits in front of the agent all the
time. That is the reason the format is worth learning: the trigger text stays cheap, and
the depth stays out of the way until something actually needs it.

<!-- mpd:viz name="skill-anatomy" src="docs/assets/src/skill-anatomy/" facts-hash="7d2f878624d25964e317eef475d24e995c77ac8e7f918b3087938b601db24f06" src-hash="33cc44c049c02ccbfa70ef53b4c7e4d2986b031eafff50190527f98259a20973" -->
<div align="center">
<img src="docs/assets/skill-anatomy.webp" width="860" alt="The three stages an agent reads a skill in. Stage one, always loaded: the SKILL.md frontmatter, which requires exactly two keys, name and description. The description is the only text an agent reads when deciding whether to load the skill at all. Stage two, loaded when the skill fires: the SKILL.md body, written as instructions aimed at the agent, opening with when not to use it, and kept under roughly 500 lines. Stage three, loaded on demand: reference/*.md, scripts/*, and assets/*, linked by relative path so they cost nothing until the skill reaches for them." />
</div>
<!-- mpd:viz end -->

Both required frontmatter keys are checked by `scripts/validate.mjs`: `name` must be
lowercase kebab-case and match the directory it sits in, and `description` must be under
1024 characters. [`templates/frontmatter.md`](./templates/frontmatter.md) documents every
optional field.

<br/>

## Project structure

```
.claude-plugin/
  marketplace.json   # makes the repo a Claude Code plugin marketplace
  plugin.json        # the bundle itself; lists every ./skills/<name>
skills/
  <name>/
    SKILL.md         # required — frontmatter + instructions
    reference/       # optional — detail loaded on demand
    scripts/         # optional — executables the skill calls
    assets/          # optional — templates and fixtures
templates/
  SKILL.template.md  # starting point for a new skill
  frontmatter.md     # every supported SKILL.md frontmatter field
scripts/
  validate.mjs       # frontmatter + manifest validator (also runs in CI)
docs/assets/
  *.webp             # the animated diagrams embedded above
  src/               # their compositions, and the repo's frozen design system
```

The plugin is sourced from the repo root and lists every skill under `skills/`. That
satisfies both installers with no duplicated files: `npx skills` discovers
`skills/*/SKILL.md` directly, and the plugin manifest points at the same directories.

<br/>

## Technology stack

| Area | Choice |
| --- | --- |
| Runtime | Node 18+ (`engines.node` in `package.json`) |
| Validator | `scripts/validate.mjs` — plain ESM, no dependencies |
| CI | GitHub Actions; the `skills + manifests` job runs on pushes to `main` and `stage`, and on every pull request |
| Distribution | skills.sh via `npx skills`, and the Claude Code plugin marketplace |
| Doc visuals | HyperFrames compositions rendered to animated WebP |

<br/>

## Contributing

[CONTRIBUTING.md](./CONTRIBUTING.md) has the authoring rules, the branch flow, and what
has to be green before a change reaches `main`. Pull requests are reviewed by an admin
and accepted or closed on quality, value, and fit with the collection, so read the
review criteria before you start building. Start a new skill from
[`templates/SKILL.template.md`](./templates/SKILL.template.md).

To try a skill before publishing it, symlink it into your agent's skills directory:

```bash
ln -s "$PWD/skills/<name>" ~/.claude/skills/<name>
```

<br/>

## Documentation

- [CONTRIBUTING.md](./CONTRIBUTING.md) — how to add a skill and get it merged.
- [`templates/frontmatter.md`](./templates/frontmatter.md) — every supported `SKILL.md` frontmatter field.
- [`docs/assets/src/DESIGN.md`](./docs/assets/src/DESIGN.md) — the frozen design system behind the diagrams above.

<br/>

## License

Released under the [MIT License](./LICENSE).

<!-- mpd:footer start -->
<div align="center">
<br/>

**Copyright © 2026 Zerø Effort. Released under the MIT license.**

</div>
<!-- mpd:footer end -->
