# pretty-hyper-docs — visual design system

One frozen system; all repo visuals derive from it. Facts come from the repo
(SKILL.md, reference/, scripts/), never invented. Frozen for this run.

## Story extraction

Audience:     developers who want their repo docs generated, truthful, and designed
Value:        writes standard project docs and renders their key diagrams as seamless-loop animated WebPs
Proof:        the hero and diagram in this skill's own README were produced by the skill's pipeline
First action: copy the folder into `.claude/skills/` and run `/pretty-hyper-docs`
Theme:        docs in, motion out — a plain markdown skeleton transforms into a living diagram

## Frozen system

Mapped from the skill's existing hero identity (`assets/readme/hero.svg`), not invented.

### Palette

| Role | Hex | Notes |
| --- | --- | --- |
| background       | `#101418` | page canvas |
| surface          | `#1a2027` | cards / panels |
| surface-raised   | `#233041` | diagram nodes |
| border           | `#2c353f` | quiet card strokes |
| ink              | `#dbe4ec` | primary text |
| muted            | `#8a97a3` | secondary text, labels |
| skeleton         | `#3d4854` | placeholder text lines |
| accent-primary   | `#4cc38a` | pipeline green: flow, success, live edges |
| warn / attention | `#d9a856` | gap-fill (no product token existed); stale/changed states only |

### Typography

| Role | Stack |
| --- | --- |
| display | `-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif` |
| body    | same as display |
| mono    | `ui-monospace, SFMono-Regular, Menlo, monospace` |

Rendered visuals must self-host or `local()` their fonts — never load a remote
font. Labels, paths, and hashes are always mono; only the wordmark and headings
use the display stack.

### Shape language

Radius 8–14 px on cards, 7 px on nodes; 2 px strokes; 1200-unit-wide canvas;
generous 48+ unit edge margins.

### Motif

The **doc-to-diagram transformation**: a plain markdown skeleton (gray line
bars) on the left, a live bordered diagram panel on the right, joined by a
dashed green pipeline arrow. Repeated lightly — skeleton bars and traveling
green pulses are the recurring cues. Never wallpaper.

### Composition rules

Compact-technical register. One strong composition per visual; left-to-right
flow reading order; important content clear of edges; labels always legible at
rendered width (1200 px → ~820 px column).

### Motion rules

- Seamless ambient loops, **8–14s** each; state at t=D equals state at t=0.
- Linear motion for continuous flow (dash travel, pulses); `power2.inOut` for
  state changes; calm, purposeful.
- No strobing, no flicker, no idle bobbing. Motion always communicates flow
  direction or a state change.
- Keep motion calm out of respect for motion-sensitive readers.

## Visual inventory

| Asset | Doc | Depicts | Tier | Source facts |
| --- | --- | --- | --- | --- |
| hero | README.md | a markdown doc flows through the render pipeline and emerges as a looping animated diagram | animated-hero | SKILL.md workflow; reference/viz-production.md; scripts/viz_to_webp.sh (2.5 MB cap) |
| lazy-rerender | README.md | hash comparison (facts/src/design) decides RE-RENDER vs REUSE; prose edits render nothing | animated-flagship | reference/embedding.md → Lazy re-render decision |
