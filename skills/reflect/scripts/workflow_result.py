#!/usr/bin/env python3
"""
workflow_result.py — read a finished Workflow run's output file, return its result.

The file the task notification names (<output-file>) is pretty-printed JSON:
{summary, agentCount, logs, result, workflowProgress, totalTokens, totalToolCalls}.
`result` is the workflow script's return value, already parsed. Searching the raw
text for a compact '{"signals_count"' finds nothing, because the file is indented;
load it and take ['result'].

The harness neutralizes tag-shaped text and speaker labels in sub-agent output:
`<tag>` arrives as `<\\tag>`, `</tag>` as `<\\/tag>`, `Assistant:` as `Assistant\\:`.
restore() undoes both, so quotes match their transcripts again.

assemble.py imports load(). As a script it prints the result's shape and,
with --out, writes the restored result.

Usage:
    workflow_result.py OUTPUT_FILE [--out WORK/workflow.json]
"""

import argparse
import json
import re
import sys

LABEL = re.compile(r"\b(Assistant|Human|User)\\:")


def restore(obj):
    if isinstance(obj, str):
        return LABEL.sub(r"\1:", obj.replace("<\\", "<"))
    if isinstance(obj, list):
        return [restore(x) for x in obj]
    if isinstance(obj, dict):
        return {k: restore(v) for k, v in obj.items()}
    return obj


def load(path):
    """The restored result of a Workflow output file, or of a JSON file that already is one."""
    with open(path) as f:
        doc = json.load(f)
    if isinstance(doc, dict) and "result" in doc and ("logs" in doc or "workflowProgress" in doc):
        doc = doc["result"]
        if isinstance(doc, str):
            doc = json.loads(doc)
    if not isinstance(doc, dict):
        raise ValueError("%s: the workflow result is %s, not an object" % (path, type(doc).__name__))
    return restore(doc)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("output_file")
    ap.add_argument("--out", help="write the restored result here")
    a = ap.parse_args()
    try:
        res = load(a.output_file)
    except (OSError, ValueError) as e:
        sys.exit(str(e))
    for k, v in res.items():
        size = len(v) if isinstance(v, (list, dict, str)) else v
        print("%-16s %s %s" % (k, type(v).__name__, size))
    if a.out:
        with open(a.out, "w") as f:
            json.dump(res, f, indent=1, ensure_ascii=False)
        print("wrote %s" % a.out)


if __name__ == "__main__":
    main()
