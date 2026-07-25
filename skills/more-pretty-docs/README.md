<div align="center">

# more-pretty-docs

**A Claude Code skill that writes a repository's standard docs and authors their key diagrams as seamless-loop animated SVG — with nothing to install.**

<!-- mpd:badges start -->
[![License: MIT](https://img.shields.io/badge/License-MIT-e0a33e.svg)](../../LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-skill-12324f)](SKILL.md)
[![Dependencies](https://img.shields.io/badge/dependencies-python3_only-12324f)](#install)
[![Styles](https://img.shields.io/badge/style_catalog-14-12324f)](reference/styles.md)
<!-- mpd:badges end -->

<!-- mpd:viz name="hero" src="docs/assets/src/hero/" facts-hash="d57b421c12d6dc8c0e189681569e63ca02047f9c90a9a59e1fbd50b121f104bf" src-hash="740e3c500f25d312eb7c8dfbea59a24648cebbc3ba683569746528dd97eb09a1" -->
<img src="docs/assets/hero.svg" alt="Animated overview on a drafted cyanotype sheet: three stations — AUTHOR writes docs/assets/name.svg, GATE runs svg_check.py until it reports zero errors, COMMIT ships that same file — with a dash travelling between them and a dashed return edge for a visual that fails the gate. There is no render station: the committed asset is its own source, and python3 is the only requirement." width="820" />
<!-- mpd:viz end -->

</div>

## What this is

more-pretty-docs creates and maintains a repository's standard documentation —
README, ARCHITECTURE, DEVELOPMENT, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY,
SUPPORT, plus tier-2 files on request — and makes it look designed. Each run
derives a frozen per-repo design system, picks a named visual style, then writes
the docs' key diagrams as animated SVG by hand.

It is the sibling of [`make-pretty-docs`](../make-pretty-docs), which does the same
job with animated WebP rendered through the HyperFrames toolchain. Same content
engine, same honesty-over-polish doctrine. The difference is the visual layer:

|  | `make-pretty-docs` | `more-pretty-docs` |
| --- | --- | --- |
| Visual format | animated WebP | animated SVG |
| Needs installing | HyperFrames CLI, ffmpeg, img2webp | nothing beyond `python3` |
| Build step | HTML composition → MP4 → WebP | none; the `.svg` you write is the asset |
| Failure mode | preflight STOP on a missing toolchain | warns, never aborts |
| Visual style | derived from the product | 14-style catalog, or derived |
| Asset budget | ≤ 2.5 MB | ≤ 150 KB |

Use `make-pretty-docs` when you specifically want WebP. Use
[`update-docs`](https://github.com/apatheticus/skills) for plain text-only docs.
Otherwise use this one — and note that every visual on this page was authored and
gated by the skill itself.

## What a run produces

- Tier-1 docs written for their audience, with facts grounded in the repo's actual
  code, manifests, and CI.
- `docs/assets/*.svg` — the committed visuals, each within a per-doc budget
  (README: hero + up to 3; technical docs: 1–2 flagship each;
  SECURITY/CODE_OF_CONDUCT: one attention banner).
- `docs/assets/src/DESIGN.md` — the frozen design system every visual derives from,
  including the resolved style spec.
- `docs/assets/src/<viz>/mpd.json` — each visual's facts, hashes and parameters.
  There is no composition source next to it, because the asset *is* the source.

LICENSE and NOTICE are never visualized or reformatted.

## The style catalog

A **style** is the look-and-feel idiom every visual in a repo is rendered in. Pass
`--style <slug>`, or let the skill derive one from the product the way it always
has. Style owns *form* — shape, material, type, composition, motion. The product's
own brand tokens still own the *palette*.

<!-- mpd:viz name="styles" src="docs/assets/src/styles/" facts-hash="9fa63f8c48ad178bf922877ee47854485801c6b4246ee2d434fe09f59456a8b9" src-hash="eb1d54baee0b070a402ee90ca46396001e2b8706c138aa0dbb7390b066ab2540" -->
<img src="docs/assets/styles.svg" alt="A drafted contact sheet of fourteen labelled tiles, each built in the style it names: swiss-minimal, flat-material, skeuomorphic, neumorphism, claymorphism, glassmorphism, neo-brutalist, editorial, maximalist, y2k-retrofuturist, terminal-minimalist, blueprint, schematic and bento-grid. Every tile carries one motion characteristic of its style — a marching rule, a material ripple, a breathing LED, a stepped nudge, a travelling signal. A note panel states the rule: style owns form, brand tokens still own the palette." width="820" />
<!-- mpd:viz end -->

Every tile above was built and gated for real. If a style could not be produced
clean at tile scale, its catalog entry was wrong and got fixed. Aliases resolve
without asking (`brutalist`, `glass`, `soft-ui`, `tui`, `bento`, …), a recognisable
free-form idiom is synthesized into a full spec and frozen into the repo's
`DESIGN.md`, and anything unresolvable prompts exactly one question. Details in
[`reference/styles.md`](reference/styles.md).

Where a style's look genuinely fights a soft gate, the style wins and the gate
softens to a **declared floor, never off** — four styles relax anything at all, and
every relaxation is printed, recorded in `mpd.json`, and named in the run report.
Structural and truth gates never soften.

## How re-authoring is decided

Every embed carries hashes for the facts it depicts, the asset itself, and the
design system. A later run rewrites a visual only when one of those changed, its
asset is missing, or `--refresh-viz` forces it:

<!-- mpd:viz name="lazy-rerender" src="docs/assets/src/lazy-rerender/" facts-hash="6212d58383a4f88e8afae3c5ae3d7168f6ab9620428169a5fe2e4476f8257292" src-hash="9b947d02145931b833626ab315b439ee6be678b61047a5d4b9be6e0998368721" -->
<img src="docs/assets/lazy-rerender.svg" alt="Animated decision flow on a drafted sheet: the stored facts, src and design hashes feed a single question — do they all still match? When everything matches the visual is reused and zero files are written. When one hash has moved, that visual alone goes back through the gate, is committed, and its hashes agree again. A prose-only edit moves no hash and re-authors nothing." width="820" />
<!-- mpd:viz end -->

Because the style spec lives inside `DESIGN.md`, changing the style moves
`design_hash` and re-authors every visual in the repo. The plan phase says so, with
a count, before touching anything.

## Install

```bash
npx skills add apatheticus/skills --skill more-pretty-docs
```

Or as part of the Claude Code plugin bundle:

```
/plugin marketplace add apatheticus/skills
/plugin install apatheticus-skills@apatheticus
```

Or copy the folder straight into a repo's skill directory:

```bash
cp -R skills/more-pretty-docs /path/to/repo/.claude/skills/more-pretty-docs
```

The skill is self-contained. At run time it needs `python3` for its two bundled
scripts and nothing else — no renderer, no `ffmpeg`, no CLI, no network. A browser
tool is optional: it is used to look at the rendered pixels, and when none is
available the run says the pixel review was skipped rather than implying it passed.

## Use

| Command | Effect |
| --- | --- |
| `/more-pretty-docs` | Full tier-1 pass: content + visuals |
| `/more-pretty-docs readme security` | Only the named docs |
| `/more-pretty-docs check` | Read-only audit of content and visual staleness |
| `--style <slug>` | Pick a catalog style (or a recognisable free-form idiom) |
| `--style auto` | Re-derive the style from the product, ignoring the stored slug |
| `--refresh-viz` / `--no-viz` / `--budget <doc>=<n>` / `--brief` / `--full` | Modifiers — see `SKILL.md` |

## Layout

```
more-pretty-docs/
├── SKILL.md              entry point: preflight, workflow, budgets, audience matrix
├── reference/            house style, per-doc specs, design-system / viz-production /
│   │                     svg-animation / embedding doctrine
│   ├── styles.md         the catalog index — read once per run to choose
│   ├── styles/           one full spec per style, read one per run
│   └── tier2/            LICENSE, NOTICE, templates, CODEOWNERS specs
├── scripts/
│   ├── svg_check.py      the gate: structure, seam arithmetic, reduced motion,
│   │                     legibility, palette, contrast, style invariants, bytes
│   ├── svg_filmstrip.py  poses N phases of a loop in one page, for the pixel read
│   ├── styles.json       the checker's machine-readable half of the catalog
│   └── audit_visuals.py  mechanical half of the visual staleness audit
└── docs/assets/          this README's own visuals, produced by the skill itself
```

## License

Released under the [MIT License](../../LICENSE) of the repository that ships it.

<!-- mpd:footer start -->
<div align="center">
<br/>

**Copyright © 2026 Zerø Effort. Released under the MIT license.**

</div>
<!-- mpd:footer end -->
