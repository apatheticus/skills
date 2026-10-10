#!/usr/bin/env python3
"""
verify_quotes.py — reflect Phase 4: every evidence quote must be verbatim.

Checks each recommendation's evidence against the transcript it cites (the main
file plus its sub-agent files) and rewrites report-data.json in place:

- A quote is split into fragments at the stitch marks extractors use
  (`…`, `->`, ` / `, `; `, `then`, `user:` and the like); fragments under 18
  characters are context, not evidence, and are not checked.
- Matching ignores what formatting changes: ANSI codes, emoji, `**`, backticks,
  curly quotes and dashes, `\\"` and `\\:` escapes, whitespace, case.
- Every fragment found: kept as is. Some found, covering at least half the
  fragment text: rebuilt from the verbatim fragments joined with ` … `. A
  fragment whose tail is narration keeps its verbatim prefix of 40+ characters.
  Otherwise the evidence is dropped.
- Evidence citing a session outside the corpus, including the running session
  and anything that continues into it, is dropped.
- A finding left with no evidence is dropped; session_ids lose excluded
  sessions, thresholds are re-applied and the list is re-ranked.

Prints one line per change. Read them: a rebuilt quote can keep a real but
off-topic fragment.

Usage:
    verify_quotes.py --data WORK/report-data.json --corpus WORK/corpus.json
"""

import argparse
import glob
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from assemble import apply_threshold, rerank  # noqa: E402

MIN_FRAGMENT = 18
MIN_PREFIX = 40
SEP = re.compile(
    r"\s*(?:->|→|\.\.\.|…|;\s|\s\|\s|\s/\s|\(x\d+\)|\s--\s|\"\s*,\s*\""
    r"|(?:^|\s)(?:then|later|user(?: \([^)]*\))?\\?:|assistant\\?:|err:|asked:|answered)\s)\s*", re.I)
SWAPS = (("“", '"'), ("”", '"'), ("’", "'"), ("‘", "'"), ("—", "-"), ("–", "-"),
         ('\\"', '"'), ("`", ""), ("\\:", ":"), ("**", ""))


def norm(x):
    x = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", x)
    x = unicodedata.normalize("NFKC", x)
    x = "".join(ch for ch in x if unicodedata.category(ch) not in ("So", "Sk", "Cf"))
    x = x.replace("\\\\", "\\")
    for a, b in SWAPS:
        x = x.replace(a, b)
    return re.sub(r"\s+", " ", x).strip().lower()


def strings(o, out):
    if isinstance(o, str):
        out.append(o)
    elif isinstance(o, list):
        for i in o:
            strings(i, out)
    elif isinstance(o, dict):
        for v in o.values():
            strings(v, out)


def fragments(q):
    out = []
    for p in SEP.split(q):
        p = (p or "").strip().strip("\"'").strip()
        p = re.sub(r"^(user|assistant|err)\\?:\s*", "", p, flags=re.I).strip().strip('"').strip()
        if len(p) >= MIN_FRAGMENT:
            out.append(p)
    return out or ([q.strip()] if q.strip() else [])


def keep(frag, text):
    """The fragment if verbatim, else its longest verbatim prefix of MIN_PREFIX+ chars, else None."""
    if norm(frag) in text:
        return frag
    words = frag.split(" ")
    for k in range(len(words) - 1, 0, -1):
        pre = " ".join(words[:k]).rstrip(" ,;:(")
        if len(pre) < MIN_PREFIX:
            break
        if norm(pre) in text:
            return pre + " …"
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--data", required=True, help="report-data.json, rewritten in place")
    ap.add_argument("--corpus", required=True)
    a = ap.parse_args()

    data = json.load(open(a.data))
    corpus = json.load(open(a.corpus))
    paths = {r["id"]: r["path"] for r in corpus["sessions"]}
    excluded = {x["id"] for x in corpus["excluded"]}
    cache = {}

    def text(sid):
        if sid not in cache:
            p = paths.get(sid)
            out = []
            if p:
                for f in [p] + glob.glob(os.path.join(os.path.dirname(p), sid, "subagents", "*.jsonl")):
                    with open(f, errors="replace") as fh:
                        for line in fh:
                            try:
                                strings(json.loads(line), out)
                            except ValueError:
                                pass
            cache[sid] = norm("\n".join(out))
        return cache[sid]

    stats = {"verbatim": 0, "rebuilt": 0, "dropped": 0}
    kept_recs, changes = [], []
    for r in data.get("recommendations") or []:
        ev = []
        for e in r.get("evidence") or []:
            sid, q = e.get("session_id", ""), e.get("quote", "")
            where = "%s %s" % (r["id"], sid[:8])
            if sid in excluded or sid not in paths:
                stats["dropped"] += 1
                changes.append("dropped  %s: %s" % (where, "excluded session" if sid in excluded else "not in the corpus"))
                continue
            frs = fragments(q)
            found = [k for k in (keep(f, text(sid)) for f in frs) if k]
            if found and len(found) == len(frs) and all(k == f for k, f in zip(found, frs)):
                stats["verbatim"] += 1
                ev.append(e)
            elif found and sum(len(k) for k in found) * 2 >= sum(len(f) for f in frs):
                e = dict(e, quote=" … ".join(k.strip().strip('"').strip() for k in found).replace("… …", "…"))
                stats["rebuilt"] += 1
                changes.append("rebuilt  %s: %s" % (where, e["quote"][:110]))
                ev.append(e)
            else:
                stats["dropped"] += 1
                changes.append("dropped  %s: not verbatim: %s" % (where, q[:90]))
        if not ev:
            changes.append("finding  %s dropped: no verbatim evidence left" % r["id"])
            continue
        r["evidence"] = ev
        r["session_ids"] = [s for s in r["session_ids"] if s not in excluded]
        if apply_threshold(r):
            changes.append("finding  %s downgraded to observation: too few sessions" % r["id"])
        kept_recs.append(r)

    before = len(data.get("recommendations") or [])
    data["recommendations"] = rerank(kept_recs)
    focus = data.get("focus")
    if isinstance(focus, dict):
        ids = {r["id"] for r in kept_recs}
        focus["ids"] = [i for i in focus.get("ids") or [] if i in ids]
    with open(a.data, "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    for c in changes:
        print(c)
    print("evidence: %(verbatim)d verbatim, %(rebuilt)d rebuilt, %(dropped)d dropped" % stats)
    print("findings: %d kept of %d; wrote %s" % (len(kept_recs), before, a.data))


if __name__ == "__main__":
    main()
