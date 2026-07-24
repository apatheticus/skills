# SKILL.md frontmatter reference

Every `SKILL.md` opens with a YAML frontmatter block delimited by `---` on the
first line and a closing `---`. Two fields are required; the rest are optional.

## Required

| Field | Rules |
| --- | --- |
| `name` | Lowercase kebab-case, `^[a-z0-9]+(-[a-z0-9]+)*$`, ≤64 chars. Must equal the containing directory name. Becomes the `/name` invocation. |
| `description` | ≤1024 chars, single line. What the skill does **and** when to use it. This is the only text an agent sees when deciding to load the skill. |

## Optional

| Field | Type | Purpose |
| --- | --- | --- |
| `allowed-tools` | comma-separated string | Restricts the skill to a tool subset, e.g. `Read, Grep, Glob` for a read-only skill. Omit to inherit the session's tools. |
| `disable-model-invocation` | boolean | `true` means the skill never auto-triggers from its description — the user must invoke `/name` explicitly. Use for destructive or interactive workflows. |
| `user-invocable` | boolean | `false` hides it from the slash-command list; the model can still load it. Use for reference-only skills that support another skill. |
| `argument-hint` | string | Placeholder shown after the slash command, e.g. `<pr-number>` or `[path]`. |
| `version` | string | Semver for the individual skill. Independent of the plugin version. |
| `license` | string | SPDX id. Defaults to the repository license (MIT) when omitted. |
| `metadata` | map | Free-form key/values for tooling. Ignored by Claude Code itself. |
| `compatibility` | string/map | Declares host-agent requirements. |
| `homepage`, `repository`, `author` | string/map | Provenance, surfaced by some skill directories. |

Unknown keys do not break the loader, but the repo validator warns on them so
typos like `allowed_tools` or `user_invocable` get caught in review.

## Examples

Auto-triggering, unrestricted:

```yaml
---
name: release-notes
description: Generate release notes from merged PRs since the last tag, grouped by change type. Use when the user asks for release notes, a changelog entry, or says "what shipped since <tag>".
---
```

Read-only, explicit invocation only, takes an argument:

```yaml
---
name: audit-deps
description: Audit dependencies for advisories, separating dev-only from production-runtime risk. Use when the user asks about vulnerabilities, Dependabot alerts, or npm audit output.
allowed-tools: Read, Grep, Glob, Bash
disable-model-invocation: true
argument-hint: [package.json path]
---
```

## Body conventions

- Address the agent in the imperative: "Run the suite", not "This skill runs the suite".
- Lead with a short "When to use" section that also says when **not** to.
- Keep the body under ~500 lines. Move depth into `reference/*.md` and link it by
  relative path so it loads only when needed.
- Reference bundled files relatively (`scripts/check.sh`) or, when the skill runs
  from an installed plugin, as `${CLAUDE_PLUGIN_ROOT}/skills/<name>/scripts/check.sh`.
- Never hardcode secrets, tokens, or machine-specific absolute paths.
