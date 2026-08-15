#!/usr/bin/env python3
"""Gate for hand-authored animated SVG produced by the prettier-svg-docs skill.

Deterministic, python3 stdlib only. Checks, in order:

  structural  no <script>, no <foreignObject>, no remote href/@import;
              viewBox, <title>, <desc>, data-loop-s present
  seam        every CSS animation duration and SMIL dur divides data-loop-s;
              every animation is infinite/indefinite
  motion a11y a prefers-reduced-motion block exists and covers every animated
              class AND every SMIL-animated element (CSS cannot stop SMIL, so
              those need display:none / visibility:hidden)
  legibility  every font-size meets its role floor
  system      every colour traces to a prettydocs.md palette role or a declared
              custom property; text contrast >= 4.5:1 against its data-bg role
  style       the resolved style's forbid / require invariants and relaxed floors
  fidelity    the style's *minimum* — required primitives, minimum filter-chain
              depth, minimum drawn geometry. Every other gate here is a ceiling
              or a legibility floor, so a flat render used to pass clean; this is
              the half that asks whether the file looks like what it claims
  diagram     OPT-IN, and only when the root carries data-diagram: the type
              resolves in diagrams.json; node/connector/focal/zone budgets; no
              diagonal connector; no label mask clipped by a later node or sitting
              inside the gap floor of any connector; node geometry on the 4-unit
              grid (skipped for a `plotted` type, whose node IS the datum); no
              animation that moves geometry; the legend below every node
  size        warn at 60 KB, fail over 150 KB

Usage:
    svg_check.py [--design prettydocs.md] [--style SLUG] [--diagrams diagrams.json]
                 [--json] FILE.svg [FILE.svg ...]

Output is one line per finding: ERROR / SOFTENED / WARN / NOTE.
Exit 0 = no errors, exit 1 = at least one ERROR. SOFTENED lines are passes that
used a declared style relaxation; record them in viz.json's `relaxed` array.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"

# Role -> minimum SVG font-size, from viz-production.md's rendered-scale table.
FONT_FLOORS = {
    "hero": 48.0,
    "title": 40.0,
    "essential": 20.0,
    "label": 18.0,
    "metadata": 16.0,
}
DEFAULT_FONT_ROLE = "label"

SMIL_TAGS = {"animate", "animateMotion", "animateTransform", "animateColor", "set"}
FILTER_PRIMITIVES = {
    "feBlend", "feColorMatrix", "feComponentTransfer", "feComposite",
    "feConvolveMatrix", "feDiffuseLighting", "feDisplacementMap", "feDropShadow",
    "feFlood", "feGaussianBlur", "feImage", "feMerge", "feMorphology",
    "feOffset", "feSpecularLighting", "feTile", "feTurbulence",
}
COLOUR_PROPS = {"fill", "stroke", "stop-color", "flood-color", "color"}
# Elements whose rx/ry are geometry, not corner radius — never a radius rule.
NON_RECT_SHAPES = {"ellipse", "circle", "radialGradient"}
# What counts as drawn geometry for the density floor. Structural wrappers (<g>,
# <defs>, <mask>) are excluded: nesting groups is not draughtsmanship.
DRAWN_TAGS = {"rect", "circle", "ellipse", "line", "path", "polyline", "polygon",
              "text", "use", "image"}
EPS = 1e-6

# --- diagram class -----------------------------------------------------------
# Properties whose animation would move a coordinate this checker measures. A
# diagram that animates one of them passes its geometry gate in one frame and
# fails in another, which is why the rule is mechanical rather than aesthetic.
GEOMETRY_PROPS = {"d", "x", "y", "cx", "cy", "r", "rx", "ry",
                  "width", "height", "x1", "y1", "x2", "y2", "points", "viewbox"}
# A quarter-arc elbow at 1200 scale advances ~10 units; a bridge hop ~20. A curve
# that travels further than this in BOTH axes is a diagonal wearing a bezier.
CORNER_SPAN_MAX = 48.0
# Below this, a "diagonal" is a rounding artefact rather than a slant.
AXIS_TOL = 0.75


# ----------------------------------------------------------------- utilities

def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def decorative(el: ET.Element, parents: dict) -> bool:
    """True when the element, or any ancestor, is aria-hidden."""
    node = el
    seen = 0
    while node is not None and seen < 64:
        if (node.get("aria-hidden") or "").strip().lower() == "true":
            return True
        node = parents.get(node)
        seen += 1
    return False


def chain_depth(filt: ET.Element) -> int:
    """Primitives that are direct children of one <filter> — the chain length."""
    return sum(1 for c in filt if local(c.tag) in FILTER_PRIMITIVES)


# Cubic/quadratic curve commands. Arcs are deliberately absent: a rounded rect and a
# cylinder cap are drawn with A, so counting them would let a mathematically perfect
# render satisfy a floor that exists to prove the outline was re-splined.
CURVE_CMDS = {"c": 6, "s": 4, "q": 4, "t": 2}
_PATH_TOKEN = re.compile(r"([MmZzLlHhVvCcSsQqTtAa])|(-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)")


def curve_segments(d: str) -> int:
    """Cubic/quadratic segments in one path's `d`, counting implicit repetition.

    A curve command may carry several coordinate groups — `C a b c d e f g h i j k l`
    is two segments, not one — so counting command letters undercounts a compactly
    written path. Divide each command's argument run by its arity instead.
    """
    total, cmd, args = 0, None, 0

    def flush() -> int:
        if cmd in CURVE_CMDS and args:
            return max(1, args // CURVE_CMDS[cmd])
        return 0

    for m in _PATH_TOKEN.finditer(d or ""):
        if m.group(1):
            total += flush()
            cmd, args = m.group(1).lower(), 0
        else:
            args += 1
    return total + flush()


def deepest_curve(by_tag: dict) -> int:
    """The most curved single path in the file."""
    return max((curve_segments(el.get("d") or "") for el in by_tag.get("path", [])),
               default=0)


def primitives_in(filters: list[ET.Element]) -> set[str]:
    """Every filter primitive used anywhere in `filters`, by local tag name."""
    found = set()
    for filt in filters:
        for child in filt:
            name = local(child.tag)
            if name in FILTER_PRIMITIVES:
                found.add(name)
    return found


def parse_time(value: str) -> float | None:
    """'4s' / '500ms' / '.5s' / '4' -> seconds."""
    m = re.fullmatch(r"\s*(-?\d*\.?\d+)\s*(ms|s)?\s*", value)
    if not m:
        return None
    n = float(m.group(1))
    return n / 1000.0 if m.group(2) == "ms" else n


def divides(loop: float, dur: float) -> bool:
    """True when `dur` fits a whole number of times into `loop`."""
    if dur <= 0:
        return False
    q = loop / dur
    return abs(q - round(q)) < 1e-6 and round(q) >= 1


def norm_hex(value: str) -> str | None:
    m = re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", value.strip())
    if not m:
        return None
    h = m.group(1).lower()
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h


def rgb(hex_colour: str) -> tuple[float, float, float]:
    h = hex_colour.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[return-value]


def luminance(hex_colour: str) -> float:
    def chan(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(c) for c in rgb(hex_colour))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg: str, bg: str) -> float:
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def composite(fg: str, bg: str, alpha: float) -> str:
    """Flatten a translucent foreground onto its ground so contrast is honest."""
    if alpha >= 1.0:
        return fg
    f, b = rgb(fg), rgb(bg)
    out = tuple(round(255 * (f[i] * alpha + b[i] * (1 - alpha))) for i in range(3))
    return "#%02x%02x%02x" % out


# ------------------------------------------------------------- CSS scanning

def strip_css_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def split_blocks(css: str) -> list[tuple[str, str]]:
    """Split CSS into (prelude, body) pairs at the top level, brace-aware."""
    out: list[tuple[str, str]] = []
    depth = 0
    buf: list[str] = []
    prelude = ""
    for ch in css:
        if ch == "{":
            if depth == 0:
                prelude = "".join(buf).strip()
                buf = []
            else:
                buf.append(ch)
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                out.append((prelude, "".join(buf)))
                buf, prelude = [], ""
            elif depth > 0:
                buf.append(ch)
            else:  # stray brace; resync
                depth = 0
                buf, prelude = [], ""
        else:
            buf.append(ch)
    return out


FONT_SIZE_TOKEN = re.compile(r"^\d*\.?\d+(?:px|pt|pc|em|rem|ex|ch|vw|vh|%)(?:/\S+)?$", re.I)


def expand_font_shorthand(value: str) -> dict[str, str]:
    """`font: 600 14px/1.4 Inter, sans-serif` -> font-size + font-family.

    Hand-authored SVG uses the shorthand constantly, and the longhand-only
    reader silently skipped every one of them: `mono_only` passed vacuously and
    no FONT_FLOORS applied. Only the two properties this checker actually reads
    are recovered; a system keyword (`font: menu`) or any value with no
    unit-bearing size token expands to nothing.
    """
    parts = value.split()
    for i, tok in enumerate(parts):
        if FONT_SIZE_TOKEN.match(tok) and i + 1 < len(parts):
            return {"font-size": tok.split("/", 1)[0],
                    "font-family": " ".join(parts[i + 1:])}
    return {}


def parse_decls(body: str) -> dict[str, str]:
    decls: dict[str, str] = {}
    for part in body.split(";"):
        if ":" not in part:
            continue
        prop, _, value = part.partition(":")
        prop, value = prop.strip().lower(), value.strip()
        if prop and value:
            # The shorthand lands first so an explicit longhand after it wins,
            # which is what the cascade does.
            if prop == "font":
                decls.update(expand_font_shorthand(value))
            decls[prop] = value
    return decls


class Stylesheet:
    """Just enough CSS to check a hand-authored SVG."""

    def __init__(self, css: str) -> None:
        self.tokens: dict[str, str] = {}          # --name -> value
        self.rules: list[tuple[str, dict]] = []   # (selector, decls) outside @media
        self.animated: dict[str, dict] = {}       # selector -> decls, has animation
        self.reduce_rules: list[tuple[str, dict]] = []
        self.keyframes: dict[str, str] = {}
        self._load(strip_css_comments(css))

    def _add_rule(self, prelude: str, decls: dict, into_reduce: bool) -> None:
        for sel in (s.strip() for s in prelude.split(",")):
            if not sel:
                continue
            if into_reduce:
                self.reduce_rules.append((sel, decls))
            else:
                self.rules.append((sel, decls))
                if "animation" in decls or "animation-name" in decls:
                    self.animated[sel] = decls
            for prop, value in decls.items():
                if prop.startswith("--"):
                    self.tokens[prop] = value

    def _load(self, css: str) -> None:
        for prelude, body in split_blocks(css):
            head = prelude.lower()
            if head.startswith("@media"):
                reduce_block = "prefers-reduced-motion" in head and "reduce" in head
                for inner_prelude, inner_body in split_blocks(body):
                    self._add_rule(inner_prelude, parse_decls(inner_body), reduce_block)
            elif head.startswith("@keyframes"):
                self.keyframes[prelude.split(None, 1)[-1].strip()] = body
            elif head.startswith("@"):
                continue
            else:
                self._add_rule(prelude, parse_decls(body), False)

    def resolve(self, value: str, depth: int = 0) -> str:
        """Expand var(--x[, fallback]) against the file's own token block."""
        if depth > 6 or "var(" not in value:
            return value
        def sub(m: re.Match) -> str:
            name = m.group(1).strip()
            fallback = (m.group(2) or "").strip()
            return self.tokens.get(name, fallback)
        return self.resolve(re.sub(r"var\(\s*(--[\w-]+)\s*(?:,([^()]*))?\)", sub, value), depth + 1)

    def decls_for(self, tag: str, classes: list[str], el_id: str | None) -> dict[str, str]:
        """Merge matching rules in source order: element, then class, then id."""
        merged: dict[str, str] = {}
        for want in ([tag] if tag else []) + [f".{c}" for c in classes] + \
                    ([f"#{el_id}"] if el_id else []):
            for sel, decls in self.rules:
                if sel == want or sel.split(":")[0] == want:
                    merged.update(decls)
        return merged

    def reduce_selectors(self) -> set[str]:
        return {sel for sel, _ in self.reduce_rules}

    def reduce_hidden(self) -> set[str]:
        out = set()
        for sel, decls in self.reduce_rules:
            if decls.get("display", "").strip() == "none" or \
               decls.get("visibility", "").strip() in {"hidden", "collapse"}:
                out.add(sel)
        return out


# ------------------------------------------------------------------ palette

def load_palette(path: Path) -> dict[str, str]:
    """Read the Palette table out of a prettydocs.md: | role | `#hex` | notes |."""
    palette: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        role = cells[0].strip("` ").lower()
        value = norm_hex(cells[1].strip("` "))
        if value and role and not role.startswith("---"):
            palette.setdefault(role.replace(" ", "-"), value)
    return palette


# -------------------------------------------------------------- the checker

class Findings:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []
        self.relaxed: set[str] = set()

    def add(self, level: str, path: str, msg: str) -> None:
        self.rows.append((level, path, msg))

    def error(self, p: str, m: str) -> None: self.add("ERROR", p, m)
    def warn(self, p: str, m: str) -> None: self.add("WARN", p, m)
    def note(self, p: str, m: str) -> None: self.add("NOTE", p, m)

    def softened(self, p: str, token: str, m: str) -> None:
        """`token` is the gate@floor string recorded in viz.json's `relaxed` array."""
        self.relaxed.add(token)
        self.add("SOFTENED", p, m)

    @property
    def n_errors(self) -> int:
        return sum(1 for lvl, _, _ in self.rows if lvl == "ERROR")


def effective_limits(style: dict | None, defaults: dict) -> dict:
    limits = dict(defaults)
    if style:
        limits.update(style.get("relax", {}))
    return limits


def check_file(path: Path, catalog: dict, slug: str | None,
               palette: dict[str, str], f: Findings,
               diagrams: dict | None = None) -> None:
    label = str(path)
    raw = path.read_text(encoding="utf-8")

    styles = catalog.get("styles", {})
    style = styles.get(slug) if slug else None
    if slug and style is None:
        f.note(label, f"style '{slug}' is not in the catalog — treating as ad-hoc: "
                      "default floors, no style invariants")
    limits = effective_limits(style, catalog.get("defaults", {}))

    # ---- parse
    #
    # This is stdlib-only by design (the skill has zero external dependencies), and
    # xml.etree is documented as vulnerable to entity-expansion attacks. A committed
    # SVG asset has no legitimate reason to carry a DTD, so refusing one both closes
    # that hole and is a real structural check in its own right.
    if re.search(r"<!(DOCTYPE|ENTITY)\b", raw, re.I):
        f.error(label, "the file declares a DOCTYPE or ENTITY — strip it; a committed "
                       "SVG asset needs no DTD, and entity expansion is an attack "
                       "surface for any tool that reads it")
        return
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        f.error(label, f"not well-formed XML — {e}")
        return

    parents: dict[ET.Element, ET.Element] = {}
    for parent in root.iter():
        for child in parent:
            parents[child] = parent
    everything = list(root.iter())
    by_tag: dict[str, list[ET.Element]] = {}
    for el in everything:
        by_tag.setdefault(local(el.tag), []).append(el)

    css = "\n".join(el.text or "" for el in by_tag.get("style", []))
    sheet = Stylesheet(css)

    # ---- structural
    for banned in ("script", "foreignObject"):
        if banned in by_tag:
            f.error(label, f"<{banned}> is present — never allowed in a committed asset")

    for el in everything:
        for key in ("href", f"{{{XLINK_NS}}}href", "src"):
            value = el.get(key)
            if value and re.match(r"(?i)^(https?:)?//|^https?:", value.strip()):
                f.error(label, f"remote reference on <{local(el.tag)}>: {value}")
    if re.search(r"@import", css, re.I):
        f.error(label, "CSS @import is present — no remote or external stylesheets")
    if re.search(r"url\(\s*['\"]?(https?:)?//", css, re.I):
        f.error(label, "CSS url() points off-host — no remote assets")
    if re.search(r"@font-face", css, re.I):
        f.warn(label, "@font-face in an SVG asset — GitHub will not fetch it; "
                      "use a system stack or convert text to paths")

    if not root.get("viewBox"):
        f.error(label, "root <svg> has no viewBox")
    for required in ("title", "desc"):
        if not by_tag.get(required):
            f.error(label, f"missing <{required}> on the root <svg>")

    loop_attr = root.get("data-loop-s")
    if loop_attr is None:
        f.error(label, "root <svg> has no data-loop-s — declare the loop length "
                       "(0 for a static)")
        loop = None
    else:
        loop = parse_time(loop_attr)
        if loop is None or loop < 0:
            f.error(label, f"data-loop-s='{loop_attr}' is not a duration")
            loop = None
        elif loop and not (8.0 <= loop <= 14.0):
            f.warn(label, f"loop is {loop:g}s — the design-system rule is 8–14s")

    smil = [el for el in everything if local(el.tag) in SMIL_TAGS]
    is_static = loop == 0

    # ---- seam
    if is_static:
        if sheet.animated or smil:
            f.error(label, "data-loop-s='0' declares a static, but the file animates")
    elif loop:
        for sel, decls in sheet.animated.items():
            shorthand = sheet.resolve(decls.get("animation", ""))
            count = decls.get("animation-iteration-count", "")
            infinite = "infinite" in shorthand.lower() or "infinite" in count.lower()
            if not infinite:
                f.error(label, f"{sel}: animation is not `infinite` — it stops mid-loop")

            durations = [d for d in (parse_time(t) for t in re.findall(
                r"(?<![\w.-])(\d*\.?\d+m?s)(?![\w-])", shorthand)) if d is not None]
            explicit = parse_time(decls.get("animation-duration", ""))
            if explicit is not None:
                durations.append(explicit)
            if not durations:
                f.warn(label, f"{sel}: no duration found in `{shorthand or 'animation'}`")
            for dur in durations[:1]:  # the first time value in the shorthand is the duration
                if not divides(loop, dur):
                    f.error(label, f"{sel}: {dur:g}s does not divide the {loop:g}s loop "
                                   f"({loop / dur:.2f} cycles) — visible seam")

            delay = parse_time(decls.get("animation-delay", ""))
            if delay is not None and delay > 0 and not divides(loop, delay):
                f.error(label, f"{sel}: positive animation-delay {delay:g}s does not "
                               f"divide the {loop:g}s loop")

        for el in smil:
            tag = local(el.tag)
            dur = parse_time(el.get("dur", ""))
            if dur is None:
                f.error(label, f"<{tag}> has no parsable dur")
            elif not divides(loop, dur):
                f.error(label, f"<{tag}> dur={dur:g}s does not divide the {loop:g}s loop")
            if el.get("repeatCount", "") != "indefinite":
                f.error(label, f"<{tag}> needs repeatCount='indefinite'")
            if tag not in {"animateMotion"}:
                f.error(label, f"<{tag}> is not allowed — CSS @keyframes for everything "
                               "except <animateMotion> along a path")

    # ---- motion accessibility
    if not is_static and (sheet.animated or smil):
        if not sheet.reduce_rules:
            f.error(label, "no @media (prefers-reduced-motion: reduce) block — mandatory "
                           "for every animated visual")
        else:
            covered = sheet.reduce_selectors()
            for sel in sheet.animated:
                if sel not in covered:
                    f.error(label, f"{sel} animates but is not in the reduced-motion block")
            hidden = sheet.reduce_hidden()
            for el in smil:
                host = parents.get(el)
                if host is None:
                    continue
                names = {f".{c}" for c in (host.get("class") or "").split()}
                if host.get("id"):
                    names.add(f"#{host.get('id')}")
                if not (names & hidden):
                    f.error(
                        label,
                        f"<{local(host.tag)}> carries SMIL but nothing in the "
                        "reduced-motion block hides it — CSS cannot stop SMIL, so it "
                        "needs `display: none` there",
                    )

    # ---- colours, legibility, contrast
    check_paint(root, parents, sheet, palette, limits, catalog, style, label, f)

    # ---- style invariants and the fidelity floor
    #
    # This runs for every file, styled or not. It used to be skipped when no style
    # resolved, which meant the multi-style contact sheet — the one asset that
    # depicts all 31 idioms — was the single file exempt from every fidelity gate.
    check_style(root, by_tag, sheet, style or {}, slug or "", label, f)
    check_attributed(by_tag, catalog, label, f)

    # ---- filter depth
    #
    # A multi-style file attributes each filter to the style it depicts with
    # data-style, and that filter is then measured against its own style's ceiling
    # rather than the file-wide one. Without attribution a contact sheet inherits
    # the global default and has to fake every material it shows.
    styles_cat = catalog.get("styles", {})
    depth_limit = int(limits.get("filter_depth", 1))
    default_depth = int(catalog.get("defaults", {}).get("filter_depth", 1))
    for filt in by_tag.get("filter", []):
        prims = chain_depth(filt)
        fid = filt.get("id", "?")
        owner = (filt.get("data-style") or "").strip().lower()
        own_limit, whose = depth_limit, ""
        if owner:
            spec = styles_cat.get(owner)
            if spec is None:
                f.error(label, f"filter #{fid} declares data-style='{owner}', which is "
                               "not a catalog style")
            else:
                own_limit = int(spec.get("relax", {}).get("filter_depth", default_depth))
                whose = f" (attributed to '{owner}')"
        if prims > own_limit:
            f.error(label, f"filter #{fid} chains {prims} primitives, limit is "
                           f"{own_limit}{whose}")
        elif prims > default_depth:
            f.softened(label, f"filter-depth@{own_limit}",
                       f"filter #{fid} chains {prims} primitives — allowed by "
                       f"floor {own_limit}{whose}")

    # ---- size
    size = os.path.getsize(path)
    fail, warn_at = int(limits["bytes_fail"]), int(limits["bytes_warn"])
    default_fail = int(catalog.get("defaults", {}).get("bytes_fail", fail))
    if size > fail:
        f.error(label, f"{size / 1024:.1f} KB exceeds the {fail / 1024:.0f} KB cap")
    elif size > default_fail:
        f.softened(label, f"bytes@{fail // 1024}KB",
                   f"{size / 1024:.1f} KB is over the {default_fail / 1024:.0f} KB default "
                   f"but within this style's {fail / 1024:.0f} KB floor")
    elif size > warn_at:
        f.warn(label, f"{size / 1024:.1f} KB is dense (warn at {warn_at / 1024:.0f} KB)")

    # ---- what this file achieved, not only what it avoided
    #
    # Every other line here reports a limit respected. Reporting fidelity
    # positively is what makes a flat render visible in a run report: it passed,
    # and it passed at depth 1 with 40 elements, which is the tell.
    # ---- diagram (opt-in: only when the root says it is one)
    #
    # A missing catalog must not be a quiet pass. Without this, a file tagged
    # data-diagram gates clean with ZERO diagram checks applied and nothing says so
    # -- the same vacuous-pass hole `gradient_units` and `mono_only` each had once.
    if diagrams is not None:
        check_diagram(root, everything, parents, by_tag, sheet, diagrams, label, f)
    elif root.get("data-diagram"):
        f.error(label, "the root declares data-diagram but scripts/diagrams.json was "
                       "not found, so not one diagram check ran — pass --diagrams or "
                       "restore the catalog rather than shipping an unchecked diagram")

    filts = by_tag.get("filter", [])
    deepest = max((chain_depth(x) for x in filts), default=0)
    drawn = sum(len(by_tag.get(t, [])) for t in DRAWN_TAGS)
    used = sorted(primitives_in(filts))
    f.note(label, f"fidelity: deepest chain {deepest}, {len(filts)} filter(s), "
                  f"{drawn} drawn elements, deepest curve {deepest_curve(by_tag)}"
                  + (f", primitives {', '.join(used)}" if used else ", no filters"))


# ------------------------------------------------------------------ diagrams
#
# Everything below fires only when the root carries data-diagram. That is the
# same shape as data-specimen: a visual that is not a diagram — a hero, a banner,
# a style specimen — never enters this code path, so adding the class moves no
# existing verdict.

NUM_RE = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
CMD_RE = re.compile(r"([MmZzLlHhVvCcSsQqTtAa])")


def path_commands(d: str) -> list[tuple[str, list[float]]]:
    """Tokenize a path `d` into (command, numbers) pairs."""
    out: list[tuple[str, list[float]]] = []
    parts = [p for p in CMD_RE.split(d) if p.strip()]
    i = 0
    while i < len(parts):
        cmd = parts[i]
        if not CMD_RE.fullmatch(cmd):
            i += 1
            continue
        nums = [float(n) for n in NUM_RE.findall(parts[i + 1])] if i + 1 < len(parts) \
            and not CMD_RE.fullmatch(parts[i + 1]) else []
        out.append((cmd, nums))
        i += 2 if nums else 1
    return out


# How many numbers each command consumes per repetition.
ARITY = {"m": 2, "l": 2, "h": 1, "v": 1, "c": 6, "s": 4, "q": 4, "t": 2, "a": 7, "z": 0}


def path_segments(d: str) -> list[tuple[str, float, float, float, float]]:
    """Walk a path into ('line'|'curve'|'arc', x0, y0, x1, y1) segments.

    Only the endpoints matter here. Orthogonality is a property of where a
    segment starts and finishes, and a control point cannot rescue a stroke that
    begins at one corner of the canvas and ends at another.
    """
    segs: list[tuple[str, float, float, float, float]] = []
    x = y = sx = sy = 0.0
    started = False
    for cmd, nums in path_commands(d):
        low = cmd.lower()
        rel = cmd.islower()
        step = ARITY[low]
        if low == "z":
            if started:
                segs.append(("line", x, y, sx, sy))
                x, y = sx, sy
            continue
        if step == 0 or not nums:
            continue
        chunks = [nums[k:k + step] for k in range(0, len(nums) - step + 1, step)]
        for n, chunk in enumerate(chunks):
            x0, y0 = x, y
            if low == "h":
                x = x0 + chunk[0] if rel else chunk[0]
            elif low == "v":
                y = y0 + chunk[0] if rel else chunk[0]
            elif low == "a":
                x = x0 + chunk[5] if rel else chunk[5]
                y = y0 + chunk[6] if rel else chunk[6]
            else:
                dx, dy = chunk[-2], chunk[-1]
                x = x0 + dx if rel else dx
                y = y0 + dy if rel else dy
            if low == "m":
                # A moveto's trailing coordinate pairs are implicit linetos.
                if n == 0:
                    sx, sy, started = x, y, True
                    continue
                segs.append(("line", x0, y0, x, y))
            elif low in {"c", "s", "q", "t"}:
                segs.append(("curve", x0, y0, x, y))
            elif low == "a":
                segs.append(("arc", x0, y0, x, y))
            else:
                segs.append(("line", x0, y0, x, y))
    return segs


def edge_segments(el: ET.Element) -> list[tuple[str, float, float, float, float]]:
    tag = local(el.tag)
    if tag == "path":
        return path_segments(el.get("d") or "")
    if tag == "line":
        try:
            return [("line", float(el.get("x1", 0)), float(el.get("y1", 0)),
                     float(el.get("x2", 0)), float(el.get("y2", 0)))]
        except ValueError:
            return []
    return []


def rect_box(el: ET.Element) -> tuple[float, float, float, float] | None:
    try:
        return (float(el.get("x", 0)), float(el.get("y", 0)),
                float(el.get("width")), float(el.get("height")))
    except (TypeError, ValueError):
        return None


def shape_box(el: ET.Element) -> tuple[float, float, float, float] | None:
    """A bounding box for any drawn shape, not only a <rect>.

    Rects alone are not enough: a `line`, `scatter` or `radar` node is a polyline,
    a circle or a polygon, so a rect-only reading returns None for the whole group
    and every check that depends on a node's extent silently skips. That is the
    vacuous-pass shape this checker's own comments describe for `mono_only` and
    `gradient_units` -- a legend drawn inside the plot area would have gated clean.
    """
    tag = local(el.tag)
    try:
        if tag == "rect":
            return rect_box(el)
        if tag in {"circle", "ellipse"}:
            cx, cy = float(el.get("cx", 0)), float(el.get("cy", 0))
            rx = float(el.get("rx") or el.get("r"))
            ry = float(el.get("ry") or el.get("r") or rx)
            return (cx - rx, cy - ry, 2 * rx, 2 * ry)
        if tag == "line":
            xs = [float(el.get("x1", 0)), float(el.get("x2", 0))]
            ys = [float(el.get("y1", 0)), float(el.get("y2", 0))]
        elif tag in {"polyline", "polygon"}:
            nums = [float(n) for n in NUM_RE.findall(el.get("points") or "")]
            xs, ys = nums[0::2], nums[1::2]
        elif tag == "path":
            segs = path_segments(el.get("d") or "")
            xs = [c for s in segs for c in (s[1], s[3])]
            ys = [c for s in segs for c in (s[2], s[4])]
        else:
            return None
    except (TypeError, ValueError):
        return None
    if not xs or not ys:
        return None
    return (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))


def group_box(el: ET.Element) -> tuple[float, float, float, float] | None:
    """Union of every drawn shape in a marked group — or the element's own box."""
    boxes = [b for b in (shape_box(s) for s in el.iter()) if b]
    if not boxes:
        return None
    x0 = min(b[0] for b in boxes)
    y0 = min(b[1] for b in boxes)
    x1 = max(b[0] + b[2] for b in boxes)
    y1 = max(b[1] + b[3] for b in boxes)
    return (x0, y0, x1 - x0, y1 - y0)


def overlap_2d(a, b) -> tuple[float, float]:
    return (min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]),
            min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))


def contained(inner, outer, eps: float = 0.5) -> bool:
    return (inner[0] >= outer[0] - eps and inner[1] >= outer[1] - eps
            and inner[0] + inner[2] <= outer[0] + outer[2] + eps
            and inner[1] + inner[3] <= outer[1] + outer[3] + eps)


def gap_to_segment(box, seg) -> float:
    """Shortest distance from a rect to an axis-aligned segment. 0 = touching."""
    _, x0, y0, x1, y1 = seg
    lo_x, hi_x = min(x0, x1), max(x0, x1)
    lo_y, hi_y = min(y0, y1), max(y0, y1)
    bx0, by0, bx1, by1 = box[0], box[1], box[0] + box[2], box[1] + box[3]
    dx = max(lo_x - bx1, bx0 - hi_x, 0.0)
    dy = max(lo_y - by1, by0 - hi_y, 0.0)
    return (dx * dx + dy * dy) ** 0.5


def selector_matches(sel: str, tag: str, classes: list[str], el_id: str | None) -> bool:
    base = sel.split(":")[0].strip()
    return base == tag or base in {f".{c}" for c in classes} or \
        (el_id is not None and base == f"#{el_id}")


def check_diagram(root, everything, parents, by_tag, sheet: Stylesheet,
                  diagrams: dict, label: str, f: Findings) -> None:
    kind = (root.get("data-diagram") or "").strip().lower()
    if not kind:
        return

    types = diagrams.get("types", {})
    spec = types.get(kind)
    if spec is None:
        for name, cand in types.items():
            if kind in cand.get("aliases", []):
                kind, spec = name, cand
                break
    if spec is None:
        f.error(label, f"data-diagram='{kind}' is not a type in diagrams.json — "
                       f"one of: {', '.join(sorted(types))}")
        return

    lim = dict(diagrams.get("defaults", {}))
    lim.update({k: v for k, v in spec.items()
                if k not in {"aliases", "summary", "unit"}})
    unit = spec.get("unit", "node")

    order = {id(el): i for i, el in enumerate(everything)}
    nodes = [el for el in everything if el.get("data-node") is not None]
    edges = [el for el in everything if el.get("data-edge") is not None]
    labels = [el for el in everything if el.get("data-label") is not None]
    focal = [el for el in everything if el.get("data-focal") is not None]
    zones = [el for el in everything if el.get("data-zone") is not None]
    legends = [el for el in everything if el.get("data-legend") is not None]

    # ---- budget
    for got, cap, what in ((len(nodes), lim.get("max_nodes"), f"{unit}s (data-node)"),
                           (len(edges), lim.get("max_edges"), "connectors (data-edge)"),
                           (len(focal), lim.get("max_focal"), "focal elements"),
                           (len(zones), lim.get("max_zones"), "zones")):
        if cap is not None and got > cap:
            f.error(label, f"{kind}: {got} {what}, budget is {cap} — split into an "
                           f"overview and a detail diagram rather than shrinking the type")

    # ---- orthogonal connectors
    diagonals = 0
    for el in edges:
        for seg in edge_segments(el):
            kindseg, x0, y0, x1, y1 = seg
            dx, dy = abs(x1 - x0), abs(y1 - y0)
            if kindseg == "line":
                if dx > AXIS_TOL and dy > AXIS_TOL:
                    diagonals += 1
                    f.error(label, f"{kind}: connector segment "
                                   f"({x0:g},{y0:g})->({x1:g},{y1:g}) is diagonal — "
                                   "off-axis connections use a rounded right-angle "
                                   "elbow, not a slant")
            elif kindseg == "curve" and dx > CORNER_SPAN_MAX and dy > CORNER_SPAN_MAX:
                # Beziers only. The rule exists to catch a STRAIGHT slant drawn as a
                # curve -- a `C` with collinear control points renders as a diagonal
                # line. An `A` cannot: a circular arc is curved by construction, and
                # `loop`'s ring is one long arc per station pair, legitimately
                # travelling hundreds of units in both axes. Treating the two alike
                # made `loop` unbuildable under its own gate.
                diagonals += 1
                f.error(label, f"{kind}: curve segment ({x0:g},{y0:g})->({x1:g},{y1:g}) "
                               f"travels {dx:g}x{dy:g} — a corner arc spans about "
                               f"{CORNER_SPAN_MAX:g}; this is a diagonal wearing a bezier")

    # ---- label geometry
    #
    # Paint order is background -> zones -> connectors -> labels -> nodes, so a
    # mask landing inside a node declared LATER is covered by the node fill and
    # the text renders as a fragment on the border. A mask over a zone is fine
    # (zones paint first) and a mask entirely inside a node is a badge chip.
    node_boxes = [(group_box(n), order[id(n)], n) for n in nodes]
    node_boxes = [(b, o, n) for b, o, n in node_boxes if b]
    gap_min = float(lim.get("label_gap_min", 6))
    worst_gap = None
    for lab in labels:
        box = rect_box(lab) or group_box(lab)
        if not box:
            continue
        lorder = order[id(lab)]
        for nbox, norder, _ in node_boxes:
            if norder <= lorder or contained(box, nbox):
                continue
            dx, dy = overlap_2d(box, nbox)
            if dx > 1.0 and dy > 1.0:
                f.error(label, f"{kind}: label mask at ({box[0]:g},{box[1]:g}) is "
                               f"clipped by a node declared later (overlap "
                               f"{dx:g}x{dy:g}) — move the label onto a free segment "
                               "of its connector")
                break
        for el in edges:
            for seg in edge_segments(el):
                if seg[0] != "line":
                    continue
                g = gap_to_segment(box, seg)
                worst_gap = g if worst_gap is None else min(worst_gap, g)
                if g < gap_min:
                    f.error(label, f"{kind}: label mask at ({box[0]:g},{box[1]:g}) sits "
                                   f"{g:.1f} units from a connector — the gap floor is "
                                   f"{gap_min:g}, so the reader can still trace the line")
                    break
            else:
                continue
            break

    # ---- 4-unit grid
    #
    # On a plotted type the node IS the datum -- a gantt bar's x and width are the
    # measurement, a scatter point's cx and cy are the values -- so enforcing the
    # grid there would round the number the chart exists to report. The skeleton
    # (axes, ticks, gridlines, the plot rect, the legend) is not a node and is still
    # checked. Declared per type rather than inferred from `max_edges == 0`, because
    # `venn`, `pyramid` and `quadrant` also have no connectors and their geometry is
    # a layout, not a measurement.
    grid = float(lim.get("grid", 4))
    off_grid = 0
    for n in ([] if lim.get("plotted") else nodes):
        for r in ([n] if local(n.tag) == "rect" else
                  [e for e in n.iter() if local(e.tag) == "rect"]):
            box = rect_box(r)
            if not box:
                continue
            bad = [f"{k}={v:g}" for k, v in zip("xywh", box)
                   if abs(v / grid - round(v / grid)) > 1e-9]
            if bad:
                off_grid += 1
                f.error(label, f"{kind}: node rect is off the {grid:g}-unit grid "
                               f"({', '.join(bad)})")

    # ---- geometry is not animated
    for name, body in sheet.keyframes.items():
        moved = sorted({p for p in re.findall(r"([-\w]+)\s*:", body)
                        if p.strip().lower() in GEOMETRY_PROPS})
        if moved:
            f.error(label, f"{kind}: @keyframes {name} animates {', '.join(moved)} — "
                           "motion explains a diagram, it never moves one; every "
                           "geometry check here measures the committed coordinates")

    moving = {n for n, body in sheet.keyframes.items()
              if re.search(r"transform\s*:[^;}]*(translate|scale)", body, re.I)}
    if moving:
        for el in nodes + edges:
            classes = (el.get("class") or "").split()
            tag, el_id = local(el.tag), el.get("id")
            for sel, decls in sheet.animated.items():
                if not selector_matches(sel, tag, classes, el_id):
                    continue
                used = decls.get("animation-name") or decls.get("animation", "")
                if any(m in used for m in moving):
                    f.error(label, f"{kind}: `{sel}` is a data-node/data-edge element "
                                   "animated with a translate/scale keyframe — a "
                                   "diagram's geometry stays where the checker "
                                   "measured it")
                    break

    # ---- legend below the drawing
    if legends:
        node_bottom = max((b[1] + b[3] for b, _, _ in node_boxes), default=None)
        if node_bottom is not None:
            for leg in legends:
                lbox = group_box(leg)
                tops = [float(t.get("y")) for t in leg.iter()
                        if local(t.tag) == "text" and t.get("y")]
                top = lbox[1] if lbox else (min(tops) if tops else None)
                if top is not None and top < node_bottom:
                    f.error(label, f"{kind}: the legend starts at y={top:g}, above the "
                                   f"lowest node edge at y={node_bottom:g} — the legend "
                                   "is a strip below the drawing, never inside it")

    # ---- what this diagram achieved, not only what it avoided
    gap_txt = f"{worst_gap:.1f}" if worst_gap is not None else "n/a"
    f.note(label, f"diagram: type={kind}, {len(nodes)} {unit}(s), {len(edges)} "
                  f"connector(s), {len(focal)} focal, {len(zones)} zone(s), "
                  f"{diagonals} diagonal, {off_grid} off-grid, "
                  f"min label gap {gap_txt}")


def font_role(el: ET.Element) -> str:
    role = (el.get("data-role") or "").strip().lower()
    return role if role in FONT_FLOORS else DEFAULT_FONT_ROLE


def check_paint(root, parents, sheet: Stylesheet, palette, limits, catalog,
                style, label: str, f: Findings) -> None:
    """Walk the tree carrying inherited paint, and check colours + text."""
    palette_hexes = {v: k for k, v in palette.items()}
    declared = {norm_hex(sheet.resolve(v)) for v in sheet.tokens.values()}
    declared.discard(None)

    text_floor = float(limits.get("contrast_text", 4.5))
    text_default = float(catalog.get("defaults", {}).get("contrast_text", 4.5))
    ui_floor = float(limits.get("contrast_ui", 3.0))

    seen_off_system: set[str] = set()
    decor_text = [0]   # aria-hidden text exempted from the contrast floor

    # A style specimen is not governed by the repo's design system — that is the
    # point of one. Its palette comes from the style spec, so its tints are on-system
    # by definition and reporting each as a deviation buries the real findings. The
    # off-system *error* below still fires on any undeclared raw hex, and contrast is
    # checked exactly the same way.
    specimen = (root.get("data-specimen") or "").strip().lower() == "true"
    off_palette = []
    for name, value in sheet.tokens.items():
        h = norm_hex(sheet.resolve(value))
        if h and palette and h not in palette_hexes:
            if specimen:
                off_palette.append(name)
            else:
                f.warn(label, f"{name}: {h} is a derived tint, not a prettydocs.md palette "
                              "role — note it in prettydocs.md if it is load-bearing")
    if off_palette:
        f.note(label, f"specimen palette: {len(off_palette)} token(s) from the style "
                      "spec rather than prettydocs.md — expected for a specimen")

    def paint_of(el, inherited: dict) -> dict:
        classes = (el.get("class") or "").split()
        decls = sheet.decls_for(local(el.tag), classes, el.get("id"))
        own = parse_decls(el.get("style", "")) if el.get("style") else {}
        ctx = dict(inherited)
        for source in (decls, {k: v for k, v in el.attrib.items()
                               if k in COLOUR_PROPS or k in
                               {"font-size", "font-family", "opacity", "fill-opacity",
                                "stroke-width", "data-bg"}}, own):
            for key, value in source.items():
                ctx[key] = value
        if el.get("data-bg"):
            ctx["data-bg"] = el.get("data-bg")
        return ctx

    def ground_hex(ctx: dict) -> str | None:
        role = (ctx.get("data-bg") or "").strip().lower()
        if role in palette:
            return palette[role]
        return norm_hex(sheet.resolve(role)) if role else None

    def walk(el, inherited: dict) -> None:
        ctx = paint_of(el, inherited)
        tag = local(el.tag)

        # every colour must trace somewhere
        for prop in COLOUR_PROPS:
            raw = ctx.get(prop) if prop in (el.attrib.keys() | {"fill", "stroke"}) else None
            raw = el.get(prop) or (sheet.decls_for(tag, (el.get("class") or "").split(),
                                                   el.get("id")).get(prop))
            if not raw:
                continue
            resolved = sheet.resolve(raw).strip()
            if resolved.lower() in {"none", "currentcolor", "transparent", "inherit"} \
               or resolved.startswith("url("):
                continue
            h = norm_hex(resolved)
            if h is None:
                continue
            if palette and h not in palette_hexes and h not in declared and h not in seen_off_system:
                seen_off_system.add(h)
                f.error(label, f"off-system colour {h} on <{tag}> {prop} — use "
                               "var(--role) from the prettydocs.md palette, or declare it "
                               "as a custom property if it is a derived tint")

        if tag == "text" or tag == "tspan":
            size = ctx.get("font-size")
            role = font_role(el)
            if size:
                m = re.match(r"\s*(\d*\.?\d+)", sheet.resolve(size))
                if m:
                    px = float(m.group(1))
                    floor = FONT_FLOORS[role]
                    if px < floor:
                        snippet = (el.text or "").strip()[:24]
                        f.error(label, f"font-size {px:g} is below the {role} floor "
                                       f"({floor:g}) — \"{snippet}\"")
            elif tag == "text":
                f.warn(label, "a <text> has no resolvable font-size")

            fg = norm_hex(sheet.resolve(ctx.get("fill", "")))
            bg = ground_hex(ctx)
            if fg and bg:
                alpha = 1.0
                for key in ("fill-opacity", "opacity"):
                    try:
                        alpha *= float(ctx.get(key, 1))
                    except (TypeError, ValueError):
                        pass
                ratio = contrast(composite(fg, bg, alpha), bg)
                snippet = (el.text or "").strip()[:24]
                # WCAG 1.4.3 exempts purely decorative text from the contrast
                # floor. aria-hidden is the author asserting exactly that, and it
                # is the only signal that a glyph is texture rather than reading
                # matter — a rain column or an engraving underlight is not text a
                # person is meant to read. Counted below so the exemption cannot
                # be used quietly to launder unreadable labels.
                if decorative(el, parents):
                    decor_text[0] += 1
                elif ratio < text_floor:
                    f.error(label, f"text contrast {ratio:.2f}:1 is below the "
                                   f"{text_floor:g}:1 floor — \"{snippet}\"")
                elif ratio < text_default:
                    f.softened(label, f"contrast-text@{text_floor:.1f}",
                               f"text contrast {ratio:.2f}:1 is under the "
                               f"{text_default:g}:1 default but above this style's "
                               f"{text_floor:g}:1 floor — \"{snippet}\"")
            elif fg and not bg:
                f.warn(label, "text has no data-bg ground in scope — contrast unchecked")

        elif tag in {"rect", "circle", "ellipse", "line", "path", "polyline", "polygon"}:
            stroke = norm_hex(sheet.resolve(ctx.get("stroke", "") or ""))
            bg = ground_hex(ctx)
            if stroke and bg and stroke != bg:
                ratio = contrast(stroke, bg)
                if ratio < ui_floor:
                    # Counted, not repeated. A hairline grid is one decision applied
                    # forty times, and forty identical lines bury every other finding.
                    key = (tag, stroke, bg, round(ratio, 2))
                    low_ui[key] = low_ui.get(key, 0) + 1

        for child in el:
            walk(child, ctx)

    low_ui: dict[tuple, int] = {}
    walk(root, {"data-bg": root.get("data-bg", "background")})
    if decor_text[0]:
        f.note(label, f"{decor_text[0]} aria-hidden text node(s) exempted from the "
                      "contrast floor as decoration (WCAG 1.4.3) — they must carry "
                      "no meaning")
    for (tag, stroke, bg, ratio), n in sorted(low_ui.items(), key=lambda kv: kv[0][3]):
        times = "" if n == 1 else f" (x{n})"
        f.warn(label, f"graphic contrast {ratio:.2f}:1 on <{tag}> stroke {stroke} over "
                      f"{bg} is under {ui_floor:g}:1{times} — fine for decoration, not "
                      "for a load-bearing border")


def check_attributed(by_tag, catalog: dict, label: str, f: Findings) -> None:
    """Hold each attributed group in a multi-style file to its own style's floor.

    The contact sheet resolves to one style (`catalog-sheet`), so a file-wide
    fidelity floor says nothing about whether the wood-grain tile actually has
    wood grain. Filters tagged `data-style="wood-grain"` are measured against
    wood-grain's own requirements instead.

    Only the filter gates apply per group. `min_elements` is a whole-canvas
    density floor and does not scale down to a tile meaningfully, so it stays a
    file-scope check.
    """
    styles_cat = catalog.get("styles", {})
    groups: dict[str, list] = {}
    for filt in by_tag.get("filter", []):
        owner = (filt.get("data-style") or "").strip().lower()
        if owner:
            groups.setdefault(owner, []).append(filt)

    for owner, filts in sorted(groups.items()):
        spec = styles_cat.get(owner)
        if spec is None:
            continue  # already reported as an unknown slug by the depth pass
        require = spec.get("require", {})

        floor = require.get("min_filter_depth")
        if floor:
            deepest = max((chain_depth(x) for x in filts), default=0)
            if deepest < int(floor):
                f.error(label, f"the '{owner}' group's deepest chain is {deepest}, "
                               f"below that style's floor of {floor}")

        wanted_all = require.get("require_filter_all")
        if wanted_all:
            present = primitives_in(filts)
            missing = [w for w in wanted_all if w not in present]
            if missing:
                f.error(label, f"the '{owner}' group is missing "
                               f"{', '.join(missing)}, which that style is built from")


def check_style(root, by_tag, sheet: Stylesheet, style: dict, slug: str,
                label: str, f: Findings) -> None:
    for banned in style.get("forbid", []):
        if banned in by_tag:
            f.error(label, f"<{banned}> is forbidden by the '{slug}' style")

    require = style.get("require", {})

    # `require_filter` is any-of: a menu, satisfied by one entry. That is the right
    # shape for "blur OR drop-shadow", and the wrong shape for a material built from
    # a specific chain — one bare feTurbulence used to satisfy wood-grain. Styles
    # whose look IS the chain use require_filter_all instead.
    wanted_any = require.get("require_filter_any") or require.get("require_filter")
    if wanted_any and not any(w in by_tag for w in wanted_any):
        f.error(label, f"the '{slug}' style requires one of {', '.join(wanted_any)} "
                       "and none is present")

    wanted_all = require.get("require_filter_all")
    if wanted_all:
        missing = [w for w in wanted_all if w not in by_tag]
        if missing:
            f.error(label,
                    f"the '{slug}' style is built from {', '.join(wanted_all)} — "
                    f"{', '.join(missing)} is missing. These primitives are the "
                    "material itself, not a suggestion of it")

    floor_depth = require.get("min_filter_depth")
    if floor_depth:
        deepest = max((chain_depth(x) for x in by_tag.get("filter", [])), default=0)
        if deepest < int(floor_depth):
            f.error(label,
                    f"deepest filter chain is {deepest}; the '{slug}' style needs at "
                    f"least {floor_depth} chained primitives. A single primitive "
                    "flattens this material into a gradient")

    # Geometry density is a property of what a diagram *says*, not of its style: a
    # README flow with four boxes is correct at 23 elements, and forcing it to 76
    # would mean padding it with decoration. So this floor binds only on specimens —
    # the catalog samples and contact sheet, whose whole job is to show the style at
    # full strength. Ordinary visuals get the number reported, not enforced.
    floor_els = require.get("min_elements")
    if floor_els:
        drawn = sum(len(by_tag.get(t, [])) for t in DRAWN_TAGS)
        is_specimen = (root.get("data-specimen") or "").strip().lower() == "true"
        if drawn < int(floor_els):
            if is_specimen:
                f.error(label,
                        f"{drawn} drawn elements is below the '{slug}' specimen floor "
                        f"of {floor_els} — a specimen has to show the style at full "
                        "strength, and this little geometry cannot")
            else:
                f.note(label,
                       f"{drawn} drawn elements (the '{slug}' specimen floor is "
                       f"{floor_els}; not enforced outside specimens)")

    # A silhouette is geometry, so no existing key reaches it. A style whose forms are
    # hand-formed rather than mathematically perfect draws each outline as a sampled,
    # re-splined path; a clean render of the *same figure* draws <rect> and <circle>,
    # and passes every other gate — the flat-render hole `min_filter_depth` closed for
    # filter-built materials, reopened one layer down. This closes it the same way, as
    # a floor on the most curved single path rather than a file-wide total, so it is
    # scale-free: a four-form README diagram clears it exactly as a specimen does.
    floor_curves = require.get("min_path_curves")
    if floor_curves:
        curves = deepest_curve(by_tag)
        if curves < int(floor_curves):
            f.error(label,
                    f"the most curved path carries {curves} cubic segment(s); the "
                    f"'{slug}' style needs at least {floor_curves}. Its forms are "
                    "re-splined silhouettes — a rect, a circle or an arc-cornered path "
                    "is the mathematically perfect render the style exists to replace")

    if require.get("mono_only"):
        families = [sheet.resolve(v) for sel, d in sheet.rules
                    for k, v in d.items() if k == "font-family"]
        families += [el.get("font-family") for el in root.iter()
                     if el.get("font-family")]
        for fam in families:
            if fam and "mono" not in fam.lower():
                f.error(label, f"the '{slug}' style is monospace-only, found "
                               f"font-family: {fam}")

    # `gradientUnits` is an attribute VALUE, so `forbid` — which matches tag names —
    # cannot reach it. A style whose shading is computed from instance geometry has to
    # have it enforced rather than described: `objectBoundingBox` resamples the
    # gradient into each element's own box, so a wide capsule ends up lit as though
    # the light had moved, and no other attribute corrects it. Note that
    # `objectBoundingBox` is the SVG *default*, which makes an omitted attribute a
    # violation rather than a neutral absence — hence checking for the wanted value
    # instead of against the banned one.
    wanted_units = require.get("gradient_units")
    if wanted_units:
        # Vacuous-pass guard, the same failure `mono_only` had: a file with no
        # gradients at all satisfies "every gradient is userSpaceOnUse" trivially.
        # A style declares this key because its volume lives in the fill, so zero
        # gradients is not a clean pass — it is the flat render the key exists to stop.
        if not (by_tag.get("linearGradient") or by_tag.get("radialGradient")):
            f.error(label, f"the '{slug}' style models volume in the fill and has no "
                           "gradients at all — the forms cannot be reading as solid")
        for tag in ("linearGradient", "radialGradient"):
            for el in by_tag.get(tag, []):
                got = (el.get("gradientUnits") or "").strip()
                # A gradient that references another inherits its attributes, so an
                # absent gradientUnits on the referencing element is correct.
                if not got and any(el.get(k) for k in
                                   ("href", f"{{{XLINK_NS}}}href")):
                    continue
                if got != wanted_units:
                    shown = got or "objectBoundingBox, by omission — it is the default"
                    f.error(label,
                            f'<{tag} id="{el.get("id") or "?"}"> has gradientUnits='
                            f"{shown}; the '{slug}' style computes every gradient axis "
                            f'from instance geometry and needs gradientUnits='
                            f'"{wanted_units}" on all of them')

    # Each entry is (radius, shortest side of the shape or None when unknown).
    # SVG clamps rx to half the side, so a min_rx floor is unsatisfiable on a shape
    # narrower than 2*floor — those are skipped rather than failed. A status marker
    # is allowed to be a small square; it just can't be as round as a cell.
    # Only <rect> has corner radii. On <ellipse>, <circle> and the radial
    # gradient elements rx/ry are the geometry itself, and reading them as
    # corners failed every rounded style that drew an ellipse.
    radii: list[tuple[float, float | None]] = []
    for el in by_tag.get("rect", []):
        side: float | None = None
        dims = []
        for key in ("width", "height"):
            value = el.get(key)
            if value:
                m = re.match(r"\s*(\d*\.?\d+)", value)
                if m:
                    dims.append(float(m.group(1)))
        if len(dims) == 2:
            side = min(dims)
        for key in ("rx", "ry"):
            value = el.get(key)
            if value:
                m = re.match(r"\s*(\d*\.?\d+)", value)
                if m:
                    radii.append((float(m.group(1)), side))
    for sel, decls in sheet.rules:
        if sel.split(":")[0].split(".")[0].split("[")[0].strip() in NON_RECT_SHAPES:
            continue
        for key in ("rx", "ry", "border-radius"):
            if key in decls:
                m = re.match(r"\s*(\d*\.?\d+)", sheet.resolve(decls[key]))
                if m:
                    radii.append((float(m.group(1)), None))

    if "max_rx" in require:
        cap = float(require["max_rx"])
        for r, _ in radii:
            if r > cap + EPS:
                f.error(label, f"corner radius {r:g} exceeds the '{slug}' maximum {cap:g}")
    if "min_rx" in require:
        floor = float(require["min_rx"])
        checkable = [(r, s) for r, s in radii
                     if r > EPS and (s is None or s >= 2 * floor - EPS)]
        if not checkable:
            f.warn(label, f"the '{slug}' style expects rounded shapes (radius "
                          f">= {floor:g}) and nothing is rounded")
        for r, _ in checkable:
            if r < floor - EPS:
                f.error(label, f"corner radius {r:g} is below the '{slug}' minimum "
                               f"{floor:g}")

    if "min_stroke_width" in require:
        floor = float(require["min_stroke_width"])
        widths: list[tuple[str, float]] = []
        for el in root.iter():
            value = el.get("stroke-width")
            if value:
                m = re.match(r"\s*(\d*\.?\d+)", value)
                if m:
                    widths.append((f"<{local(el.tag)}>", float(m.group(1))))
        for sel, decls in sheet.rules:
            if "stroke-width" in decls:
                m = re.match(r"\s*(\d*\.?\d+)", sheet.resolve(decls["stroke-width"]))
                if m:
                    widths.append((sel, float(m.group(1))))
        for where, w in widths:
            if 0 < w < floor - EPS:
                f.error(label, f"stroke-width {w:g} on {where} is below the '{slug}' "
                               f"minimum {floor:g}")


# ---------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="+")
    ap.add_argument("--design", help="path to prettydocs.md (palette + contrast grounds)")
    ap.add_argument("--style", help="resolved style slug or alias")
    ap.add_argument("--catalog", help="path to styles.json (defaults to alongside this script)")
    ap.add_argument("--diagrams", help="path to diagrams.json (defaults to alongside this script)")
    ap.add_argument("--json", action="store_true", help="emit a JSON summary as well")
    args = ap.parse_args()

    catalog_path = Path(args.catalog) if args.catalog else Path(__file__).with_name("styles.json")
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR  {catalog_path}: unreadable style catalog — {e}", file=sys.stderr)
        return 2

    diagrams_path = Path(args.diagrams) if args.diagrams \
        else Path(__file__).with_name("diagrams.json")
    diagrams: dict | None = None
    if diagrams_path.exists():
        try:
            diagrams = json.loads(diagrams_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"ERROR  {diagrams_path}: unreadable diagram catalog — {e}",
                  file=sys.stderr)
            return 2
    elif args.diagrams:
        print(f"ERROR  {diagrams_path}: diagram catalog not found", file=sys.stderr)
        return 2

    slug = args.style
    if slug:
        slug = slug.strip().lower()
        if slug not in catalog["styles"]:
            for name, spec in catalog["styles"].items():
                if slug in spec.get("aliases", []):
                    slug = name
                    break

    palette: dict[str, str] = {}
    f = Findings()
    if args.design:
        design = Path(args.design)
        if design.exists():
            palette = load_palette(design)
            if not palette:
                f.note(str(design), "no palette table found — colour and contrast "
                                    "checks are limited")
        else:
            f.note(str(design), "prettydocs.md not found — colour and contrast checks skipped")
    else:
        f.note("-", "no --design given — colour and contrast checks skipped")

    for name in args.files:
        path = Path(name)
        if not path.exists():
            f.error(name, "file not found")
            continue
        check_file(path, catalog, slug, palette, f, diagrams)

    for level, where, msg in f.rows:
        print(f"{level:<9}{where}: {msg}")

    softened = sorted(f.relaxed)
    if softened:
        print(f"\nrelaxed: {json.dumps(softened)}")
    print(f"\n{f.n_errors} error(s), "
          f"{sum(1 for l, _, _ in f.rows if l == 'WARN')} warning(s), "
          f"{sum(1 for l, _, _ in f.rows if l == 'SOFTENED')} softened"
          + (f" [style: {slug}]" if slug else ""))

    if args.json:
        print(json.dumps({
            "style": slug,
            "errors": f.n_errors,
            "relaxed": softened,
            "findings": [{"level": l, "file": w, "message": m} for l, w, m in f.rows],
        }, indent=2))

    return 1 if f.n_errors else 0


if __name__ == "__main__":
    sys.exit(main())
