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

Doc-visual state is **per project**, and this repo is six projects: the root plus each
`skills/<name>/`. Every one carries the same block:

```
<project>/docs/assets/<viz>.webp|.svg   # committed — the embedded assets
<project>/.prettydocs/.gitignore        # committed — byproduct rules, project-relative
<project>/.prettydocs/prettydocs.md     # committed — frozen design system + provenance
<project>/.prettydocs/src/<viz>/        # committed — viz.json (+ index.html for WebP)
```

## Commands

```bash
npm run validate   # frontmatter + both manifests; exits 1 on error
npm run sync       # rewrite plugin.json skills[] from disk (do this after adding a skill)
```

CI (`.github/workflows/validate.yml`) runs `validate` on push/PR and fails if `plugin.json` has drifted from `skills/`.

## Branches

- **`main` is the default branch.** `stage` is still where work happens — it has no protection, so push directly — but `main` is what a clone, a fork, and a bare `gh pr create` now target. Pass `--head stage` explicitly when opening a PR from a local `stage`.
- **`main` is protected and requires a pull request.** `enforce_admins` is on, so even the repo owner cannot push to it directly — a direct push is rejected with `GH006: Changes must be made through a pull request`. Ship by opening a `stage` → `main` PR.
- **Every PR is reviewed by an admin**, who accepts it or closes it on quality, value, and fit with the collection. That guarantee comes from the access model — merging needs write access and `apatheticus` is the only collaborator — not from a review count.
- **`required_approving_review_count` stays `0`, deliberately. Do not raise it.** GitHub does not let a PR author approve their own PR, and this repo has one admin, so a count of `1` can never be satisfied: `main` goes unmergeable until protection is loosened. Setting it while turning `enforce_admins` off is worse — the requirement becomes decorative *and* direct pushes to `main` stop being blocked. Raise it only after a second admin collaborator exists.
- `required_conversation_resolution` is **on**: every review thread must be resolved before `main` will merge. This is the enforceable half of the review policy on a single-admin repo.
- The `validate` workflow's job — status-check context **`skills + manifests`**, pinned to app id `15368` — is a required check, so a red run blocks the merge.
- That context string is the job's `name:` in `validate.yml`, not the workflow name. **Renaming the job breaks branch protection silently:** the old context never reports, and the PR sits on "Expected — waiting for status" forever. Rename the job and the protection rule together.
- `strict` is off, so `stage` does not have to be up to date with `main` to merge. Turn it on only if you start committing to `main` outside the `stage` PR flow.
- `Closes #N` auto-closes on merges into the default branch, which is `main` — so a `stage` → `main` PR carrying the keyword now closes its issue on merge. It does **not** fire when work is pushed straight to `stage`; that is the case to close by hand.

## Rules

- Never hand-edit `plugin.json`'s `skills[]` — run `npm run sync`.
- Adding a skill: `skills/<name>/SKILL.md` where the frontmatter `name` equals the directory name, then sync, validate, add a README table row, and bump `plugin.json` `version` (minor for a new skill or a renamed slug, patch for a fix).
- Start a new skill from `templates/SKILL.template.md`; `templates/frontmatter.md` documents every supported field and `CONTRIBUTING.md` holds the authoring rules.

## Current state

Scaffolded 2026-07-24. **Five skills shipped** — `human-voice`, `pretty-hyper-docs`, `pretty-svg-docs`, `reflect`, `security-audit-full-report` — and the repo validates green at plugin version **0.11.0**. `pretty-svg-docs` ships a **31-style** catalog as of 2026-07-25 (14 → 31, folding in the `svg-style-exemplars` reference set), with a full-width **specimen per style** at `docs/samples/<slug>.svg`. `human-voice` carries a **36-pattern** catalog. The scaffold-only `new-skill` example was removed once a real skill landed — its frontmatter reference survives as `templates/frontmatter.md`. Work lands on `stage` (pushed to `origin`, `github-personal:apatheticus/skills.git`) and reaches `main` only by PR; eleven PRs have merged that way, most recently **PR #11** on 2026-07-26 UTC, which shipped the 0.10.0 rename.

**`svg_check.py` gates fidelity, not just safety.** Every other check class is a ceiling (filter depth, bytes, radius) or a legibility floor (font size, contrast) — none of them asks whether a visual *looks like* the style it claims, so a flat, styleless render used to pass clean. Styles now declare their material in `scripts/styles.json` via `require_filter_all`, `min_filter_depth` and `min_elements`, and the checker prints a per-file `NOTE` reporting the chain depth, filter count and drawn-element count it actually found. `deepest chain 1` under a floor of 3 is the tell that a material was faked. Two attributes drive it: `data-specimen="true"` marks a catalog sample (**`min_elements` binds only on specimens** — a README diagram with four boxes is correct at 23 elements, and padding it would be worse output), and `data-style="<slug>"` on a `<filter>` measures that chain against the floor of the style it depicts rather than the file-wide one.

The contact sheet `docs/assets/styles.svg` is **1200×4458** and is gated as its own declared `catalog-sheet` style (`filter_depth: 5`, `bytes_fail: 300 KB`, `min_elements: 620`). It used to be the one asset gated *without* `--style`, which silently gave it global `filter_depth: 1` and made `check_style` skip it entirely — so the single file depicting all 31 idioms was the only one exempt from every fidelity gate, and every material on it was faked. Each tile is now that style's own specimen scaled down rather than a redrawing, so the sheet cannot be less faithful than the catalog it indexes or drift from it. Read that skill's `.prettydocs/prettydocs.md` before editing it — the per-specimen token namespacing, `isolation: isolate` and per-tile `data-bg` are all load-bearing.

Every skill's README visuals were authored by running `pretty-svg-docs` on itself, so they double as the worked example. One resolved style per skill: `human-voice` → `editorial`, `pretty-svg-docs` → `bento-grid`, `reflect` → `neumorphism`, `security-audit-full-report` → `flat-material`. `editorial` and `bento-grid` **require no filter**, and `editorial` forbids blur, shadow and gradient outright, so for those two the fidelity floor is drawn density and typographic craft rather than a filter chain. Don't "fix" a zero-filter NOTE on either: `bento-grid` allows one soft shadow *or* a hairline and never both, and these boards use the hairline.

`pretty-hyper-docs` is the exception and the sibling producer: its visuals are animated **WebPs** rendered through HyperFrames (`docs/assets/*.webp`, capped at 2.5 MB), and its `viz.json` files carry no `producer` or `style` field — which is exactly how `pretty-svg-docs` recognises a foreign visual and offers to adopt it. Its own `audit_visuals.py` does not check `producer`, so it never reports `FOREIGN` against itself.

**Every visual embed is centered, and that is now mechanically enforced.** The shape is a `<div align="center">` wrapper around an `<img>`, *inside* the `pd:viz` marker pair; `audit_visuals.py` (both copies) reports **`UNCENTERED`** otherwise. Three things this depends on, all documented in each skill's `reference/embedding.md` → Centering: GitHub's sanitiser strips `style=`, so `align` on the wrapper is the only mechanism that survives; `align="center"` on the `<img>` itself is inline *vertical* alignment and centers nothing — the footer icon in `house-style.md` uses it correctly for that and must not be "fixed" or flagged; and Markdown `![alt](path)` can never be centered, which is why a marker-pair embed is always an `<img>` tag. This resolved a live contradiction — `embedding.md` prescribed Markdown image syntax while every doc exemplar used `<img … width="820">`, and with no agreement on the embed shape alignment had never been stated. Heroes only *looked* centered because the README header block encloses them; that inheritance is not the rule. Note that embed markup is covered by **none** of the three hashes (`facts_hash`, `src_hash`, `design_hash`), so rewriting an embed re-renders nothing and moves no `viz.json`.

Two traps around that checker. Its `<img>` matcher steps over quoted attribute values instead of stopping at the first `>`, because alt text legitimately contains one (`client -> server`, and the architecture exemplar's placeholder ends `.>`) — a naive `[^>]*` reads that as the end of the tag and reports `UNCENTERED` on a correctly centered embed. And any grep sweep for stray `<img` must be **code-span aware**: both skills' reference docs discuss `` `<img>` `` in prose a dozen times, which a plain substring match reports as markup. The sweep that matters is **65 wrapped images and 4 exemptions**, none of them a `pd:viz` embed: two footer icons in `house-style.md` (inline vertical alignment, correct as written) and two README header logos in `reference/readme.md`, which sit inside a shared header `<div align="center">` alongside the title and badges rather than wrapping alone. All 14 real embeds pass `UNCENTERED`.

**Renamed and re-namespaced in 0.10.0.** `make-pretty-docs` → `pretty-hyper-docs`, `more-pretty-docs` → `pretty-svg-docs`, so the name states the renderer. The `mpd` prefix abbreviated *make-pretty-docs* and mapped to neither skill afterwards, so it retired to `pd`: `pd:viz`, `pd:footer`, **`pd:badges`** (a third marker family that is easy to miss — 28 occurrences), and `mpd.json` → **`viz.json`**. The manifest is `viz.json` rather than `prettydocs.json` because it would otherwise read as a sibling of the design contract, in a directory that already holds HyperFrames' own `meta.json`.

**Three legacy layers are load-bearing and must not be "simplified".** They serve repos already processed by the old skills, which cannot be migrated from here: both audit scripts match `m?pd:` so `mpd:viz` still parses; both fall back to `mpd.json` when `viz.json` is absent; and `pretty-svg-docs` treats `PRODUCER_OWNED = {"pretty-svg-docs", "more-pretty-docs"}` as owned rather than comparing one string. Drop that alias set and the skill reports every visual it ever produced `FOREIGN` and offers to adopt its own prior work. A scratchpad fixture carrying all four old forms at once audits clean.

**Discovery is relaxed; persistence is prescriptive.** The design system is *found* through a five-rung ladder per project (own `.prettydocs/prettydocs.md` → nearest ancestor's → an explicit `DESIGN.md` → a README carrying design language → a broad identity sweep) but *written* to exactly one path. The rule that keeps this safe: **a hit below rung 2 is a source to map from, never the contract** — `design_hash` covers `prettydocs.md` alone, with `design_source_path`/`design_source_hash` recording provenance and warning on upstream movement instead of forcing re-renders. Rung 3 outranks rung 4 deliberately, and every rung tries the project dir before its children (a bare `<project>/*/DESIGN.md` glob skips `<project>/DESIGN.md`). Exclusions and schema sniffing are mandatory: a relaxed search in this very repo finds `skills/reflect/reference/design-system/DESIGN.md`, which is an unrelated skill's *HTML report* system in YAML frontmatter.

**A missing design contract is now a `PROBLEM` with a non-zero exit.** It used to be a stderr note with exit 0, which left every `DRIFT` comparison unreachable while the run still looked clean. It fires only when the project actually embeds visuals. Note that removing one project's contract inside *this* repo does not exercise that path — it inherits the root's and reports `DRIFT` instead; the `PROBLEM` needs no contract in any ancestor, which only a fixture produces.

**`.prettydocs/.gitignore` anchoring is the reason the folder is self-contained.** A pattern containing a slash resolves relative to its own `.gitignore`, so `src/**/_qa/` inside `.prettydocs/` correctly ignores `.prettydocs/src/hero/_qa/`. Verified with `git check-ignore`. That removed the "maintain the `.gitignore` entries" step from phase 6 of both skills, and five projects' root `.gitignore` held nothing else and were deleted.

**The migration was hash-neutral, by construction.** All three hashes are taken over file **bytes**, so relocating an unchanged file yields an unchanged hash: 41 pure renames moved six projects with zero re-renders and zero `DRIFT`. Expect the same of any future move. The `facts_hash` formula is `printf '%s\n'` semantics — every fact followed by a newline, **including a trailing one after the last** — not a plain `\n` join; the docs' prose said otherwise until it was corrected against what the committed manifests were actually hashed with.

**`pretty-hyper-docs`' `lazy-rerender` composition fails its own gate.** `npx hyperframes check` reports `content_overlap` between `#src-eq` and `#src-neq` at t=6.25–11.38s. This predates 0.10.0 (verified against the original committed file) and it means the visual **cannot be legitimately re-rendered** until it is fixed, because `viz-production.md` requires 0 errors before any render. Its `docs/assets/lazy-rerender.webp` is therefore frozen; the 0.10.0 rename changed only its HTML `<title>`, which is never drawn into a frame, so `src_hash` was recorded without a re-render.

**Three visible "MPD" strings survive in the style catalog** — `MPD` in `blueprint`, `SER. MPD-031-A` in `brushed-metal`, `ATTY DKT. MPD-031` in `patent-drawing`, each mirrored into the contact sheet. They read as drafting metadata but almost certainly abbreviate *more-pretty-docs* plus the 31-style count. Left alone deliberately: fixing them means re-authoring three specimens **and** their tiles in the 243 KB contact sheet, which is the most fragile asset here. Decide it on its own merits, not as rename cleanup.

**DEPLOYMENT.md is a signal-gated Tier-1 doc in both pretty-docs skills, as of 0.11.0.** It is listed in Tier 1 but written only when the evidence pass finds a real deploy target — platform config, container/IaC artefacts, a CI workflow that *deploys* rather than merely runs, or migrations plus a runtime service. No signal means the doc is reported `N/A — no deploy target` and nothing is written, which is why a library gets none and why **this repo gets none**: its one workflow validates, it does not deploy. The gate is what keeps the doc honest — a fabricated deploy guide is worse than no guide, because someone follows it during an incident. The spec is `reference/deployment.md` in both skills, and the two copies differ **only** by asset format (the `animated SVG`/`animated WebP` budget line and the one `<img src>` extension), exactly like the existing `architecture.md`/`development.md` pairs; keep it that way.

**`BUDGETS.get()` fails OPEN, which is why `"DEPLOYMENT": 2` in both `audit_visuals.py` copies is load-bearing rather than cosmetic.** An unlisted doc gets `None`, which the checker reads as *unlimited*, silently. Measured on a fixture with three marker pairs in a DEPLOYMENT.md: the pre-0.11.0 checker exits 0 with zero budget findings; with the dict entry it exits 1 with `BUDGET — 3 visuals, budget is 2`. Any future doc type added to the Tier-1 list needs its `BUDGETS` row in the same change, or its budget is unenforced and nothing says so.

**The DEPLOYMENT flagship visual is conditional on a conditional section, and the spec says so deliberately.** The first flagship is the promotion path — but a promotion path only exists above one environment, and the spec's own anti-fabrication rule forbids drawing one that doesn't. On a single-environment project the first flagship goes to deploy ordering instead. This was found by running the spec against a real Railway project rather than by reading it. The same run found that stating **migrate-first-then-deploy** as a universal invariant is wrong — a schema step inside the container's `startCommand` is a different and common model — so the guidance now demands the project's actual ordering and names asserting the canonical one as the most damaging sentence the doc can carry.

**`audit_visuals.py` takes doc *files*, not a project root** — the directory goes in `--root`, so the working form is `--root <dir> <doc>.md …`. Passing the directory as the doc (`audit_visuals.py .`) used to raise `IsADirectoryError` from a bare traceback in both copies, because `p.exists()` is true for a directory and the not-found guard never fired. Both copies now carry an `is_dir()` guard that reports it as a `PROBLEM` with the corrected command and exits 1. Keep the two copies in step: this loop is identical in both and there is no shared module.

**Known contradiction, not yet resolved:** `embedding.md` says a technical doc's `<details>` Mermaid block sits inside the `pd:viz` marker pair, while `reference/architecture.md` puts it outside. The spec's own rationale ("everything between the markers is regenerable wholesale") argues for inside. Deliberately left alone during the centering pass — it is a separate defect and worth its own decision.

**Do not read branch skew as commit counts.** Merges into `main` use a merge commit deliberately — squash or rebase would rewrite the SHAs and permanently diverge the two branches — so `main` shows as one commit "ahead" of `stage` per merge while the content is identical. Compare with `git diff origin/main origin/stage` (empty means in sync); `git rev-list --count` will mislead you.

Validator constraints worth knowing before authoring, all enforced by `scripts/validate.mjs`:

- `parseFrontmatter` reads flat scalar keys only and treats indented continuation lines as `''`, so a multi-line `description: |` block fails the required-key check. Keep `description` on one line (≤1024 chars).
- An unquoted `description` cannot contain a colon followed by a space. Real YAML parsers throw `Nested mappings are not allowed in compact mappings` and installers **skip the file silently**, so the skill goes invisible instead of failing loudly — this shipped undetected in `pretty-hyper-docs` until a live `npx skills add` run exposed it. Use an em dash, or quote the whole value.
- The README Skills table is machine-checked: one row per `skills/<name>`, a link to the skill directory, a non-empty human-written description, and column 3 exactly `npx skills add <slug> -s <name>` (slug derived from `plugin.json`'s `repository`). The table is delimited by `<!-- skills:table start/end -->`; row order is not checked.
