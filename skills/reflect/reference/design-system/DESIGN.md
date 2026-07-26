---
version: alpha
name: Neumorphic Fresh
description: >-
  A motion-rich soft-UI (neumorphic) design system with a bright mint→teal→cyan
  accent story and springy motion. Surfaces share one tonal base per theme and
  are raised by paired light/dark shadows rather than borders or fill changes.
  Ships in both light and dark themes. Token values below are the LIGHT theme
  (canonical); dark-theme equivalents are suffixed `-dark`. See README.md for
  full brand context and SKILL.md for the agent entry point.
colors:
  # ---- Brand accent ramp (theme-independent hues) ----
  primary: "#11d3a3"          # mint — the signature accent
  primary-strong: "#0bb98d"   # mint pressed / active
  primary-soft: "#6cf0cf"     # mint tint
  secondary: "#12b5c9"        # teal
  tertiary: "#28c8e8"         # cyan
  lime: "#8fe06a"             # energy accent
  # ---- Semantic ----
  success: "#2fc97a"
  warning: "#f5a623"
  danger: "#fb6b6b"
  info: "#3fb6f0"
  # ---- Light theme surfaces (neumorphic: surface == background) ----
  neutral: "#e6e9ef"          # the single tonal base / canvas
  background: "#e6e9ef"
  surface: "#e6e9ef"          # cards share the canvas color, raised by shadow
  surface-2: "#edf0f5"        # subtly raised section
  surface-inset: "#e1e5ec"    # pressed wells (inputs, tracks)
  # ---- Light theme shadow stops (drive every elevation) ----
  shadow-light: "#ffffff"     # top-left highlight
  shadow-dark: "#c3cad6"      # bottom-right shadow
  # ---- Light theme text ----
  on-surface: "#2b303b"            # primary text (fg1)
  on-surface-secondary: "#5b6472"  # secondary text (fg2)
  on-surface-tertiary: "#8a93a4"   # tertiary / captions (fg3)
  on-accent: "#06241d"             # deep teal-black for text on accent fills
  # ---- Hairlines (used sparingly) ----
  line: "#2b303b"             # apply at ~8% alpha — borders are nearly absent
  # ---- Dark theme equivalents ----
  background-dark: "#23262e"
  surface-dark: "#23262e"
  surface-2-dark: "#272b34"
  surface-inset-dark: "#1f222a"
  shadow-light-dark: "#2e333e"
  shadow-dark-dark: "#15171d"
  on-surface-dark: "#eef1f6"
  on-surface-secondary-dark: "#aab3c2"
  on-surface-tertiary-dark: "#717b8c"
  on-accent-dark: "#042019"
typography:
  display:
    fontFamily: Sora
    fontSize: 72px
    fontWeight: 800
    lineHeight: 1.1
    letterSpacing: -0.02em
  headline-lg:                 # h1
    fontFamily: Sora
    fontSize: 52px
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: -0.02em
  headline-md:                 # h2
    fontFamily: Sora
    fontSize: 38px
    fontWeight: 700
    lineHeight: 1.28
    letterSpacing: -0.02em
  headline-sm:                 # h3
    fontFamily: Sora
    fontSize: 28px
    fontWeight: 600
    lineHeight: 1.28
    letterSpacing: -0.01em
  title:                       # h4
    fontFamily: Sora
    fontSize: 20px
    fontWeight: 600
    lineHeight: 1.28
  body-lg:                     # lead
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: 400
    lineHeight: 1.7
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.55
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.55
  label-md:                    # buttons, UI labels (display family)
    fontFamily: Sora
    fontSize: 14px
    fontWeight: 600
    lineHeight: 1.28
    letterSpacing: -0.01em
  caption:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.55
  overline:                    # tiny tracked caps eyebrow
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: 700
    lineHeight: 1
    letterSpacing: 0.12em
  mono:                        # code, data, timestamps
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.55
rounded:
  xs: 8px
  sm: 12px
  md: 18px
  lg: 26px
  xl: 34px
  2xl: 44px
  full: 999px
spacing:
  base: 16px
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  2xl: 32px
  3xl: 40px
  4xl: 48px
  5xl: 64px
  6xl: 80px
  7xl: 112px
  content-max: 1200px
components:
  # ---- Default / secondary button: raised soft pill ----
  button:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    padding: 11px 20px
  button-hover:
    textColor: "{colors.primary-strong}"
  button-active:
    textColor: "{colors.on-surface-secondary}"
  # ---- Primary: fresh gradient fill with accent glow ----
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-accent}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    padding: 11px 20px
  button-primary-hover:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.on-accent}"
  # ---- Ghost: pressed-in well ----
  button-ghost:
    backgroundColor: "{colors.surface-inset}"
    textColor: "{colors.on-surface-secondary}"
    rounded: "{rounded.full}"
  # ---- Danger ----
  button-danger:
    backgroundColor: "{colors.danger}"
    textColor: "#ffffff"
    rounded: "{rounded.full}"
  # ---- Card: same color as page, raised by shadow ----
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: 24px
  # ---- Input / textarea / select: pressed well ----
  input:
    backgroundColor: "{colors.surface-inset}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: 14px 18px
  input-placeholder:
    textColor: "{colors.on-surface-tertiary}"
  # ---- Badge / chip ----
  badge:
    backgroundColor: "#11d3a324"
    textColor: "{colors.primary-strong}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.full}"
    padding: 5px 13px
  chip:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface-secondary}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.full}"
    padding: 8px 15px
  chip-active:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-accent}"
  # ---- Toggle switch ----
  switch:
    backgroundColor: "{colors.surface-inset}"
    rounded: "{rounded.full}"
    height: 30px
    width: 54px
  switch-active:
    backgroundColor: "{colors.primary}"
  # ---- Tooltip: small raised surface ----
  tooltip:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.sm}"
    padding: 6px 11px
---

# Neumorphic Fresh — DESIGN.md

> **How this fits together.** This `DESIGN.md` is the machine-readable + prose
> source of truth for the visual system. It pairs with two companion docs:
>
> - **`README.md`** — full brand narrative: content voice, the five brand rules,
>   the file/asset index, and per-kit notes. Read it for *why* and *how to apply*.
> - **`SKILL.md`** — the agent entry point (Agent-Skills compatible). Start there
>   when you want to *build* something with this system.
> - **`colors_and_type.css`** + **`components.css`** — the live CSS tokens and
>   `nf-*` primitives. The tokens in this file's front matter mirror those CSS
>   custom properties; the CSS is the runtime implementation.
>
> Token values in the front matter are the **light theme** (canonical). Dark-theme
> values carry a `-dark` suffix. Prose uses descriptive color names (e.g. "mint")
> that correspond to systematic token names (e.g. `primary`); the tokens are
> normative, the prose explains application.

## Overview

Neumorphic Fresh is a soft-UI system where every element appears **carved from or
pressed into a single soft surface**. Depth comes almost entirely from a paired
highlight (top-left) and shadow (bottom-right) derived from one tonal base — there
are virtually no hard borders or contrasting card fills. "Fresh" counters the usual
muted, grey neumorphism with a lively mint→teal→cyan accent, real semantic color,
crisp focus rings and energetic spring motion.

**Personality:** warm, calm, confident — a thoughtful product team that sweats the
details. Approachable expertise, never cutesy. **Feel:** spacious, pillowy, tactile;
things lift when you hover and sink when you press. **Audience:** product, SaaS,
dashboards, marketing and portfolio surfaces that want to feel friendly and modern
without sacrificing legibility. The system runs **balanced neumorphism**: soft
surfaces, but with accent fills, AA text contrast and visible focus states so it
stays usable rather than purely decorative. Copy is **sentence case** everywhere,
short, and emoji-free in product chrome.

## Colors

The palette is one shared tonal base per theme, energized by a fresh accent ramp.

- **Primary — Mint (#11d3a3):** the signature accent. Drives primary actions
  (typically as the mint→teal→cyan gradient), active states, focus glow and data
  viz. Pair with `on-accent` deep teal-black for text on top.
- **Secondary — Teal (#12b5c9)** and **Tertiary — Cyan (#28c8e8):** the rest of the
  accent ramp. Together with mint they form the signature 120° gradient used on
  primary buttons, toggles, progress fills and gradient text. **Lime (#8fe06a)**
  adds occasional energy.
- **Neutral / Surface (#e6e9ef light, #23262e dark):** the single canvas color that
  *all* surfaces share. Cards are not a different color than the page — they are the
  same color, raised by shadow. This is the core neumorphic rule.
- **Shadow stops (`shadow-light` #ffffff / `shadow-dark` #c3cad6):** every raised or
  inset element is built from this highlight + shadow pair, both derived from the
  base. They are the engine of the whole system (see Elevation & Depth).
- **Text:** three levels — `on-surface` (#2b303b primary), `on-surface-secondary`
  (#5b6472), `on-surface-tertiary` (#8a93a4 captions). On accent fills use
  `on-accent` (#06241d) for AA contrast.
- **Semantic:** success #2fc97a, warning #f5a623, danger #fb6b6b, info #3fb6f0 —
  each also used at low alpha as a soft "wash" background for badges and banners.

Dark theme keeps the same hues on a #23262e base; accent swatches brighten slightly
(see `*-dark` tokens). Both themes are switched via `data-theme` on `<html>`.

## Typography

Three families carry the system, loaded from Google Fonts:

- **Display — Sora:** geometric, slightly technical, friendly. All headings,
  buttons, numbers and labels. Tight tracking (-0.02em) at large display sizes.
- **Body — Plus Jakarta Sans:** humanist geometric, warm. Paragraphs, labels, UI
  text. 16px body at 1.55 line-height for comfortable reading.
- **Mono — JetBrains Mono:** code, data and timestamps.

The scale runs fluidly from an 11–12px tracked-caps **overline** up to a 72px
**display**. Front-matter `fontSize` values are the upper bound of each fluid step;
in CSS these are implemented with `clamp()` (see `--fs-*` in `colors_and_type.css`).
**Casing:** sentence case for headings and labels; ALL-CAPS reserved only for the
`overline` eyebrow, set with wide 0.12em tracking.

## Layout

A **fluid grid** for small screens and a **fixed-max-width grid** (≈1200px,
`content-max`) for marketing desktop; app surfaces are fluid. Spacing follows a **4px
base scale** (`xs` 4 → `7xl` 112) so rhythm stays consistent.

Because neumorphic shadows need breathing room, **padding skews generous and elements
rarely touch** — cards use 24px internal padding, sections are airy. Fixed chrome (top
bars, sidebars) sits on the base color and is separated from content by **elevation,
not by lines**. Related items are grouped by containment inside raised cards rather
than by dividers.

## Elevation & Depth

Depth is the heart of this system and is conveyed entirely through **paired soft
shadows**, never flat drop-shadows or borders. Every raised element casts a dark
offset toward the bottom-right (`shadow-dark`) and a light offset toward the
top-left (`shadow-light`), both tinted from the tonal base:

- **Raised levels (el-1 / el-2 / el-3):** increasing offset + blur (4/4/9 →
  12/12/26px) for chips, buttons, cards and panels. A heavier `el-float` is used for
  modals and popovers.
- **Inset wells (inset-1 / inset-2):** the same shadows reversed *inward* to create
  pressed wells — used for inputs, slider/progress tracks, ghost buttons and any
  active/pressed state.
- **Accent glow:** primary buttons, slider thumbs and progress fills add a colored
  bloom (`0 6px 20px rgba(17,211,163,.45)`) under the element.

**Motion maps to depth:** hover *raises* elevation (element lifts, often
`translateY(-1…-3px)`); press *sinks* it into an inset and scales to ~0.98. Toggles
and switches bounce into place with a spring ease. All motion respects
`prefers-reduced-motion`. Exact shadow recipes live as `--el-*` / `--inset-*` /
`--glow-accent` in `colors_and_type.css`.

## Shapes

The shape language is **soft and pillowy — no sharp corners anywhere**. Rounding is
generous: `xs` 8px → `2xl` 44px, plus a `full` 999px pill.

- Buttons, chips, badges, toggles and segmented controls are **full pills**.
- Cards and panels use `lg` (26px); inputs and smaller surfaces use `md` (18px).
- Larger feature surfaces and hero panels reach `xl`/`2xl`.

Soft is the brand: when in doubt, round more rather than less.

## Components

All primitives are implemented as `nf-*` classes in `components.css`. Key atoms:

- **Buttons** — raised soft pills. *Default/secondary* shares the surface color and
  lifts on hover (text shifts to mint on hover, sinks into an inset on press).
  *Primary* fills with the fresh gradient + accent glow and uses `on-accent` text.
  *Ghost* is a pressed-in well; *danger* uses the danger hue with a red glow. Sizes
  `sm`/`base`/`lg` and an icon-only circular variant.
- **Input fields** — pressed wells (`surface-inset` + inset shadow), no border, 18px
  radius. Focus deepens the inset and adds a 3px accent-wash ring. Same treatment for
  textarea and select; labels in `label-md`, placeholder in `on-surface-tertiary`.
- **Checkboxes & radios** — raised soft squares/circles that invert to a gradient
  fill + inset when checked, with a spring transition.
- **Toggle switch** — inset track; the thumb is a raised circle that springs across.
  Checked track fills with the fresh gradient.
- **Chips & badges** — pill chips toggle to a gradient fill when active; badges use a
  low-alpha semantic wash with matching text color.
- **Tooltips** — a small raised surface (`el-2`) appearing above the trigger with a
  short spring fade-in.
- **Sliders, progress, spinners, segmented controls, avatars, dividers, skeletons** —
  all follow the same raised/inset + gradient-accent logic; see `components.css`.

Component tokens (background, text, radius, padding) are defined in the front matter
and reference the color/typography/rounded scales. Where a token shows a flat
`primary` background, the live CSS upgrades it to the mint→teal→cyan **gradient** —
gradients can't be expressed as a single Color token, so treat `primary` as the
gradient's anchor.

## Iconography

**Lucide** is the house icon set (CDN: `https://unpkg.com/lucide@latest`), chosen
because its rounded caps/joins and consistent 2px stroke match the soft geometry.
Use outline icons at 1.75–2px stroke, 18–24px in UI; reserve filled glyphs for tiny
status dots and active nav items. Icons inherit `currentColor`. Feature icons sit in
a raised round chip tinted with the accent wash. **No emoji** in chrome. Drop custom
SVGs into `assets/icons/` to override. Brand logo variants live in `assets/logo-*.svg`.

## Do's and Don'ts

- **Do** keep every surface the same tonal base color and raise it with paired
  shadows. **Don't** give a card a different fill color than the page.
- **Do** use the fresh mint→teal→cyan gradient for the single most important action
  per screen. **Don't** scatter accent fills across many competing buttons.
- **Do** round generously and keep spacing airy — shadows need room. **Don't**
  introduce sharp corners or let neumorphic elements touch.
- **Do** map motion to depth: lift on hover, sink on press, spring toggles into
  place. **Don't** use flat drop-shadows, hard borders, or static states.
- **Do** use `on-accent` (deep teal-black) for text on accent fills and maintain
  WCAG AA contrast (4.5:1 for body text). **Don't** rely on color alone — keep focus
  rings and clear pressed states.
- **Do** write sentence-case, short, calm copy. **Don't** use emoji in product chrome
  or marketing copy, or ALL-CAPS outside the tracked overline.
- **Do** reserve glass/blur for overlays over imagery. **Don't** make transparency the
  default surface.
