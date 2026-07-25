#!/usr/bin/env python3
"""Gate for hand-authored animated SVG produced by the more-pretty-docs skill.

Deterministic, python3 stdlib only. Checks, in order:

  structural  no <script>, no <foreignObject>, no remote href/@import;
              viewBox, <title>, <desc>, data-loop-s present
  seam        every CSS animation duration and SMIL dur divides data-loop-s;
              every animation is infinite/indefinite
  motion a11y a prefers-reduced-motion block exists and covers every animated
              class AND every SMIL-animated element (CSS cannot stop SMIL, so
              those need display:none / visibility:hidden)
  legibility  every font-size meets its role floor
  system      every colour traces to a DESIGN.md palette role or a declared
              custom property; text contrast >= 4.5:1 against its data-bg role
  style       the resolved style's forbid / require invariants and relaxed floors
  fidelity    the style's *minimum* — required primitives, minimum filter-chain
              depth, minimum drawn geometry. Every other gate here is a ceiling
              or a legibility floor, so a flat render used to pass clean; this is
              the half that asks whether the file looks like what it claims
  size        warn at 60 KB, fail over 150 KB

Usage:
    svg_check.py [--design DESIGN.md] [--style SLUG] [--json] FILE.svg [FILE.svg ...]

Output is one line per finding: ERROR / SOFTENED / WARN / NOTE.
Exit 0 = no errors, exit 1 = at least one ERROR. SOFTENED lines are passes that
used a declared style relaxation; record them in mpd.json's `relaxed` array.
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


# ----------------------------------------------------------------- utilities

def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def chain_depth(filt: ET.Element) -> int:
    """Primitives that are direct children of one <filter> — the chain length."""
    return sum(1 for c in filt if local(c.tag) in FILTER_PRIMITIVES)


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
    """Read the Palette table out of a DESIGN.md: | role | `#hex` | notes |."""
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
        """`token` is the gate@floor string recorded in mpd.json's `relaxed` array."""
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
               palette: dict[str, str], f: Findings) -> None:
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
    filts = by_tag.get("filter", [])
    deepest = max((chain_depth(x) for x in filts), default=0)
    drawn = sum(len(by_tag.get(t, [])) for t in DRAWN_TAGS)
    used = sorted(primitives_in(filts))
    f.note(label, f"fidelity: deepest chain {deepest}, {len(filts)} filter(s), "
                  f"{drawn} drawn elements"
                  + (f", primitives {', '.join(used)}" if used else ", no filters"))


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

    for name, value in sheet.tokens.items():
        h = norm_hex(sheet.resolve(value))
        if h and palette and h not in palette_hexes:
            f.warn(label, f"{name}: {h} is a derived tint, not a DESIGN.md palette role "
                          "— note it in DESIGN.md if it is load-bearing")

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
                               "var(--role) from the DESIGN.md palette, or declare it "
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
                if ratio < text_floor:
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
                    f.warn(label, f"graphic contrast {ratio:.2f}:1 on <{tag}> stroke is "
                                  f"under {ui_floor:g}:1 — fine for decoration, not for a "
                                  "load-bearing border")

        for child in el:
            walk(child, ctx)

    walk(root, {"data-bg": root.get("data-bg", "background")})


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

    if require.get("mono_only"):
        families = [sheet.resolve(v) for sel, d in sheet.rules
                    for k, v in d.items() if k == "font-family"]
        families += [el.get("font-family") for el in root.iter()
                     if el.get("font-family")]
        for fam in families:
            if fam and "mono" not in fam.lower():
                f.error(label, f"the '{slug}' style is monospace-only, found "
                               f"font-family: {fam}")

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
    ap.add_argument("--design", help="path to DESIGN.md (palette + contrast grounds)")
    ap.add_argument("--style", help="resolved style slug or alias")
    ap.add_argument("--catalog", help="path to styles.json (defaults to alongside this script)")
    ap.add_argument("--json", action="store_true", help="emit a JSON summary as well")
    args = ap.parse_args()

    catalog_path = Path(args.catalog) if args.catalog else Path(__file__).with_name("styles.json")
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR  {catalog_path}: unreadable style catalog — {e}", file=sys.stderr)
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
            f.note(str(design), "DESIGN.md not found — colour and contrast checks skipped")
    else:
        f.note("-", "no --design given — colour and contrast checks skipped")

    for name in args.files:
        path = Path(name)
        if not path.exists():
            f.error(name, "file not found")
            continue
        check_file(path, catalog, slug, palette, f)

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
