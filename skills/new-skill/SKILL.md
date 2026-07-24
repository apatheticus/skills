---
name: new-skill
description: Scaffold a new agent skill inside this repository — create skills/<name>/SKILL.md with valid frontmatter, register it in .claude-plugin/plugin.json, and verify it with the repo validator. Use when the user says "new skill", "add a skill", "scaffold a skill", "create a skill in this repo", or wants to publish a skill from this marketplace.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# New Skill

Add a skill to this repository so it ships through both distribution channels — `npx skills add` and the Claude Code plugin marketplace — without a broken manifest.

## When to use

The user wants a new skill authored **in this repo**. If they want a skill in `~/.claude/skills` for personal use only, this is the wrong tool — write the file there directly.

## Steps

### 1. Settle the name

Ask for a name if one was not given. Constraints, all enforced by the validator:

- lowercase kebab-case, `^[a-z0-9]+(-[a-z0-9]+)*$`, max 64 characters
- unique across `skills/` — check with `ls skills/`
- the directory name and the frontmatter `name` must be identical
- name it after the **job**, not the topic (`release-notes`, not `releases`) — the name is what the user types as `/name`

### 2. Write the description

This is the single highest-leverage field: it is the only thing an agent sees when deciding whether to load the skill. Write it as *what it does* plus *when to trigger*, and include the literal phrases a user would say.

```
description: <what it does, concretely>. Use when <trigger 1>, <trigger 2>, or the user says "<phrase>".
```

Bad: `Helps with tests.`
Good: `Run the repo's test suite, triage failures, and fix the smallest failing case first. Use when tests fail, CI goes red, or the user says "fix the tests".`

Max 1024 characters. Read `reference/frontmatter.md` for every supported field, including `allowed-tools`, `disable-model-invocation`, and `argument-hint`.

### 3. Create the files

```
skills/<name>/
  SKILL.md              # required — the skill itself
  reference/*.md        # optional — details loaded on demand
  scripts/*             # optional — executables the skill invokes
  assets/*              # optional — templates, fixtures
```

Start from `templates/SKILL.template.md` at the repo root. Keep `SKILL.md` under ~500 lines; push detail into `reference/` and point at it by relative path, so it is read only when needed.

Reference bundled files by path relative to the skill directory (`reference/frontmatter.md`), or with `${CLAUDE_PLUGIN_ROOT}` when the skill runs as part of the installed plugin.

### 4. Register it in the plugin manifest

`.claude-plugin/plugin.json` lists every skill explicitly. Do not hand-edit it — run:

```bash
npm run sync
```

That rewrites `skills[]` from what is actually on disk, so the plugin install and the repo never drift.

### 5. Validate

```bash
npm run validate
```

Must exit 0. It checks frontmatter, name/directory agreement, description length, manifest coverage, and that every path in both manifests resolves. Fix anything it reports before finishing — the same script gates CI.

### 6. Report back

Tell the user the skill path, the exact trigger phrase, and how to try it locally:

```bash
npx skills add apatheticus/skills          # once published
# or, before publishing, test against the working tree:
ln -s "$PWD/skills/<name>" ~/.claude/skills/<name>
```

## Rules

- One skill, one job. If the description needs "and also", it is two skills.
- Never write secrets, tokens, or absolute machine-specific paths into a skill — this repo is public.
- Prefer imperative instructions to an agent over prose explanation for a human reader.
- Do not add a skill to `plugin.json` by hand; `npm run sync` is the source of truth.
