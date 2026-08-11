#!/usr/bin/env python3
"""Durable engagement state for security-audit-full-report.

The orchestrating session never reads a `findings.json`. This script does, and
returns a few counts as JSON. That is the whole point of it: a run's findings
file is tens to hundreds of KB of trace data, and the only things the loop
actually needs from it are "how many confirmed", "how many of those are new",
and "what keys to remember".

Subcommands
    init      create the engagement dir, ledger.md and findings-index.json
    dedupe    read run-N/findings.json, report new vs known  (does not mutate)
    commit    dedupe, append to the index, advance the counter, decide
    selfcheck run the assertions at the bottom of this file

Everything is stdlib. No third-party packages, by design — this runs on
whatever machine the engagement is on.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

MEDPLUS = {"medium", "high", "critical"}
LEDGER_NAME = "ledger.md"
INDEX_NAME = "findings-index.json"

# Order is the order they appear in ledger.md.
FIELDS = [
    "status",
    "target",
    "engagement_dir",
    "design_system",
    "max_cycles",
    "next_run",
    "consecutive_zero_new_medplus",
]


def norm(s) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def finding_key(f: dict) -> tuple[str, list[str]]:
    """Structural identity for a finding: the set of sink (file, scope) pairs.

    Deliberately NOT `root_cause` + `title`. Those are free prose, their wording
    drifts between runs, and keying on them is what forced the previous design to
    ask a model to fuzzy-merge — which biased the loop toward declaring
    convergence. `trace[].file` and `trace[].scope` come from data the audit's own
    Phase 6 verifies against the source, so they are stable across runs.

    `line` is excluded on purpose: line numbers move when unrelated code above
    them changes, which would make the same finding look new every cycle.

    Two findings that reach the same sink scope are the same finding. Two that
    reach different sinks are different findings, even if a human would call them
    one root cause — that errs toward counting a finding as NEW, which resets the
    convergence counter and buys another cycle. Erring the other way would let the
    loop report convergence it had not earned. `max_cycles` bounds the cost of
    erring in this direction; nothing bounds the cost of erring in the other.
    """
    trace = f.get("trace") or []
    sinks = [t for t in trace if t.get("kind") == "sink"]
    weak = False
    if not sinks:
        # No step declared itself the sink — fall back to the terminal step.
        sinks = trace[-1:]
        weak = True
    parts = sorted({f"{norm(t.get('file'))}::{norm(t.get('scope'))}" for t in sinks if t})
    if not parts or parts == ["::"]:
        parts = [f"title::{norm(f.get('title'))}"]
        weak = True
    digest = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return ("weak:" if weak else "") + digest, parts


def load_findings(run_dir: Path):
    """Return (findings_list, error_message). A bad file is not fatal."""
    p = run_dir / "findings.json"
    if not p.exists():
        return None, f"{p} missing"
    try:
        data = json.loads(p.read_text())
    except Exception as exc:  # malformed JSON is a logged condition, not a crash
        return None, f"{p} malformed: {exc}"
    if isinstance(data, dict):
        for key in ("findings", "results", "output"):
            if isinstance(data.get(key), list):
                data = data[key]
                break
    if not isinstance(data, list):
        return None, f"{p} is not a list of findings"
    return data, None


# ---------------------------------------------------------------- ledger i/o

def read_ledger(engagement: Path) -> dict:
    led = {}
    for line in (engagement / LEDGER_NAME).read_text().splitlines():
        if line.startswith("## "):
            break
        m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if m:
            led[m.group(1)] = m.group(2).strip()
    return led


def write_ledger(engagement: Path, led: dict, log_line: str | None = None) -> None:
    p = engagement / LEDGER_NAME
    tail = "## Per-cycle log\n"
    if p.exists():
        txt = p.read_text()
        at = txt.find("## Per-cycle log")
        if at >= 0:
            tail = txt[at:].rstrip("\n") + "\n"
    if log_line:
        tail += f"- {log_line}\n"
    head = [f"# security-audit-full-report engagement {engagement.name}", ""]
    head += [f"{k}: {led[k]}" for k in FIELDS if k in led]
    p.write_text("\n".join(head) + "\n\n" + tail)


def load_index(engagement: Path) -> dict:
    p = engagement / INDEX_NAME
    if not p.exists():
        return {"findings": []}
    try:
        data = json.loads(p.read_text())
    except Exception:
        return {"findings": []}
    data.setdefault("findings", [])
    return data


def save_index(engagement: Path, idx: dict) -> None:
    (engagement / INDEX_NAME).write_text(json.dumps(idx, indent=2) + "\n")


# ------------------------------------------------------------- subcommands

def cmd_init(engagement: Path, target: Path, max_cycles: int, design_system: str | None) -> dict:
    engagement.mkdir(parents=True, exist_ok=True)
    led = {
        "status": "running",
        "target": str(target),
        "engagement_dir": str(engagement),
        "design_system": design_system or "bundled SaaS Pro",
        "max_cycles": str(max_cycles),
        "next_run": "1",
        "consecutive_zero_new_medplus": "0",
    }
    (engagement / LEDGER_NAME).write_text("")  # fresh, so write_ledger keeps no stale tail
    write_ledger(engagement, led)
    save_index(engagement, {"findings": []})
    return led


def cmd_dedupe(engagement: Path, run: int) -> dict:
    idx = load_index(engagement)
    seen = {r["key"] for r in idx["findings"]}
    out = {
        "run": run,
        "error": None,
        "confirmed": 0,
        "med_plus": 0,
        "new_medplus": 0,
        "known_hits": 0,
        "new": [],
    }
    findings, err = load_findings(engagement / f"run-{run}")
    if err:
        out["error"] = err
        return out
    for f in findings:
        if not isinstance(f, dict) or f.get("verdict") != "confirmed":
            continue
        out["confirmed"] += 1
        sev = norm((f.get("severity") or {}).get("overall_severity"))
        key, parts = finding_key(f)
        if sev in MEDPLUS:
            out["med_plus"] += 1
        if key in seen:  # also collapses duplicates within this same run
            out["known_hits"] += 1
            continue
        seen.add(key)
        out["new"].append(
            {
                "key": key,
                "run": run,
                "title": (f.get("title") or "")[:200],
                "severity": sev,
                "sink": parts,
            }
        )
        if sev in MEDPLUS:
            out["new_medplus"] += 1
    return out


def is_legacy(engagement: Path) -> bool:
    """A v1 engagement: accumulated findings kept as prose in ledger.md, no index.

    Resuming one under v2 would silently start from an empty dedup surface, count
    every already-known finding as new, and burn the full cycle budget. Loud is the
    only safe behaviour — the v1 list cannot be recovered, because its keys were
    free text and this version keys on trace sinks.
    """
    p = engagement / LEDGER_NAME
    if not p.exists() or (engagement / INDEX_NAME).exists():
        return False
    return "## Accumulated confirmed findings" in p.read_text()


def cmd_commit(engagement: Path, run: int) -> dict:
    if is_legacy(engagement):
        return {
            "run": run,
            "decision": "stop",
            "status": "legacy-engagement",
            "legacy_ledger": True,
            "error": (
                "this engagement was created by v1, which keyed dedup on prose and kept "
                "the accumulated list in ledger.md. Its keys cannot be converted. Start a "
                "fresh engagement rather than resuming this one."
            ),
        }
    led = read_ledger(engagement)
    res = cmd_dedupe(engagement, run)

    idx = load_index(engagement)
    idx["findings"].extend(res["new"])
    save_index(engagement, idx)

    counter = int(led.get("consecutive_zero_new_medplus", 0))
    counter = counter + 1 if res["new_medplus"] == 0 else 0
    led["consecutive_zero_new_medplus"] = str(counter)
    led["next_run"] = str(run + 1)

    max_cycles = int(led.get("max_cycles", 5))
    if counter >= 2:
        led["status"] = "converged"
        decision = "stop"
    elif run >= max_cycles:
        led["status"] = "max-cycles-reached"
        decision = "stop"
    else:
        led["status"] = "running"
        decision = "continue"

    note = f" [{res['error']}]" if res["error"] else ""
    write_ledger(
        engagement,
        led,
        f"run {run}: {res['confirmed']} confirmed, {res['med_plus']} med+, "
        f"{res['new_medplus']} new med+, counter={counter}{note}",
    )
    return {
        "run": run,
        "decision": decision,
        "status": led["status"],
        "confirmed": res["confirmed"],
        "med_plus": res["med_plus"],
        "new_medplus": res["new_medplus"],
        "consecutive_zero_new_medplus": counter,
        "next_run": int(led["next_run"]),
        "total_accumulated": len(idx["findings"]),
        "error": res["error"],
    }


# -------------------------------------------------------------- selfcheck

def _finding(sink_file, scope, sev="high", verdict="confirmed", title="t", kind="sink"):
    return {
        "verdict": verdict,
        "title": title,
        "root_cause": "wording that drifts between runs",
        "trace": [
            {"kind": "entrypoint", "file": "routes.ts", "line": 1, "scope": "handler"},
            {"kind": kind, "file": sink_file, "line": 42, "scope": scope},
        ],
        "severity": {"overall_severity": sev},
    }


def selfcheck() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        eng = Path(tmp) / "20260811"
        cmd_init(eng, Path("/target"), 3, None)
        assert (eng / LEDGER_NAME).exists() and (eng / INDEX_NAME).exists()
        assert read_ledger(eng)["status"] == "running"

        def write_run(n, findings):
            d = eng / f"run-{n}"
            d.mkdir(parents=True, exist_ok=True)
            (d / "findings.json").write_text(json.dumps(findings))

        # run 1 — two distinct med+ sinks, one low, one rejected, one intra-run dup
        write_run(1, [
            _finding("db.ts", "query", "high"),
            _finding("render.ts", "html", "medium"),
            _finding("log.ts", "write", "low"),
            _finding("evil.ts", "boom", "critical", verdict="rejected"),
            _finding("db.ts", "query", "high", title="same sink, different words"),
        ])
        r1 = cmd_commit(eng, 1)
        assert r1["confirmed"] == 4, r1           # rejected excluded
        assert r1["med_plus"] == 3, r1            # high, medium, and the dup
        assert r1["new_medplus"] == 2, r1         # dup collapsed by sink key
        assert r1["consecutive_zero_new_medplus"] == 0, r1
        assert r1["decision"] == "continue", r1
        assert r1["total_accumulated"] == 3, r1   # 2 med+ and the low

        # run 2 — the same bugs, reworded, different line numbers. Zero new.
        write_run(2, [
            _finding("db.ts", "query", "high", title="completely different phrasing"),
            _finding("render.ts", "html", "medium", title="also reworded"),
        ])
        r2 = cmd_commit(eng, 2)
        assert r2["new_medplus"] == 0, r2
        assert r2["consecutive_zero_new_medplus"] == 1, r2
        assert r2["decision"] == "continue", r2

        # run 3 — findings.json missing entirely. A valid zero-new cycle.
        (eng / "run-3").mkdir(parents=True, exist_ok=True)
        r3 = cmd_commit(eng, 3)
        assert r3["error"] and "missing" in r3["error"], r3
        assert r3["new_medplus"] == 0, r3
        assert r3["consecutive_zero_new_medplus"] == 2, r3
        assert r3["decision"] == "stop" and r3["status"] == "converged", r3

        # a new sink resets the counter, and max_cycles stops the loop
        eng2 = Path(tmp) / "20260812"
        cmd_init(eng2, Path("/target"), 2, None)
        for n, sink in ((1, "a.ts"), (2, "b.ts")):
            d = eng2 / f"run-{n}"
            d.mkdir(parents=True, exist_ok=True)
            (d / "findings.json").write_text(json.dumps([_finding(sink, "s", "high")]))
        c1 = cmd_commit(eng2, 1)
        assert c1["decision"] == "continue", c1
        c2 = cmd_commit(eng2, 2)
        assert c2["new_medplus"] == 1, c2         # genuinely new sink
        assert c2["consecutive_zero_new_medplus"] == 0, c2
        assert c2["decision"] == "stop" and c2["status"] == "max-cycles-reached", c2

        # a trace with no declared sink still keys, and is marked weak
        k, _ = finding_key({"trace": [{"kind": "propagation", "file": "x.ts", "scope": "f"}]})
        assert k.startswith("weak:"), k
        # malformed JSON is logged, not raised
        d = eng2 / "run-9"
        d.mkdir(parents=True, exist_ok=True)
        (d / "findings.json").write_text("{not json")
        assert "malformed" in (cmd_dedupe(eng2, 9)["error"] or ""), "malformed not handled"

        # a v1 engagement is refused loudly rather than silently re-counting
        old = Path(tmp) / "20260101"
        old.mkdir(parents=True, exist_ok=True)
        (old / LEDGER_NAME).write_text(
            "# engagement\nstatus: running\nmax_cycles: 5\nnext_run: 2\n"
            "consecutive_zero_new_medplus: 1\n\n"
            "## Accumulated confirmed findings\n- some prose key\n\n## Per-cycle log\n"
        )
        assert is_legacy(old), "v1 ledger not detected"
        r = cmd_commit(old, 2)
        assert r["decision"] == "stop" and r.get("legacy_ledger") is True, r
        assert not (old / INDEX_NAME).exists(), "must not create state for a refused engagement"
        # and a v2 engagement is never mistaken for one
        assert not is_legacy(eng), "v2 engagement misdetected as legacy"

    print("selfcheck: all assertions passed")
    return 0


# -------------------------------------------------------------------- cli

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init")
    p.add_argument("--engagement", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--max-cycles", type=int, default=5)
    p.add_argument("--design-system", default=None)

    for name in ("dedupe", "commit"):
        p = sub.add_parser(name)
        p.add_argument("--engagement", required=True)
        p.add_argument("--run", type=int, required=True)

    sub.add_parser("selfcheck")

    a = ap.parse_args()
    if a.cmd == "selfcheck":
        return selfcheck()
    eng = Path(a.engagement).expanduser().resolve()
    if a.cmd == "init":
        out = cmd_init(eng, Path(a.target).expanduser().resolve(), a.max_cycles, a.design_system)
    elif a.cmd == "dedupe":
        out = cmd_dedupe(eng, a.run)
    else:
        out = cmd_commit(eng, a.run)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
