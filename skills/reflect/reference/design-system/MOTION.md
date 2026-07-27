# SaaS Pro — MOTION.md

Motion standard for SaaS Pro. Based on Material Design motion durations/easing and disability-safe practice (WCAG 2.3.3 Animation from Interactions), tuned to the brand's "soft physics" feel.

## 1. Principles
1. **Inform, then delight.** Motion explains hierarchy (what appeared, where it came from). Playfulness is budgeted: springs only on small elements.
2. **Fast chrome, slow data.** Controls respond ≤ 180ms; data visualizations may take up to 1.3s to draw because they reward watching.
3. **One hero per view.** A single count-up or chart draw per screen; everything else enters quietly.

## 2. Tokens
| Token | Value | Use |
|---|---|---|
| --dur-instant | 100ms | press feedback, focus ring |
| --dur-fast | 180ms | hover, tooltip, tab switch |
| --dur-base | 280ms | entrances, toasts, modals |
| --dur-slow | 450ms | progress bars, layout shifts |
| --dur-hero | 800ms | rings, gauges, count-ups |
| --ease-out | cubic-bezier(.16,1,.3,1) | all entrances (default) |
| --ease-in-out | cubic-bezier(.65,0,.35,1) | loops, back-and-forth |
| --ease-spring | cubic-bezier(.34,1.56,.64,1) | toggles, chips, docks, modals |

## 3. Patterns
- **Entrance**: fade-up 10px, `--dur-base --ease-out`, stagger 40–60ms per sibling (keyframes `sp-fade-up`, `sp-scale-in`).
- **Press**: scale(0.97) at `--dur-instant`. **Hover lift**: translateY(-2px) + shadow deepen at `--dur-fast`.
- **Charts**: lines draw via dash-offset (`sp-draw`, ≤1.3s); bars grow from baseline staggered 50ms (`sp-bar-grow`); rings/gauges sweep `--dur-hero`.
- **Counters**: ease-out-cubic count-up ≤ 1.2s (AnimatedCounter).
- **Loading**: spinner 0.9s linear; skeleton shimmer 1.4s linear (`sp-shimmer`); dots pulse staggered 160ms.
- **Toasts**: spring in from +12px (`sp-toast-in`); countdown bar linear.
- **Ambient float** (`sp-float`, 3s): empty-state icons and marketing chips only — never data.

## 4. Choreography
Screen load order: chrome (instant) → cards stagger top-left → bottom-right → the one hero animation. Total settle < 1.2s.

## 5. Libraries
- CSS keyframes (in `tokens/motion.css`) cover 90% of cases — prefer them.
- **GSAP** for orchestrated sequences (stagger timelines, scroll reveals): `gsap.from('.card', { y: 22, opacity: 0, stagger: 0.08, ease: 'power3.out' })`.
- **three.js / WebGL** only for hero/marketing moments: brand-colored geometry, ambient
  rotation ≤ 0.02 rad/frame, always behind content, **never on data screens**. (Upstream
  SaaS Pro illustrates this in a reference sheet that is not bundled here.)

## 6. Reduced motion
Under `prefers-reduced-motion: reduce`: disable float/shimmer loops and WebGL rotation; entrances become opacity-only; counters and charts render final state immediately. Never rely on motion to convey status.
