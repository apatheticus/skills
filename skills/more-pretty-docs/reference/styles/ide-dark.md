# ide-dark

**Primary axis:** material · **Aliases:** `editor-dark`, `dev-tool`, `ide`

<div align="center">
<img src="../../docs/samples/ide-dark.svg" alt="The ide-dark specimen — the Source, Transform, Store diagram rendered in this style at full width." width="820">
</div>


## Intent

The chrome of a dark-theme code editor: softly rounded panes on a near-black canvas,
a one-step-lighter panel surface, hairline dividers, a syntax-highlight palette used
sparingly, and a status strip along the bottom. Choose it for language tooling,
linters, formatters, LSP servers, extensions, and developer tools whose surface *is*
an editor.

**Compare `terminal-minimalist`:** that style is a TUI — radius `0`, monospace
everywhere, a character grid, `exit 0`. This one is the GUI wrapped around it:
rounded panes, mixed proportional and mono type, Bézier connectors, eased motion. If
the visual has panes and a sidebar, you're here; if it has a prompt, you're there.

## Palette treatment

Three greys and a syntax set. Canvas (`#0D1117`), pane surface one step lighter
(`#161B22`), divider (`#30363D`), and text in a light neutral. On top of that, at
most **three** syntax hues borrowed from the repo's palette — conventionally a green
for success or strings, an amber for warning, and a blue for identifiers. Syntax
colour is semantic: a hue means one thing across the whole board, never decoration.

## Shape language

Radius `6`–`10` on panes, `4` on inline chips, `999` on status pills. Dividers are
`1` hairlines in the divider grey — never a heavier rule, and never a shadow doing a
divider's job. Panes tile edge to edge at a single gutter; a sidebar is narrower than
the editor pane by a clear ratio, not by a few pixels.

## Material / depth

Nearly flat, with one step of elevation. Depth is **surface lightness**: canvas,
pane, chip, each one step up. A single soft `feDropShadow` is permitted on a floating
element — an autocomplete popover, a hover card — and nowhere else. No gradients, no
texture, no bevels.

## Type treatment

Mono for anything that is code, identifiers, paths or numbers — JetBrains Mono, IBM
Plex Mono, ui-monospace. A UI sans for labels, tab titles and the status strip. Code
at `20`–`22`, UI labels at `18`–`20`, one `40+` title. Never set prose in the mono
face or code in the sans; the split *is* the style, and collapsing it reads as a
mockup rather than an editor.

## Motion character

Small and eased, the way an editor's own UI moves. A caret blink on `steps(1, end)`
at `2s`. A diff gutter mark fading in and holding. A packet or highlight travelling a
Bézier connector between panes at `6s`, `cubic-bezier(.4,0,.2,1)`. One or two
motions; an editor that animates constantly is a distraction, not a tool.

## SVG recipes

Pane stack, hairline divider, status strip and caret:

```svg
<style>
  svg { --canvas:#0d1117; --pane:#161b22; --div:#30363d; --ink:#e6edf3;
        --ok:#3fb950; --warn:#d29922; --id:#58a6ff; }
  .canvas{ fill: var(--canvas); }
  .pane  { fill: var(--pane); stroke: var(--div); stroke-width: 1; }
  .div   { stroke: var(--div); stroke-width: 1; }
  .code  { fill: var(--ink); font-family: 'JetBrains Mono', 'IBM Plex Mono',
           ui-monospace, Consolas, monospace; font-size: 21px; }
  .ui    { fill: var(--ink); font-family: -apple-system, 'Segoe UI', Inter,
           system-ui, sans-serif; font-size: 19px; }
  .ok    { fill: var(--ok); }  .warn { fill: var(--warn); }  .id { fill: var(--id); }
  .caret { animation: caret 2s steps(1, end) infinite; }
  @keyframes caret { 0%,49% { opacity: 1 } 50%,100% { opacity: 0 } }
  .flow  { offset-rotate: 0deg; animation: flow 6s cubic-bezier(.4,0,.2,1) infinite; }
  @media (prefers-reduced-motion: reduce) {
    .caret { animation: none; opacity: 1 } .flow { display: none }
  }
</style>

<rect class="canvas" x="0" y="0" width="1200" height="620"/>
<rect class="pane" x="40"  y="40" width="260" height="500" rx="8"/>
<rect class="pane" x="320" y="40" width="840" height="500" rx="8"/>
<line class="div"  x1="320" y1="470" x2="1160" y2="470"/>

<text class="code" x="348" y="104"><tspan class="id">parse</tspan>(source)</text>
<rect class="caret" x="520" y="86" width="10" height="24" fill="var(--ink)"/>

<rect x="320" y="492" width="840" height="48" fill="var(--pane)"/>
<text class="ui ok" x="348" y="522">0 problems</text>
```

The Bézier connector between panes is a `<path>` with `animateMotion`/`<mpath>` or a
CSS `offset-path`; either way the SMIL variant needs an explicit `display: none`
rule under reduced motion, since SMIL ignores the media query.

## Relaxes

| Gate | Default → floor |
| --- | --- |
| filter depth | 1 → **2** chained primitives per element |

Two covers a popover shadow built as blur plus offset rather than a single
`feDropShadow`. Contrast is not relaxed: `#e6edf3` on `#161b22` is about 14:1, and
the syntax hues were picked to clear 4.5:1 on the pane surface — verify any
substitute from the repo's own palette rather than assuming.

## Never

Prose in the mono face or code in the sans, a fourth syntax hue, a hue that means two
different things, gradients, texture, a shadow standing in for a divider, radius
above `10` on a pane, a light canvas, or continuous ambient motion.
