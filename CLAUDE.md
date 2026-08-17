# skills

Public repository publishing agent skills, installable two ways from one source tree.

## Facts

- GitHub: `apatheticus/skills`, personal account, MIT, public — nothing secret, no machine-specific absolute paths.
- Git auth pins to the personal SSH key by directory via `core.sshCommand` in an `includeIf` gitconfig — see the `github-identities` skill for the machine-side wiring. The stored `origin` is the HTTPS URL and is correct as-is — `url."git@github.com:".insteadOf` rewrites it transparently, which is why `git remote get-url` and `git config remote.origin.url` disagree. Do not "fix" the remote.
- Distribution 1 — skills.sh: `npx skills add apatheticus/skills`, which discovers `skills/*/SKILL.md` directly from GitHub. **No npm publish is involved**; `package.json` is `private: true` and exists only to hold the validation scripts.
- Distribution 2 — Claude Code plugin: marketplace `apatheticus`, publishing **two** plugins — `apatheticus-skills` and `apatheticus-security`. Both source the repo root, so both channels read the same `skills/` directory with no duplication.
- **There is no `.claude-plugin/plugin.json`, and adding one back would break the split.** A single root manifest cannot express two disjoint subsets of one root. Two marketplace entries share `source: "./"` instead, each carrying `"strict": false` and its own inline `skills[]`.
- The `npx skills` channel has **no concept of sets** — it discovers `skills/*/SKILL.md` flat — so it is unaffected by the split and offers every skill individually. Two sets is a plugin-channel fact only.
- **Never quote a version number in this file.** Read the shipped versions off `git show origin/main:.claude-plugin/marketplace.json`; the working tree may hold an unshipped bump. A written count or version here has gone stale every time it has been tried.

## Layout

```
.claude-plugin/marketplace.json   # marketplace AND both plugins; each entry has its own skills[]
skills/<name>/SKILL.md            # the skills themselves (+ optional reference/, scripts/, assets/)
templates/SKILL.template.md       # starting point for a new skill
scripts/validate.mjs              # validator, no dependencies, also runs in CI
```

Doc-visual state is **per project**, and this repo is nine projects: the root plus each
`skills/<name>/`. Every one carries the same block:

```
<project>/docs/assets/<viz>.webp|.svg   # committed — the embedded assets
<project>/.prettydocs/.gitignore        # committed — byproduct rules, project-relative
<project>/.prettydocs/prettydocs.md     # committed — frozen design system + provenance
<project>/.prettydocs/src/<viz>/        # committed — viz.json (+ index.html for WebP)
```

## Commands

```bash
npm run validate   # frontmatter + marketplace + README table; exits 1 on error
npm run sync       # sort each plugin entry's skills[] (it will NOT assign a set)
```

CI (`.github/workflows/validate.yml`) runs `validate` on push/PR and fails if `marketplace.json` has drifted from `skills/`.

## Branches

- **`main` is the default branch and is protected.** `enforce_admins` is on, so even the owner cannot push to it — a direct push is rejected with `GH006`. Ship by opening a `stage` → `main` PR.
- **`stage` is where work happens.** It has no protection, so push to it directly. Pass `--head stage` explicitly when opening a PR, since a bare `gh pr create` targets `main` on both ends.
- Merge with `--merge`, never `--squash` or `--rebase`. `stage` is long-lived; rewriting its SHAs diverges the two branches permanently and every later PR carries phantom conflicts. Never delete `stage`.
- **Do not read branch skew as commit counts.** Each merge leaves `main` one merge commit "ahead" while the content is identical. Sync is `git diff origin/main origin/stage` being empty; `git rev-list --count` will mislead you.
- **`required_approving_review_count` stays `0`. Do not raise it.** GitHub does not let a PR author approve their own PR and this repo has one admin, so `1` can never be satisfied and `main` goes unmergeable. Raise it only after a second admin collaborator exists.
- `required_conversation_resolution` is on. `strict` is off, so `stage` need not be up to date with `main` to merge.
- The required status check context is **`skills + manifests`** (app id `15368`), which is the *job's* `name:` in `validate.yml`, not the workflow name. **Renaming the job breaks branch protection silently** — the old context never reports and the PR waits forever. Rename the job and the protection rule together.
- `Closes #N` fires only on merges into `main`. Work pushed straight to `stage` needs its issue closed by hand.

## Rules

- **Set membership in `marketplace.json` is hand-written.** Which plugin a new skill belongs to is a judgement call, so `npm run sync` only sorts each entry's `skills[]` and never assigns one. `validate.mjs` enforces the invariant instead: a skill listed by no plugin is an error, and a skill listed by two is an error.
- **Never rewrite `marketplace.json` with a JSON serializer, not even to bump `version`.** `json.dumps` defaults to `ensure_ascii=True` and mangles the `ø` in `Zerø Effort`. `npm run validate` still passes — it parses the file, it does not compare bytes — so this reaches CI looking green and reds there. Bump the version with a single-line `Edit`, or run `npm run sync` afterwards to restore the file. To reproduce the CI check locally you must **commit first**: `node scripts/validate.mjs --sync && git diff --quiet -- .claude-plugin/marketplace.json` compares against `HEAD`.
- **Adding a skill:** `skills/<name>/SKILL.md` where the frontmatter `name` equals the directory name → list it in exactly one plugin's `skills[]` → sync → validate → add a README table row → bump that plugin's `version`.
- **Versioning the two entries: the test is whether the change invalidates work a skill has already produced, not how large the diff is.** Bump **minor** for a new skill, a renamed slug, or anything that stops previously-conforming output from conforming — a tightened gate, a raised floor, a withdrawn relaxation, a newly required marker/field/section, or a change to how a skill is reached. Bump **patch** for everything else: a bug fix, a corrected measurement, a loosened or purely additive change, a re-authored asset meeting the same contract. Where a checker exists the test is mechanical: run the new checker against the *previous* release's committed assets; anything red means minor. Note the asymmetry — a fix that *loosens* a gate is a patch, a fix that *tightens* one is not.
- Per-skill `SKILL.md` `version` is optional and independent of the plugin version. Bump the entry that owns the changed skill; a change to `validate.mjs`, CI or the root README bumps both.
- Start a new skill from `templates/SKILL.template.md`. `templates/frontmatter.md` documents every supported field; `CONTRIBUTING.md` holds the authoring rules.

## Checkers — all of these fail open

**CI runs `validate.mjs` and nothing else.** It never runs `svg_check.py`, `audit_visuals.py`, `audit_state.py`, or any `.prettydocs/` manifest check, so a red asset gate reaches `main` looking green. Run them by hand before shipping a visual or script change.

- **`svg_check.py` without `--design` and `--style` checks almost nothing and still prints `0 error(s)`.** No `--design` means an empty palette, so every contrast test degrades to a WARN and the off-system-colour gate never fires; no `--style` means no style invariant or fidelity floor applies. Always pass both.
- **`data-bg` naming a role that does not resolve is a WARN, not an error**, and the contrast floor is then not applied to that text at all. Treat `text has no data-bg ground in scope` as a failure.
- **`audit_visuals.py` takes doc *files*; the directory goes in `--root`.** A path prefixed with the skill name doubles against `--root` and reports every doc missing; a bare `README.md` from the repo root audits the *repo's* README against a skill's manifests. Working form: `( cd "$skill" && python3 scripts/audit_visuals.py --root . *.md )`.
- **`BUDGETS.get()` returns `None` for an unlisted doc, which the checker reads as *unlimited*, silently.** Any new Tier-1 doc type needs its `BUDGETS` row in the same change.
- There is **no shared module** — three copies of `audit_visuals.py`, two of `svg_check.py` and `styles.json`. Keep them in step. CI diffs the `describe_parity` block between the two copies that carry it and fails on divergence.

## Per-skill landmines

- **`reflect` carries two design systems and they are constantly confused.** `reference/design-system/` (SaaS Pro) styles the HTML report the skill *generates*; `.prettydocs/prettydocs.md` governs `reflect`'s own README visuals and is *mapped from* the first. Check which one you are in before editing. SaaS Pro is light-only — do not invent a dark theme or a `data-theme` toggle for the report.
- **`pretty-hyper-docs`' `lazy-rerender` composition fails its own gate** (`npx hyperframes check` reports `content_overlap`), so its WebP cannot legitimately be re-rendered until that is fixed. Treat the asset as frozen.
- **`security-audit-full-report`:** never reinstate `/loop` as a convenience — it re-injects both skill stacks every firing and collapses the delegation boundary. Never call `TaskOutput` on a cycle agent; its output file symlinks the full subagent transcript into the orchestrator, which is exactly what the design exists to keep out. Never spawn a second cycle agent for the same run. Bump `KEY_VERSION` in `audit_state.py` whenever `finding_key` changes, or the next change silently recounts every known finding.
- **Seven of eight skills carry `disable-model-invocation: true`; `human-voice` deliberately does not** — it fires on ordinary editing requests where a user would never think to name a skill. The asymmetry is the design, not drift. `user-invocable` is an orthogonal axis (slash list vs model listing) and stays where it is.
- **Do not trim `prettier-svg-docs`' `description` / `when_to_use`.** `validate.mjs` errors if any `diagrams.json` type slug stops appearing in that text, and Claude Code truncates the combined pair at 1,536 chars from the end — the key trigger belongs at the front.

## Deliberate — do not tidy

- **Three legacy layers serve repos processed under the old skill names** and cannot be migrated from here: all three audit scripts match `m?pd:`, all three fall back to `mpd.json` when `viz.json` is absent, and `prettier-svg-docs` treats `PRODUCER_OWNED = {PRODUCER, "pretty-svg-docs", "more-pretty-docs"}` as owned. Drop the alias set and the skill reports every visual it ever produced `FOREIGN`.
- **Mutual `FOREIGN` between the three pretty-docs skills is the intended migration path**, not a bug. Do not add siblings to `PRODUCER_OWNED`.
- **Three visible `MPD` strings survive in the style catalog** (`blueprint`, `brushed-metal`, `patent-drawing`), mirrored into the contact sheet. Fixing them means re-authoring three specimens *and* their tiles in the most fragile asset here. Decide it on its own merits, not as rename cleanup.
- **Both `prettydocs.md` files say a hairline grid applies "thirty-one times".** It illustrates `(xN)` aggregation and never tracked the catalog. Editing it moves `design_hash`, which invalidates every visual in that project.
- **13 `@keyframes` blocks across the catalog do not return to origin at `100%`** — full rotations, tiled-pattern wraps, travelling pulses. Unadjudicated on purpose; "fixing" them would change six specimens' intent.
- **`align="center"` on the footer `<img>` in `house-style.md` is inline *vertical* alignment and is correct there.** The centering rule that `audit_visuals.py` enforces is a `<div align="center">` wrapper, and only `pd:viz` embeds are subject to it.
- **Re-stamping a `viz.json` without re-rendering is legitimate only when the contract edit was a corrected measurement**, not a design decision — and say so where the next run will see it.

## Known unresolved

- `embedding.md` puts a technical doc's `<details>` Mermaid block *inside* the `pd:viz` marker pair; `reference/architecture.md` puts it *outside*. `pretty-plain-docs` states one position and applies it everywhere; the other two still contradict themselves.
- `reflect` ships no `assets/template.html`, so every run re-authors the report from `report-guide.md` prose. Adding one is a separate decision, not a swap detail.
- Alt text and `<desc>` are covered by no hash. `describe_parity` in `audit_visuals.py` checks numbers, not meaning — a description of the wrong subject with no numbers in it passes. `pretty-hyper-docs` is permanently uncovered: a rendered WebP has no text to extract.

## Validator constraints

All enforced by `scripts/validate.mjs`:

- `parseFrontmatter` reads flat scalar keys only and treats indented continuation lines as `''`, so a multi-line `description: |` block fails the required-key check. Keep `description` on one line.
- **An unquoted `description` cannot contain a colon followed by a space.** Real YAML parsers throw and installers **skip the file silently**, so the skill goes invisible instead of failing loudly. Use an em dash, or quote the whole value.
- The README Skills table is machine-checked and has **four** columns: a link to the skill directory, the backticked name of the plugin whose `skills[]` lists it, a non-empty human-written description, and exactly `npx skills add <slug> -s <name>`. The slug comes from `package.json`'s `repository.url`. Delimited by `<!-- skills:table start/end -->`; row order is not checked.
