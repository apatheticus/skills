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
- **Every PR is reviewed by an admin**, who accepts it or closes it on quality, value, and fit with the collection. That guarantee comes from the access model — merging needs write access and `apatheticus` is the only collaborator — not from a review count.
- **`required_approving_review_count` stays `0`, deliberately. Do not raise it.** GitHub does not let a PR author approve their own PR, and this repo has one admin, so a count of `1` can never be satisfied: `main` goes unmergeable until protection is loosened. Setting it while turning `enforce_admins` off is worse — the requirement becomes decorative *and* direct pushes to `main` stop being blocked. Raise it only after a second admin collaborator exists.
- `required_conversation_resolution` is **on**: every review thread must be resolved before `main` will merge. This is the enforceable half of the review policy on a single-admin repo.
- The `validate` workflow's job — status-check context **`skills + manifests`**, pinned to app id `15368` — is a required check, so a red run blocks the merge.
- That context string is the job's `name:` in `validate.yml`, not the workflow name. **Renaming the job breaks branch protection silently:** the old context never reports, and the PR sits on "Expected — waiting for status" forever. Rename the job and the protection rule together.
- `strict` is off, so `stage` does not have to be up to date with `main` to merge. Turn it on only if you start committing to `main` outside the `stage` PR flow.
- `Closes #N` only auto-closes on merges into the default branch, which is now `stage`. A PR merged into `main` will **not** close the issue; close it by hand.

## Rules

- Never hand-edit `plugin.json`'s `skills[]` — run `npm run sync`.
- Adding a skill: `skills/<name>/SKILL.md` where the frontmatter `name` equals the directory name, then sync, validate, add a README table row, and bump `plugin.json` `version` (minor for a new skill, patch for a fix).
- Start a new skill from `templates/SKILL.template.md`; `templates/frontmatter.md` documents every supported field and `CONTRIBUTING.md` holds the authoring rules.

## Current state

Scaffolded 2026-07-24. Three skills shipped (`human-voice`, `make-pretty-docs`, `more-pretty-docs`); repo validates green at plugin version 0.7.0. `more-pretty-docs` ships a **31-style** catalog as of 2026-07-25 (14 → 31, folding in the `svg-style-exemplars` reference set), with a full-width **specimen per style** at `docs/samples/<slug>.svg`. The scaffold-only `new-skill` example was removed once a real skill landed — its frontmatter reference survives as `templates/frontmatter.md`. Work lands on `stage` (pushed to `origin`, `github-personal:apatheticus/skills.git`) and reaches `main` only by PR. PR #3 merged `stage` into `main` on 2026-07-26 UTC, shipping 0.5.3 → 0.7.0.

**`svg_check.py` gates fidelity, not just safety.** Every other check class is a ceiling (filter depth, bytes, radius) or a legibility floor (font size, contrast) — none of them asks whether a visual *looks like* the style it claims, so a flat, styleless render used to pass clean. Styles now declare their material in `scripts/styles.json` via `require_filter_all`, `min_filter_depth` and `min_elements`, and the checker prints a per-file `NOTE` reporting the chain depth, filter count and drawn-element count it actually found. `deepest chain 1` under a floor of 3 is the tell that a material was faked. Two attributes drive it: `data-specimen="true"` marks a catalog sample (**`min_elements` binds only on specimens** — a README diagram with four boxes is correct at 23 elements, and padding it would be worse output), and `data-style="<slug>"` on a `<filter>` measures that chain against the floor of the style it depicts rather than the file-wide one.

The contact sheet `docs/assets/styles.svg` is **1200×4458** and is gated as its own declared `catalog-sheet` style (`filter_depth: 5`, `bytes_fail: 300 KB`, `min_elements: 620`). It used to be the one asset gated *without* `--style`, which silently gave it global `filter_depth: 1` and made `check_style` skip it entirely — so the single file depicting all 31 idioms was the only one exempt from every fidelity gate, and every material on it was faked. Each tile is now that style's own specimen scaled down rather than a redrawing, so the sheet cannot be less faithful than the catalog it indexes or drift from it. Read that skill's `docs/assets/src/DESIGN.md` before editing it — the per-specimen token namespacing, `isolation: isolate` and per-tile `data-bg` are all load-bearing.

Both skills' README visuals were authored by running `more-pretty-docs` on itself, so they double as the worked example. `human-voice` runs `editorial`, `more-pretty-docs` runs `bento-grid` — **neither style requires a filter**, and `editorial` forbids blur, shadow and gradient outright, so for these two the fidelity floor is drawn density and typographic craft rather than a filter chain. Don't "fix" a zero-filter NOTE on either: `bento-grid` allows one soft shadow *or* a hairline and never both, and these boards use the hairline.

**Do not read branch skew as commit counts.** Merges into `main` use a merge commit deliberately — squash or rebase would rewrite the SHAs and permanently diverge the two branches — so `main` shows as one commit "ahead" of `stage` per merge while the content is identical. Compare with `git diff origin/main origin/stage` (empty means in sync); `git rev-list --count` will mislead you.

Validator constraints worth knowing before authoring, all enforced by `scripts/validate.mjs`:

- `parseFrontmatter` reads flat scalar keys only and treats indented continuation lines as `''`, so a multi-line `description: |` block fails the required-key check. Keep `description` on one line (≤1024 chars).
- An unquoted `description` cannot contain a colon followed by a space. Real YAML parsers throw `Nested mappings are not allowed in compact mappings` and installers **skip the file silently**, so the skill goes invisible instead of failing loudly — this shipped undetected in `make-pretty-docs` until a live `npx skills add` run exposed it. Use an em dash, or quote the whole value.
- The README Skills table is machine-checked: one row per `skills/<name>`, a link to the skill directory, a non-empty human-written description, and column 3 exactly `npx skills add <slug> -s <name>` (slug derived from `plugin.json`'s `repository`). The table is delimited by `<!-- skills:table start/end -->`; row order is not checked.
