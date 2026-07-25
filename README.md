# skills

Agent skills published by Zerø Effort ([@apatheticus](https://github.com/apatheticus)).

[![skills.sh](https://skills.sh/b/apatheticus/skills)](https://skills.sh/apatheticus/skills)
[![validate](https://github.com/apatheticus/skills/actions/workflows/validate.yml/badge.svg)](https://github.com/apatheticus/skills/actions/workflows/validate.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

Every skill here ships from one source tree through two managed channels, plus a
manual copy. `npx skills` writes editable files into your project and you pull
updates yourself. The Claude Code plugin installs the whole bundle as managed
files that update when this repo does. Take the first if you expect to edit the
skills, the second if you would rather not think about it.

## Install

### `npx skills` — works with Claude Code, Codex, Cursor, Copilot, Gemini CLI, and other [Agent Skills](https://agentskills.io) hosts

```bash
npx skills add apatheticus/skills
```

Pick the skills and the agents you want; the CLI writes editable copies into your
project. Useful variants:

```bash
npx skills add apatheticus/skills -g              # install globally, not per-project
npx skills add apatheticus/skills -a claude-code  # target one agent
npx skills update <skill-name>                    # pull later changes
```

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

### Manual — a single skill, no tooling

```bash
git clone https://github.com/apatheticus/skills.git
cp -R skills/<skill-name> ~/.claude/skills/<skill-name>
```

### Removing

`npx skills` and manual copies are yours to delete: remove the skill directory
the install wrote. The plugin comes out through Claude Code:

```bash
claude plugin uninstall apatheticus-skills@apatheticus
claude plugin marketplace remove apatheticus
```

Restart Claude Code afterward. The skill list is read at session start, so a
removed skill stays visible until the next session.

## Skills

| Skill | What it does |
| --- | --- |
| [`human-voice`](./skills/human-voice) | Strip signs of AI-generated writing and rewrite prose so it reads as human-authored. Picks a register first (editorial, professional, technical, or regulated) so a spec never gets an essay's voice. Yields to a compliance skill for federal work. |
| [`make-pretty-docs`](./skills/make-pretty-docs) | Write a repo's standard docs against the truth of the code, then render their key diagrams as seamless-loop animated WebPs via HyperFrames. Re-renders only what changed. |

<!-- Keep this table in step with skills/. `npm run validate` checks the manifests, not this table. -->

## Repository layout

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
```

The plugin is sourced from the repo root and lists every skill under `skills/`.
This layout satisfies both installers with no duplicated files: `npx skills`
discovers `skills/*/SKILL.md` directly, and the plugin manifest points at the same
directories.

## Developing

```bash
npm run validate   # check frontmatter, names, and both manifests — exits 1 on error
npm run sync       # rewrite plugin.json skills[] from what is on disk
```

CI runs `validate` on every push and pull request, and fails if `plugin.json` has
drifted from `skills/`.

To try a skill before publishing, symlink it into your agent's skills directory:

```bash
ln -s "$PWD/skills/<name>" ~/.claude/skills/<name>
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for authoring rules, and start a new
skill from [`templates/SKILL.template.md`](./templates/SKILL.template.md).

## License

[MIT](./LICENSE)
