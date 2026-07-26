<div align="center">

# pretty-svg-docs

**A Claude Code skill that writes a repository's standard docs and authors their key diagrams as seamless-loop animated SVG — with nothing to install.**

<!-- pd:badges start -->
[![License: MIT](https://img.shields.io/badge/License-MIT-e0a33e.svg)](../../LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-skill-12324f)](SKILL.md)
[![Dependencies](https://img.shields.io/badge/dependencies-python3_only-12324f)](#install)
[![Styles](https://img.shields.io/badge/style_catalog-31-12324f)](reference/styles.md)
<!-- pd:badges end -->

<!-- pd:viz name="hero" src=".prettydocs/src/hero/" facts-hash="e427d9ffd6fe932b10a704f334210d0ec7362a9c45e6ab2567ebeeda7fdf3746" src-hash="d115683ab5235fb3865e6753ec919fe27eaf9560264a7fd2f32537cfc86acdb7" -->
<div align="center">
<img src="docs/assets/hero.svg" alt="Animated board of eight cells. The widest names the skill and its claim — animated SVG, authored, not rendered. A runtime cell reads python3 and nothing else, and the single accent-filled cell reports zero dependencies. One cell nests the pipeline as a small diagram, author then gate then commit, with a status dot visiting each station in turn and no render station between them, because the committed asset is its own source. Two cells count what the skill carries: thirty-one catalog idioms, of which one is chosen per repo, and the eight classes the bundled checker applies to every visual, the eighth being fidelity. Along the bottom the verdict cell reads zero errors, required before any visual is embedded, beside a meter that fills and settles, and the last cell gives the loop as twelve seconds, seam-exact." width="820" />
</div>
<!-- pd:viz end -->

</div>

## What this is

pretty-svg-docs creates and maintains a repository's standard documentation —
README, ARCHITECTURE, DEVELOPMENT, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY,
SUPPORT, plus tier-2 files on request — and makes it look designed. Each run
derives a frozen per-repo design system, picks a named visual style, then writes
the docs' key diagrams as animated SVG by hand.

It is the sibling of [`pretty-hyper-docs`](../pretty-hyper-docs), which does the same
job with animated WebP rendered through the HyperFrames toolchain. Same content
engine, same honesty-over-polish doctrine. The difference is the visual layer:

|  | `pretty-hyper-docs` | `pretty-svg-docs` |
| --- | --- | --- |
| Visual format | animated WebP | animated SVG |
| Needs installing | HyperFrames CLI, ffmpeg, img2webp | nothing beyond `python3` |
| Build step | HTML composition → MP4 → WebP | none; the `.svg` you write is the asset |
| Failure mode | preflight STOP on a missing toolchain | warns, never aborts |
| Visual style | derived from the product | 31-style catalog, or derived |
| Asset budget | ≤ 2.5 MB | ≤ 150 KB |

Use `pretty-hyper-docs` when you specifically want WebP. Use
[`update-docs`](https://github.com/apatheticus/skills) for plain text-only docs.
Otherwise use this one — and note that every visual on this page was authored and
gated by the skill itself, in the `bento-grid` style.

## What a run produces

- Tier-1 docs written for their audience, with facts grounded in the repo's actual
  code, manifests, and CI.
- `docs/assets/*.svg` — the committed visuals, each within a per-doc budget
  (README: hero + up to 3; technical docs: 1–2 flagship each;
  SECURITY/CODE_OF_CONDUCT: one attention banner).
- `.prettydocs/prettydocs.md` — the frozen design system every visual derives from,
  including the resolved style spec.
- `.prettydocs/src/<viz>/viz.json` — each visual's facts, hashes and parameters.
  There is no composition source next to it, because the asset *is* the source.

LICENSE and NOTICE are never visualized or reformatted.

## The style catalog

A **style** is the look-and-feel idiom every visual in a repo is rendered in. Pass
`--style <slug>`, or let the skill derive one from the product the way it always
has. Style owns *form* — shape, material, type, composition, motion. The product's
own brand tokens still own the *palette*.

<!-- pd:viz name="styles" src=".prettydocs/src/styles/" facts-hash="33ebe05a0c9d07aebe81b14ad473b53cba1c9f2a06b373fbd52bc50b74da294a" src-hash="fb22c210ca132ec3dbb7ab756a1e0c5cdbb5233305815b18637bbf58fe7f7e19" -->
<div align="center">
<img src="docs/assets/styles.svg" alt="A contact sheet of thirty-one animated style specimens in alphabetical order, two to a row: bento-grid, blueprint, brushed-metal, claymorphism, codex-leonardo, console-elbow, digital-rain, draughtsman-notebook, editorial, flat-material, glassmorphism, holographic-projection, hud, ide-dark, isometric-3d, lofi-wireframe, maximalist, neo-brutalist, neumorphism, oil-impasto, patent-drawing, pencil-lined-paper, rough-sketch, schematic, skeuomorphic, swiss-minimal, terminal-minimalist, watercolor, whiteboard-marker, wood-grain and y2k-retrofuturist. Every cell is that style’s own full-width specimen scaled down, so each carries its real filter chains, grain and lighting — lit impasto relief, displaced wood grain, anisotropic brushed metal, true backdrop blur — rather than a flattened imitation. Each also carries one motion characteristic of its style. The final accent-bordered cell reports that all thirty-one were built and gated at their declared filter floors." width="820" />
</div>
<!-- pd:viz end -->

Every cell above **is** that style's own specimen, scaled — not a redrawing of it.
Each specimen is built at 1200 × 460 and gated under its own `--style`, so it gets
that style's real filter floors: `oil-impasto` keeps its five-primitive lit relief,
`wood-grain` its displaced growth rings. Every specimen also ships full-width under
[`docs/samples/`](docs/samples/) and is embedded at the top of its spec file. If a
style could not be produced clean, its catalog entry was wrong and got fixed. Aliases resolve
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
always filter depth, and every relaxation is printed, recorded in `viz.json`, and
named in the run report. `neumorphism` is the only style that relaxes *contrast*.
Structural and truth gates never soften.

## How re-authoring is decided

Every embed carries hashes for the facts it depicts, the asset itself, and the
design system. A later run rewrites a visual only when one of those changed, its
asset is missing, or `--refresh-viz` forces it:

<!-- pd:viz name="lazy-rerender" src=".prettydocs/src/lazy-rerender/" facts-hash="bf26d51f835b407ee1493bae83c0b3045b726b77381c32beecead0ee9649b828" src-hash="e6543fa10d251e551e8b41e7ef0ee90575b4406b7cec67844e93fcf6add794ef" -->
<div align="center">
<img src="docs/assets/lazy-rerender.svg" alt="Animated board of ten cells. The accent-filled cell holds the verdict when none of the six triggers fired: reuse, meaning the embed may be rewritten but nothing is rendered. Three cells name the hashes that are compared, each showing its digest twice, stored above fresh, as two identical rows that read as a match: the facts the visual depicts, which moves when the evidence does; the committed svg itself, where a hand-edit shows up; and the design system, which moves every visual at once. A status dot visits the three in turn. Three further cells carry the triggers that are not hashes at all — the asset missing from its path, a marker disagreeing with its manifest, and a run forced with refresh-viz. The last row states both outcomes: if any one of the six fired, that visual alone is re-authored and commits fresh hashes while every other visual is left alone; a prose-only edit moves no hash and re-authors nothing." width="820" />
</div>
<!-- pd:viz end -->

Because the style spec lives inside `DESIGN.md`, changing the style moves
`design_hash` and re-authors every visual in the repo. The plan phase says so, with
a count, before touching anything.

## Install

```bash
npx skills add apatheticus/skills --skill pretty-svg-docs
```

Or as part of the Claude Code plugin bundle:

```
/plugin marketplace add apatheticus/skills
/plugin install apatheticus-skills@apatheticus
```

Or copy the folder straight into a repo's skill directory:

```bash
cp -R skills/pretty-svg-docs /path/to/repo/.claude/skills/pretty-svg-docs
```

The skill is self-contained. At run time it needs `python3` for its two bundled
scripts and nothing else — no renderer, no `ffmpeg`, no CLI, no network. A browser
tool is optional: it is used to look at the rendered pixels, and when none is
available the run says the pixel review was skipped rather than implying it passed.

## Use

| Command | Effect |
| --- | --- |
| `/pretty-svg-docs` | Full tier-1 pass: content + visuals |
| `/pretty-svg-docs readme security` | Only the named docs |
| `/pretty-svg-docs check` | Read-only audit of content and visual staleness |
| `--style <slug>` | Pick a catalog style (or a recognisable free-form idiom) |
| `--style auto` | Re-derive the style from the product, ignoring the stored slug |
| `--refresh-viz` / `--no-viz` / `--budget <doc>=<n>` / `--brief` / `--full` | Modifiers — see `SKILL.md` |

## Layout

```
pretty-svg-docs/
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

<!-- pd:footer start -->
<div align="center">
<br/>

**Copyright © 2026 Zerø Effort. Released under the MIT license.**

</div>
<!-- pd:footer end -->
