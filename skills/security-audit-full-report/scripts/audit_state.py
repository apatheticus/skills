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
              --unvalidated records the run without touching the counter
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
STOP_STATUSES = {"converged", "max-cycles-reached"}

# Bump whenever finding_key changes. An index carries the version its keys were
# computed with; resuming under a different one is refused, because the index
# stores keys and not traces, so old keys cannot be recomputed. Silently
# continuing would make every known finding look new and burn the cycle budget.
KEY_VERSION = 2
KEY_KINDS = ("entrypoint", "sink")

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
    """Structural identity for a finding: its attack path's endpoints.

    The key is the set of (file, scope) pairs at the trace's **entrypoints and
    sinks**, each tagged with which it is. Deliberately NOT `root_cause` + `title`:
    those are free prose, their wording drifts between runs, and keying on them is
    what forced the previous design to ask a model to fuzzy-merge — which biased the
    loop toward declaring convergence. `trace[].file` and `trace[].scope` come from
    data the audit's own Phase 6 verifies against the source, so they are stable
    across runs.

    `line` is excluded on purpose: line numbers move when unrelated code above
    them changes, which would make the same finding look new every cycle.

    **The sink alone is not an identity, and assuming it was is a bug this key has
    already had.** It presumes one defect per scope, and a function can hold
    several: over 50 confirmed findings from one real engagement, five pairs of
    genuinely distinct defects — different root causes, different remediations —
    collapsed onto a single sink key, and in every case the lower-severity one was
    silently absorbed. Adding the entrypoint separates three of those five,
    including the only cross-run collapse, because two defects in one scope are
    usually reached from different entry points.

    The propagation steps are excluded, and that is measured rather than assumed:
    including them separates nothing further and *creates* a collision, because one
    finding's entrypoint can be another's propagation step, and a set of locations
    cannot tell those apart.

    Two defects that share both endpoints still collide, and no key derived from the
    trace can separate them — the trace is the path, and they have the same path.
    That residual is handled by never collapsing within a run and by logging every
    cross-run suppression to the ledger, not by widening the key further.
    """
    trace = f.get("trace") or []
    steps = [(t.get("kind"), t) for t in trace if t.get("kind") in KEY_KINDS]
    weak = False
    if not steps:
        # No step declared its role — the first and last are the best guess.
        steps = [("entrypoint", t) for t in trace[:1]] + [("sink", t) for t in trace[-1:]]
        weak = True
    parts = set()
    for kind, t in steps:
        loc = f"{norm(t.get('file'))}::{norm(t.get('scope'))}"
        if loc != "::":
            parts.add(f"{kind}::{loc}")
    parts = sorted(parts)
    if not parts:
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
    data.setdefault("key_version", 1)
    if "committed_runs" not in data:
        # Migrating an index written before commit was made idempotent. Per-finding
        # run numbers are the only record there is, so a run that committed zero
        # findings is invisible and stays unguarded — one-time, in-flight only.
        data["committed_runs"] = sorted(
            {r["run"] for r in data["findings"] if isinstance(r.get("run"), int)}
        )
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
    save_index(engagement, {"key_version": KEY_VERSION, "findings": [], "committed_runs": []})
    return led


def cmd_dedupe(engagement: Path, run: int) -> dict:
    """Split this run's confirmed findings into new and already-known.

    Two rules here exist because the key can under-count, which is the direction
    that lets the loop stop early:

    Dedup is **across runs only**. Two findings in one run that share a key are
    kept as two, because a run's `findings.json` is a set the audit has already
    adjudicated — it is not supposed to contain one bug twice, so a collision
    within it is evidence of two defects on one path rather than of a duplicate.
    Measured on a real engagement, every intra-run collision was a distinct defect.

    Every cross-run suppression is **recorded**, not just counted. If the key is
    going to decide that this run's finding is last run's finding, that decision
    has to be visible in the ledger and reversible by a human, because it is the
    one place a real finding can leave the engagement without anyone seeing it go.
    """
    idx = load_index(engagement)
    known = {}
    for r in idx["findings"]:
        known.setdefault(r["key"], r)
    out = {
        "run": run,
        "error": None,
        "confirmed": 0,
        "med_plus": 0,
        "new_medplus": 0,
        "known_hits": 0,
        "suppressed": [],
        "suppressed_medplus": 0,
        "same_path_pairs": [],
        "new": [],
    }
    findings, err = load_findings(engagement / f"run-{run}")
    if err:
        out["error"] = err
        return out
    this_run: dict[str, str] = {}
    for f in findings:
        if not isinstance(f, dict) or f.get("verdict") != "confirmed":
            continue
        out["confirmed"] += 1
        sev = norm((f.get("severity") or {}).get("overall_severity"))
        title = (f.get("title") or "")[:200]
        key, parts = finding_key(f)
        if sev in MEDPLUS:
            out["med_plus"] += 1
        if key in known:
            prior = known[key]
            out["known_hits"] += 1
            out["suppressed"].append(
                {
                    "key": key,
                    "severity": sev,
                    "title": title,
                    "first_seen_run": prior.get("run"),
                    "first_seen_title": prior.get("title"),
                }
            )
            if sev in MEDPLUS:
                out["suppressed_medplus"] += 1
            continue
        if key in this_run:
            out["same_path_pairs"].append({"key": key, "titles": [this_run[key], title]})
        else:
            this_run[key] = title
        out["new"].append(
            {
                "key": key,
                "run": run,
                "title": title,
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


def cmd_commit(engagement: Path, run: int, validated: bool = True) -> dict:
    """Record run N and decide whether the loop continues.

    Two things here exist to stop the loop declaring convergence it has not earned,
    and both guard the *dangerous* direction — the one the dedup key's own
    one-directional error argument does not cover.

    Committing the same run twice is a no-op. The harness may notify more than once
    for a single agent completion (observed: four times for one cycle), and an
    unguarded repeat re-dedups the run against an index that already contains it,
    scores `new_medplus: 0`, and advances the counter. Two spurious notifications
    are enough to converge a one-cycle engagement.

    `validated=False` records a cycle that did not finish adjudicating — the hunters
    ran but validation or verification never did — and leaves the counter alone. An
    audit that ran and found nothing is evidence toward convergence; an audit that
    died before validating anything is evidence of nothing. Scoring the second as
    the first converts a failure into proof of cleanliness.
    """
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
    idx = load_index(engagement)

    if idx["key_version"] != KEY_VERSION and (idx["findings"] or idx["committed_runs"]):
        return {
            "run": run,
            "decision": "stop",
            "status": "stale-key-version",
            "stale_key_version": True,
            "index_key_version": idx["key_version"],
            "expected_key_version": KEY_VERSION,
            "error": (
                f"this engagement's index was keyed by finding_key v{idx['key_version']}, "
                f"and this script keys v{KEY_VERSION}. The index stores keys, not traces, so "
                "the old ones cannot be recomputed. Resuming would count every already-known "
                "finding as new and burn the cycle budget. Start a fresh engagement; the "
                "existing run-N directories and report are unaffected."
            ),
        }
    idx["key_version"] = KEY_VERSION

    if run in idx["committed_runs"]:
        status = led.get("status", "running")
        return {
            "run": run,
            "decision": "stop" if status in STOP_STATUSES else "continue",
            "status": status,
            "duplicate": True,
            "consecutive_zero_new_medplus": int(led.get("consecutive_zero_new_medplus", 0)),
            "next_run": int(led.get("next_run", run + 1)),
            "total_accumulated": len(idx["findings"]),
            "error": f"run {run} is already committed; nothing changed",
        }

    res = cmd_dedupe(engagement, run)
    idx["findings"].extend(res["new"])
    idx["committed_runs"].append(run)
    save_index(engagement, idx)

    counter = int(led.get("consecutive_zero_new_medplus", 0))
    if validated:
        counter = counter + 1 if res["new_medplus"] == 0 else 0
    led["consecutive_zero_new_medplus"] = str(counter)
    led["next_run"] = str(run + 1)

    max_cycles = int(led.get("max_cycles", 5))
    if validated and counter >= 2:
        led["status"] = "converged"
        decision = "stop"
    elif run >= max_cycles:
        led["status"] = "max-cycles-reached"
        decision = "stop"
    else:
        led["status"] = "running"
        decision = "continue"

    note = f" [{res['error']}]" if res["error"] else ""
    if validated:
        log = (
            f"run {run}: {res['confirmed']} confirmed, {res['med_plus']} med+, "
            f"{res['new_medplus']} new med+, counter={counter}{note}"
        )
    else:
        log = (
            f"run {run}: UNVALIDATED — {res['confirmed']} confirmed, {res['med_plus']} med+, "
            f"not counted toward convergence, counter={counter} (unchanged){note}"
        )
    # Every decision the key made on this run's behalf, so a human can reverse one.
    for s in res["suppressed"]:
        log += (
            f'\n  - suppressed as known [{s["severity"] or "?"}]: "{s["title"]}"'
            f' — same path as run {s["first_seen_run"]} "{s["first_seen_title"]}"'
            f' (key {s["key"]})'
        )
    for p in res["same_path_pairs"]:
        log += (
            f'\n  - kept as distinct, same path (key {p["key"]}): '
            + " + ".join(f'"{t}"' for t in p["titles"])
        )
    write_ledger(engagement, led, log)
    return {
        "run": run,
        "decision": decision,
        "status": led["status"],
        "validated": validated,
        "confirmed": res["confirmed"],
        "med_plus": res["med_plus"],
        "new_medplus": res["new_medplus"],
        "suppressed": len(res["suppressed"]),
        "suppressed_medplus": res["suppressed_medplus"],
        "same_path_pairs": len(res["same_path_pairs"]),
        "consecutive_zero_new_medplus": counter,
        "next_run": int(led["next_run"]),
        "total_accumulated": len(idx["findings"]),
        "error": res["error"],
    }


# -------------------------------------------------------------- selfcheck

def _finding(sink_file, scope, sev="high", verdict="confirmed", title="t", kind="sink",
             entry="handler"):
    return {
        "verdict": verdict,
        "title": title,
        "root_cause": "wording that drifts between runs",
        "trace": [
            {"kind": "entrypoint", "file": "routes.ts", "line": 1, "scope": entry},
            {"kind": kind, "file": sink_file, "line": 42, "scope": scope},
        ],
        "severity": {"overall_severity": sev},
    }


def selfcheck() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        eng = Path(tmp) / "20260811"
        cmd_init(eng, Path("/target"), 5, None)
        assert (eng / LEDGER_NAME).exists() and (eng / INDEX_NAME).exists()
        assert read_ledger(eng)["status"] == "running"

        def write_run(n, findings):
            d = eng / f"run-{n}"
            d.mkdir(parents=True, exist_ok=True)
            (d / "findings.json").write_text(json.dumps(findings))

        # run 1 — three distinct med+ paths, one low, one rejected, and one pair
        # sharing a whole path. The pair is kept as two: a run's findings.json is
        # already adjudicated, so a collision inside it is two defects on one path.
        write_run(1, [
            _finding("db.ts", "query", "high"),
            _finding("render.ts", "html", "medium"),
            _finding("log.ts", "write", "low"),
            _finding("evil.ts", "boom", "critical", verdict="rejected"),
            _finding("db.ts", "query", "high", title="second defect, same path"),
            # same sink as the first, reached from somewhere else — a different
            # finding. Keying on the sink alone silently absorbed this class.
            _finding("db.ts", "query", "medium", title="same sink, other entrypoint",
                     entry="adminHandler"),
        ])
        r1 = cmd_commit(eng, 1)
        assert r1["confirmed"] == 5, r1           # rejected excluded
        assert r1["med_plus"] == 4, r1
        assert r1["new_medplus"] == 4, r1         # nothing collapses within a run
        assert r1["same_path_pairs"] == 1, r1     # the pair, recorded not merged
        assert r1["consecutive_zero_new_medplus"] == 0, r1
        assert r1["decision"] == "continue", r1
        assert r1["total_accumulated"] == 5, r1
        assert "kept as distinct, same path" in (eng / LEDGER_NAME).read_text()

        # a different entrypoint really is a different key, not just a different row
        assert finding_key(_finding("db.ts", "query"))[0] != \
               finding_key(_finding("db.ts", "query", entry="adminHandler"))[0]

        # run 2 — the same bugs, reworded, different line numbers. Zero new, and
        # every suppression is named in the ledger rather than merely counted.
        write_run(2, [
            _finding("db.ts", "query", "high", title="completely different phrasing"),
            _finding("render.ts", "html", "medium", title="also reworded"),
        ])
        r2 = cmd_commit(eng, 2)
        assert r2["new_medplus"] == 0, r2
        assert r2["suppressed"] == 2 and r2["suppressed_medplus"] == 2, r2
        assert r2["consecutive_zero_new_medplus"] == 1, r2
        assert r2["decision"] == "continue", r2
        led_txt = (eng / LEDGER_NAME).read_text()
        assert "suppressed as known [high]" in led_txt and "completely different phrasing" in led_txt

        # committing run 2 again is a no-op. An unguarded repeat would score
        # new_medplus 0 against an index that already holds run 2 and advance the
        # counter, so two spurious notifications would converge the engagement.
        before = json.loads((eng / INDEX_NAME).read_text())
        dup = cmd_commit(eng, 2)
        assert dup.get("duplicate") is True, dup
        assert dup["consecutive_zero_new_medplus"] == 1, dup
        assert dup["decision"] == "continue" and dup["status"] == "running", dup
        assert json.loads((eng / INDEX_NAME).read_text()) == before, "duplicate mutated the index"
        assert read_ledger(eng)["consecutive_zero_new_medplus"] == "1", read_ledger(eng)

        # run 3 — the cycle died before validating anything. Recorded, but the
        # counter must not move: a crash is not evidence toward convergence.
        (eng / "run-3").mkdir(parents=True, exist_ok=True)
        r3 = cmd_commit(eng, 3, validated=False)
        assert r3["validated"] is False, r3
        assert r3["consecutive_zero_new_medplus"] == 1, r3   # unchanged, not 2
        assert r3["decision"] == "continue" and r3["status"] == "running", r3
        assert 3 in load_index(eng)["committed_runs"], "unvalidated run not recorded"
        assert "UNVALIDATED" in (eng / LEDGER_NAME).read_text()

        # run 4 — findings.json missing entirely, but the cycle ran. A valid
        # zero-new cycle, and the second in a row, so the loop converges.
        (eng / "run-4").mkdir(parents=True, exist_ok=True)
        r4 = cmd_commit(eng, 4)
        assert r4["error"] and "missing" in r4["error"], r4
        assert r4["new_medplus"] == 0, r4
        assert r4["consecutive_zero_new_medplus"] == 2, r4
        assert r4["decision"] == "stop" and r4["status"] == "converged", r4

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

        # an index keyed by an older finding_key is refused for the same reason a v1
        # ledger is: its keys cannot be recomputed, so resuming would recount
        # everything. A freshly initialised index is upgraded silently instead.
        stale = Path(tmp) / "20260813"
        cmd_init(stale, Path("/target"), 5, None)
        d = stale / "run-1"
        d.mkdir(parents=True, exist_ok=True)
        (d / "findings.json").write_text(json.dumps([_finding("a.ts", "s", "high")]))
        assert cmd_commit(stale, 1)["decision"] == "continue"   # empty index, no refusal
        si = load_index(stale)
        si["key_version"] = KEY_VERSION - 1
        save_index(stale, si)
        r = cmd_commit(stale, 2)
        assert r.get("stale_key_version") is True and r["decision"] == "stop", r
        assert load_index(stale)["key_version"] == KEY_VERSION - 1, "refusal must not mutate"

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
        if name == "commit":
            p.add_argument(
                "--unvalidated",
                action="store_true",
                help="the cycle did not finish adjudicating; record it but leave the "
                     "convergence counter alone",
            )

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
        out = cmd_commit(eng, a.run, validated=not a.unvalidated)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
