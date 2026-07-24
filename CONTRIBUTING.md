# Contributing

Thanks for adding to this repo. A skill lands here only if it works against a
real target, not just in theory.

## Quick path

```bash
git clone https://github.com/apatheticus/skills.git
cd skills
mkdir -p skills/<your-skill>
cp templates/SKILL.template.md skills/<your-skill>/SKILL.md
npm run sync        # registers it in .claude-plugin/plugin.json
npm run validate    # must exit 0
```

## Skill layout

```
skills/<name>/
  SKILL.md       # required
  reference/     # optional — long detail, loaded only when linked
  scripts/       # optional — executables the skill invokes
  assets/        # optional — templates, fixtures, examples
```

The directory name **is** the skill name and **is** the slash command. Group
skills in subdirectories (`skills/<group>/<name>/`) only once there are enough to
justify it — the validator and both installers handle nesting.

## Frontmatter

Two fields are required; everything else is optional. Full reference:
[`templates/frontmatter.md`](./templates/frontmatter.md).

```yaml
---
name: release-notes
description: Generate release notes from merged PRs since the last tag, grouped by change type. Use when the user asks for release notes, a changelog entry, or says "what shipped since <tag>".
---
```

- `name` — lowercase kebab-case, ≤64 chars, identical to the directory name.
- `description` — ≤1024 chars. **What it does** plus **when to trigger**, including
  the literal phrases a user would say. This is the only text an agent reads when
  deciding whether to load your skill; a vague description means the skill never
  fires. Write it last, after the body exists.

## Writing the body

- **One skill, one job.** If the description needs "and also", split it.
- **Imperative, addressed to the agent.** "Run the suite and fix the first
  failure", not "This skill helps with testing".
- **Open with when *not* to use it.** Name the adjacent skill it gets confused with.
- **Be concrete.** Exact commands, exact paths, exact flags. An agent cannot infer
  your repo's conventions.
- **Keep `SKILL.md` under ~500 lines.** Push depth into `reference/*.md` and link
  it by relative path so it loads on demand. The validator warns past that.
- **Reference bundled files relatively** (`scripts/check.sh`), or as
  `${CLAUDE_PLUGIN_ROOT}/skills/<name>/scripts/check.sh` when the skill runs from
  an installed plugin. Never an absolute path from your machine.
- **State how to verify.** Every skill that changes something should end by
  checking the real artifact — the running app, the rendered output, the actual
  API response — not by declaring success.

## Never commit

- Secrets, API keys, tokens, or `.env` contents. This repo is public and every
  installed copy is world-readable.
- Machine-specific absolute paths (`/Users/<you>/...`).
- Destructive commands that run without confirmation (`rm -rf`, force pushes,
  `DROP TABLE`) — gate them behind an explicit user confirmation step.
- Anything that exfiltrates repo contents to a third-party service without saying
  so in the skill body.

## Before opening a PR

1. `npm run sync && npm run validate` — clean, exits 0.
2. Actually run the skill end to end against a real target. Fold whatever broke
   back into `SKILL.md`.
3. Add a row to the Skills table in [README.md](./README.md).
4. Bump `version` in `.claude-plugin/plugin.json` — minor for a new skill, patch
   for a fix to an existing one. Plugin installs update on version change.

## Review criteria

A PR is merged when the skill is: single-purpose, triggered reliably by its
description, verified against something real, and safe to run in a repo the
author does not control.
