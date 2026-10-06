#!/usr/bin/env python3
"""
render_report.py — fill the bundled reflect template with a run's JSON.

The template (assets/template.html) carries all CSS, fonts, GSAP and the renderer
inline; a run supplies only data. This script validates that data, swaps it into
the template's three JSON blocks, writes the report, and checks the result:
headings against reference/report-guide.md § Structure, no external requests,
each block id exactly once, and WCAG AA contrast for reading text in both themes.
Any failure exits non-zero. Never Read the template or the report into context.

Usage:
    render_report.py --data D.json --status S.json --out REPORT.html
    render_report.py --sample --out SAMPLE.html      # render the template's own sample
    render_report.py --vendor DESIGN_SYSTEM_DIR      # maintainer: re-vendor the CSS
"""

import argparse
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "template.html")
GUIDE = os.path.join(HERE, "..", "reference", "report-guide.md")

BLOCKS = ["cc-reflection-data", "cc-reflection-status", "cc-reflection-meta"]
STATIC_IDS = ["nf-tokens", "nf-patch", "nf-components", "nf-fonts", "report",
              "theme-boot", "vendor-gsap", "renderer"]
VERDICTS = {"new-skill", "automation", "fix", "keep-doing", "observation", "nothing"}
FAMILIES = {"friction", "repetition", "wins", "environment"}
EFFORTS = {"minutes": 0, "hour": 1, "day": 2}
STATES = {"open", "done", "wontdo"}
# URLs that may appear outside the data blocks: SVG namespaces and licence notices.
URL_ALLOW = ("http://www.w3.org/", "https://gsap.com", "https://lucide.dev",
             "https://openfontlicense.org/", "https://github.com/googlefonts/sora",
             "https://github.com/tokotype/PlusJakartaSans",
             "https://github.com/JetBrains/JetBrainsMono")
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def block_re(bid):
    return re.compile(r'(<script type="application/json" id="%s">)(.*?)(</script>)' % re.escape(bid), re.S)


def read_block(doc, bid):
    m = block_re(bid).search(doc)
    return json.loads(m.group(2)) if m else None


def encode(obj):
    # '<' only ever occurs inside JSON strings, so < is lossless and keeps
    # '</script>' and '<!--' out of the block.
    return "\n" + json.dumps(obj, indent=1, ensure_ascii=False).replace("<", "\\u003c") + "\n"


# ---------------------------------------------------------------- validation

def validate(data, status):
    errs, warns = [], []

    def need(obj, key, where, kind=None):
        if not isinstance(obj, dict) or key not in obj:
            errs.append("missing: %s.%s" % (where, key))
            return None
        v = obj[key]
        if kind and not isinstance(v, kind):
            errs.append("wrong type: %s.%s should be %s" % (where, key, kind.__name__ if isinstance(kind, type) else "/".join(k.__name__ for k in kind)))
            return None
        return v

    g = need(data, "generated", "data", str)
    if g and not ISO.match(g):
        errs.append("bad date: data.generated %r" % g)
    w = need(data, "window", "data", dict)
    if w:
        need(w, "kind", "data.window", str)
        for k in ("from", "to"):
            v = need(w, k, "data.window", str)
            if v and not ISO.match(v):
                errs.append("bad date: data.window.%s %r" % (k, v))
    need(data, "sessions_analyzed", "data", int)
    need(data, "projects", "data", list)
    if "limit" not in data:
        errs.append("missing: data.limit (an integer, or null for limit=all)")
    elif data["limit"] is not None and not (isinstance(data["limit"], int) and data["limit"] > 0):
        errs.append("bad value: data.limit must be a positive integer or null")
    hero = need(data, "hero", "data", dict)
    if hero:
        need(hero, "verdict", "data.hero", str)
        need(hero, "summary", "data.hero", str)
        for i, k in enumerate(hero.get("kpis") or []):
            for f in ("label", "value"):
                need(k, f, "data.hero.kpis[%d]" % i)
    m = need(data, "methodology", "data", dict)
    if m:
        need(m, "triage", "data.methodology", list)
        need(m, "sampled", "data.methodology", str)
        need(m, "unreadable", "data.methodology", list)
        need(m, "limitations", "data.methodology", list)

    prior = data.get("prior")
    if prior is not None and not (isinstance(prior, dict) and (prior.get("date") or prior.get("edition"))):
        errs.append("bad value: data.prior must be null or {edition, date}")

    recs = need(data, "recommendations", "data", list) or []
    ids, ranks = set(), []
    for i, r in enumerate(recs):
        at = "data.recommendations[%d]" % i
        rid = need(r, "id", at, str)
        if rid:
            at = "recommendation %s" % rid
            if not SLUG.match(rid):
                errs.append("bad id: %s is not a kebab-case slug" % rid)
            if rid in ids:
                errs.append("duplicate id: %s" % rid)
            ids.add(rid)
        rk = need(r, "rank", at, int)
        if rk is not None:
            ranks.append(rk)
        v = need(r, "verdict", at, str)
        if v and v not in VERDICTS:
            errs.append("bad verdict: %s %r" % (at, v))
        f = need(r, "family", at, str)
        if f and f not in FAMILIES:
            errs.append("bad family: %s %r" % (at, f))
        lv = need(r, "leverage", at, int)
        if lv is not None and not 1 <= lv <= 10:
            errs.append("bad leverage: %s %r (1-10)" % (at, lv))
        e = need(r, "effort", at, str)
        if e and e not in EFFORTS:
            errs.append("bad effort: %s %r" % (at, e))
        s = need(r, "session_ids", at, list)
        if s is not None and not s:
            errs.append("empty: %s.session_ids" % at)
        need(r, "streak", at, int)
        need(r, "title", at, str)
        need(r, "rationale", at, str)
        need(r, "example", at, str)
        if prior is not None:
            t = need(r, "trend", at, str)
            if t and t not in ("new", "recurring"):
                errs.append("bad trend: %s %r" % (at, t))
        evs = need(r, "evidence", at, list)
        if evs is not None and not evs:
            errs.append("empty: %s.evidence (every finding cites at least one quote)" % at)
        for j, ev in enumerate(evs or []):
            for k in ("quote", "session_id", "project", "date"):
                need(ev, k, "%s.evidence[%d]" % (at, j))
    if ranks and sorted(ranks) != list(range(1, len(ranks) + 1)):
        errs.append("bad ranks: must be 1..%d, each once" % len(ranks))
    # Rank in code, never by an agent: leverage desc, effort asc, sessions desc, id asc.
    try:
        want = sorted(recs, key=lambda r: (-r["leverage"], EFFORTS[r["effort"]], -len(r["session_ids"]), r["id"]))
        got = sorted(recs, key=lambda r: r["rank"])
        if [r["id"] for r in want] != [r["id"] for r in got]:
            errs.append("bad ranks: order does not follow leverage desc, effort asc, sessions desc, id asc")
    except (KeyError, TypeError):
        pass

    if prior is not None:
        for i, a in enumerate(data.get("adopted") or []):
            for k in ("id", "title", "leverage", "raised"):
                need(a, k, "data.adopted[%d]" % i)
    foc = data.get("focus")
    if isinstance(foc, dict):
        need(foc, "term", "data.focus", str)
        need(foc, "summary", "data.focus", str)
        for fid in need(foc, "ids", "data.focus", list) or []:
            if fid not in ids:
                errs.append("unknown id in data.focus.ids: %s" % fid)
    elif foc is not None and not isinstance(foc, str):
        errs.append("bad value: data.focus must be null or {term, summary, ids}")

    p = data.get("panorama") or {}
    n = len(p.get("days") or [])
    for key in ("trend", "tokens_daily"):
        for se in (p.get(key) or {}).get("series") or []:
            if len(se.get("values") or []) != n:
                errs.append("length mismatch: panorama.%s series %r has %d values for %d days"
                            % (key, se.get("name"), len(se.get("values") or []), n))
    for i, row in enumerate((p.get("heatmap") or {}).get("rows") or []):
        if len(row.get("values") or []) != 24:
            errs.append("length mismatch: panorama.heatmap.rows[%d] needs 24 hourly values" % i)

    items = need(status, "items", "status", dict) or {}
    for k, v in items.items():
        if not isinstance(v, dict) or v.get("state") not in STATES:
            errs.append("bad state: status.items.%s must be open, done or wontdo" % k)
    for r in recs:
        if r.get("verdict") not in ("keep-doing", "nothing") and r.get("id") not in items:
            warns.append("ledger has no entry for %s; it renders as open" % r.get("id"))
    return errs, warns


# ---------------------------------------------------------------- post-checks

def guide_headings():
    text = open(GUIDE, encoding="utf-8").read()
    m = re.search(r"^## Structure.*?$(.*?)^## ", text, re.S | re.M)
    if not m:
        return None
    names = re.findall(r"^\d+\. \*\*(.+?)\*\*", m.group(1), re.M)
    return names[1:]  # item 1, Hero, is the <h1>; the rest are the <h2>s in order


def check_headings(doc):
    want = guide_headings()
    markup = re.sub(r"<!--.*?-->|<(script|style)\b[^>]*>.*?</\1>", "", doc, flags=re.S)
    got = [html.unescape(re.sub(r"<[^>]+>", "", h)).strip()
           for h in re.findall(r"<h2[^>]*>(.*?)</h2>", markup, re.S)]
    ok = want is not None and got == want
    print("headings match: %s" % ("yes" if ok else "no"))
    if not ok:
        print("  guide:  %s" % want)
        print("  report: %s" % got)
    return ok


def check_urls(doc):
    body = doc
    for bid in BLOCKS:
        body = block_re(bid).sub(lambda m: m.group(1) + m.group(3), body)
    bad = sorted({u for u in re.findall(r"""https?://[^\s"'<>)]+""", body) if not u.startswith(URL_ALLOW)})
    print("external requests: %s" % ("none" if not bad else "FOUND %s" % bad))
    return not bad


def check_ids(doc):
    ok = True
    for bid in BLOCKS + STATIC_IDS:
        n = len(re.findall(r'\bid="%s"' % re.escape(bid), doc))
        if n != 1:
            print("block id %s: found %d, want exactly 1" % (bid, n))
            ok = False
    if ok:
        print("block ids: each exactly once")
    return ok


# --- contrast: resolve the vendored tokens, then measure the pairs the report layer sets

def _decls(css, selector_re):
    m = re.search(selector_re + r"\s*\{(.*?)\n\}", css, re.S)
    return dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", m.group(1))) if m else {}


def _rgba(v, env, depth=0):
    v = v.strip()
    m = re.match(r"var\((--[\w-]+)\)$", v)
    if m:
        if depth > 8 or m.group(1) not in env:
            raise ValueError("unresolved %s" % v)
        return _rgba(env[m.group(1)], env, depth + 1)
    m = re.match(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$", v)
    if m:
        h = m.group(1)
        h = "".join(c * 2 for c in h) if len(h) == 3 else h
        return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)] + [1.0]
    m = re.match(r"rgba?\(([^)]+)\)$", v)
    if m:
        p = [float(x) for x in m.group(1).replace("/", ",").split(",")]
        return [p[0] / 255, p[1] / 255, p[2] / 255, p[3] if len(p) > 3 else 1.0]
    raise ValueError("unparsed colour %s" % v)


def _over(fg, bg):
    a = fg[3]
    return [fg[i] * a + bg[i] * (1 - a) for i in range(3)] + [1.0]


def _mix(a, pa, b):
    return [a[i] * pa + b[i] * (1 - pa) for i in range(3)] + [1.0]


def _lum(c):
    ch = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c[:3]]
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def _ratio(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def check_contrast(doc):
    m = re.search(r'<style id="nf-tokens">(.*?)</style>', doc, re.S)
    if not m:
        print("contrast: nf-tokens block not found")
        return False
    css = m.group(1)
    base = _decls(css, r":root")
    light = dict(base, **_decls(css, r':root,\s*\[data-theme="light"\]'))
    dark = dict(light, **_decls(css, r'\[data-theme="dark"\]'))
    ok = True
    for name, env in (("light", light), ("dark", dark)):
        try:
            c = lambda t: _rgba("var(%s)" % t, env)
            surf = c("--surface")
            wash = lambda t: _over(c(t), surf)
            fg1 = c("--fg1")
            mix = lambda t, p: _mix(c(t), p, fg1)
            meta = _mix(c("--fg3"), 0.45, fg1)
            pairs = [
                ("body text", fg1, c("--bg")), ("secondary text", c("--fg2"), c("--bg")),
                ("meta lines", meta, c("--bg")), ("quotes on wells", fg1, c("--surface-inset")),
                ("secondary on wells", c("--fg2"), c("--surface-inset")), ("meta on wells", meta, c("--surface-inset")),
                ("accent badge / new-skill", mix("--accent-press", .40), wash("--accent-wash")),
                ("automation / info badge", mix("--info", .40), wash("--info-wash")),
                ("fix / warning badge", mix("--warning", .34), wash("--warning-wash")),
                ("keep-doing / done / success badge", mix("--success", .40), wash("--success-wash")),
                ("corroborated chip", mix("--success", .38), wash("--success-wash")),
                ("came-back overline", mix("--warning", .34), wash("--warning-wash")),
                ("came-back note", fg1, wash("--warning-wash")),
                ("code chip", mix("--accent-press", .40), c("--surface-inset")),
            ] + [("primary button on %s" % s, c("--fg-on-accent"), _rgba(s, env))
                 for s in re.findall(r"#[0-9a-fA-F]{6}", env["--grad-fresh"])]
        except (ValueError, KeyError) as e:
            print("contrast (%s): cannot resolve tokens: %s" % (name, e))
            ok = False
            continue
        fails = ["%s %.2f" % (label, _ratio(a, b)) for label, a, b in pairs if _ratio(a, b) < 4.5]
        worst = min(_ratio(a, b) for _, a, b in pairs)
        print("contrast (%s): %s" % (name, "AA, lowest %.2f:1" % worst if not fails else "FAIL %s" % "; ".join(fails)))
        ok = ok and not fails
    return ok


# ---------------------------------------------------------------- re-vendor

def vendor(ds_dir, tpl_path):
    doc = open(tpl_path, encoding="utf-8").read()
    for bid, fname in (("nf-tokens", "colors_and_type.css"), ("nf-components", "components.css")):
        src = os.path.join(ds_dir, fname)
        if not os.path.isfile(src):
            sys.exit("error: %s not found" % src)
        css = "".join(l for l in open(src, encoding="utf-8").readlines() if "<link" not in l)
        pat = re.compile(r'(<style id="%s">\n)(.*?)(</style>)' % bid, re.S)
        if len(pat.findall(doc)) != 1:
            sys.exit("error: template has no single style#%s block" % bid)
        old = pat.search(doc).group(2)
        doc = pat.sub(lambda m: m.group(1) + css + m.group(3), doc)
        print("%s: %s (%d -> %d bytes)" % (bid, "unchanged" if old == css else "replaced", len(old), len(css)))
    open(tpl_path, "w", encoding="utf-8").write(doc)
    print("now run: render_report.py --sample --out <scratch>/sample.html, and look at it in both themes")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--data", help="report data JSON (the cc-reflection-data block)")
    ap.add_argument("--status", help="merged status ledger JSON (OUT_DIR/reflect-status.json)")
    ap.add_argument("--out", help="report path to write")
    ap.add_argument("--sample", action="store_true", help="render the template's own sample data")
    ap.add_argument("--template", default=TEMPLATE, help="template path (default: the bundled one)")
    ap.add_argument("--vendor", metavar="DIR", help="re-vendor colors_and_type.css + components.css from DIR")
    a = ap.parse_args()

    if a.vendor:
        vendor(a.vendor, a.template)
        return
    if not a.out or not (a.sample or (a.data and a.status)):
        ap.error("need --out and either --sample or both --data and --status")
    if not os.path.isfile(a.template):
        sys.exit("error: template not found at %s" % a.template)
    doc = open(a.template, encoding="utf-8").read()
    for bid in BLOCKS:
        if len(block_re(bid).findall(doc)) != 1:
            sys.exit("error: template must hold exactly one %s block" % bid)

    if a.sample:
        data, status = read_block(doc, BLOCKS[0]), read_block(doc, BLOCKS[1])
    else:
        try:
            data = json.load(open(a.data, encoding="utf-8"))
            status = json.load(open(a.status, encoding="utf-8"))
        except (OSError, ValueError) as e:
            sys.exit("error: %s" % e)

    errs, warns = validate(data, status)
    for w in warns:
        print("warning: %s" % w)
    if errs:
        for e in errs:
            print(e)
        sys.exit("error: %d problem(s) in the data; nothing written" % len(errs))

    meta = {"file": os.path.basename(a.out), "from": data["window"]["from"],
            "to": data["window"]["to"], "generated": data["generated"]}
    for bid, obj in zip(BLOCKS, (data, status, meta)):
        doc = block_re(bid).sub(lambda m, o=obj: m.group(1) + encode(o) + m.group(3), doc)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(doc)

    out = open(a.out, encoding="utf-8").read()
    rt = all(read_block(out, b) == o for b, o in zip(BLOCKS, (data, status, meta)))
    print("data blocks: %s" % ("round-trip ok" if rt else "MISMATCH after write"))
    results = [rt, check_headings(out), check_urls(out), check_ids(out), check_contrast(out)]
    shown = [r for r in data["recommendations"] if r["verdict"] != "nothing"]
    lim = data["limit"] if data["limit"] is not None else len(shown)
    print("wrote %s (%d KB) · showing %d of %d" % (a.out, os.path.getsize(a.out) // 1024, min(lim, len(shown)), len(shown)))
    if not all(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
