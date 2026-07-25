<div align="center">

# more-pretty-docs

**A Claude Code skill that writes a repository's standard docs and authors their key diagrams as seamless-loop animated SVG — with nothing to install.**

<!-- mpd:badges start -->
[![License: MIT](https://img.shields.io/badge/License-MIT-e0a33e.svg)](../../LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-skill-12324f)](SKILL.md)
[![Dependencies](https://img.shields.io/badge/dependencies-python3_only-12324f)](#install)
[![Styles](https://img.shields.io/badge/style_catalog-31-12324f)](reference/styles.md)
<!-- mpd:badges end -->

<!-- mpd:viz name="hero" src="docs/assets/src/hero/" facts-hash="d57b421c12d6dc8c0e189681569e63ca02047f9c90a9a59e1fbd50b121f104bf" src-hash="f62f5bdd642db1bf2d651220f0bc4d403b7d75e2cb195fcdfa89e10b0f8f8299" -->
<img src="docs/assets/hero.svg" alt="Animated overview on a board of six cells: the project name, a runtime cell reading python3, and a focal cell reporting zero dependencies. Along the bottom, three numbered cells carry the pipeline — author name.svg, gate it until svg_check.py reports zero errors, commit that same file — and a status dot lights them one at a time. There is no render cell: the committed asset is its own source, and python3 is the only requirement." width="820" />
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
| Visual style | derived from the product | 31-style catalog, or derived |
| Asset budget | ≤ 2.5 MB | ≤ 150 KB |

Use `make-pretty-docs` when you specifically want WebP. Use
[`update-docs`](https://github.com/apatheticus/skills) for plain text-only docs.
Otherwise use this one — and note that every visual on this page was authored and
gated by the skill itself, in the `bento-grid` style.

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

<!-- mpd:viz name="styles" src="docs/assets/src/styles/" facts-hash="ee8709bedc3f2b8e38fdcb5d106371f18dcdae84f4451c6b1c6c98f38063ef73" src-hash="963cae7bd0d95e1a68134cdc4adde549420b3d9dbed69c5ea6942087222ea49e" -->
<img src="docs/assets/styles.svg" alt="A board of thirty-one labelled cells in alphabetical order, each built in the style it names: bento-grid, blueprint, brushed-metal, claymorphism, codex-leonardo, console-elbow, digital-rain, draughtsman-notebook, editorial, flat-material, glassmorphism, holographic-projection, hud, ide-dark, isometric-3d, lofi-wireframe, maximalist, neo-brutalist, neumorphism, oil-impasto, patent-drawing, pencil-lined-paper, rough-sketch, schematic, skeuomorphic, swiss-minimal, terminal-minimalist, watercolor, whiteboard-marker, wood-grain and y2k-retrofuturist. Every cell carries one motion characteristic of its style — a marching rule, a material sheen travelling along the grain, a breathing LED, a stepped nudge, glyph columns falling out of phase, counter-rotating reticle rings, an isometric block bobbing while its shadow shrinks. The one accent-filled cell reports that all thirty-one were built and gated clean." width="820" />
<!-- mpd:viz end -->

Every cell above was built and gated for real. If a style could not be produced
clean at cell scale, its catalog entry was wrong and got fixed. Aliases resolve
without asking (`brutalist`, `glass`, `soft-ui`, `tui`, `bento`, `excalidraw`,
`hologram`, `patent`, `whiteboard`, …), a recognisable free-form idiom is synthesized
into a full spec and frozen into the repo's `DESIGN.md`, and anything unresolvable
prompts exactly one question.

### Every style, A to Z

Each slug links to its full nine-field spec.

| Style | Axis | What it is |
| --- | --- | --- |
| [`bento-grid`](reference/styles/bento-grid.md) | composition | Unequal cells in one tight grid, each with one job |
| [`blueprint`](reference/styles/blueprint.md) | material | White line work on cyanotype ground, drafted and annotated |
| [`brushed-metal`](reference/styles/brushed-metal.md) | material | Anisotropic grain, a travelling sheen, engraved type |
| [`claymorphism`](reference/styles/claymorphism.md) | material | Fat rounded volumes, playful pastel depth |
| [`codex-leonardo`](reference/styles/codex-leonardo.md) | era | Brown ink on aged rag, cross-hatch, mirrored marginalia |
| [`console-elbow`](reference/styles/console-elbow.md) | era | Elbow frame on black, flat colour as zoning |
| [`digital-rain`](reference/styles/digital-rain.md) | era + material | Falling glyph columns; structure in the negative space |
| [`draughtsman-notebook`](reference/styles/draughtsman-notebook.md) | era | Graphite on gridded stock — precise, but drawn by a person |
| [`editorial`](reference/styles/editorial.md) | composition | Print hierarchy — a lede, a rule, generous margin |
| [`flat-material`](reference/styles/flat-material.md) | material | One elevation step, confident colour fields |
| [`glassmorphism`](reference/styles/glassmorphism.md) | material | Frosted panels over a coloured ground |
| [`holographic-projection`](reference/styles/holographic-projection.md) | material | Glowing wireframe in a projection cone, scanlines |
| [`hud`](reference/styles/hud.md) | composition | Reticles, tick scales, brackets instead of boxes |
| [`ide-dark`](reference/styles/ide-dark.md) | material | Rounded dark panes, hairline dividers, syntax palette |
| [`isometric-3d`](reference/styles/isometric-3d.md) | composition | Three lit faces per block, shadows that track height |
| [`lofi-wireframe`](reference/styles/lofi-wireframe.md) | composition | Greyboxes and squiggles — deliberately unfinished |
| [`maximalist`](reference/styles/maximalist.md) | composition | Density as the message; layered, loud, deliberate |
| [`neo-brutalist`](reference/styles/neo-brutalist.md) | material | Hard offset shadows, black rules, unapologetic colour |
| [`neumorphism`](reference/styles/neumorphism.md) | material | Extruded from one surface; shadow and highlight, no borders |
| [`oil-impasto`](reference/styles/oil-impasto.md) | material | Lit height field, canvas weave, travelling gloss |
| [`patent-drawing`](reference/styles/patent-drawing.md) | era | Black on white, reference characters, no colour at all |
| [`pencil-lined-paper`](reference/styles/pencil-lined-paper.md) | material | Handwriting on ruled stock, graphite grain |
| [`rough-sketch`](reference/styles/rough-sketch.md) | composition | Doubled strokes and hachure fills — the meeting diagram |
| [`schematic`](reference/styles/schematic.md) | composition | Symbol alphabet, net labels, no perspective |
| [`skeuomorphic`](reference/styles/skeuomorphic.md) | material | Objects that look like objects — bevel, sheen, weight |
| [`swiss-minimal`](reference/styles/swiss-minimal.md) | composition | Strict grid, thin rules, type doing the work |
| [`terminal-minimalist`](reference/styles/terminal-minimalist.md) | material | Mono type on a dark field; a TUI that isn't ASCII art |
| [`watercolor`](reference/styles/watercolor.md) | material | Transparent washes that multiply, ink line laid last |
| [`whiteboard-marker`](reference/styles/whiteboard-marker.md) | material | Fat marker strokes at 88% — thinking out loud |
| [`wood-grain`](reference/styles/wood-grain.md) | material | Wandering grain, travelling varnish, burned labels |
| [`y2k-retrofuturist`](reference/styles/y2k-retrofuturist.md) | era | Chrome gradients, wide tracking, optimistic tech |

Two dials cut across the table and are usually the right answer when a request lands
*between* two styles: **roughness** (the hand-drawn family is one displacement scale,
`0.7` ruled → `4.5` improvised) and **grain ratio** (the material family is one
`feTurbulence` x:y ratio, equal → isotropic, extreme → directional).

Three cautions the catalog does not paper over. Display faces are **never fetched**,
so hand-drawn styles degrade to system handwriting on GitHub. `watercolor`,
`oil-impasto` and `lofi-wireframe` are **decorative**: their contrast floor is *not*
relaxed, and each spec names the move that earns its labels back. And
`console-elbow`, `holographic-projection` and `digital-rain` reproduce a visual
language only — the skill declines to add logos, insignia, wordmarks or fictional
alphabets on request rather than treating them as a customisation option.

Full rules and the resolution ladder: [`reference/styles.md`](reference/styles.md).

Where a style's look genuinely fights a soft gate, the style wins and the gate
softens to a **declared floor, never off** — 21 of the 31 relax something, almost
always filter depth, and every relaxation is printed, recorded in `mpd.json`, and
named in the run report. `neumorphism` is the only style that relaxes *contrast*.
Structural and truth gates never soften.

## How re-authoring is decided

Every embed carries hashes for the facts it depicts, the asset itself, and the
design system. A later run rewrites a visual only when one of those changed, its
asset is missing, or `--refresh-viz` forces it:

<!-- mpd:viz name="lazy-rerender" src="docs/assets/src/lazy-rerender/" facts-hash="6212d58383a4f88e8afae3c5ae3d7168f6ab9620428169a5fe2e4476f8257292" src-hash="c133cdd2fb823db9f7d7da302b071195201ab9f802bbbc3133ee0352914919c3" -->
<img src="docs/assets/lazy-rerender.svg" alt="Animated decision board: three cells name the hashes that get compared — the facts the visual depicts, the committed svg itself, and the design system — and a status dot visits them one at a time. The focal cell holds the verdict: while all three still match, the visual is reused. If any one has moved, that visual alone is re-authored and commits fresh hashes. A prose-only edit moves no hash and re-authors nothing." width="820" />
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
