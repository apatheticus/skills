---
version: "1.0"
name: SaaS Pro
description: >-
  A light, glass-and-gradient dashboard system built for reporting: numbers first,
  soft physics, blue-tinted neutrals. Two card worlds on one page — white cards for
  KPIs and prose, dark navy cards for dense data (every chart and every table).
  There is no dark page theme and one must not be invented. Token values below are
  transcribed from tokens/*.css, which is the runtime implementation.
authority: >-
  The CSS files in tokens/ are authoritative. This frontmatter mirrors them for
  machine reads and is not a second source of truth — if the two ever disagree,
  the CSS is correct and this block is stale. components.css is a hand-derived
  CSS projection of the upstream React components and is authoritative for class
  names; the prose in section 5 is authoritative for how to use them.
colors:
  # ---- Brand core (indigo) ----
  brand-500: "#5B5FEF"          # the signature indigo
  brand-600: "#4A4AE8"          # links, active text, pressed
  brand-700: "#3B36D6"          # link hover
  brand-400: "#7B7FF5"
  brand-300: "#A3A7FA"
  brand-100: "#E6E7FE"          # soft badge ground
  brand-050: "#F3F4FF"          # secondary button ground
  # ---- Blue secondary (gradient terminus, chart series) ----
  blue-500: "#3B82F6"
  blue-400: "#60A5FA"
  blue-100: "#DBEAFE"
  # ---- Accents: icon tiles, chart series, soft badge tints ONLY ----
  accent-coral: "#FF7A8A"
  accent-coral-soft: "#FFE4E8"
  accent-green: "#2ECC9A"
  accent-green-soft: "#D9F7EC"
  accent-orange: "#F9A03F"
  accent-orange-soft: "#FEF0DD"
  accent-purple: "#8B5CF6"
  accent-purple-soft: "#EDE7FD"
  accent-teal: "#22C7C7"
  accent-teal-soft: "#DAF6F6"
  # ---- Semantic: status only. The raw hue is a FILL, not a text colour ----
  success: "#22B07D"
  success-soft: "#DCF6EC"
  warning: "#F59E0B"
  warning-soft: "#FEF3D9"
  danger: "#EF4458"
  danger-soft: "#FDE3E7"
  info: "#3B82F6"
  info-soft: "#DBEAFE"
  # ---- Semantic TEXT ramp. Defined in components.css, not tokens/. Each raw
  # hue scaled down in linear luminance until it clears 4.5:1 on its own soft
  # ground: 5.26, 4.55, 4.90, 5.02. Use these for any semantic TEXT ----
  success-strong: "#15714F"
  warning-strong: "#B45309"     # upstream's own value, kept verbatim
  danger-strong: "#B8303F"      # also the filled danger button's ground
  info-strong: "#2B5FB8"
  # ---- Neutral "ink" scale: cool, blue-tinted. Never pure gray, never pure black ----
  ink-900: "#12142B"            # headings
  ink-800: "#1E2142"            # table cell text
  ink-700: "#333759"
  ink-600: "#4C5273"            # body text
  ink-500: "#6A7091"            # labels
  ink-400: "#9297B3"            # muted / overlines / axis ticks
  ink-300: "#BEC2D6"
  ink-200: "#DDDFEB"
  ink-100: "#EDEEF6"            # tracks, gridlines, neutral badge ground
  ink-050: "#F6F7FC"            # sunken rows, hover ground
  white: "#FFFFFF"
  # ---- Dark data-card palette. A CARD surface, not a page theme ----
  navy-900: "#23265E"
  navy-800: "#2B2F76"
  navy-700: "#383D8F"
  navy-line: "rgba(255,255,255,0.12)"
  navy-text: "rgba(255,255,255,0.92)"
  navy-text-dim: "rgba(255,255,255,0.55)"
  # ---- Gradients: identity, not decoration ----
  grad-brand: "linear-gradient(135deg, #6A6FF7 0%, #4A4AE8 55%, #3B82F6 100%)"
  grad-header: "linear-gradient(90deg, #5B5FEF 0%, #3B82F6 100%)"
  grad-coral: "linear-gradient(150deg, #FF9AA7 0%, #FF7A8A 60%, #F9A03F 130%)"
  grad-green: "linear-gradient(150deg, #4ADCB0 0%, #2ECC9A 100%)"
  grad-orange: "linear-gradient(150deg, #FFB95C 0%, #F9A03F 100%)"
  grad-purple: "linear-gradient(150deg, #A78BFA 0%, #8B5CF6 100%)"
  grad-navy: "linear-gradient(165deg, #2E3277 0%, #23265E 100%)"
  grad-page: "linear-gradient(180deg, #F2F4FF 0%, #FAFBFF 40%, #F4F6FE 100%)"
  # ---- Semantic aliases: prefer these in markup ----
  text-heading: ink-900
  text-body: ink-600
  text-muted: ink-400
  text-on-brand: "#FFFFFF"
  surface-page: "#F4F6FE"
  surface-card: "#FFFFFF"
  surface-raised: "#FFFFFF"
  surface-sunken: ink-050
  surface-glass: "rgba(255,255,255,0.65)"
  surface-dark: navy-900
  border-subtle: "rgba(28,32,84,0.08)"
  border-default: "rgba(28,32,84,0.13)"
  border-glass: "rgba(255,255,255,0.55)"
  focus-ring: "0 0 0 3px rgba(91,95,239,0.30)"
typography:
  families:
    sans: "'Plus Jakarta Sans', 'Segoe UI', system-ui, -apple-system, sans-serif"
    mono: "'JetBrains Mono', ui-monospace, 'SF Mono', monospace"
  scale:                         # --text-*
    2xs: 11px                    # the floor; never smaller
    xs: 12px
    sm: 13px
    md: 14px
    lg: 16px
    xl: 20px
    2xl: 26px
    3xl: 34px
    4xl: 44px
  weights:                       # --weight-*
    regular: 400
    medium: 500
    semibold: 600
    bold: 700
    extrabold: 800
  leading:                       # --leading-*
    tight: 1.15
    snug: 1.35
    normal: 1.55
  tracking:                      # --tracking-*
    tight: -0.02em
    caps: 0.08em
  roles:                         # derived from section 3; implemented by components.css
    kpi:
      fontSize: 30px             # 30–44px depending on prominence
      fontWeight: 800
      letterSpacing: -0.02em
      fontVariantNumeric: tabular-nums
    card-title:
      fontSize: 14px
      fontWeight: 700
    label:
      fontSize: 13px             # 12–13px
      fontWeight: 600
    body:
      fontSize: 13px             # 13–14px
      fontWeight: 400
      lineHeight: 1.55
    overline:
      fontSize: 11px
      fontWeight: 700
      textTransform: uppercase
      letterSpacing: 0.06em      # 0.06–0.08em
      color: ink-400
radius:                          # --radius-*
  xs: 6px                        # badges
  sm: 10px                       # buttons, inputs
  md: 14px                       # alerts
  lg: 18px                       # cards
  xl: 24px                       # panels, glass
  2xl: 32px
  pill: 999px                    # pills, progress tracks, search
spacing:
  grid: 4px                      # base grid; every gap is a multiple
  scale:                         # --space-*
    1: 4px
    2: 8px
    3: 12px
    4: 16px
    5: 20px
    6: 24px
    8: 32px
    10: 40px
    12: 48px
    16: 64px
  cardPadding: 20px
  cardGutter: 18px               # 16–18px
shadows:                         # --shadow-*
  xs: "0 1px 2px rgba(28,32,84,0.06)"
  sm: "0 2px 8px rgba(28,32,84,0.08)"
  md: "0 8px 24px rgba(28,32,84,0.10)"     # resting card
  lg: "0 16px 48px rgba(28,32,84,0.14)"    # hover / overlay
  glow-brand: "0 8px 24px rgba(91,95,239,0.35)"
  glow-green: "0 8px 24px rgba(46,204,154,0.35)"
  glow-coral: "0 8px 24px rgba(255,122,138,0.35)"
  inner-glass: "inset 0 1px 0 rgba(255,255,255,0.7)"
motion:                          # full standard in MOTION.md
  durations:
    instant: 100ms
    fast: 180ms
    base: 280ms
    slow: 450ms
    hero: 800ms
  easings:
    out: "cubic-bezier(0.16, 1, 0.3, 1)"
    in-out: "cubic-bezier(0.65, 0, 0.35, 1)"
    spring: "cubic-bezier(0.34, 1.56, 0.64, 1)"
    linear: linear
  keyframes:                     # defined in tokens/motion.css
    - sp-fade-up
    - sp-scale-in
    - sp-spin
    - sp-pulse
    - sp-shimmer
    - sp-float
    - sp-bar-grow
    - sp-draw
    - sp-toast-in
components:                      # class API in components.css; rules in section 5
  page: "sp-page — the --grad-page ground; no upstream counterpart"
  type: "sp-display, sp-h1, sp-h2, sp-h3, sp-h4, sp-lead, sp-p, sp-small, sp-overline, sp-kpi, sp-code"
  card: "sp-card, --hover, --dark, __title — light by default, dark for every chart and table"
  glass: "sp-glass — chrome only, never a data surface"
  stat: "sp-stat, __label, __value, __delta — the KPI tile; direction via [data-trend]"
  table: "sp-table, --dark, --compact, __mono — first column 600, statuses always a badge"
  badge: "sp-badge, --neutral/--success/--warning/--danger/--info/--brand, --dot"
  pill: "sp-pill — filter chips; selected state via [aria-pressed]"
  alert: "sp-alert, --info/--success/--warning/--danger, __title, __body"
  icontile: "sp-icontile, --coral/--green/--orange/--purple/--navy — the signature motif"
  progress: "sp-progress, __label, __value, __track, __bar"
  ring: "sp-ring, --turn, __arc, __readout — radial meter; --turn ONLY for dash-array rings, never a polar gauge"
  segment: "sp-segment, __btn, .is-active — verdict/family filter"
  search: "sp-search, __input — text search across clusters"
  button: "sp-btn, --primary/--secondary/--ghost/--danger, --sm/--lg, --icon (base IS outline)"
  tooltip: "sp-tip — hover label from [data-tip]; not an accessible name"
  divider: "sp-divider"
  empty: "sp-empty, __icon, __title, __message"
---

# SaaS Pro — DESIGN.md

The visual standard for all SaaS Pro surfaces. Derived from a glassmorphic dashboard
inspiration image held upstream and not bundled here. Grounded in WCAG 2.2 contrast
requirements and platform conventions (Material elevation logic, Apple HIG glass-material
usage), adapted to the brand.

## 1. Principles
1. **Numbers first.** The data is the interface. Type hierarchy exists to make KPIs legible in under a second.
2. **Two worlds, one page.** Light glass chrome + white KPI cards; dark navy cards for dense data (charts, tables). Never mix a third card style.
3. **Color means something.** Gradients are identity (chrome, active states, icon chips). Semantic colors are status only. Neutrals do the reading work.
4. **Soft physics.** Everything floats: wide blue-tinted shadows, generous radii, lift-on-hover. Nothing is flat, nothing is harsh.

## 2. Color
- Brand: indigo `--brand-500 #5B5FEF` → blue `--blue-500 #3B82F6`; gradients run 135–150°.
- Neutral "ink" scale is blue-tinted; never use pure grays (#888) or pure black.
- Dark surfaces: `--navy-900 #23265E` with white-alpha text (92% primary / 55% dim) and 12% white lines.
- Accents (coral, green, orange, purple, teal) appear ONLY as: icon-tile fills, chart series, avatar fallbacks, soft-badge tints. Never page or card backgrounds.
- Contrast: body text ≥ 4.5:1. **Three corrections to this rule, each computed
  rather than assumed — see components.css's header for the numbers.** (a)
  `ink-600` on white passes at 7.60:1, but `ink-400`/`--text-muted` is 2.88:1
  and must not carry text; use `ink-500` (4.84:1). (b) "pure white ≥ 600 weight
  at ≥ 12px" does **not** rescue small white text on `--grad-brand`: the outer
  stops are 4.02:1 and 3.68:1, and WCAG large text needs ≥ 18.66px bold. Small
  white text on a filled control uses solid `--brand-600` (6.11:1); gradients
  carry white type only at display sizes, and otherwise live on non-text
  surfaces where 3:1 applies. (c) A raw semantic hue is a fill, not a text
  colour — `--success` on `--success-soft` is 2.43:1. Semantic text uses the
  `--*-strong` ramp.
- **This system is light-only.** There is no dark page theme, no `prefers-color-scheme`
  block, and no `data-theme` switch. `--navy-*` is a card surface for dense data, not a
  page ground. Do not promote it to one — the dark neutrals, lines and washes that would
  need are not defined here, and inventing them is out of scope for a consumer.

## 3. Typography
- Family: Plus Jakarta Sans (400/500/600/700/800); JetBrains Mono 400/600 for IDs, amounts, timestamps, code.
- KPI numbers: 30–44px / 800 / -0.02em / tabular-nums.
- Card titles: 14px/700. Labels: 12-13px/600. Body: 13-14px/400-500 at 1.55.
- Overlines: 11px/700, uppercase, +0.06–0.08em, ink-400.
- Minimum text size 11px. Never letterspace lowercase body text.

## 4. Space, radius, elevation
- 4px base grid. Card padding 20px; card gutters 16–18px (dashboard grid 18).
- Radii: buttons/inputs 10px, cards 18px, panels/modals 24px, icon tiles ≈ 32% of size, pills 999px.
- Shadows: `--shadow-md` resting card, `--shadow-lg` hover/overlay. Gradient elements may add colored glow (`--shadow-glow-*`) — max one glowing element per region.
- Glass recipe (chrome only): rgba(255,255,255,0.55–0.72) + backdrop-blur(16–24px) + 1px rgba-white border + inset top highlight.

## 5. Components (canonical rules)
- **Button**: one `primary` per view; `glow` reserved for the hero CTA. Icons 15–16px leading.
- **Card**: light by default; `dark` for any chart or table. Dark cards never nest in dark cards.
- **IconTile**: the signature motif — gradient chip + white icon; use to give lists/statuses personality. One color family per list is fine; rainbow across a list is fine; random per-render color is not.
- **Table**: first column 600 weight; IDs/amounts mono; statuses always Badge, single word.
- **Badge**: soft bg + strong text; `dot` for live states.
- **Modal**: scrim rgba(18,20,43,0.45) + blur(6px); spring-scale in.
- **Toast**: glass, bottom-right stack, 8px gap; auto-dismiss 5s with countdown bar.
- **Sidebar**: active route = gradient pill + glow. **Topbar**: always the brand gradient. **Dock**: floating glass, gradient tiles, spring hover.

Upstream ships React implementations of all of these. The copy bundled here is
`components.css` — a hand-derived CSS projection covering the subset a static report
uses. Modal, Toast, Sidebar, Topbar and Dock have **no** class in it; their rules above
are retained because they document the system, not because a report renders them.

## 6. Iconography
Lucide-style 1.75–2px stroke, round caps, 16/20/24px. White inside gradient tiles,
currentColor elsewhere. No emoji, no filled icon fonts. Upstream ships a stand-in icon
set that is not bundled here — inline the handful of SVG paths you actually need.

## 7. Accessibility
- Text contrast ≥ 4.5:1, computed, not eyeballed. `components.css` already
  satisfies it for every class it defines; the four overrides it makes to do so
  are listed in its header. Hand-authored markup and hand-built SVG have to
  clear the same floor — see the three corrections in section 2.
- Chart furniture (gridlines, hairline borders, faint dividers) is exempt: it is
  decoration, not meaningful non-text content, and forcing 3:1 on a gridline
  would wreck the chart. Anything a reader must *distinguish* to read the data —
  a series colour, a zone band, an icon carrying meaning — is not exempt.
- Focus: always visible — `--focus-ring` 3px brand at 30%.
- Hit targets ≥ 32px dense UI, ≥ 44px touch surfaces.
- Motion respects `prefers-reduced-motion` (see MOTION.md §6).
- Don't encode meaning in color alone — pair with icon, dot, or label.
