# skills

Public repository publishing agent skills, installable two ways from one source tree.

## Facts

- GitHub: `apatheticus/skills` (personal account — this tree is under `/Volumes/Data/dev/`, so git auth pins to `github-personal:`).
- License: MIT. Public repo — nothing secret, no machine-specific absolute paths.
- Distribution 1 — skills.sh: `npx skills add apatheticus/skills`. Discovers `skills/*/SKILL.md` directly from GitHub. **No npm publish involved**; `package.json` is `private: true` and exists only to hold the validation scripts.
- Distribution 2 — Claude Code plugin: `/plugin marketplace add apatheticus/skills` then `/plugin install apatheticus-skills@apatheticus`.
- Marketplace name is `apatheticus`; plugin name is `apatheticus-skills`. The plugin sources from the repo root (`"source": "./"`), so both channels read the same `skills/` directory with no duplication.

## Layout

```
.claude-plugin/marketplace.json   # marketplace: one plugin, source "./"
.claude-plugin/plugin.json        # plugin: skills[] lists every ./skills/<name>
skills/<name>/SKILL.md            # the skills themselves (+ optional reference/, scripts/, assets/)
templates/SKILL.template.md       # starting point for a new skill
scripts/validate.mjs              # validator, no dependencies, also runs in CI
```

## Commands

```bash
npm run validate   # frontmatter + both manifests; exits 1 on error
npm run sync       # rewrite plugin.json skills[] from disk (do this after adding a skill)
```

CI (`.github/workflows/validate.yml`) runs `validate` on push/PR and fails if `plugin.json` has drifted from `skills/`.

## Branches

- **`stage` is the default branch.** Do all work there; it has no protection, so push directly.
- **`main` is protected and requires a pull request.** `enforce_admins` is on, so even the repo owner cannot push to it directly — a direct push is rejected with `GH006: Changes must be made through a pull request`. Ship by opening a `stage` → `main` PR.
- Self-merge works: `required_approving_review_count` is `0`. No status checks are required on merge yet, so a red CI run does not block a PR — `validate` is advisory until that is turned on.
- `Closes #N` only auto-closes on merges into the default branch, which is now `stage`. A PR merged into `main` will **not** close the issue; close it by hand.

## Rules

- Never hand-edit `plugin.json`'s `skills[]` — run `npm run sync`.
- Adding a skill: `skills/<name>/SKILL.md` where the frontmatter `name` equals the directory name, then sync, validate, add a README table row, and bump `plugin.json` `version` (minor for a new skill, patch for a fix).
- Start a new skill from `templates/SKILL.template.md`; `templates/frontmatter.md` documents every supported field and `CONTRIBUTING.md` holds the authoring rules.

## Current state

Scaffolded 2026-07-24. Two skills shipped (`human-voice`, `make-pretty-docs`); repo validates green at plugin version 0.4.0. The scaffold-only `new-skill` example was removed once a real skill landed — its frontmatter reference survives as `templates/frontmatter.md`. Work lands directly on `main`, which is pushed to `origin` (`github-personal:apatheticus/skills.git`).

Validator constraint worth knowing before authoring: `parseFrontmatter` in `scripts/validate.mjs` treats indented continuation lines as `''`, so a multi-line `description: |` block fails the required-key check. Keep `description` on a single line (≤1024 chars).
