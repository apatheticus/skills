# skills

Public repository publishing agent skills, installable two ways from one source tree.

## Facts

- GitHub: `apatheticus/skills` (personal account). This tree is under `/Volumes/Data/dev/`, so as of 2026-07-27 git auth pins to the `id_personal` SSH key by directory, via `core.sshCommand` in `~/.gitconfig-personal`. The stored `origin` is still `https://github.com/apatheticus/skills.git` and needs no change — `url."git@github.com:".insteadOf` rewrites it onto SSH transparently, so `git remote get-url` reports the SSH form while `git config remote.origin.url` reports the stored HTTPS one. The old `github-personal:` host alias is no longer how this repo authenticates.
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

Doc-visual state is **per project**, and this repo is seven projects: the root plus each
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
- **Never rewrite `plugin.json` with a JSON serializer, not even to bump `version`.** Python's `json.dumps` defaults to `ensure_ascii=True` and turns the `ø` in `Zerø Effort` into `ø` in two places. `npm run validate` still passes — it parses the file, it does not compare bytes — so this reaches CI green-looking and reds there, because the workflow runs `validate.mjs --sync` and then `git diff --quiet` on the result. Bump the version with an `Edit` on the one line, or run `npm run sync` afterwards to restore the file. To reproduce the CI check locally you must **commit first**: `node scripts/validate.mjs --sync && git diff --quiet -- .claude-plugin/plugin.json` compares against `HEAD`, so it fails on any uncommitted change to that file and tells you nothing.
- Adding a skill: `skills/<name>/SKILL.md` where the frontmatter `name` equals the directory name, then sync, validate, add a README table row, and bump `plugin.json` `version` per the rule below.
- **Versioning `plugin.json`: the test is whether the change invalidates work a skill has already produced, not how large the diff is.** Bump **minor** for a new skill, a renamed slug, or any change that stops a skill's *previously-conforming output* from conforming — a tightened gate, a raised floor, a withdrawn relaxation, a newly required marker, manifest field or doc section. Bump **patch** for everything else: a bug fix, a corrected measurement, a loosened or purely additive change (a new style, a new pattern), a re-authored asset that meets the same contract. Where a checker exists the test is mechanical rather than a judgment call — run the new `svg_check.py` / `audit_visuals.py` against the *previous* release's committed assets; anything that goes red means minor. **0.13.0 is the worked example, and it is the case the old wording got wrong:** the glassmorphism rebuild read as a "fix" by every ordinary measure, but it reded `reflect`'s two boards inside this repo and would red any downstream repo the skill had already processed, so it took the minor. Note the asymmetry that makes the old phrasing dangerous — a fix that *loosens* a gate is a patch, a fix that *tightens* one is not.
- Per-skill `SKILL.md` `version` is optional (`pretty-hyper-docs` and `pretty-svg-docs` carry none) and independent of the plugin version. Bump the ones that exist alongside a change to that skill; `plugin.json` is the only version a user installs against, so it is the one the rule above governs.
- Start a new skill from `templates/SKILL.template.md`; `templates/frontmatter.md` documents every supported field and `CONTRIBUTING.md` holds the authoring rules.

## Current state

Scaffolded 2026-07-24. **Eight skills shipped** — `gauntlet-builder`, `human-voice`, `prettier-svg-docs`, `pretty-hyper-docs`, `pretty-plain-docs`, `reflect`, `security-audit-full-report`, `website-security-scan` — and the repo validates green at plugin version **0.22.1**. Read that number off
`git show origin/main:.claude-plugin/plugin.json` rather than the working tree — an
in-flight bump is not a shipped version, and this line went stale by a release because
0.21.0 merged without it moving. `prettier-svg-docs` ships a **32-style** catalog (14 → 31 on 2026-07-25, folding in the `svg-style-exemplars` reference set; → 32 with `soft-vinyl` on 2026-07-28, revised to its v2 spec on 2026-07-29), with a full-width **specimen per style** at `docs/samples/<slug>.svg`. Since 0.19.0 it also ships a **27-type diagram taxonomy** with a **specimen per type** at `docs/samples/types/<slug>.svg`, all authored in `flat-material`. `human-voice` carries a **36-pattern** catalog. The scaffold-only `new-skill` example was removed once a real skill landed — its frontmatter reference survives as `templates/frontmatter.md`. Work lands on `stage` (pushed to `origin`, stored as `https://github.com/apatheticus/skills.git` and rewritten onto SSH per the auth note above) and reaches `main` only by PR. **This line deliberately carries no merged-PR count.** It used to, and the count was structurally unmaintainable: every PR that corrected it made it wrong by one again the moment it merged, which is exactly what happened twice. Get the number from the API instead — `gh pr list --repo apatheticus/skills --state merged --limit 100 --json number --jq 'length'` — and do not reintroduce a written total here.

**`svg_check.py` gates fidelity, not just safety.** Every other check class is a ceiling (filter depth, bytes, radius) or a legibility floor (font size, contrast) — none of them asks whether a visual *looks like* the style it claims, so a flat, styleless render used to pass clean. Styles now declare their material in `scripts/styles.json` via `require_filter_all`, `min_filter_depth` and `min_elements`, and the checker prints a per-file `NOTE` reporting the chain depth, filter count and drawn-element count it actually found. `deepest chain 1` under a floor of 3 is the tell that a material was faked. Two attributes drive it: `data-specimen="true"` marks a catalog sample (**`min_elements` binds only on specimens** — a README diagram with four boxes is correct at 23 elements, and padding it would be worse output), and `data-style="<slug>"` on a `<filter>` measures that chain against the floor of the style it depicts rather than the file-wide one.

The contact sheet `docs/assets/styles.svg` is **1200×4721** and is gated as its own declared `catalog-sheet` style (`filter_depth: 5`, `bytes_fail: 400 KB` — raised from 300 KB at 0.14.0, where the animated sheet reached 97.9% of the old cap, `min_elements: 620`). It used to be the one asset gated *without* `--style`, which silently gave it global `filter_depth: 1` and made `check_style` skip it entirely — so the single file depicting all 31 idioms was the only one exempt from every fidelity gate, and every material on it was faked. Each tile is now that style's own specimen scaled down rather than a redrawing, so the sheet cannot be less faithful than the catalog it indexes or drift from it. Read that skill's `.prettydocs/prettydocs.md` before editing it — the per-specimen token namespacing, `isolation: isolate` and per-tile `data-bg` are all load-bearing.

Every skill's README visuals were authored by running `pretty-svg-docs` on itself, so they double as the worked example. One resolved style per skill: `human-voice` → `editorial`, `pretty-svg-docs` → `bento-grid`, `pretty-plain-docs` → `schematic`, `reflect` → `glassmorphism`, `security-audit-full-report` → `flat-material`. `editorial` and `bento-grid` **require no filter**, and `editorial` forbids blur, shadow and gradient outright, so for those two the fidelity floor is drawn density and typographic craft rather than a filter chain. Don't "fix" a zero-filter NOTE on either: `bento-grid` allows one soft shadow *or* a hairline and never both, and these boards use the hairline.

**`pretty-svg-docs` became `prettier-svg-docs` at 0.19.0, and the rename is honest: it
gained a theory of the diagram it did not have.** The host was a strong documentation
*pipeline* with a weak *drawing* layer — it knew which documents exist, where their
visuals live, how a visual's state is tracked and invalidated, what material a style is
made of and how a loop stays seam-exact, and it had **no** taxonomy, selection rule,
connector grammar, layout grid, complexity budget, focal rule or geometry gate. What
got drawn inside the frame was improvised per run. Merged in from
[`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design) (MIT):
a **27-type catalog** with per-type layout grammar and budgets, **7 semantic patterns**
for when behaviour rather than structure carries the meaning, the six connector rules,
the 4-unit grid, and **87 icons**. The merge is asymmetric on purpose — upstream emits
self-contained HTML and forbids hand-authoring SVG, its motion model is static-first on
a byte-pinned JS controller, and it links Google Fonts; the host wins on all three, and
upstream's `references/animation.md` contributes exactly **one** rule (never animate
layout coordinates, connector routes, `viewBox`, node dimensions or semantic text).
`THIRD_PARTY.md` records the boundary.

**The load-bearing design move is that the new `diagram` check class is opt-in by
`data-diagram` on the root**, the same shape as the existing `data-specimen`. That is
what made a 27-type gate a *minor* rather than a breaking change: re-gating every
committed SVG against the new checker with the unchanged catalog returns a **byte-identical
per-file verdict** — sorted diff against the pre-change baseline is empty. Beware the
unsorted diff: the rename moves `pretty-plain-docs` past `prettier-svg-docs`
alphabetically, so 70 lines look changed and none are.

**The machine half is where the value is, and the prose half could not have carried
it** — the same conclusion `glassmorphism` reached at 0.13.0. Nine checks fire only on a
tagged root: the type resolves in `scripts/diagrams.json`; node/connector/focal/zone
budgets; no diagonal connector; no label mask clipped by a node painted later or sitting
inside the gap floor of any connector; node geometry on the 4-unit grid; no animation
that moves geometry; the legend below every node; and a positive `NOTE` reporting what
it counted (`0 diagonal, 0 off-grid, min label gap 8.0` is what says the grammar was
*applied* rather than merely avoided). `scripts/test_diagram_check.py` is **37 fixtures,
19 negative and 18 positive**, no fixture files on disk. **Semantic attributes make the
ported checks exact rather than heuristic** — upstream's `verify-geometry.py` guesses
that a node is a `<rect>` ≥60×40 and a label plate is 20–120 × 8–14, and its own ADR-0005
concedes the thresholds need revisiting per type; `data-node` and `data-label` mean
nothing is guessed. That is a strict improvement over the source and should be stated as
one.

**Building 27 specimens against the grammar found twelve defects in the grammar, and
reading it would have produced none of them.** The three worst: (1) **every SVG snippet
in `diagram-grammar.md` was not well-formed XML** — `<g data-node>` is an HTML-style
valueless attribute, so copying the file's own examples fails with `not well-formed
(invalid token)` at a line and column naming neither the attribute nor the cause; 36
attributes across 14 files now carry `="true"`. (2) **The grammar's `radius 4/6/8` was an
ERROR under two shipped styles** — `bento-grid` declares `min_rx: 12` and `swiss-minimal`
`max_rx: 2`, in production and not only for specimens; radius is now style-owned and
grid-exempt. (3) **`bento-grid`'s column grid is arithmetically incompatible with the
4-unit node grid**, and there is no fix at the margin or gutter: a 4-divisible column
needs `2m + 5g ≡ 0 (mod 6)`, and the frozen 20-unit gutter fixes `g = 5`, leaving
`2m ≡ 5 (mod 6)` — unsatisfiable over the integers. The node grid wins for `[data-node]`
geometry and only that. Also fixed: §6's own node-box snippet was off §10's grid
(`height="18"`, `x="X+10"`) and specified `rx="3"` below `flat-material`'s floor; §8's
zone numbers were mutually unsatisfiable (≥20 clearance *and* `−40` *and* an 18-tall
plate at `Y+5` yields 17); §10's list read as an enumeration when the checker gates
divisibility; the node-height list omitted 80, which is §6's own canonical box; and the
`label` floor is 18, restated as 20 in three type references.

**Two vacuous-pass holes were closed in the new class, both the shape this repo has
documented twice before.** A file tagged `data-diagram` with `diagrams.json` missing
gated clean with **zero** diagram checks applied and nothing said so — now a loud error.
And `group_box` read only `<rect>`, so a `line`, `scatter` or `radar` node (a polyline, a
circle, a polygon) produced no bounding box at all, the node dropped out, and the legend
check **silently skipped** — a legend drawn inside the plot area would have passed. Both
carry fixture pairs.

**Two config keys were deleted rather than left looking enforced.** `label_gap_max` and
`attach_gap_min` sat in `diagrams.json` and nothing read either. The gap check measures a
label against *every* connector in the file, so it cannot honestly say a label is too far
from the one it belongs to — and `diagrams.json`'s `$note` now records that every key in
it is read. For the same reason `diagram-grammar.md` §4 says outright that **three of the
six connector rules are checked and three are not**: rules 3, 4 and 5 each need an
ownership link between a connector and a node that the drawing does not declare.

**The five plotting types carry `plotted: true`, and the reason is a claim the spec made
that the code did not honour.** §10 said plotted coordinates were exempt from the grid
"because `svg_check.py` reads only `[data-node]` rect geometry" — but on a `bar` or a
`gantt` the datum *is* the node rect's width, so the one number the exemption existed to
protect was the one number being rounded onto a 4-unit lattice. Now declared per type
rather than inferred from `max_edges == 0`, because `venn`, `pyramid` and `quadrant` also
have no connectors and their geometry is a layout, not a measurement.

**Three CI defects, all found by running the steps rather than writing them.**
`audit_visuals.py` resolves each doc against `--root`, so a prefixed path from the repo
root *doubles* and every doc reports `file not found`, while a *bare* `README.md` from
the repo root silently audits the **repo's own** README against a skill's manifests and
reports a visual that exists in neither. The working form is `( cd "$skill" && python3
scripts/audit_visuals.py --root . *.md )`. Second: the SVG gate resolved a style from
`p.parent.name == "samples"`, so all 27 type specimens — under `samples/types/` — fell
through to a `viz.json` that does not exist and were gated **with no `--style` at all**,
leaving every `flat-material` invariant unenforced; an unresolvable style is now a loud
error rather than a silent skip. Third: the 87 icons are *assets*, not boards, and gating
them as visuals reds the build on files that are correct.

**The type specimens are drawn in `flat-material` and the choice was forced, not
aesthetic.** `bento-grid` (`min_rx: 12`) and `swiss-minimal` (`max_rx: 2`) both collide
with a node box at `rx="8"`; `flat-material` declares `min_rx: 4`, which the grammar's
default set satisfies, and its required `feDropShadow` is the one case where the
grammar's "borders, not shadows" defers to a style. One style across all 27 is also the
point of the contact sheet: the variable is the layout grammar and nothing else.
`docs/assets/types.svg` is built by `scripts/build_type_sheet.py` rather than hand-authored
— each tile is that type's own specimen scaled 0.45833, so the sheet cannot drift from the
catalog it indexes. The script namespaces every class, id, `url(#…)`, `href="#…"` and
`@keyframes` name per tile (without it, tile 3's `.name` silently restyles tile 19),
sizes each row to the taller of its pair, and **asserts** all 27 `:root` blocks are
identical rather than assuming it — tokens are deliberately not namespaced, which is only
safe because every specimen resolves to one style.

**The icon set was restructured rather than copied, and the measurement is why.**
Upstream ships 87 icons as one **107 KB** markdown file; as a `reference/` file it would
load on every request touching an architecture diagram — five times the entire skill
body. Split into one file per icon under `assets/` (never loaded), a 7 KB `INDEX.md` for
lookup and a 5 KB `reference/icons.md` for the mechanism, drawing three icons costs
**13 KB against 107 KB**, and drawing none costs 5 KB. Two upstream defects surfaced in
the split: `dagster.svg` carried a hardcoded `fill="#fff"` in a `currentColor` set, and
`hop.svg` shipped an Inkscape `<metadata>` block using `rdf:`/`cc:`/`inkscape:` prefixes
its root never binds — invisibly malformed inside a markdown fence, and `unbound prefix`
the moment it becomes a file.

**The frontmatter was re-cut against the real mechanism, and the old cap was measuring
the wrong thing.** `MAX_DESCRIPTION = 1024` in `scripts/validate.mjs` was self-imposed;
Claude Code caps the **combined** `description` + `when_to_use` at **1,536** in the skill
listing and truncates from the end, which is why the key trigger belongs at the front.
The skill now runs 541 + 986 = **1,528**, names all 27 type slugs, and `validate.mjs`
**fails the build** if a slug in `diagrams.json` is missing from that text — upstream's
own rule, and the reason it matters is that the host previously named four styles of 32
and zero diagram types, so 28 styles and every type were unreachable by name. Two traps
worth keeping: the first draft carried `dependencies: no renderer`, a colon-space that
real YAML parsers reject and installers skip **silently**; and the guidance document's
"roughly 144 words" for upstream's description does not reproduce — it measures 579
chars / 70 words at v2.4.

**The skill's own `lazy-rerender.svg` was re-authored from a card grid into a real
`flowchart`, and that is not decoration.** The repo's standing claim is that every
skill's README visuals were authored by running the skill on itself; a release adding a
diagram grammar and using it in none of its own visuals makes that claim false. It now
gates `9 steps, 3 connectors, 1 focal, 1 zone, 0 diagonal, 0 off-grid, min label gap
8.0`, with the seam proven in pixels at **0 differing pixels** for `t=0` vs `t=12s`
against a same-pose floor of 0. **The control had to be `t=3s`, not the usual midpoint** —
the only animation is `6s`, so `t=6` equals `t=0` by arithmetic and would have read as a
broken harness. Its `alt` text was silently false afterwards (it still described "ten
cells"); nothing checks alt content, so that is a hand check belonging beside any
re-author.

**0.19.1 is the first end-to-end self-run of the merged skill — `prettier-svg-docs` over
its own `README.md` — and the two findings worth keeping are both about a check that
reads green while checking nothing.** (1) **`house-style.md`'s quality gate 6 prescribed a
command that could not perform the two checks its own sentence named.** It said run
`python3 scripts/svg_check.py <file.svg>` and promised "palette conformance, contrast" —
but without `--design` the palette is empty, so every contrast test degrades to the
`text has no data-bg ground in scope` WARN and the off-system-colour gate never fires,
and without `--style` no style invariant or fidelity floor applies. **Both flags fail
open, and the run still prints `0 error(s)`.** Measured on this repo's own hero: 29
warnings without `--design`, `0/0/0` with it. The only signal is one `NOTE` on the *first*
line of output, which `tail` eats — and `tail` is how anyone reads a checker that prints a
line per finding. `viz-production.md:209` had the correct form all along and CI passes both
flags, so the defect was confined to the gate list SKILL.md phase 7 actually sends you to.
Gate 6 now carries the full command and states the fail-open behaviour outright. (2) **The
alt/`<desc>` staleness above recurred immediately, on a different file.** `hero.svg`'s
`<desc>` and its README `alt` both read "the **eight** classes … the eighth being fidelity"
while the board itself draws `9` and "the ninth is diagram" — the drawing was updated at
0.19.0 and its two accessible descriptions were not. `src_hash` covers the SVG's *bytes*,
so editing the `<desc>` moves it and the audit correctly reported `STALE`; what nothing
covers is whether the description still matches what is drawn. Two consecutive re-authors
have now shipped a false accessible name, which retires "a hand check belonging beside any
re-author" as a sufficient answer — the honest options are a machine check comparing drawn
numerals against the alt text, or accepting it as a known unchecked surface and saying so.
Seven further defects were text-only and are visible in the diff: a `31` style badge, a
31-row A–Z table missing `soft-vinyl`, "21 of the 31", "two bundled scripts" three lines
above a block listing three, two survivals of the pre-0.10.0 `DESIGN.md` name for the
design contract, a Layout tree omitting the entire 0.19.0 addition, and SKILL.md's
"Thirty-one named idioms" contradicted by "all thirty-two" twenty lines later. **Patch —
no checker, style or catalog changed, so nothing previously produced stops conforming;
`svg_check.py`, `styles.json` and `diagrams.json` are untouched.**

**0.20.0 closes the open half of that entry — `MISDESCRIBED`, a machine check for
whether a visual's description still matches what it draws — and the reusable part is
the measurement, not the code.** Alt text and `<desc>` are covered by no hash at all
(`src_hash` is bytes, `facts_hash` is the manifest, embed markup is covered by neither),
which is why a re-author that updates the board and forgets the description moves
`src_hash` without moving the falsehood. **Three of the four obvious designs were
measured against the repo's own 16 committed embeds and rejected, and the rejection that
matters is the intuitive one.** Requiring every drawn numeral to appear in the
description gives **146** findings, nearly all contact-sheet chrome and chart axis
ticks. Requiring the reverse — every number in the description to appear on the board —
**produces the identical verdict on the buggy file and the fixed one**, because the
description's *other* number ("a board of eight cells") is unaccounted in both; it would
have nagged forever without once distinguishing the defect, and it is exactly the check
a reasonable person writes first. A cardinal-plus-noun variant gives 4. What ships is
two clauses at **0** findings across the whole corpus: a text node whose *whole content*
is a plain integer must appear in the alt or `<desc>` as a numeral or a number word
(`32` ↔ "thirty-two"), and an ordinal in the description must appear as an ordinal in
the drawing or `facts[]` — **the second gated on the drawing using ordinals at all**,
without which ordinary positional prose ("the first, extract … the second, cluster")
fires on every board that does not number itself. `data-specimen="true"` is exempt and
is the single change that took 146 → 0: a contact sheet's numbers belong to the tiles it
indexes.

**The regression is run against the real defect, not a fixture of it.** `git show
ce0fb1d:` yields the pre-0.19.1 hero, and the check fires on **both** clauses there and
is clean at `HEAD` — a green fixture suite does not substitute for that, because the
fixtures were written after the fix and could encode the wrong shape. The suite itself
was **mutation-tested**: disabling the specimen opt-out, the comma-grouped value regex,
ordinal detection and number-word equivalence each reds a *distinct* fixture, and
restoring returns 29/29. A suite that passes on the first run has proved nothing until
you have made it fail.

**Two structural notes.** The check lives in `audit_visuals.py` rather than
`svg_check.py` because it is the only script that sees the markdown `alt` *and* the
asset — `svg_check.py` never sees a README. And it is a **pure function on strings**,
`describe_parity(svg_text, alt, facts)`, which is what made `scripts/test_alt_parity.py`
possible at all: `audit_doc` has no such seam, which is precisely why `audit_visuals.py`
had **no test of any kind** until now, and why CLAUDE.md already records three defects in
it found by hand. Two smaller traps closed in passing: the specimen opt-out is anchored
on `<svg` rather than the first `>` in the file, since an `<?xml?>` prolog would
otherwise end the slice before the root tag and **silently** reopen all 146; and alt
extraction walks the tag with the quote-stepping idiom `CENTERED` already uses, because
alt text legitimately contains `>` (`client -> server`) — the same defect that once
reported a correctly centered embed as `UNCENTERED`.

**Scope is decided by the asset, not by staging.** `pretty-plain-docs` takes the check
verbatim; `pretty-hyper-docs` is **permanently uncovered**, because a rendered WebP has
no text to extract — that is a structural exclusion, not a deferral, and recording it
here is what stops a later run reading it as drift. Since the two copies share no module,
CI now **diffs the `describe_parity` block between them** and fails on divergence, which
is a stronger answer than the standing "keep the three copies in step" instruction.
**Minor, and the mechanical test decides it**: the corpus measures 0 today, but a
downstream repo whose alt text carries this drift conformed under 0.19.x and reds under
0.20.0 — a tightened gate, which the repo rule names directly. Known gaps, stated rather
than papered over: a range ("sections 1 to 3" does not contain 2) is not expanded, the
two contact sheets get no parity check by design, and the check reads numbers, not
meaning — a description of the wrong subject with no numbers in it still passes.

**`viz.json` gained `diagram_type` and `budget_cuts[]`, and `diagram_type` has three
states rather than two.** A slug means the visual is a diagram of that type; **absent**
means nobody asked, which on a structural visual in a technical doc is an `UNTYPED`
finding; and explicit **`null`** means the question was asked and the honest answer is
none — a hero, a banner, a contact sheet. Without the third state the audit nags forever
about a visual that will never have a type, and an unasked question looks identical to an
answered one. `budget_cuts[]` extends the mechanism `relaxed[]` already uses one layer up:
a softened gate is recorded so the softening is auditable, and a cut is recorded so the
omission is — otherwise content dropped to fit nine nodes and content nobody noticed are
indistinguishable to the next run.

**`gauntlet-builder` is the eighth skill (0.22.0), and 0.22.1 gave it the README that
makes the repo's standing claim true** — every skill's visuals are authored by running
`prettier-svg-docs` on it. Full release detail for the skill itself is in
`.claude/state/stage.md`; what belongs here is what its **first `terminal-minimalist`
run** found, because that style had never been used outside its own specimen.

**The style collides with `diagram-grammar.md` in two places, and both resolve the same
way — §6 gives radius to the style, so the style wins and the divergence gets recorded
rather than silently split.** `styles.json` declares `max_rx: 0`, which makes
`flowchart`'s stadium terminator (`rx=28`) and the grammar's default node box (`rx=8`)
both errors; the terminator's *kind* is then carried by a solid semantic fill and a glyph,
which is this style's own vocabulary doing the job shape was doing. And the grammar's
mandatory rounded elbow (`r=10`) is on this style's `Never` list, so connectors turn hard.
Orthogonality — the part `svg_check.py` actually measures — is unaffected either way, so
neither divergence costs a check. Both are written into
`skills/gauntlet-builder/.prettydocs/prettydocs.md`, which is where the next run will look.

**The 4-unit grid check reads EVERY `<rect>` inside a `[data-node]` group, not just the
node box** — `svg_check.py:931-941` iterates `n.iter()`. So the style's canonical **3-unit
status rail is an error** the moment it appears on a diagram, and the fix is 4 rather than
an exemption. Worth knowing before laying out any board whose style prescribes a
sub-4-unit detail: a hairline, a 2-unit rule, a 3-unit rail are all fine as chrome and all
illegal inside a node group.

**Fidelity here is drawn density and mono discipline, not a filter chain.**
`terminal-minimalist` declares no `min_filter_depth` and *forbids* all four of
`feGaussianBlur`, `feDropShadow`, `linearGradient` and `radialGradient`, so both boards
gate clean at `deepest chain 0, 0 filter(s)` — the same shape as `editorial` and
`bento-grid`, and a zero-filter NOTE on any of the three is correct rather than a faked
material. It is also genuinely the cheapest style measured here: **4.3 KB and 8.1 KB**
against a 60 KB warn.

**One defect only the render showed, and it is a new shape.** A marching-dash return path
written `stroke-dasharray: 16 880` draws one dash and 864 units of nothing, so the *route*
is invisible and only a tick appears to move through empty space. Every gate passed —
seam arithmetic, orthogonality, contrast, the diagram class — because nothing is wrong
with the file; what is wrong is that the resting state carries no information. `8 8` with
a one-period offset march fixes it and keeps the dash semantic. The general form: **a gate
can prove an animation is seam-exact without any of them asking whether the thing being
animated is visible at rest**, which is exactly what the phase-4 pixel read is for.

**Patch, and the mechanical test decides it**: no checker, style, catalog or contract file
was touched, so every previously committed asset re-gates to a byte-identical verdict by
construction, and a downstream repo conforming under 0.22.0 still conforms. Contrast
0.13.1, which was also additive and also a patch, and 0.14.0, which looked identical in
kind and took a minor because it raised a gate.


**`reflect` carries TWO design systems and they are constantly confused. Read this before touching either.** System **A** is the *report* system at `skills/reflect/reference/design-system/`, which styles the HTML report the skill generates — as of 0.12.1 that is **SaaS Pro**, swapped in from Neumorphic Fresh. System **B** is `skills/reflect/.prettydocs/prettydocs.md`, which governs the skill's own README visuals (`docs/assets/hero.svg`, `pipeline.svg`) and is listed in the per-skill style table above. B is *mapped from* A's tokens via a 16-row table, so the 0.12.1 swap left it stale — the README pictures advertised a soft-UI look for a glass-and-gradient report — and **0.12.2 closed that gap**: B was re-derived from `reference/design-system/tokens/colors.css`, style `neumorphism` → **`glassmorphism`**, both visuals re-authored, and the five README badge hexes moved off the old mint/teal ramp onto `brand-600` / `ink-900` / `brand-700` / `success-strong`. There is no longer a stale-by-design debt here. B still records A only as `design_source_path` — `design_hash` covers `prettydocs.md` alone, so a future SaaS Pro refresh **warns** rather than forcing a re-render.

**`glassmorphism` was derived, not chosen, and it is rendered light — which is the opposite of how the catalog draws it.** The derivation is not aesthetic preference: the report's own §1 hero is `sp-glass`, and `--surface-glass` / `--border-glass` are first-class SaaS Pro tokens, so the product already *is* a glass system. But SaaS Pro is light-only and says so, and `--navy-*` is a card surface that must not be promoted to a page ground — so the field is a light lavender page with brand-ramp blobs and the panes are near-white with dark ink. That inverts the style's most common failure mode (the spec warns white-on-glass lands at 1.68:1) instead of fighting it. **Three** divergences are deliberate and documented in B, and a later run must not "correct" them: the pane edge ramp runs `glass` → `brand` rather than white → white, because a white border on a near-white pane over a light page is invisible; the §4 glass recipe's **inset top highlight is omitted**, because on a light pane there is no darker interior for it to separate from and it reads as a stray hairline; and the catalog's **inner rim** is kept but drawn in `brand` at `0.16` rather than white, for the same reason as the first. The second and third are different strokes and the distinction is easy to lose: the omitted one is a horizontal highlight inside the top edge only, the kept one traces the whole perimeter and is what gives the pane thickness. Drop both and the pane has one hairline and no depth.

**Three findings from authoring those two boards, none of which reading the specs would have produced.**
(1) **`pane` is a palette role that is a *measurement*, and it moves whenever the material does.** The ground under a label is the whole pane stack composited over whichever blob is behind it, so the ratio is a *range*, not a number, and `data-bg="pane"` points every label at the worst case. Declaring the role as pure white would pass `--ink-500` at 4.84:1 when it actually renders far lower. It was `#DBDCFB` when a pane was two flat `glass` layers at `0.60` and `0.45`; at 0.13.0 the second layer became a directional tint ramp (`0.46 → 0.22`) and the role moved to **`#CDCEF8`**. The pane did not get darker overall — **its worst corner did**, because a ramp spans `0.24` of coverage across one pane and the flat layer spanned nothing. The role tracks the worst corner, so a directional ramp is a contrast change even when it looks like a lighting change. Heavier coverage is not the fix either: at `0.92` the frost stops being visible and the pane is just a white rectangle.
(2) **Blob cores belong under the panes, not in the gaps between them.** Both intuitive placements are wrong and both were rendered before being rejected: a core in the outer margin reads as a saturated wall down one edge, and a core parked in a gap reads as a glowing bar competing with the type beside it. Cores under the panes give the frost something to reveal, which is the entire payoff, and only the skirts fall in the negative space.
(3) **`svg_filmstrip.py` defaulted its output to the pre-0.10.0 layout** — `<project>/docs/assets/src/<name>/_qa` — while its own docstring and `--help` both said `.prettydocs/src/<name>/_qa`. No `.gitignore` anywhere matches the old path, so every run silently produced a ~50 KB harness staged for commit in a directory the migration had already retired. Fixed in `pretty-svg-docs` as a `default_out()` helper that keeps the legacy path only for a project that still has `docs/assets/src/` and no `.prettydocs/`. It is the only copy — the two sibling skills do not ship this script.

**The catalog `glassmorphism` specimen carried the seam defect its own spec forbids, and 0.12.3 fixed it.** `docs/samples/glassmorphism.svg` animated with `alternate` at `12s` inside a `data-loop-s="12"` loop — **one** half-cycle, so `t=D` was the far end of the drift rather than the start, and the visual jumped at the wrap-around. It now uses symmetric `0% / 50% / 100%` keyframes, which `reference/svg-animation.md` rule 5 calls the reliable form and which returns to origin by arithmetic rather than by parity. `reflect`'s boards already used that form, which is why they never copied the bug. **`svg_check.py` still cannot catch this class** — it only proves each duration divides `data-loop-s` and that the animation is `infinite` — so parity remains a hand check.

The same change had to land in `docs/assets/styles.svg`, because each tile is that style's own specimen scaled down and therefore carries its animation verbatim. Two facts made that safe to repeat: the fix was CSS-only, so **no drawn-element count moved**, and both files re-gated to their pre-edit verdicts. (The numbers in that sentence — glassmorphism's `min_elements` floor of 39 and the sheet at 31 softened — were superseded at 0.13.0; see the photorealism entry below.)

**`glassmorphism` did not look like glassmorphism, and 0.13.0 rebuilt the style around the reason.** It had a frost and nothing else: a blurred copy of the ground clipped to a rectangle, a flat tint, a gradient edge. No refraction, no specular, no grain, no contact shadow — so it read as a translucent panel, not as glass. The rebuild is a **photorealistic** recipe ported from a user-supplied reference (`RECREATE-GLASSMORPHISM.md`): eight cheap passes per surface, in a load-bearing order — real backdrop sample, scrim, tint ramp, one shared light pool, frost grain, top bevel, then outside the clip an asymmetric rim ramp and an inner rim, with a blurred contact shadow laid down before any glass. Both specimens, both contact-sheet tiles, both style specs and both `styles.json` copies moved together, plus `reflect`'s two boards.

**The prose could not have made that stick on its own — the machine half is the fix.** `glassmorphism` required only `feGaussianBlur` at chain depth 1, which is *exactly* what a flat frost has, so a styleless render gated clean and the catalog specimen had been that render since it shipped. It now requires `feGaussianBlur`, `feTurbulence` **and** `feDisplacementMap` at `min_filter_depth: 3`, with the depth ceiling relaxed `1 → 3` to admit the `refract` chain. `min_elements` went `39 → 71`. Note the asymmetry that makes this class of bug survivable: **`require_filter_all` is a floor and `filter_depth` is a ceiling, and raising the floor without raising the ceiling makes the style unsatisfiable** — the specimen errored on all three of its own chains before the `relax` entry went in. The grain pass stayed prose-only deliberately: `feColorMatrix` is too generic a primitive to require without over-fitting the gate to one recipe.

**Tightening a shared style gate is never local, and the blast radius is the thing to check first.** `reflect`'s `hero.svg` and `pipeline.svg` also resolve to `glassmorphism` and passed at chain depth 1, so the same commit had to re-author them or ship them red. They took the **light-ground variant**: the scrim inverts (the catalog darkens its sample so white text survives, this system lightens it so dark text does) and everything else about the stack is unchanged. Their key light is **parked rather than swept** — the catalog animates it, which would be a third motion idea, and System B allows two, both already spent on the drift and the ordered emphasis. It stays a material pass; it just does not move. Each board grew one refracting element to satisfy the floor honestly rather than decoratively: the hero's corpus rail under the session dots, the pipeline's phase rail under the heading.

**Contrast is where this style actually fails, and the measurement has to be a sweep, not a sample.** The specimen's centre panel measured **3.59:1** under `Transform` at a `.46` scrim, where the violet orb core sits. What fixed it was three changes together, not one: scrim `.46 → .58`, the light pool's centre stop `.34 → .20`, and the violet orb's core opacity `.95 → .72`, landing a worst case of **6.10:1** across twelve label boxes at eight phases. Scrim alone was not the lever — past about `.66` the frost stops being visible and the panel is a dark rectangle. The method is in the style spec: render with the label layer hidden and the animation parked at several phases, take the *lightest* pixel per label box for light text (the *darkest* for dark text on a light ground — reflect's boards invert this and getting it backwards silently reports the text colour as the ground), and set `data-bg` to that measured composite.

**A `<use href="#scene">` recipe needs `xmlns:xlink` on the root, and both contact sheets lacked it.** The reference emits `href` and `xlink:href` on every `<use>` for older renderers; dropping the second into a sheet whose root never declared the namespace makes the file **not well-formed**, reported only as `unbound prefix: line N, column M`.

**Two verification facts worth keeping.** The seam check no longer needs the Playwright scroll dance: `chrome-headless-shell` rendering the whole SVG paused at an injected `animation-delay` involves no scrolling at all, so `t=0` vs `t=12s` is directly comparable — and it still catches the `alternate` bug, because under `alternate` the pose at `t=D` is the far end rather than the origin. But **large rasters are not bit-deterministic across chrome invocations**: the 1200×4458 sheet showed 6–14 differing pixels at the seam against a *same-pose* floor of 10–16 and a known-different control of 244,000. Establish the same-pose noise floor before reporting a seam number on anything that big; the three smaller files returned exact 0.

**`soft-vinyl` is the 32nd style and the first added since the catalog was assembled** —
animated in `pretty-svg-docs`, static in `pretty-plain-docs`, ported from a user-supplied
`SOFT-VINYL-SPEC.md` plus a reference primitive sheet. Soft-touch collectible material:
one upper-left light vector for the whole figure, a shadow edge that *glows warm* toward a
subsurface peach instead of going dark, and five primitives (sphere, capsule, cylinder,
slab, contact shadow). **It relaxes nothing** — one `feGaussianBlur` per contact shadow at
the default `filter_depth: 1` — which makes it the fidelity argument in miniature: volume
lives in the fill, so a material this rich needs no filter chain at all. (The counts in
this paragraph were superseded at 0.14.0; see the v2 entries below.)

**Its machine half is a new check class, `gradient_units`, and it exists because `forbid`
cannot see attribute values.** The style's defining invariant is
`gradientUnits="userSpaceOnUse"` on every gradient: the SVG default, `objectBoundingBox`,
resamples the gradient into each element's own bounding box, so a wide capsule ends up lit
as though the light had moved and no other attribute corrects it. `forbid` matches tag
names, so the invariant was unreachable — the same shape of hole as pre-0.13.0
glassmorphism. Two details make the check correct, both fixture-tested: because
`objectBoundingBox` is the **default**, an *omitted* `gradientUnits` is a violation rather
than a neutral absence; and a gradient that inherits via `href`/`xlink:href` is exempt,
because it inherits its parent's units. It also carries a **vacuous-pass guard** — zero
gradients in the file is an error, since "every gradient is `userSpaceOnUse`" is otherwise
trivially true of the flat render the key exists to stop. That is the identical hole
`mono_only` once had, and the checker's own comment says so. The key was provably inert
before `soft-vinyl` declared it: all 64 pre-existing assets re-gated unchanged.

**`soft-vinyl` v2 landed at 0.14.0 and changed what the style *is*, not how it is gated
only.** The user's target was the reference matrix's `terracotta · jitter 0.85 ·
hand-formed` row, so two things moved together: the house ramp went bone → **terracotta**
(`lit #F8D39F`, `albedo #E5B981`, `shade #D69350`, `deep #AD6E2C`, `sss #F2AE78`,
`occ #8E5B2B`), and every form large enough to show it is now a **sampled, wobbled,
re-splined silhouette** rather than a `<rect>` or `<circle>`. Bone survives as the second
named ramp. Both specimens are now **124 drawn elements, 9 outline paths, 33 gradients and
4 shared blur filters** at `min_elements: 120`, 45 KB each, and both gate 0/0/0. The
palette lost two roles: `slablit` and `caplit` are gone, because a hex brighter than `lit`
cannot be derived from a base hue and therefore cannot survive a recolour.

**The machine half is a second new check class, `min_path_curves`, and it is the same hole
one layer down.** `gradient_units` closed "the shading is fake"; nothing asked whether the
*silhouette* was, and a clean render of this same figure — every form a `<rect>`,
`<circle>` or arc-cornered path — passed every other gate. The key counts cubic and
quadratic segments in path `d` data. Three design points, all fixture-tested (eight
fixtures, including implicit coordinate repetition and exponent notation): **arcs
deliberately do not count**, because `A` is precisely what a mathematically perfect rounded
corner uses, so counting it would let the render the floor exists to reject satisfy the
floor; the floor is on the **deepest single path**, not a file-wide total, which makes it
scale-free so a four-form README diagram clears it exactly as a specimen does; and it
inherits `min_filter_depth`'s limitation, that one conforming outline satisfies it. The
previous release's committed specimen returns **0** on every path.

**Verbatim transcription of the wobble recipe was impossible, and measuring first is what
made that visible.** §5.5 fixes arc-length spacing at 3.5px, which puts 423 points on a
680×64 slab and costs **72 KB for one form**; this figure comes to ~265 KB that way against
a 150 KB ceiling, and jitter 0.0 is barely cheaper because the re-spline runs regardless —
the cost is the resample, not the wobble. The spec's own "cost is not a concern, 21,472
bytes raw" was measured on v1, which emitted no paths at all; the v2 reference matrix is
261 KB for 16 forms and never says so. Three documented divergences bring it to 45 KB.
**Cap the point count, not the spacing** — the wobble is indexed by `t = i/n` and is
therefore identical at any n, so only corner fidelity degrades, which is invisible at embed
width. **Emit each outline once and `<use>` it** for base, rim, clip and a slab's depth
copy; this is *not* the `<use>` the generator-first rule forbids, which is about
*instancing* a primitive at a new size and resampling its gradient — here geometry and
coordinates are identical, and a depth copy is the same outline translated, which
`<use y="…">` expresses exactly. And **below ~1px of displacement a form stays a
primitive**: `amp = jitter × size × 0.045`, so at 0.85 a form needs a short dimension of
~39px to reach 1.5px, and a 24px badge or connector gets 0.9px — invisible, at 5 KB. Those
surviving rects are also what keeps `min_rx` reachable, since it collects radii from
`<rect>` only and merely *warns* when nothing is rounded.

**Two more errors in the source spec, and this pair matters more than the first.** (1) The
v1 §6 recolour table had **the saturation direction inverted on every stop** — it saturated
shadows, which reads as cheap plastic — and it was not merely wrong in direction but
**self-inconsistent**: applied to bone's own albedo it cannot reproduce bone, predicting
`lit #FDFCFC` (a desaturated near-white) against the actual `#F7EFE1`, and missing all four
derived stops. The v2 table reproduces **both** named ramps at zero channel delta, which is
the property to check after adding a ramp. (2) §6 supplies a recolouring procedure and §7.3
states "`INK` on a slab face measures approximately 8:1", and **the two are never
reconciled** — a recoloured ramp moves the label ground and the spec keeps the same global
ink. On terracotta the neutral `#4A3B2A` measures **4.08:1** and fails. So `ink`/`inksoft`
are now measurement-driven, not global: both are the ramp's own hue dropped in lightness
until the sweep clears (`#392B18` / `#715533`, worst box 5.19:1, ground 12.29:1 / 6.18:1).

**Contrast here must be measured as a sweep over rendered pixels, and the reason is mass
undulation.** The four clipped ellipses that give a hand-shaped mass its broad tonal
variation composite *over* the base ramp, so the ground under a label is a rendered pixel
and not a declared colour: the worst label box measures **34.80** where the `shade` stop
itself is 35.74. Method — hide the label layer, park the animation at several phases, take
the **darkest** pixel per label box (darkest, because the ink is dark on a light ground;
taking the lightest reports the ground and is the mistake glassmorphism's inverse case
makes easy), then set `data-bg` to what you measured. One stop *position* moved to buy the
margin: the slab's `albedo` stop 70% → **78%**, which the extension rules sanction because
positions are adjustable and colours are not.

**Bounding a seam diff to the cell that changed is what makes a contact-sheet number mean
anything.** Whole-raster, the 1200×4721 animated sheet has a **same-pose noise floor of
21–23k differing pixels** with max channel deltas over 160 — 32 animating tiles on 5.67M
pixels — so a sheet-wide seam of 9–23k is indistinguishable from noise in both directions,
and one of the two controls also lands inside the floor and reads as a pass. Cropped to the
soft-vinyl cell (`610,3328 550×211`, from its own `clipPath` rect) the answer is exact:
floor **0**, seam **0**, controls 5,107 px (4.40%) and 2,391 px (2.06%). The specimen alone
is 0 / 0 against controls of 26,133 and 16,760.

**One pre-existing defect fixed in passing, and it was an accessibility one.**
`pretty-plain-docs`' contact sheet identified itself as the *animated* skill's in three
places, all from the 0.12.0 port: `<title>The pretty-svg-docs style catalog`, the drawn
`PRETTY-SVG-DOCS` kicker, and a `<desc>` reading "thirty-two **animated** style specimens"
while the README alt text beside it said static. Two of the three are the asset's
accessible name and description. Separately, **`soft-vinyl` was never added to either
skill's `.prettydocs/src/samples/manifest.json`** at 0.13.1 — 31 records against 32
specimens, in a file whose own note says "one record per style specimen". Nothing catches
either: CI runs `validate.mjs`, which reads frontmatter and manifests, and never
`svg_check.py` or these manifests. An integrity sweep over the other 31 records found no
drift.

**Two errors in the source spec, both found by measuring rather than reading, and the
reference implementation fails one of them.** Its §10 test 6 states "peak luminance ≤ `LIT`
+ 4", but `LIT` `#F7EFE1` is **not the brightest value in its own palette**: §5.4's slab
starts at `#FBF5EA` (relative luminance 91.75) and §5.3's cylinder cap at `#FDF8EE` (94.19)
against a threshold of 90.94 — so `vinyl-primitives.svg` itself peaks at 92.66 and fails.
Restated as **peak ≤ the brightest declared stop**, which is provable for a shading-only
render because a gradient only interpolates between the stops you declared; a specular
highlight is precisely what introduces a value brighter than all of them. Our specimen
peaks 92.55, *below* the reference. **0.14.0 dissolved this rather than restating it**: the
v2 recipe drops both hardcoded stops (neither is derivable from a base hue, so neither
survives a recolour) and uses `LIT` in their place, which makes `LIT` the brightest value in
the palette again and the original test correct by construction. Our specimen now peaks
**69.05**, `LIT`'s luminance exactly and not one level over. Note the measurement trap that
comes with it: the *ground* is lighter than every stop in either ramp, so a whole-canvas
peak reports the ground and proves nothing — sample inside form interiors, and beware a
probe box that clips ground above a short bar. Separately, §5.4's slab axis
`(x+0.30w, y) → (x+0.45w, y+h)` is **aspect-dependent**: that `0.15w` horizontal run is
subordinate to the height only while the slab is roughly as tall as it is wide, which every
slab in the reference is. At 680×64 it dominates, the ramp completes inside the first sixth
of the width and the rest clamps to `SHADE` — the form reads flat and dark. Clamped to
`min(0.15w, 0.45h)`, which reduces to the published formula exactly when the slab is
square-ish.

**The contact sheets reflowed rather than simply gaining a tile, and 33 cells is odd.** 32
style cells fill exactly 16 rows, so the summary cell no longer pairs with a style; it now
spans **both columns on a row of its own** rather than leaving a visible hole beside it.
Height went **4458 → 4721**. Inserting alphabetically between `skeuomorphic` and
`swiss-minimal` flips the column of every later cell, and a cell's position is written in
**four** places — the `clipPath` rect, the inner `<g transform="translate(…)">`, the border
rect and the `sh-slug` text — which must move together; verified programmatically at 0
mismatches across all 32 cells in both sheets. Both still gate to **0 errors, 27 warnings,
34 softened**, identical to each other and to their pre-edit verdicts.

**A seam control has to sit inside the window that actually moves.** The first control —
`t=3s` of a `6s` settle — returned 0 differing pixels and read as a broken harness. It
wasn't: the keyframes hold `scale(1,1)` from 0–58%, so `t=3s` *is* `t=0` by construction.
Controls at 66 / 76 / 86% give 23,758 / 27,007 / 12,934 differing pixels, all bounded to
the Transform slab's box, against a seam of exactly 0. A hold-then-event animation makes
the usual "diff the midpoint" control worthless.

**The static sibling does not raster-match the animated one at rest, and that is not a
defect.** They differ by 41,607 pixels at a max channel delta of **7** — and it is *not*
noise: the same-file floor is exactly 0 rendered twice, and the number reproduces exactly.
Chrome composites the animated layer and that shifts gradient dithering document-wide,
including over forms nowhere near the animated group. Every drawn element and every
gradient/filter def is provably identical between the two files. The static skill's claim
is "gates to the identical verdict", never "renders identically" — do not upgrade it to the
stronger one on the strength of a pixel diff.

**0.13.1 is the first use of the amended bump rule, and the rule decided it mechanically
rather than by judgement.** A new style is purely additive: no existing style's gate moved,
the new `require` key is inert for the other 32, and all 64 pre-existing assets gate
identically — so **patch**. The per-skill `SKILL.md` field is ordinary semver and took a
minor (`pretty-plain-docs` 0.2.0 → 0.3.0), which is consistent because the invalidation
rule governs `plugin.json` alone and says so.

**0.14.0 is the other half of that worked example, and together they are the clearest
statement of the rule.** Same style, same skills, same *kind* of change — a style's material
was revised and its two specimens re-authored — and it took a **minor** where 0.13.1 took a
patch, for one reason: this one raises a gate. The test is mechanical, so run it rather than
arguing it. Two verdict sweeps over all 76 committed assets, the first with the new checker
against the *old* catalog and the second with both new: the checker patch alone moves
**nothing** (76 files, 0 errors, 385 warnings, 138 softened, per-file diff empty), and the
catalog change moves exactly the two previous-release soft-vinyl specimens from `0/0/0` to
`2/0/0`. Reding the previous release's own conforming output is the definition of minor.
The re-authored specimens then re-gate `0/0/0` and the full sweep returns to the identical
baseline, which is the other half of the proof: the floor is met honestly, not by relaxing
anything.

**One count reference was deliberately left reading stale.** Both `prettydocs.md` files say
a hairline grid "applied thirty-one times reads as one finding rather than thirty-one" —
that is an illustration of `(xN)` aggregation and never tracked the catalog: no aggregated
warning count equals 31, and the largest is 52. Editing it would move `design_hash`, which
the skill's own facts call a trigger that invalidates every visual in the repo. The
*genuine* count claims were fixed (`all 31 idioms`, `31 sets of --ground and --ink`, `the
31 catalog styles`), which did move both `design_hash`es — and there the consequence split:
`pretty-svg-docs`' hero **draws** "31 idioms" so it was really re-authored and re-gated,
while `pretty-plain-docs`' hero draws no count at all, so its manifest was re-stamped with
nothing to render. Same rule as 0.13.0, and the split is the useful part.

**One pre-existing defect fixed in passing: `pretty-plain-docs`' `styles.md` said "The nine
fields" over a table of eight.** `Motion character` was dropped when the static sibling was
ported at 0.12.0 and the section heading was never renamed, in two places.

**`design_hash` moved for two projects and two visuals were re-stamped without re-rendering — deliberately.** Correcting the softened count in `pretty-plain-docs`' `prettydocs.md` moves that project's `design_hash`, which the skill's own facts call a RE-RENDER trigger that "invalidates every visual in the repo at once". Its `hero` and `lazy-rerender` depend on nothing that changed, so their manifests were re-stamped and the assets left alone; regenerating them would produce the same bytes. `reflect`'s `design_hash` also moved and there **both** visuals were genuinely re-authored. The rule is right as a default and the exception is narrow: re-stamp without re-rendering only when the contract edit is a corrected measurement rather than a design decision, and say so where a later run will see it.

**One pre-existing defect surfaced and was fixed in passing: `pretty-plain-docs` had three assets failing their own gate on a raw `#000000`.** Its `prettydocs.md` carries a 7-role palette where `pretty-svg-docs` carries 71 — the sibling's *Catalog swatches* section, which includes `sw-black`, was never ported at 0.12.0 — so the same `flood-color="#000000"` that passes in one skill errors in the other. It had been red since it shipped, and nothing caught it because CI runs `validate.mjs` (frontmatter and manifests) and never `svg_check.py`. It also made a documented claim false in three places: the static sheet was said to gate to *the same verdict as the animated original* while actually gating 1 error. Fixed by routing the hex through a declared token (`--sh-shadow` in both sheets, `--shadow` in `flat-material.svg`), which is the remedy the checker's own error message offers and needs no `design_hash` move. The palette asymmetry itself is left alone — it causes no failure now.

**Verifying a seam in pixels needs a specific method, and the obvious one gives a wrong answer.** Playwright *element* screenshots of two filmstrip phases sit at different scroll positions, and the sub-pixel offset shifts the whole raster: `#p0` vs `#p6` reported the sheet's seam as 28–64% differing with a max channel delta over 200, *worse* than the mid-loop control, which is impossible. Two captures of the same element return 0 differing pixels, which is how you tell a positional shift from capture noise. What works: inject a style override re-posing **one** element's `animation-delay`, hold `window.scrollTo` fixed, take **viewport** screenshots, crop an integer box. That gives seam `0 / 494,860` px on the specimen and `0 / 2,290,800` px on the sheet, against controls of 60% and 47% at `t=6s`. Always diff a known-different pose — a seam result of 0 means nothing without it.

**`alternate` appears nowhere else in the repo's SVGs**, confirmed against `HEAD` rather than the working tree; all 32 specimens carry `data-loop-s="12"` and the other 31 have no `alternate` in any form. The one other `git grep` hit, `skills/reflect/docs/assets/hero.svg:75`, is a *comment* explaining why that file avoids it. Separately, 13 `@keyframes` blocks across the catalog do not return to origin at `100%` — all are full `rotate(360deg)` sweeps (visually identical at both ends), tiled-pattern wraps like `digital-rain`'s 240px fall, or the travelling-pulse idiom (`swiss-minimal`'s `.sm-dot` runs `translateX(0 → 370px)` with no clip or fade, then resets). Rule 5 addresses *yoyo* motion specifically, so these are a different question, unadjudicated and deliberately untouched — "fixing" them would change six specimens' intent.

**The SaaS Pro swap had to hand-write the component layer, because SaaS Pro ships no CSS.** All 43 of its components are React `.jsx` with inline JavaScript style objects and **zero class names** — `components/display/Table.jsx` is the proof. Neumorphic Fresh had given `reflect` a 58-class `nf-*` CSS API that got inlined verbatim; there was no equivalent to copy. So `design-system/components.css` is a **hand-derived CSS projection** of the subset a static report renders — **74 distinct classes across 28 families**, prefix `sp-*` because `tokens/motion.css` already owns it — transcribed from each component's style object. Recount with `grep -ohE '^[[:space:]]*\.sp-[a-z0-9_-]+' components.css | tr -d ' .' | sort -u | wc -l` rather than trusting this line. 19 components are deliberately **not** ported (Modal, Toast, Sidebar, forms, …) and the file says so in its header, so absence never reads as oversight. Two documented divergences: `.sp-btn`'s base *is* the outline variant so an unmodified button is never unstyled, and `.sp-page` has no upstream counterpart because nothing else supplies `--grad-page`.

**The report lost its light/dark toggle in that swap, deliberately.** SaaS Pro's tokens are light-only — no dark block, no `prefers-color-scheme`. `--navy-*` is a *card surface for dense data* (its DESIGN.md §2 "Two worlds, one page"), not a page theme, and promoting it to page level would mean inventing dark neutrals, lines and washes the system does not define. So `data-theme` and the OS-preference default are gone, and `report-guide.md` now says outright that one must not be invented. What replaced it: light page, and **`sp-card--dark` under every chart and every table**. A chart still has to hold up on *both card grounds*, which is what the chart references' own `dark` prop models — that is not the same claim as "both themes".

**Nothing machine-checks any of this, which is why the real-run step is the gate.** `scripts/validate.mjs` checks frontmatter, `plugin.json` sync and the root README table; the one workflow runs only that. No CSS lint, no HTML lint, no contrast check. A dangling `sp-*` reference or an unresolved `var()` leaves CI green and renders silently unstyled. Two `comm` diffs cover it — the class list in `report-guide.md` against the classes defined in `components.css`, both directions, and every `var(--*)` in `components.css` against the tokens actually defined — and **the sp-* one must union in `tokens/motion.css`'s nine `@keyframes` names**, or the nine legitimate `sp-fade-up`/`sp-draw`-style references in the prose read as dangling classes. The class list in `report-guide.md` is enumerated **completely, with no trailing "…"**: the old open-ended `nf-*` list is exactly what let a reference dangle unnoticed.

**Generating a real report found five defects that reading the CSS could not, and all five were in the hand-derived layer.** (1) **Every type class set an explicit light-ground colour with no dark-card override**, so a heading inside the dark card DESIGN.md *mandates* for every chart and table rendered at **1.30:1** and a paragraph at **1.83:1** — invisible. `.sp-card--dark` sets `color`, but a child `.sp-h4` with its own `color` beats inheritance. (2) A blanket `.sp-ring > svg { transform: rotate(-90deg) }` broke two charts at once: it squashed a polar gauge to 149×170 against a 170×149 viewBox *and* double-rotated a donut whose SVG already carried the transform, moving its first segment to six o'clock. The rotation belongs to dash-array rings only (`ProgressRing`, `DonutChart` set it inline upstream; `Gauge`/`SegmentGauge` compute `startAngle 225` themselves), so it is now opt-in as **`sp-ring--turn`**. (3) Small white text on `--grad-brand` fails — 4.02:1 and 3.68:1 at the outer stops — and DESIGN.md's own "white at ≥600 weight, ≥12px" does **not** rescue it, because WCAG large text needs ≥18.66px bold. (4) `--ink-400`/`--text-muted` is **2.88:1** on white and four roles used it as text. (5) Three of five soft badge grounds fail at 11px/700 (`--success` 2.43:1, `--danger` 3.07:1, `--info` 3.01:1); upstream had already fixed exactly one by hardcoding `#B45309` for warning text, so the fix extends that into a **`--*-strong` ramp** defined in `components.css` — the `tokens/` files stay a literal subset of the download so a refresh is a diff.

**Two verification traps specific to this swap.** The vendored CSS deliberately contains the strings `data-theme`, `prefers-color-scheme` and `@import` **inside comments** telling a reader not to reintroduce them, so `grep -c data-theme report.html` returns non-zero on a perfectly correct report — check `data-theme=`, `@media[^{]*prefers-color-scheme` and `^\s*@import\s` instead. And the `sp-*` cross-check between `report-guide.md` and `components.css` must **union in `tokens/motion.css`'s nine `@keyframes` names** and use a character class including `_`, or `sp-fade-up` reads as a dangling class and `sp-card__title` truncates to `sp-card`.

**`security-audit-full-report` was rewritten at 0.15.0 from a proof-of-concept into a delegating orchestrator, and the defect it fixes was hidden by a sentence in its own spec.** Its §4a said *"it fans out its own sub-agents; their output stays out of this context"* — flatly contradicted by `security-audit/SKILL.md:33`, *"Subagents do NOT write files — they return results to you via the Task tool."* `security-audit` is built to be run **by** the primary agent and to collect every hunter, validator and per-finding verifier return into whoever invoked it. Running it inline cost a **measured 67 KB floor of skill text per cycle** (its SKILL.md + four phase files + `report-schema.json`, up to 112 KB once `ATTACK-CLASSES.md` routes to the domain companions) *before any agent reported* — and `/loop` multiplied that by `max_cycles` in one accumulating context. The false claim is why the problem survived: it read as already-solved. **When a skill asserts something about context, check it against what the skill it drives says about context.**

**Nesting was verified, not assumed, and the verification changed the design.** The whole rewrite rests on a subagent being able to invoke a skill *and* let that skill fan out — if sub-subagents were capped, the audit would collapse to serial single-context hunting inside the runner, which is **worse** than the context cost, because coverage is the entire point. A throwaway probe settled it: one spawn, then three concurrent spawns from a single message returning out of launch order (2017/2474/3261 ms against launch order A,B,C — serial cannot produce that), plus a successful `Skill` load. So §4a delegates to one cold `general-purpose` agent that runs `security-audit` verbatim, re-implementing nothing. **`Explore` and `Plan` are declared without the `Agent` tool** and cannot fan out — spawning a cycle agent as either silently destroys the audit, which is why SKILL.md names the type.

**`/loop` was removed deliberately and must not be reinstated as a convenience.** It re-injects both skill stacks every firing and keeps every cycle in one context; it was buying only a re-fire trigger, and `ledger.md` already supplied the resumability. Cycles now run spawn → commit → decide. The heavy briefs moved to `reference/{cycle,report,verify}-agent.md`, **passed by path and never read by the orchestrator** — that, not SKILL.md's own diet, is where the win is: SKILL.md only fell 15.8 → 11.2 KB, while 29 KB of brief plus the whole `security-audit` stack now loads exclusively in agents that die with it.

**The dedup key changed from prose to structure, and that dissolved a correctness smell rather than merely relocating it.** v1 keyed on `root_cause` + `title`, then had to tell the model to fuzzy-merge — and justified that rule by its *effect on termination*: "under-merging here would keep the counter from ever reaching convergence." That biases toward merging exactly when convergence is slow, so the loop can report `converged` having absorbed genuinely new findings. v2 keys on the set of **sink `file::scope` pairs in `trace`** — data `security-audit`'s own Phase 6 verifies against source — so no model judgment is involved at all. `line` is excluded on purpose: it moves when unrelated code above it changes. The residual error is deliberately one-directional — one bug reachable through two sinks counts twice, resets the counter and buys a cycle, which `max_cycles` bounds; nothing would bound the opposite error. `scripts/audit_state.py` owns all of it (`init`/`dedupe`/`commit`) plus a `selfcheck` asserting the full decision path. **CI runs `validate.mjs` only and never this**, same blind spot as `svg_check.py`. A v1 engagement is refused loudly (`legacy_ledger: true`, nothing written) because its prose keys cannot be converted, and silently continuing would recount every known finding.

**A live end-to-end run of 2.0.0 against a real repo found ten defects, and 0.15.1 fixes the two that could make the loop declare convergence it had not earned. Both live in the same place — the counter's *inputs*, which the one-directional argument above never covered.** That argument is about the dedup *key*, and it is sound; what it does not touch is anything that advances the counter without a cycle having earned it. (1) `commit` was not idempotent. The harness may fire a completion notification more than once — **cycle 1 notified four times** — and SKILL.md §4b said "when the agent returns, run commit", so a literal orchestrator re-dedups the run against an index that already holds it, scores `new_medplus: 0`, and increments. Two spurious notifications converge a one-cycle engagement. It now tracks `committed_runs` in the index and returns `{"duplicate": true}` having changed nothing. **Measured against a copy of the live engagement, with the pre-fix code as the control on an identical copy: pre-fix the duplicate took the counter 0 → 1 and rewrote `status: done` back to `running`; post-fix, nothing moved.** An index written before the fix is migrated on read by seeding `committed_runs` from per-finding `run` numbers — which is what caught that duplicate — but a run that committed *zero* findings leaves no trace there, so one case stays unguarded on an in-flight engagement and none on a fresh one. (2) §4c told the orchestrator to commit a failed cycle as "a valid zero-new cycle". **An audit that ran and found nothing is evidence toward convergence; an audit that died before validating anything is evidence of nothing**, and scoring the second as the first converts a crash into a clean bill of health. The cycle agent now returns `validated` and §4c routes on it: `false` → `commit --unvalidated`, which logs the run, keeps its candidates on disk and leaves the counter alone. Notably the *cycle agent caught this itself* during the run and refused to let its own dead cycle be counted — the brief was more careful than the orchestrator spec it served, which is the argument for putting the judgment in the brief and the enforcement in the script. Both fixes are patch-shaped on their own: a 2.0.0 engagement still resumed correctly after them.

**0.16.0 then fixed the third and worst of that set, and it is the one the design certified as impossible.** §4b's "nothing would bound the opposite error" is an argument about the dedup *key* — and the key was under-counting. Keying on the sink presumes **one defect per scope**, and a function holds several: across the 50 confirmed findings of that engagement, **five pairs of genuinely distinct defects collapsed onto one key**, and the lower-severity one was silently absorbed every time. One collapse was cross-run. The engagement escaped a false convergence only by luck — the absorbed findings happened to be `low` or intra-run, so `new_medplus` was untouched; a run-2 *medium* sharing a scope with any run-1 finding would have gone straight into the counter. **The key is now the attack path's endpoints — entrypoint and sink, each part tagged with its role** — which separates three of the five, including the only cross-run one. The other two share their whole path and **no trace-derived key can separate them**, because the trace *is* the path. **Widening further is worse, and this is measured rather than argued: including the propagation steps separates nothing more and creates a *new* collision**, because one finding's entrypoint can be another's propagation step and a set of locations cannot tell the roles apart. So two flanking rules carry the residual, both erring in the bounded direction: **dedup is cross-run only** (a collision inside one already-adjudicated `findings.json` is two defects on one path — which all four intra-run collisions here actually were), and **every cross-run suppression is named in the ledger** with both titles and the key. The key still makes a judgment; it no longer makes one invisibly. Re-run over the engagement's own two `findings.json` against the pre-fix code on an identical copy: run 1's new med+ **25 → 27**, run 2's suppressions **2 → 0**, index total **45 → 50** — which closes the gap that run's report recorded between the page (50) and the index (45). **0.16.0 is a minor, and the trigger is the key change rather than the behaviour change**: the index stores keys and not traces, so old keys cannot be recomputed, and `commit` now refuses an index carrying an older `key_version` (`stale_key_version: true`, nothing written) exactly as it refuses a v1 ledger. A 2.x engagement can no longer be resumed, which is previously-produced work ceasing to conform. Bump `KEY_VERSION` whenever `finding_key` changes, or the next change to it silently recounts every known finding instead.

**0.16.1 closes the fourth, and it is the one that falsifies the skill's own opening sentence.** *"Your session holds the ledger. Nothing else"* holds on the designed path and breaks on the error path: an agent deep in the tree that reports with `SendMessage(to: "general-purpose")` is addressing an agent **type**, not a name — nothing answers to it, delivery fails, and **the harness promotes that agent's full report to the top-level session rather than dropping it**. Observed five times in one engagement, ~100k tokens of hunter reports, one of them a seven-finding report with its coverage section. The delegation boundary is real; it has an unguarded escape hatch, and the hatch points at the single context the design exists to keep empty. **`security-audit` never mentions `SendMessage` in any of its eight files**, checked rather than assumed — so this is emergent agent behaviour, not an upstream instruction, which makes prompt-level containment the only available lever. `cycle-agent.md` now carries the rule as literal prompt text and **requires it to be propagated into the prompts `security-audit` writes for the agents it fans out**, the same propagation the output-directory override already needed and for the same reason: a leak cannot be closed in a prompt you never wrote. SKILL.md states the failure mode where the orchestrator will see it and gives the one instruction the brief cannot — **a report from an agent you did not spawn is not a return value**; don't act on it, relay it, or fold it into the ledger. Two limits stay stated rather than papered over: an instruction is not an enforcement mechanism, and the 73-minute cycle-3 stall that followed the bounce remains **inferred, not proven** — closing the bounce is not evidence the stall closed with it. **Patch**: prompt text only, no contract or key change.

**0.16.2 closes the fifth — the trigger that made the first two reachable.** §4b said *"when the agent returns, run commit"*, and the completion notification is unreliable **in both directions**: cycle 1 notified **four times** for one completion, cycle 3 notified **zero** times, having already been stopped (completed) with the notification simply lost. The first is what D2 turned into false convergence; the second hangs the loop forever waiting for something that already happened. **The obvious fix — poll for `run-N/findings.json` — is wrong**, because a cycle that dies before adjudicating legitimately produces none, so its absence cannot distinguish "still working" from "died" and treating it as a reason to keep waiting reintroduces the hang from the other side. A new **§4a′** establishes completion from the system cheapest-first: take the notification if it came (duplicates are free now that `commit` is idempotent); otherwise watch `run-N/` for new bytes, since `security-audit` writes candidate files as it goes — **the stalled cycle had written 13 of them, so the signal was there and unread**; and after a long quiet stretch, send the cycle agent a one-line probe. §4a therefore **names it `cycle-<N>`**: an unnamed agent has no address, which is the same root cause as D1's bounce, and an agent that already finished replies from its transcript and says so. Two guard rails, the second found by reading the tool's own docs rather than by reasoning: **never spawn a second cycle agent for the same run** (two audits writing one `run-N/` corrupt the artifact being waited on), and **never call `TaskOutput` on a cycle agent** — for a local agent its output file is a **symlink to the full subagent transcript**, so the obvious way to check on a quiet agent dumps into the orchestrator exactly what the design exists to keep out. The natural fix for a stall is a trap for the skill's central claim. **Patch**: prose only.

**0.17.0 takes three at once, and only one of them is mechanical — the other two are honesty defects, which is the class this skill is most exposed to.** (1) *The report files are a deliverable and the briefs never said so.* A cycle agent hit the guard against agents writing unsolicited report/summary `.md` files, read it as a wall, and reported that `REPORT.md` and `FINDINGS-DETAIL.md` "exist only in this cycle's transcript" — which is to say, were destroyed when it died. The guard has a deliverable exception and this is exactly it. Harmless there, because nothing downstream reads those two files, but **the report agent's HTML sits behind the same guard** and there it is the entire output; both briefs now claim the exception explicitly. (2) *There was no vocabulary for an engagement a human stopped.* `STOP_REASON` accepted `converged` or `max-cycles-reached`, and both assert the cycle budget was spent — so an operator halting at 3 of 5 (an ordinary thing to do when a cycle costs two hours) had to be reported as a completeness that was never established or a budget that was never spent. **`halted-by-operator` is the third value**, read off the ledger rather than inferred: `status: running` at report time *is* the halt. The enforcement is in `report-agent.md` §3a — anything but `converged`, or any run committed `--unvalidated`, requires a **completeness banner** above the counts saying the findings are a floor, and the brief is told to re-derive that from `ledger.md` rather than trust the value it was handed. The engagement that surfaced this stopped at 3 of 5 with run 2 still adding 6 new med+ findings and run 3's 33 candidates unadjudicated. (3) *Wall-clock was never disclosed.* §3 stated the cycle count and never the hours; measured, cycles 1–3 ran **2h 18m / ~50m / ~1h 50m**, so `max_cycles: 5` is most of a working day and a session limit **will** interrupt it — cycle 2 proved that, and the ledger absorbed it correctly with only the agent's return lost. Both facts are now stated in preflight, the second as the feature it is. **Minor, and the trigger is the banner**: a `max-cycles-reached` report built under 3.0.2 conformed then and does not now, which the repo rule names directly as a newly required doc section. Neither README visual moved — `halted-by-operator` is a stop reason and not a ledger status, so the two-mode status band (`running → converged | max-cycles-reached → done`) is still exactly right, and `audit_visuals.py` re-gates both `OK` with no hash movement. Three stale strings fixed in passing, all left behind by earlier fixes in this same session: the README's cycle-agent return contract still said "5 fields" in two places after `validated` was added, its selfcheck sentence claimed "duplicate sinks collapsed within a run" two clauses before correctly saying such pairs are kept as two, and `report-agent.md` still described the index as "keyed structurally by sink `file::scope`" after 0.16.0 moved the key to the path's endpoints.

**0.18.0 fixed the bundled template, and the interesting part is *why* it published wrong numbers rather than that it did.** `assets/template.html` shipped three severity tiers where the audit's `report-schema.json` permits five — verified at the source, `overall_severity` is exactly `['informational','low','medium','high','critical']` — so any engagement finding either extra tier forced the report agent into per-render surgery across the CSS, the KPI row, the donut, the legend and the filter bar. **That is the defect; the published error was its symptom.** A real report had both tiers hand-added to four of those five surfaces and missed the KPI row, so its severity tiles summed to **49 against a stated total of 50**, with the Low tile carrying a "plus 1 informational" caption under a number that excluded it. The fix is therefore not "add two tiers" — it is **one `SEV` table that drives all five surfaces at once**, with the KPI tiles marked `data-sev` and filled from it, so extending a tier can no longer reach four places out of five. A tier with **no** findings hides its own tile and filter button rather than rendering a zero, which is what makes the visible tiles sum to the stated total by construction, and `.kpis` moved to `auto-fit`/`minmax` so the row reflows at anything from 4 to 7 tiles. The brief now says **touch nothing** about tiers, which it could not honestly say before.

**Rendered, not reasoned — three fixtures through `chrome-headless-shell` with `--dump-dom`.** All-five (3/14/22/10/1): visible tiles sum 50 = stated 50, five donut segments, six filter buttons, hero chip promotes to `3 critical`. Two-tier (2 high, 3 medium): the three empty tiers hide both tile and button, sum 5 = 5, chip reads `2 high`. Zero-finding: renders clean with no tiles, no `conic-gradient()` — the donut needed an explicit `if(!total) return`, because `acc/total*360` is `NaN` at zero and the old three-tier code had the same latent hole. The second scaling defect in the same file was the card stagger: `i*0.02s` with `animation-fill-mode: both` was sized for ~17 findings, and at 50 the last card sat at opacity 0 for **1.26s** — blank at load, in a screenshot and in print. The previous engagement's builder measured that and capped it, but **in the generated file**, so the next engagement over ~20 findings would hit it again; the cap (`Math.min(i*0.02,0.3)`) is now upstream, measured at max delay `0.3s` for 50 cards and `0.08s` for 5. **Both defects share one shape — a per-engagement workaround for a template-level bug — which is the argument for fixing them here rather than in the brief.**

**One pre-existing accessibility failure fixed in passing, in the same file.** Badge text is 11px/700, below WCAG's large-text threshold, so every badge needs ≥4.5:1 against its own soft ground — and `.badge.medium` was `#B5730A` on `#FEF3D9` at **3.51:1**. It is now `#B45309`, which measures **4.55:1** and is the hex SaaS Pro already hardcodes for warning text in `reflect`'s `components.css`, so the two skills agree. The two new tiers were measured before being chosen rather than after: critical `#6D28D9` on `#EDE6FE` is **5.87:1** (above the existing high badge at 4.70) and informational `#333759` on `#EDEEF6` is **9.92:1**. Critical takes the purple accent deliberately — it has to read as *beyond* `--danger`, not as more of it — and informational takes the ink ramp, which is blue-tinted rather than grey, because it is the one tier that is not a concern. **Minor**: a report built under 3.1.0 that found a critical or informational finding does not match what the template now emits, and the `F[]` ordering contract changed from `high→low` to `critical→informational`.

**0.18.1 closes the last of the ten, and the fix is mostly a deletion — because 0.18.0 is what made the deletion correct.** `verify-agent.md` served a local page over `python3 -m http.server`, loaded two browser skills, then drove it: screenshot the hero, expand a card, click a severity filter, click a run filter. On the engagement that surfaced this it verified **nothing**, because the browser stack it assumed was not installed (`npx @playwright/mcp install-browser chrome-for-testing` is a no-op, `playwright install chrome` hits a sudo gate). The obvious fix is to name a fallback browser. **The better one is to notice that most of what it drove no longer varies.** The template's tiers, donut, filters and badges are fixed behind 0.18.0's `touch nothing` rule and were proved against three fixtures; clicking a filter per engagement re-tests code that cannot have changed. What varies is `F[]` and the placeholders — transcribed fresh each run — so the pass is now a **static reconcile** of that array against the builder's returned counts, plus **one render**.

**One render, not zero, and the reason is a defect class grep cannot see.** A finding title containing `</script>` yields a file that parses fine as HTML and renders a page with no findings on it. Measured on a fixture whose only defect was exactly that: every static check passed clean — 0 unreplaced placeholders, 0 literal `undefined`, `F[]` still 7 entries by regex — while the render returned `id="kpiTotal">—`, one malformed card, and `Uncaught SyntaxError` on the console. **A surviving em dash in `kpiTotal` is the signature of a dead script**, since every number on that page is written by the script. The render costs one command — `chrome-headless-shell --dump-dom` on the `file://` URL, no server, no Playwright, no MCP, no install gate. Verified that `file://` is fine here (the block that motivated the `http.server` applies to the extension-driven path, not `--dump-dom`), that the script executes before the dump, and that page errors surface on stderr as `INFO:CONSOLE … Uncaught` — distinct from Chrome's own `cv_display_link_mac` startup noise, which the brief names so it is not mistaken for a page error. Every assertion in the brief's table was run verbatim against a 4-tier fixture: per-severity card counts off `article.finding`, stated total off `#kpiTotal`, visible tiles summing to it (7 = 7), and the empty tier hiding **both** its tile and its filter button.

**Honesty about the render is a separate field from the verdict, on purpose.** With no headless Chrome anywhere, the pass runs the reconcile alone and returns `render_checked: false` with `browser: "none"` rather than failing, faking it, or installing something — and SKILL.md §5 tells the orchestrator to repeat that caveat instead of sending the verifier back for a browser. Folding it into `verified` would have made a browserless machine block a good report; folding it into silence is what the old brief effectively did. The return grew 6 → 8 fields. **Patch, and the mechanical test decides it**: no artifact on disk changes shape — the report, ledger and index are untouched — so nothing previously produced stops conforming; the changed contract is a transient agent return consumed once at the end of an engagement. Contrast 0.17.0, which was minor because a *report* built under the old rules no longer conformed.

**The reusable half is the coupling, and the brief states it rather than assuming it.** Skipping the interaction pass is only sound while the template stays untouched; if a future run hand-edits it, the frozen-and-fixture-tested premise is gone and so is the argument. So divergence between the generated file's script or CSS and `assets/template.html` is itself a `blocking` finding — the one check that guards the reasoning behind all the others.

**0.18.2 reorders §4a′'s ladder, and the reordering is what 0.16.2 should have written.** That release established completion cheapest-first and put the notification at rung 1 because a notification that arrives is free. **The ranking was on the wrong axis** — cheap only matters among signals that are *correct*, and across every cycle observed the notification has fired four times for one completion and not at all for three others, so it has never once been both. The filesystem has been right every time and costs one `ls`. Rung 1 is now `run-N/`, the notification drops to rung 2 with **never wait on it**, and the probe stays last; `findings.json` present and no longer growing is named as the strongest signal short of the agent, with the caveat that the brief rewrites that file during verification. **§5 inherits the same ladder**, because the report agent runs on the same channel and did the same thing — it finished, wrote its HTML, and never notified, and a notification-first orchestrator went looking **an hour** after the deliverable was complete. One portability bug fixed with it: `find -newermt '-20 minutes'`, which 0.16.2 offered as an alternative to `ls -lt`, errors under `bfs` on macOS. **Patch** — prose only, no artifact on disk changes shape, same class as 0.16.2 itself.

**0.18.3 fixes the defect that D5 turned out to be, which is not the defect D5 was filed as.** A cycle agent reported that *"the harness blocked the Write tool for report-shaped .md files"* and, citing the one-strike rule for permission denials, did not retry — so `REPORT.md` and `FINDINGS-DETAIL.md` were lost with the agent. 0.17.0 answered it by asserting the deliverable exception in both briefs, and the standing conclusion was that the real fix belonged in the hook. **There is no hook.** Swept afterwards: every `Write`-matching hook on that machine is `PostToolUse` — user settings, the target project's `settings.local.json`, and the `impeccable` plugin, all three — and `PostToolUse` runs after the tool succeeds and cannot stop it; no `deny` or `ask` permission rule touches `Write` or `.md` at all. Nothing blocked the write. **The agent declined it, described its own reluctance as a denial, and then applied a rule for real gates to a gate that was never there.** The re-run under an identical configuration wrote both files normally, which is the tell: a hook is deterministic and a self-imposed reluctance is not, so *non-reproduction was itself the evidence* — and it is the evidence that a hook-side hunt would have kept explaining away. Both briefs now make the agent separate a **real denial** (returns an error from the tool; quote it verbatim, one strike applies, report the gate) from **its own reluctance** (no error attached; not a gate, one strike does not apply, write the file), and require the exact error text whenever a blocked write is reported — so a future misdiagnosis of this shape cannot be stated without producing the thing that would disprove it. **Patch** — prose only. The general lesson is worth more than the fix: **an agent's account of *why* it failed is not primary-source evidence about the system**, and this one sent a defect log to the wrong layer for two releases.

**Its two README visuals took different treatments, and the split is the reusable part.** `two-mode.svg` drew four statements that the rewrite made false (`/loop` firings, "start the loop — then stop for this turn", "§4a – §4d", "runs every firing"), so it was genuinely re-authored — text-only, verified at **46 drawn elements and the identical 0-error/28-warning verdict** before and after, then rendered headless to confirm no string overflowed its card. `hero.svg` draws the convergence counter and the stop rule, neither of which changed, so when its manifest's stale dedup *fact* was corrected its `facts_hash` moved and its `src_hash` deliberately did not — re-stamped, not re-rendered. That is the same narrow exception 0.13.x established, and `audit_visuals.py` is what surfaced the stale fact; reading the SVG would not have. Both `viz.json` hash formulas were confirmed against their recorded values before editing (`facts_hash` = `printf '%s\n'` over the facts, `src_hash` = the SVG bytes, `design_hash` = `prettydocs.md` bytes) rather than assumed. **0.15.0 is a minor**: a v1 `ledger.md` no longer drives the skill correctly, which is previously-produced work ceasing to conform.

**`reflect` still has no report template, and that is the largest remaining gap in the skill.** There is no `assets/template.html` — the sibling `security-audit-full-report` ships one — so every run re-authors the eight sections, the nav, the detail cards and the filters from `report-guide.md` prose. **That prose is where the aesthetic actually lives**, which is why a design-system swap is mostly a prose edit. Adding a template is a separate decision, not a swap detail.

`pretty-hyper-docs` is the exception and the sibling producer: its visuals are animated **WebPs** rendered through HyperFrames (`docs/assets/*.webp`, capped at 2.5 MB), and its `viz.json` files carry no `producer` or `style` field — which is exactly how `pretty-svg-docs` recognises a foreign visual and offers to adopt it. Its own `audit_visuals.py` does not check `producer`, so it never reports `FOREIGN` against itself.

**Every visual embed is centered, and that is now mechanically enforced.** The shape is a `<div align="center">` wrapper around an `<img>`, *inside* the `pd:viz` marker pair; `audit_visuals.py` (all three copies) reports **`UNCENTERED`** otherwise. Three things this depends on, all documented in each skill's `reference/embedding.md` → Centering: GitHub's sanitiser strips `style=`, so `align` on the wrapper is the only mechanism that survives; `align="center"` on the `<img>` itself is inline *vertical* alignment and centers nothing — the footer icon in `house-style.md` uses it correctly for that and must not be "fixed" or flagged; and Markdown `![alt](path)` can never be centered, which is why a marker-pair embed is always an `<img>` tag. This resolved a live contradiction — `embedding.md` prescribed Markdown image syntax while every doc exemplar used `<img … width="820">`, and with no agreement on the embed shape alignment had never been stated. Heroes only *looked* centered because the README header block encloses them; that inheritance is not the rule. Note that embed markup is covered by **none** of the three hashes (`facts_hash`, `src_hash`, `design_hash`), so rewriting an embed re-renders nothing and moves no `viz.json`.

Two traps around that checker. Its `<img>` matcher steps over quoted attribute values instead of stopping at the first `>`, because alt text legitimately contains one (`client -> server`, and the architecture exemplar's placeholder ends `.>`) — a naive `[^>]*` reads that as the end of the tag and reports `UNCENTERED` on a correctly centered embed. And any grep sweep for stray `<img` must be **code-span aware**: all three skills' reference docs discuss `` `<img>` `` in prose a dozen times, which a plain substring match reports as markup. The sweep that matters is **85 wrapped images and 3 exemptions** as of 0.12.0, none of them a `pd:viz` embed: one README header logo per skill in `reference/readme.md`, each sitting inside a shared header `<div align="center">` alongside the title and badges rather than wrapping alone. **State the method with the number or it cannot be reproduced**: classify each `<img>` by whether it falls inside a match of `audit_visuals.py`'s own `CENTERED` regex, over git-tracked `.md` files, with fenced code blocks and code spans stripped first. Strip the fences and the footer-icon exemplars in `house-style.md` drop out of the count — they are illustrations of markup, not markup — which is why an earlier figure here read 4. All 17 real embeds pass `UNCENTERED`.

**Renamed and re-namespaced in 0.10.0.** `make-pretty-docs` → `pretty-hyper-docs`, `more-pretty-docs` → `pretty-svg-docs`, so the name states the renderer. The `mpd` prefix abbreviated *make-pretty-docs* and mapped to neither skill afterwards, so it retired to `pd`: `pd:viz`, `pd:footer`, **`pd:badges`** (a third marker family that is easy to miss — 28 occurrences), and `mpd.json` → **`viz.json`**. The manifest is `viz.json` rather than `prettydocs.json` because it would otherwise read as a sibling of the design contract, in a directory that already holds HyperFrames' own `meta.json`.

**Three legacy layers are load-bearing and must not be "simplified".** They serve repos already processed by the old skills, which cannot be migrated from here: all three audit scripts match `m?pd:` so `mpd:viz` still parses; all three fall back to `mpd.json` when `viz.json` is absent; and `pretty-svg-docs` treats `PRODUCER_OWNED = {"pretty-svg-docs", "more-pretty-docs"}` as owned rather than comparing one string. Drop that alias set and the skill reports every visual it ever produced `FOREIGN` and offers to adopt its own prior work. A scratchpad fixture carrying all four old forms at once audits clean.

**Discovery is relaxed; persistence is prescriptive.** The design system is *found* through a five-rung ladder per project (own `.prettydocs/prettydocs.md` → nearest ancestor's → an explicit `DESIGN.md` → a README carrying design language → a broad identity sweep) but *written* to exactly one path. The rule that keeps this safe: **a hit below rung 2 is a source to map from, never the contract** — `design_hash` covers `prettydocs.md` alone, with `design_source_path`/`design_source_hash` recording provenance and warning on upstream movement instead of forcing re-renders. Rung 3 outranks rung 4 deliberately, and every rung tries the project dir before its children (a bare `<project>/*/DESIGN.md` glob skips `<project>/DESIGN.md`). Exclusions and schema sniffing are mandatory: a relaxed search in this very repo finds `skills/reflect/reference/design-system/DESIGN.md`, which is an unrelated skill's *HTML report* system in YAML frontmatter.

**A missing design contract is now a `PROBLEM` with a non-zero exit.** It used to be a stderr note with exit 0, which left every `DRIFT` comparison unreachable while the run still looked clean. It fires only when the project actually embeds visuals. Note that removing one project's contract inside *this* repo does not exercise that path — it inherits the root's and reports `DRIFT` instead; the `PROBLEM` needs no contract in any ancestor, which only a fixture produces.

**`.prettydocs/.gitignore` anchoring is the reason the folder is self-contained.** A pattern containing a slash resolves relative to its own `.gitignore`, so `src/**/_qa/` inside `.prettydocs/` correctly ignores `.prettydocs/src/hero/_qa/`. Verified with `git check-ignore`. That removed the "maintain the `.gitignore` entries" step from phase 6 of every pretty-docs skill, and five projects' root `.gitignore` held nothing else and were deleted.

**The migration was hash-neutral, by construction.** All three hashes are taken over file **bytes**, so relocating an unchanged file yields an unchanged hash: 41 pure renames moved six projects with zero re-renders and zero `DRIFT`. Expect the same of any future move. The `facts_hash` formula is `printf '%s\n'` semantics — every fact followed by a newline, **including a trailing one after the last** — not a plain `\n` join; the docs' prose said otherwise until it was corrected against what the committed manifests were actually hashed with.

**`pretty-hyper-docs`' `lazy-rerender` composition fails its own gate.** `npx hyperframes check` reports `content_overlap` between `#src-eq` and `#src-neq` at t=6.25–11.38s. This predates 0.10.0 (verified against the original committed file) and it means the visual **cannot be legitimately re-rendered** until it is fixed, because `viz-production.md` requires 0 errors before any render. Its `docs/assets/lazy-rerender.webp` is therefore frozen; the 0.10.0 rename changed only its HTML `<title>`, which is never drawn into a frame, so `src_hash` was recorded without a re-render.

**Three visible "MPD" strings survive in the style catalog** — `MPD` in `blueprint`, `SER. MPD-031-A` in `brushed-metal`, `ATTY DKT. MPD-031` in `patent-drawing`, each mirrored into the contact sheet. They read as drafting metadata but almost certainly abbreviate *more-pretty-docs* plus the 31-style count. Left alone deliberately: fixing them means re-authoring three specimens **and** their tiles in the 243 KB contact sheet, which is the most fragile asset here. Decide it on its own merits, not as rename cleanup.

**DEPLOYMENT.md is a signal-gated Tier-1 doc in all three pretty-docs skills, as of 0.11.0.** It is listed in Tier 1 but written only when the evidence pass finds a real deploy target — platform config, container/IaC artefacts, a CI workflow that *deploys* rather than merely runs, or migrations plus a runtime service. No signal means the doc is reported `N/A — no deploy target` and nothing is written, which is why a library gets none and why **this repo gets none**: its one workflow validates, it does not deploy. The gate is what keeps the doc honest — a fabricated deploy guide is worse than no guide, because someone follows it during an incident. The spec is `reference/deployment.md` in all three skills. The `pretty-hyper-docs` and `pretty-svg-docs` copies differ **only** by asset format (the `animated SVG`/`animated WebP` budget line and the one `<img src>` extension), exactly like the existing `architecture.md`/`development.md` pairs; keep it that way. The `pretty-plain-docs` copy diverges further and deliberately — see the static-sibling entry below.

**`BUDGETS.get()` fails OPEN, which is why `"DEPLOYMENT": 2` in all three `audit_visuals.py` copies is load-bearing rather than cosmetic.** An unlisted doc gets `None`, which the checker reads as *unlimited*, silently. Measured on a fixture with three marker pairs in a DEPLOYMENT.md: the pre-0.11.0 checker exits 0 with zero budget findings; with the dict entry it exits 1 with `BUDGET — 3 visuals, budget is 2`. Any future doc type added to the Tier-1 list needs its `BUDGETS` row in the same change, or its budget is unenforced and nothing says so.

**The DEPLOYMENT flagship visual is conditional on a conditional section, and the spec says so deliberately.** The first flagship is the promotion path — but a promotion path only exists above one environment, and the spec's own anti-fabrication rule forbids drawing one that doesn't. On a single-environment project the first flagship goes to deploy ordering instead. This was found by running the spec against a real Railway project rather than by reading it. The same run found that stating **migrate-first-then-deploy** as a universal invariant is wrong — a schema step inside the container's `startCommand` is a different and common model — so the guidance now demands the project's actual ordering and names asserting the canonical one as the most damaging sentence the doc can carry.

**`audit_visuals.py` takes doc *files*, not a project root** — the directory goes in `--root`, so the working form is `--root <dir> <doc>.md …`. Passing the directory as the doc (`audit_visuals.py .`) used to raise `IsADirectoryError` from a bare traceback in both copies, because `p.exists()` is true for a directory and the not-found guard never fired. All copies now carry an `is_dir()` guard that reports it as a `PROBLEM` with the corrected command and exits 1. Keep the three copies in step: this loop is identical in all of them and there is no shared module.

**`pretty-plain-docs` is the static sibling, added at 0.12.0.** Same content engine, same
eight Tier-1 docs, same `pd:` markers and hash triad, same 32-style catalog — the visuals
are **static SVG** and nothing moves. Its own style is `schematic`, one of the ten that
relax nothing, so its visuals prove the base gates rather than a softened set.

**Five things about it that are load-bearing:**

- **`data-loop-s="0"` was already the siblings' documented static marker**, so it was kept
  rather than replaced. Its only permitted value here is `0`, and that single declaration
  *is* the whole animation ban — no new attribute was invented. The ban fires on five
  paths, all verified: a non-zero loop, `@keyframes` + `animation:`, an **unreferenced**
  `@keyframes` (the residue of a careless conversion, invisible to a grep for
  `animation:`), any SMIL tag including `<animateMotion>` which the animated sibling
  permits, and a bare `animation: none`.
- **Its `svg_check.py` has six check classes where the sibling's has eight.** The seam and
  motion-accessibility classes are gone; the ban lives inside **structural**, because it is
  a rule about what a committed file may contain. `divides()`, `SMIL_TAGS`-driven seam
  logic and `Stylesheet.reduce_rules`/`reduce_selectors()`/`reduce_hidden()` were deleted.
  Everything else is byte-for-byte the same gate, and `scripts/styles.json` is **identical**
  to the sibling's — not one of its per-style keys was animation-related.
- **Mutual `FOREIGN` across the three skills is the intended migration path, not a bug.**
  `PRODUCER_OWNED = {"pretty-plain-docs"}` with **no legacy alias**, because this skill has
  no prior work to own. Running it on an animated repo offers to re-author the visuals as
  stills; running `pretty-svg-docs` on a repo it processed offers to animate them. Verified
  in both directions: 3 `FOREIGN` each way, nothing else reported. Do not "fix" this by
  adding the siblings to `PRODUCER_OWNED`.
- **It diverges from both siblings on two documented points, deliberately.** Every
  structural visual carries a `<details>` Mermaid source **including README body diagrams**
  (the siblings give README embeds rich alt text and no Mermaid) — an animated visual holds
  meaning in motion that no graph can express, while a static diagram is *only* structure,
  so the machine-checkable source is both achievable and worth more. And the `<details>`
  block sits **outside** the `pd:viz` pair, matching every doc exemplar; the sibling
  `embedding.md` puts it inside, which is the contradiction noted below, and this skill
  states one position and applies it everywhere.
- **`reference/charts.md` is net-new** — there was no axis, tick, legend or series
  vocabulary in either sibling to port. Its gate is provenance: a plotted value is allowed
  only if the next run can **recompute** it from the repository's source. *Recomputable*,
  not merely *committed* — a committed coverage report or benchmark log satisfies the weaker
  reading and is still forbidden, because it is a snapshot of a run rather than a property
  of the code. Where the two readings disagree the Forbidden table wins.

**The 31-specimen conversion was mechanical and is provably faithful.** Every specimen
animated via CSS `@keyframes` only — **zero SMIL anywhere in the skill**, so `<animate` and
`dur=` are permanent false negatives when grepping. Conversion folds each
`@media (prefers-reduced-motion: reduce)` rule's resting values onto the base rule, then
deletes the keyframes, the animation declarations and the reduce block. The reduce block is
the *specification* for the resting state, not a hint. Fold, don't delete: **nine specimens
sit at exactly `min_elements`**, so removing an element breaks the floor. Result: all 32
pass at their own style and **not one drawn-element count changed**; the contact sheet gates
to the identical verdict as the animated original (**0 errors, 27 warnings, 34 softened**
as of 0.13.0, 31 before it),
at 283 KB rather than 294 KB (260 / 271 KB before soft-vinyl's v2 revision, 229 / 243 KB before `soft-vinyl` landed at all). That equivalence is the evidence nothing about a style's
fidelity depended on it moving.

Two traps when de-animating a *spec* file rather than an asset. Dead-class detection must
compare against the **sibling** copy — the specs use illustrative class names that were
never defined (`.sh-d`, `.face`, `.ring`), and stripping tokens on "no rule selects it"
silently deletes them. And **an XML comment cannot contain `--`**, which bites precisely
when documenting this skill's own flags: `<!-- --refresh-viz … -->` makes the file
not well-formed, and the checker can only report `invalid token` at a line and column.

**`data-bg` fails quietly and is the one gate that does.** The value must name a palette
role exactly as the Palette table spells it. A name that does not resolve is a **`WARN`,
not an `ERROR`** — *"text has no data-bg ground in scope — contrast unchecked"* — and the
contrast floor is then not applied to that text at all. `data-bg="accent"` against a role
called `accent-primary` reads as a clean pass. Treat that WARN as a failure. Found by
running the skill against a real repo, not by reading the checker.

**The DEPLOYMENT signal must be searched across the whole tree, case-insensitively.** The
same real-repo run found `Docs/Deploy/DEPLOYMENT.md` — a full production deploy guide — in a
repo with no platform config, no container, and a CI workflow that only validates. Checking
the root alone reports `N/A — no deploy target` on a repo that has one, and then risks
authoring a **second** deploy doc beside the real one, which is the defect the
design-system ladder already forbids for `prettydocs.md`.

**Known contradiction, not yet resolved:** `embedding.md` says a technical doc's `<details>` Mermaid block sits inside the `pd:viz` marker pair, while `reference/architecture.md` puts it outside. The spec's own rationale ("everything between the markers is regenerable wholesale") argues for inside. Deliberately left alone during the centering pass — it is a separate defect and worth its own decision.

**Do not read branch skew as commit counts.** Merges into `main` use a merge commit deliberately — squash or rebase would rewrite the SHAs and permanently diverge the two branches — so `main` shows as one commit "ahead" of `stage` per merge while the content is identical. Compare with `git diff origin/main origin/stage` (empty means in sync); `git rev-list --count` will mislead you.

Validator constraints worth knowing before authoring, all enforced by `scripts/validate.mjs`:

- `parseFrontmatter` reads flat scalar keys only and treats indented continuation lines as `''`, so a multi-line `description: |` block fails the required-key check. Keep `description` on one line (≤1024 chars).
- An unquoted `description` cannot contain a colon followed by a space. Real YAML parsers throw `Nested mappings are not allowed in compact mappings` and installers **skip the file silently**, so the skill goes invisible instead of failing loudly — this shipped undetected in `pretty-hyper-docs` until a live `npx skills add` run exposed it. Use an em dash, or quote the whole value.
- The README Skills table is machine-checked: one row per `skills/<name>`, a link to the skill directory, a non-empty human-written description, and column 3 exactly `npx skills add <slug> -s <name>` (slug derived from `plugin.json`'s `repository`). The table is delimited by `<!-- skills:table start/end -->`; row order is not checked.
