#!/usr/bin/env python3
"""
assemble.py — reflect Phase 3 step 6 and Phase 4 step 2: build report-data.json.

Joins the Workflow result (extraction-guide.md § Workflow return value), the
corpus counts from corpus.py, the run's own prose (narrative.json), the prior
edition and the status ledger into the data block report-guide.md § Embedded
data block specifies. Everything mechanical happens here, in code:

- each cluster joined to its decision; /insights additions appended
- thresholds: new-skill needs >= 3 distinct sessions, automation and fix >= 2,
  anything short becomes an observation
- findings the ledger marks wontdo are dropped
- streak, trend (recurring if the prior edition or the ledger knows the id),
  adopted (prior actionable findings now absent and not wontdo)
- rank: leverage desc, effort asc, session count desc, id asc

narrative.json holds what only the run can write:
    {"hero": {"verdict": "...", "summary": "...", "kpis": [...]},   kpis optional
     "focus": null | {"term": "...", "summary": "...", "ids": [...]},
     "notes": {...},                                                 optional
     "methodology": {"triage": [...], "sampled": "...", "pipeline": [...],
                     "limitations": [...]}}

The ledger is read, never written: render_report.py owns the merge.

Usage:
    assemble.py --workflow OUTPUT_FILE --corpus WORK/corpus.json \\
        --narrative WORK/narrative.json [--prior-report PRIOR_DIR/cc-reflection-YYYYMMDD.html] \\
        [--status PRIOR_DIR/reflect-status.json] [--limit 15|all] --out WORK/report-data.json
"""

import argparse
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_report import EFFORTS, read_block  # noqa: E402
from workflow_result import load  # noqa: E402

ACTIONABLE = ("new-skill", "automation", "fix")
MIN_SESSIONS = {"new-skill": 3, "automation": 2, "fix": 2}
EVIDENCE_KEYS = ("quote", "summary", "session_id", "project", "date", "severity")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def rank_key(r):
    return (-r["leverage"], EFFORTS.get(r["effort"], 1), -len(r["session_ids"]), r["id"])


def apply_threshold(r):
    """Downgrade a verdict its distinct-session count cannot carry. Returns True if it changed."""
    need = MIN_SESSIONS.get(r["verdict"])
    if need and len(set(r["session_ids"])) < need:
        r["verdict"] = "observation"
        return True
    return False


def rerank(recs):
    recs.sort(key=rank_key)
    for i, r in enumerate(recs, 1):
        r["rank"] = i
    return recs


def edition_date(ed):
    return "%s-%s-%s" % (ed[:4], ed[4:6], ed[6:8]) if ed and re.fullmatch(r"\d{8}", ed) else None


def read_json(path, default):
    if not path or not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--workflow", required=True, help="Workflow output file, or its extracted result")
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--narrative", required=True)
    ap.add_argument("--prior-report", help="the most recent earlier cc-reflection-*.html")
    ap.add_argument("--status", help="the status ledger to read (missing means empty)")
    ap.add_argument("--limit", default="15")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    if a.limit == "all":
        limit = None
    elif a.limit.isdigit() and int(a.limit) > 0:
        limit = int(a.limit)
    else:
        sys.exit("bad --limit %r: a positive integer or all" % a.limit)

    wf = load(a.workflow)
    corpus = read_json(a.corpus, None) or sys.exit("missing corpus: %s" % a.corpus)
    nar = read_json(a.narrative, None) or sys.exit("missing narrative: %s" % a.narrative)
    ledger = (read_json(a.status, {}) or {}).get("items") or {}
    rows = {r["id"]: r for r in corpus["sessions"]}

    prior, prior_recs = None, {}
    if a.prior_report:
        with open(a.prior_report) as f:
            doc = f.read()
        pdata = read_block(doc, "cc-reflection-data") or {}
        m = re.search(r"cc-reflection-(\d{8})\.html$", a.prior_report)
        edition = m.group(1) if m else None
        prior = {"edition": edition, "date": pdata.get("generated") or edition_date(edition)}
        prior_recs = {r["id"]: r for r in pdata.get("recommendations") or [] if r.get("id")}

    # ------------------------------------------------------------ findings
    decisions = {d.get("id"): d for d in wf.get("decisions") or []}
    cons = wf.get("consolidation") or wf.get("consol") or {}
    corr = {c.get("id"): c for c in cons.get("corroboration") or []}
    items, notes = [], []
    for c in wf.get("clusters") or []:
        d = decisions.get(c.get("id"))
        if not d:
            notes.append("no decision for cluster %s; skipped" % c.get("id"))
            continue
        items.append({**c, **d})
    for add in cons.get("additions") or []:
        if not any(add.get("id") == i.get("id") for i in items):
            items.append({**add, "corroborated": True,
                          "corroboration": add.get("corroboration") or "Surfaced by /insights and confirmed in the transcript."})

    recs, dropped_wontdo, downgraded = [], [], []
    for it in items:
        rid = slug(it.get("id") or it.get("title"))
        if (ledger.get(rid) or {}).get("state") == "wontdo":
            dropped_wontdo.append(rid)
            continue
        ev = []
        for e in it.get("evidence") or []:
            e = {k: e[k] for k in EVIDENCE_KEYS if e.get(k) not in (None, "")}
            row = rows.get(e.get("session_id")) or {}
            e.setdefault("project", row.get("project") or "")
            if "date" not in e and row.get("start"):
                e["date"] = row["start"][:10]
            ev.append(e)
        if not ev:
            notes.append("%s has no evidence; skipped" % rid)
            continue
        pr = prior_recs.get(rid)
        c = corr.get(it.get("id")) or {}
        r = {
            "id": rid,
            "verdict": it.get("verdict"),
            "title": it.get("title"),
            "family": it.get("family"),
            "leverage": int(it.get("leverage") or 1),
            "effort": it.get("effort"),
            "session_ids": sorted(set(it.get("session_ids") or [e["session_id"] for e in ev])),
            "streak": (pr.get("streak", 1) + 1) if pr else 1,
            "trend": "recurring" if (pr or rid in ledger) else "new",
            "projects": sorted({e["project"] for e in ev if e.get("project")}),
            "rationale": it.get("rationale"),
            "example": it.get("example") or it.get("concrete_example"),
            "example_lang": it.get("example_lang") or "text",
            "evidence": ev,
            "corroborated": bool(it.get("corroborated", c.get("corroborated", False))),
            "corroboration": it.get("corroboration") or c.get("note") or "",
        }
        if apply_threshold(r):
            downgraded.append(rid)
        recs.append(r)
    rerank(recs)

    adopted = None
    if prior is not None:
        now_ids = {r["id"] for r in recs}
        adopted = sorted(
            ({"id": pid, "title": p.get("title"), "leverage": p.get("leverage"),
              "raised": edition_date((ledger.get(pid) or {}).get("first_seen")) or prior["date"]}
             for pid, p in prior_recs.items()
             if pid not in now_ids and p.get("verdict") in ACTIONABLE
             and (ledger.get(pid) or {}).get("state") != "wontdo"),
            key=lambda x: -(x["leverage"] or 0))

    # ------------------------------------------------------------- the rest
    hero = dict(nar.get("hero") or {})
    came_back = sum(1 for r in recs if (ledger.get(r["id"]) or {}).get("state") == "done")
    hero.setdefault("kpis", [
        {"label": "Findings", "value": len(recs), "sub": "showing %d" % min(len(recs), limit or len(recs))},
        {"label": "Came back", "value": came_back, "sub": "marked done, recurring"},
        {"label": "Sessions", "value": corpus["sessions_analyzed"], "sub": "in window"},
    ])
    nm = nar.get("methodology") or {}
    rows_all = corpus["sessions"]
    data = {
        "generated": dt.date.today().isoformat(),
        "window": corpus["window"],
        "focus": nar.get("focus"),
        "design_system": "Neumorphic Fresh",
        "sessions_analyzed": corpus["sessions_analyzed"],
        "projects": corpus["projects"],
        "insights_coverage": corpus["insights_coverage"],
        "tokens": corpus["tokens"],
        "limit": limit,
        "prior": prior,
        "hero": hero,
        "recommendations": recs,
        "panorama": corpus["panorama"],
        "methodology": {
            "corpus": nm.get("corpus") or [
                ["Transcripts", "%d in window, %.0f MB" % (len(rows_all), sum(r["mb"] for r in rows_all))],
                ["Excluded", ", ".join("%s (%s)" % (x["id"][:8], x["why"]) for x in corpus["excluded"])],
                ["Signals", str(wf.get("signals_count", "n/a"))],
            ],
            "triage": nm.get("triage") or [],
            "sampled": nm.get("sampled") or "none, every session was read",
            "unreadable": sorted(set((nm.get("unreadable") or []) + (wf.get("unreadable") or []))),
            "pipeline": nm.get("pipeline") or [],
            "limitations": nm.get("limitations") or [],
            "projects": corpus["methodology_projects"],
        },
    }
    if adopted is not None:
        data["adopted"] = adopted
    if nar.get("notes"):
        data["notes"] = nar["notes"]

    with open(a.out, "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    v = {}
    for r in recs:
        v[r["verdict"]] = v.get(r["verdict"], 0) + 1
    print("findings: %d (%s)" % (len(recs), ", ".join("%d %s" % (n, k) for k, n in sorted(v.items(), key=lambda x: -x[1]))))
    if downgraded:
        print("downgraded to observation, too few sessions: %s" % ", ".join(downgraded))
    if dropped_wontdo:
        print("dropped, ledger says wontdo: %s" % ", ".join(dropped_wontdo))
    if prior is not None:
        print("trend: %d recurring, %d new, %d adopted" % (
            sum(r["trend"] == "recurring" for r in recs), sum(r["trend"] == "new" for r in recs), len(adopted)))
    for n in notes:
        print("note: %s" % n)
    print("wrote %s" % a.out)


if __name__ == "__main__":
    main()
