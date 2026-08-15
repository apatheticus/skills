<div align="center">

# skills

**Agent skills published by Zerø Effort, installable from one source tree through two managed channels.**

<!-- pd:badges start -->
[![install: npx skills](https://img.shields.io/badge/install-npx%20skills-E2E6FB)](https://skills.sh) [![validate](https://github.com/apatheticus/skills/actions/workflows/validate.yml/badge.svg)](https://github.com/apatheticus/skills/actions/workflows/validate.yml) [![license: MIT](https://img.shields.io/badge/license-MIT-E2E6FB)](./LICENSE) [![contributing](https://img.shields.io/badge/contributing-guidelines-0B0F1A)](./CONTRIBUTING.md)
<!-- pd:badges end -->

<!-- pd:viz name="hero" src=".prettydocs/src/hero/" facts-hash="e80dc438d0637e7a65b534b879dc1fda6ebe72ee145886a7496cff6b72fb3185" src-hash="3df42bbf22933406f74a4f54ed46c893ab3699f186aa38837952cfe9950317a6" -->
<div align="center">
<img src="docs/assets/hero.webp" width="860" alt="One source tree feeding two install channels. On the left, a skill directory: skills/&lt;name&gt;/ holding SKILL.md plus optional reference/, scripts/, and assets/ folders. Two paths lead right from it. The first is skills.sh — running npx skills add apatheticus/skills writes editable copies into your own project. The second is the Claude Code plugin — adding the marketplace and installing apatheticus-skills@apatheticus gives you a managed bundle that updates when the repo does. Both channels read the same skills/ directory." />
</div>
<!-- pd:viz end -->

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
npx skills add apatheticus/skills -s human-voice -s prettier-svg-docs   # two
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
| [`gauntlet-builder`](./skills/gauntlet-builder) | Interview yourself into knowing what you are actually building, one question at a time, and turn every answer into a binary check — then emit a Gauntlet Loop prompt that builds against those checks with a fresh blind critic every round. The output is an answer key, not a plan: it says how you would know the work came out wrong, and lists what nobody has decided as explicitly ungradeable so a critic reports "cannot judge" instead of guessing. A bundled linter proves the bar is checkable before anything runs against it. | `npx skills add apatheticus/skills -s gauntlet-builder` |
| [`human-voice`](./skills/human-voice) | Strip signs of AI-generated writing and rewrite prose so it reads as human-authored. Picks a register first (editorial, professional, technical, or regulated) so a spec never gets an essay's voice. Yields to a compliance skill for federal work. | `npx skills add apatheticus/skills -s human-voice` |
| [`pretty-hyper-docs`](./skills/pretty-hyper-docs) | Write a repo's standard docs against the truth of the code, then render their key diagrams as seamless-loop animated WebPs via HyperFrames. Re-renders only what changed. | `npx skills add apatheticus/skills -s pretty-hyper-docs` |
| [`pretty-plain-docs`](./skills/pretty-plain-docs) | The same docs engine again, with the diagrams as static SVG — nothing animates, so the output survives a print stylesheet, a PDF export, and a reviewer whose renderer rasterises SVG. Carries the same 32-style catalog, adds a Mermaid source under every structural diagram, and refuses to chart a number the repo cannot recompute. | `npx skills add apatheticus/skills -s pretty-plain-docs` |
| [`prettier-svg-docs`](./skills/prettier-svg-docs) | The same docs engine, but the diagrams are seamless-loop animated SVG written directly — no renderer, no ffmpeg, nothing to install. A 32-style catalog decides what a board is made of and a 27-type diagram taxonomy decides what it is shaped like, each with a gated full-width specimen. The bundled checker proves the loop is seam-exact and that the drawing obeys its own grammar — no diagonal connectors, no label clipped by a node, nothing off the grid — before anything is committed. | `npx skills add apatheticus/skills -s prettier-svg-docs` |
| [`security-audit-full-report`](./skills/security-audit-full-report) | Loop a security audit over a codebase until it stops finding anything new — each cycle hunts the ground the last one missed — then merge every run into one interactive HTML report. State lives on disk, so a run survives compaction and resumes where it stopped. Drives Cloudflare's `security-audit` skill; it does not re-implement the hunting. | `npx skills add apatheticus/skills -s security-audit-full-report` |
| [`reflect`](./skills/reflect) | Mine your own Claude Code session transcripts for what keeps going wrong, what quietly works, and which setup changes would pay off most — then hand back one self-contained interactive HTML report. Every recommendation cites a session ID and a verbatim quote; a proposed skill needs three separate sessions behind it. Diagnosis only, and nothing leaves the machine. | `npx skills add apatheticus/skills -s reflect` |
| [`website-security-scan`](./skills/website-security-scan) | Scan a live site and the email domains sharing its name from the outside — headers, DNS and mail authentication, TLS, exposed files, open ports — and render the result as an interactive HTML report that diffs itself against the previous run. Severity is scored against a written target profile rather than CVSS, which is also what makes it useful for checking whether a vendor's scorecard is telling the truth. | `npx skills add apatheticus/skills -s website-security-scan` |
<!-- skills:table end -->

Add `-g` to any of those to install globally instead of into the current project. Stack
`-s` flags to take several at once.

<!-- `npm run validate` enforces this table: one row per skills/<name>, a link to the skill
     directory, a non-empty description you write yourself, and the exact install command.
     Row order is not checked, so curate it. -->

### Renamed

`0.10.0` renamed two skills so the name says which renderer you get.
`0.19.0` renamed one again, because it stopped being the same skill: it gained a
27-type diagram taxonomy, a connector grammar and a geometry gate, so the diagrams are
now designed rather than improvised.

| Was | Now |
| --- | --- |
| `make-pretty-docs` | [`pretty-hyper-docs`](./skills/pretty-hyper-docs) — HyperFrames → animated WebP |
| `more-pretty-docs` → `pretty-svg-docs` | [`prettier-svg-docs`](./skills/prettier-svg-docs) — animated SVG, nothing to install |

Visuals produced under either old name are still recognised as this skill's own work
and are never reported as foreign, so a repo processed before the rename needs no
migration.

How you get the new names depends on the channel you installed through:

- **Plugin channel** re-syncs the whole plugin, so the old directories disappear on update.
  Nothing to do.
- **`npx skills` channel** copies into `.claude/skills/<name>/`. The old commands stop
  resolving, but an existing local copy **persists beside** the new one, and two skills with
  overlapping descriptions will both compete to trigger. Delete the old copies once:

```bash
rm -rf .claude/skills/make-pretty-docs .claude/skills/more-pretty-docs \
       .claude/skills/pretty-svg-docs
```

Existing visuals keep working. The marker and manifest names changed too — `mpd:viz` →
`pd:viz`, `mpd.json` → `viz.json` — and the frozen design system moved from
`docs/assets/src/DESIGN.md` to `.prettydocs/prettydocs.md`. All three skills still read every
old form and rewrite it in place the next time they touch a doc, so nothing needs
re-rendering.

<br/>

## What a skill looks like

A skill is read in stages, and only the first stage sits in front of the agent all the
time. That is the reason the format is worth learning: the trigger text stays cheap, and
the depth stays out of the way until something actually needs it.

<!-- pd:viz name="skill-anatomy" src=".prettydocs/src/skill-anatomy/" facts-hash="7d2f878624d25964e317eef475d24e995c77ac8e7f918b3087938b601db24f06" src-hash="33cc44c049c02ccbfa70ef53b4c7e4d2986b031eafff50190527f98259a20973" -->
<div align="center">
<img src="docs/assets/skill-anatomy.webp" width="860" alt="The three stages an agent reads a skill in. Stage one, always loaded: the SKILL.md frontmatter, which requires exactly two keys, name and description. The description is the only text an agent reads when deciding whether to load the skill at all. Stage two, loaded when the skill fires: the SKILL.md body, written as instructions aimed at the agent, opening with when not to use it, and kept under roughly 500 lines. Stage three, loaded on demand: reference/*.md, scripts/*, and assets/*, linked by relative path so they cost nothing until the skill reaches for them." />
</div>
<!-- pd:viz end -->

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
.prettydocs/
  prettydocs.md      # the repo's frozen design system
  src/<viz>/         # each diagram's composition and its viz.json manifest
```

Every project root repeats the `docs/assets/` + `.prettydocs/` pair — this repo is seven of
them, the root plus each `skills/<name>/`.

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
- [`.prettydocs/prettydocs.md`](./.prettydocs/prettydocs.md) — the frozen design system behind the diagrams above.

<br/>

## License

Released under the [MIT License](./LICENSE).

<!-- pd:footer start -->
<div align="center">
<br/>

**Copyright © 2026 Zerø Effort. Released under the MIT license.**

</div>
<!-- pd:footer end -->
