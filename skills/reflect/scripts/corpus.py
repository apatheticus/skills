#!/usr/bin/env python3
"""
corpus.py — reflect Phases 0 and 2: scope the transcripts, then count them.

Lists every top-level transcript under ~/.claude/projects whose mtime falls in
the window, and drops the running session plus every transcript that continues
into it: a fork or resume carries this conversation's history, and quoting it
makes the report cite itself. Then counts what the Usage panorama shows,
following report-guide.md § The Usage panorama — tokens deduped by message.id,
tool calls by tool_use.id, assistant turns by message.id (one message is split
into a record per content block), and only events inside the window.

Writes one JSON file:
    window          {kind, from, to}
    excluded        [{id, why}]
    sessions        one row per in-window transcript: path, project, size, turns,
                    prompts, errors, interrupts, sub-agent runs, first prompt,
                    /insights meta and facet, and a triage priority
                    (high | medium | low | empty) for Phase 2
    tokens, projects, sessions_analyzed, insights_coverage, panorama,
    methodology_projects    copied into report-data.json by assemble.py

Usage:
    corpus.py --window 30d --self SESSION_ID --out WORK/corpus.json
"""

import argparse
import collections
import datetime as dt
import glob
import json
import os
import re
import sys

PROJECTS = os.path.expanduser("~/.claude/projects")
USAGE = os.path.expanduser("~/.claude/usage-data")
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
INTERRUPT = "[Request interrupted by user"
# Tag-led user text that is still the user typing: a slash command or a paste.
# Everything else that opens with '<' (task notifications, command output) is the harness.
USER_TAGS = ("<command-name>", "<pasted_content")
FACET_KEYS = ("outcome", "claude_helpfulness", "friction_counts", "friction_detail",
              "user_satisfaction_counts", "brief_summary", "underlying_goal")
SID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def parse_window(s):
    if s == "all":
        return None
    m = re.fullmatch(r"(\d+)d", s)
    if not m or int(m.group(1)) < 1:
        sys.exit("bad --window %r: use Nd (e.g. 30d) or all" % s)
    return int(m.group(1))


def local(ts):
    try:
        return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone()
    except (TypeError, ValueError, AttributeError):
        return None


def records(path):
    with open(path, errors="replace") as f:
        for line in f:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def continues_into(path):
    """Session ids this transcript says it continued in (fork or resume)."""
    with open(path, "rb") as f:
        data = f.read()
    if b'"continued-in"' not in data:
        return set()
    out = set()
    for line in data.splitlines():
        if b'"continued-in"' in line:
            try:
                o = json.loads(line)
            except ValueError:
                continue
            if o.get("continuedInSessionId"):
                out.add(o["continuedInSessionId"])
    return out


def error_kind(text):
    t = text[:400].lower()
    if "doesn't want to proceed" in t or "rejected" in t:
        return "user rejected"
    if "permission" in t or "denied" in t:
        return "permission denied"
    if "interrupt" in t:
        return "interrupted"
    if "timed out" in t or "timeout" in t:
        return "timeout"
    if "string to replace" in t or "has not been read" in t or "no such file" in t or "does not exist" in t:
        return "file / edit"
    if "exit code" in t:
        return "non-zero exit"
    return "other"


def block_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(b.get("text", "") for b in content if isinstance(b, dict))
    return ""


def priority(row):
    """Phase 2 triage from counts and /insights facets. Focus matching stays with the run."""
    if row["turns"] == 0:
        return "empty"
    f = row["facet"] or {}
    if (f.get("friction_counts") or (f.get("outcome") not in (None, "fully_achieved"))
            or row["tool_errors"] >= max(3, row["turns"] // 10) or row["interrupts"]
            or (row["minutes"] or 0) > 180 or row["mb"] > 20):
        return "high"
    if f.get("outcome") == "fully_achieved" and not row["tool_errors"] and row["turns"] < 60:
        return "low"
    return "medium"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--window", default="30d", help="Nd or all (default 30d)")
    ap.add_argument("--self", dest="self_id", required=True, help="the running session's id")
    ap.add_argument("--out", required=True, help="corpus JSON to write")
    a = ap.parse_args()

    if not SID.match(a.self_id or ""):
        sys.exit("--self %r is not a session id. If it reads ${CLAUDE_SESSION_ID}, this Claude Code "
                 "did not fill it in: pass the id from this session's transcript name instead." % a.self_id)
    days_back = parse_window(a.window)
    now = dt.datetime.now().astimezone()
    cutoff = now - dt.timedelta(days=days_back) if days_back else None

    # ---------------------------------------------------------- scope (Phase 0)
    main_files = {}
    for p in glob.glob(os.path.join(PROJECTS, "*", "*.jsonl")):
        sid = os.path.basename(p)[:-6]
        if cutoff and dt.datetime.fromtimestamp(os.path.getmtime(p)).astimezone() < cutoff:
            continue
        main_files[sid] = p

    parent_of = {}
    for sid, p in main_files.items():
        for child in continues_into(p):
            parent_of.setdefault(child, set()).add(sid)
    excluded = {a.self_id: "the running session"}
    todo = [a.self_id]
    while todo:
        for parent in parent_of.get(todo.pop(), ()):
            if parent not in excluded:
                excluded[parent] = "continues into the running session"
                todo.append(parent)

    # --------------------------------------------------------------- count
    from_date = cutoff.date() if cutoff else None
    seen_msg, seen_tool, seen_err = set(), set(), set()
    tokens = collections.Counter()
    tok_day = collections.defaultdict(collections.Counter)
    tok_proj = collections.Counter()
    turns_day = collections.defaultdict(collections.Counter)
    heat = {w: [0] * 24 for w in WEEKDAYS}
    tools = collections.Counter()
    tools_day = collections.Counter()
    errs = collections.Counter()
    rows = []

    for sid, path in sorted(main_files.items()):
        if sid in excluded:
            continue
        subs = sorted(glob.glob(os.path.join(os.path.dirname(path), sid, "subagents", "*.jsonl")))
        row = {"id": sid, "path": path, "project": None, "mb": round(os.path.getsize(path) / 1e6, 1),
               "start": None, "end": None, "minutes": None, "turns": 0, "prompts": 0,
               "tool_errors": 0, "interrupts": 0, "subagents": 0, "first_prompt": ""}
        first = last = None
        for f in [path] + subs:
            is_main = f == path
            active = False
            for r in records(f):
                if is_main and row["project"] is None and r.get("cwd"):
                    row["project"] = os.path.basename(r["cwd"].rstrip("/")) or r["cwd"]
                t = local(r.get("timestamp"))
                if t is None or (from_date and t.date() < from_date):
                    continue
                active = True
                proj = row["project"] or os.path.basename(os.path.dirname(path))
                day = t.date().isoformat()
                m = r.get("message") if isinstance(r.get("message"), dict) else {}
                if r.get("type") == "assistant":
                    if is_main:
                        first = first or t
                        last = t
                    mid = m.get("id")
                    if mid and mid not in seen_msg:
                        seen_msg.add(mid)
                        u = m.get("usage") or {}
                        c = {"input": u.get("input_tokens") or 0,
                             "cache_create": u.get("cache_creation_input_tokens") or 0,
                             "cache_read": u.get("cache_read_input_tokens") or 0,
                             "output": u.get("output_tokens") or 0}
                        tokens.update(c)
                        tok_day[day].update(c)
                        tok_proj[proj] += sum(c.values())
                        if is_main:
                            row["turns"] += 1
                            turns_day[day][proj] += 1
                            heat[WEEKDAYS[t.weekday()]][t.hour] += 1
                    for b in m.get("content") or []:
                        if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("id") not in seen_tool:
                            seen_tool.add(b.get("id"))
                            name = b.get("name") or "?"
                            if name.startswith("mcp__"):
                                name = "mcp:" + name.split("__")[1][:24]
                            tools[name] += 1
                            tools_day[day] += 1
                elif r.get("type") == "user" and is_main and not r.get("isMeta"):
                    c = m.get("content")
                    blocks = [{"type": "text", "text": c}] if isinstance(c, str) else (c if isinstance(c, list) else [])
                    for b in blocks:
                        if not isinstance(b, dict):
                            continue
                        if b.get("type") == "tool_result" and b.get("is_error"):
                            key = b.get("tool_use_id")
                            if key not in seen_err:
                                seen_err.add(key)
                                row["tool_errors"] += 1
                                errs[error_kind(block_text(b.get("content")))] += 1
                        elif b.get("type") == "text":
                            txt = b.get("text") or ""
                            head = txt.lstrip()
                            if INTERRUPT in txt:
                                row["interrupts"] += 1
                            elif head and (not head.startswith("<") or head.startswith(USER_TAGS)) \
                                    and not head.startswith("This session is being continued"):
                                row["prompts"] += 1
                                row["first_prompt"] = row["first_prompt"] or re.sub(r"\s+", " ", txt)[:160]
            if not is_main and active:
                row["subagents"] += 1
        row["project"] = row["project"] or os.path.basename(os.path.dirname(path))
        if first:
            row["start"], row["end"] = first.isoformat()[:16], last.isoformat()[:16]
            row["minutes"] = round((last - first).total_seconds() / 60)
        row["meta"] = os.path.exists(os.path.join(USAGE, "session-meta", sid + ".json"))
        facet_path = os.path.join(USAGE, "facets", sid + ".json")
        row["facet"] = None
        if os.path.exists(facet_path):
            try:
                fj = json.load(open(facet_path))
                row["facet"] = {k: fj.get(k) for k in FACET_KEYS if k in fj}
            except ValueError:
                pass
        row["priority"] = priority(row)
        rows.append(row)

    # ------------------------------------------------------------ panorama
    analyzed = [r for r in rows if r["turns"]]
    start = from_date or min((dt.date.fromisoformat(r["start"][:10]) for r in analyzed), default=now.date())
    days = [(start + dt.timedelta(i)).isoformat() for i in range((now.date() - start).days + 1)]
    by_proj = collections.Counter()
    for d in days:
        by_proj.update(turns_day.get(d) or {})
    order = [p for p, _ in by_proj.most_common()]
    series = [{"name": p, "values": [(turns_day.get(d) or {}).get(p, 0) for d in days]} for p in order[:5]]
    if len(order) > 5:
        series.append({"name": "other", "values": [sum((turns_day.get(d) or {}).get(p, 0) for p in order[5:])
                                                   for d in days]})
    starts = collections.Counter(r["start"][:10] for r in analyzed)
    total_tok = sum(tokens.values())
    by_day = lambda key: [(tok_day.get(d) or {}).get(key, 0) for d in days]
    per_start_day = lambda key: [sum(r[key] for r in analyzed if r["start"][:10] == d) for d in days]
    panorama = {
        "days": days,
        "kpis": [
            {"label": "Sessions", "value": len(analyzed),
             "sub": "%d in window, %d with no turns" % (len(rows), len(rows) - len(analyzed)),
             "spark": [starts.get(d, 0) for d in days]},
            {"label": "Assistant turns", "value": sum(r["turns"] for r in analyzed),
             "sub": "main threads, deduped by message", "spark": [sum((turns_day.get(d) or {}).values()) for d in days]},
            {"label": "Tool calls", "value": sum(tools.values()), "sub": "incl. sub-agents",
             "spark": [tools_day.get(d, 0) for d in days]},
            {"label": "Tool errors", "value": sum(r["tool_errors"] for r in analyzed), "sub": "main threads",
             "spark": per_start_day("tool_errors")},
            {"label": "Tokens", "value": total_tok,
             "sub": "%.0f%% cache read" % (100.0 * tokens["cache_read"] / total_tok) if total_tok else "none recorded",
             "spark": [sum((tok_day.get(d) or {}).values()) for d in days]},
            {"label": "Sub-agent runs", "value": sum(r["subagents"] for r in analyzed),
             "sub": "across %d sessions" % sum(1 for r in analyzed if r["subagents"]),
             "spark": per_start_day("subagents")},
        ],
        "trend": {"title": "Assistant turns per day", "sub": "Main-thread turns, stacked by project.", "series": series},
        "mix": {"title": "Where the turns went", "sub": "Share of main-thread turns by project.", "unit": "turns",
                "items": [{"name": p, "value": v} for p, v in by_proj.most_common()]},
        "detail": [
            {"title": "Top tools", "sub": "Calls across main threads and sub-agents.",
             "items": [{"name": n, "value": v} for n, v in tools.most_common(8)]},
            {"title": "Tool errors by kind", "sub": "Main-thread error results, bucketed by message.",
             "items": [{"name": n, "value": v} for n, v in errs.most_common()]},
        ],
        "tokens_daily": {"title": "Tokens per day", "sub": "Deduped by message id, incl. sub-agents.",
                         "series": [{"name": "cache read", "values": by_day("cache_read")},
                                    {"name": "cache write", "values": by_day("cache_create")},
                                    {"name": "output", "values": by_day("output")},
                                    {"name": "input", "values": by_day("input")}]},
        "tokens_by_project": {"title": "Tokens by project", "sub": "All four components summed.",
                              "items": [{"name": p, "value": v} for p, v in tok_proj.most_common()]},
        "heatmap": {"title": "When you work", "sub": "Assistant turns by weekday and hour, local time.",
                    "unit": "turns", "rows": [{"label": w, "values": heat[w]} for w in WEEKDAYS]},
        "quadrant": {"title": "Where each recommendation sits", "sub": "Leverage against effort, shown findings only."},
    }
    if not total_tok:
        for k in ("tokens_daily", "tokens_by_project"):
            panorama.pop(k)

    sessions_by_proj = collections.Counter(r["project"] for r in analyzed)
    out = {
        "window": {"kind": a.window, "from": days[0], "to": days[-1]},
        "excluded": [{"id": k, "why": v} for k, v in excluded.items()],
        "sessions": rows,
        "sessions_analyzed": len(analyzed),
        "projects": [p for p, _ in sessions_by_proj.most_common()],
        "insights_coverage": round(sum(1 for r in analyzed if r["meta"]) / len(analyzed), 2) if analyzed else 0.0,
        "tokens": {k: tokens[k] for k in ("input", "cache_create", "cache_read", "output")},
        "panorama": panorama,
        "methodology_projects": [{"name": p, "sessions": n, "tokens": tok_proj.get(p, 0)}
                                 for p, n in sessions_by_proj.most_common()],
    }
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    pri = collections.Counter(r["priority"] for r in rows)
    print("window %s: %s to %s" % (a.window, days[0], days[-1]))
    print("sessions: %d in window, %d analyzed (%s), %d excluded (%s)" % (
        len(rows), len(analyzed), ", ".join("%d %s" % (pri[k], k) for k in ("high", "medium", "low", "empty") if pri[k]),
        len(excluded), ", ".join(k[:8] for k in excluded)))
    print("tokens: %s total, %d tool calls, %d tool errors" % (
        format(total_tok, ","), sum(tools.values()), sum(errs.values())))
    print("wrote %s" % a.out)


if __name__ == "__main__":
    main()
