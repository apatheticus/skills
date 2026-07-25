# skills — visual design system

One frozen system; all repo visuals derive from it. Facts come from the repo
(README, manifests, `scripts/validate.mjs`, CI), never invented. Frozen for this
run.

The visual language is adapted from the **Cinetica design system**, whose tokens
are mapped to doc roles below rather than reinvented. Cinetica's product
names, copy, and iconography are **not** used here — only the formal language:
monochrome two-world contrast, HUD chrome, corner brackets, hard-decelerating
motion.

## Story extraction

Audience:     Engineers who install agent skills, and the few who write them.
Value:        One source tree of agent skills that installs through two managed channels.
Proof:        `scripts/validate.mjs` gates every skill and both manifests; CI fails on drift.
First action: `npx skills add apatheticus/skills`
Theme:        A targeting reticle over a loadable unit — a skill directory is framed, verified, then loaded by an agent.

## Frozen system

### Palette

Mapped from Cinetica tokens (`tokens/colors.css`) to doc roles:

| Product token | Value | Doc role |
| --- | --- | --- |
| `--cn-black` | `#000000` | background |
| `--cn-navy-800` | `#0b0f1a` | surface (cards, panels) |
| `--cn-white` | `#ffffff` | ink |
| `--cn-wash` | `#e2e6fb` | accent-primary (the one soft light in a mono world) |
| `--cn-gray-300` | `#bdb6b7` | accent-secondary / muted ink |
| `--cn-gray` (`--cn-gray-800`) | `#312b2c` | hairline |
| `--cn-gray-500` | `#7a7172` | corner bracket, resting state |
| `--cn-caution` | `#c2b287` | attention (semantic only, never decoration) |

| Role | Hex | Notes |
| --- | --- | --- |
| background       | `#000000` | page canvas, the void world |
| surface          | `#0b0f1a` | cards / panels |
| ink              | `#ffffff` | primary text |
| accent-primary   | `#e2e6fb` | active path, current state |
| accent-secondary | `#bdb6b7` | muted labels, inactive edges |
| hairline         | `#312b2c` | structural rules and connectors — never text |
| bracket (resting)| `#7a7172` | corner-bracket marks before they go active |
| warn / attention | `#c2b287` | gate and check states only |

Cinetica's hue ban carries over: nothing outside this table. `#e2e6fb` and
`#0b0f1a` are flagged approximations in the source system (screenshot-sampled
from WebGL gradients); they are used here as literal values, which is fine for
flat rendering.

### Typography

Cinetica specifies Gabarito 900, Montserrat, Instrument Serif, and Martian Mono,
all loaded from Google Fonts. Rendered visuals may not fetch remote fonts, so
every family here is one the HyperFrames compiler self-hosts. Montserrat is a
direct hit; the other two roles are substitutions, recorded as gap-fills rather
than brand claims.

| Role | Family | Stands in for |
| --- | --- | --- |
| display | `Montserrat` at weight 900, uppercase, `-0.02em` | Gabarito 900 — same geometric grotesque character |
| body | `Montserrat` at 400 | Montserrat 400 — exact |
| mono | `"JetBrains Mono"` at 400, uppercase, `0.1em` tracking for chrome | Martian Mono 400 |

Any family outside this list falls back through the compiler's alias map, which
changes the rendered pixels silently. Name only these three.

Tracking is the chrome signal, exactly as in the source: `0.1em`-tracked
uppercase mono marks a label as HUD chrome; untracked text is content. No
Instrument Serif equivalent is used — this repo has no manifesto voice.

Hierarchy comes from size, case, and family. Never from weight or tracking
alone.

### Shape language

- Square by default. Radius budget: `0` for panels and cards, `42px` pill for
  anything that reads as an action, `4px` for terminal/field surfaces.
- Stroke weight `1px` for hairlines, `2px` for an active path.
- Spacing unit `16px`; gaps run 16 / 32 / 48.
- **Flat. No box-shadows anywhere.** Depth is z-index stacking and alpha only.

### Motif

The **four-corner bracket** — four independent L-marks framing an element like a
targeting reticle. Project-derived: a skill is a self-contained directory that
an agent targets, verifies, and loads, and the bracket is what marks a unit as
loadable. It frames skill units and the current step of a pipeline. Used
lightly, never as wallpaper. The secondary cue is a **tick ruler** hairline,
carrying the instrumented, verified feel of the validator.

### Composition rules

Compact-technical. One strong composition per visual, not several decorative
graphics. Content stays 48–64 units clear of the edges. HUD chrome (tracked mono
labels, tick rules) frames the frame; the diagram itself sits in the middle
third and carries all the meaning.

### Motion rules

- Seamless ambient loops, **12s**; state at t=D equals state at t=0.
- House ease `cubic-bezier(0.625, 0.05, 0, 1)` — snappy in, hard deceleration,
  zero overshoot. GSAP equivalent: a custom ease, or `power3.inOut` where a
  custom ease is unavailable. No bounce, no overshoot, no elastic.
- Durations follow Cinetica's clusters: 300ms micro, 600ms reveal, 850ms
  entrance, 1200ms travel.
- Motion always communicates flow direction or a state change. No strobing, no
  flicker, no idle bobbing. Opacity never drops below `0.2` on a persistent
  element.
- Every periodic cycle count divides the 12s duration exactly, so the loop seam
  is invisible.

## Visual inventory

| Asset | Doc | Depicts | Tier | Source facts |
| --- | --- | --- | --- | --- |
| `hero` | README.md | One source tree of skills reaching an agent host through two install channels | animated-hero | `skills/`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, README install section |
| `skill-anatomy` | README.md | What a skill directory holds and what an agent reads first | animated-flagship | `scripts/validate.mjs`, `templates/SKILL.template.md`, `CONTRIBUTING.md` |
| `pr-lifecycle` | CONTRIBUTING.md | The change path from a `stage` commit to a merge into `main` | animated-flagship | `CLAUDE.md`, `.github/workflows/validate.yml`, `.github/pull_request_template.md` |
