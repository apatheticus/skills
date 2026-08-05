#!/usr/bin/env python3
"""
render_report.py — turn a scan JSON into the SaaS Pro HTML report.

Everything mechanical is derived here (KPI tiles, severity donut, change lists,
port rows, methodology) so the model's only job is judgment and prose. Anything
the model does author goes into the JSON under `narrative`, `remediation`, or a
finding's `body_html`, and this script picks it up.

The script is safe to run on a raw scan JSON with no model input at all — it
falls back to generated prose. That fallback exists so the pipeline can be
smoke-tested end to end, not because a report should ship without a human-
readable verdict written over it.

Usage:
    render_report.py <scan.json> [--template <path>] [--out <path.html>]
"""

import argparse
import json
import os
import re
import sys

SEV_ORDER = ["material", "low", "informational", "accepted"]
SEV_LABEL = {"material": "Material", "low": "Low",
             "informational": "Informational", "accepted": "Accepted"}
SEV_COLOR = {"material": "#EF4458", "low": "#F9A03F",
             "informational": "#5B5FEF", "accepted": "#9297B3"}

PORT_SERVICES = {
    21: "FTP", 22: "SSH", 25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3",
    143: "IMAP", 443: "HTTPS", 465: "SMTPS submission", 587: "Submission",
    993: "IMAPS", 995: "POP3S", 1433: "MSSQL", 2082: "cPanel", 2083: "cPanel (SSL)",
    2086: "WHM", 2087: "WHM (SSL)", 2095: "Webmail", 2096: "Webmail (SSL)",
    2222: "SSH (alt)", 3306: "MySQL/MariaDB", 5432: "PostgreSQL",
    6379: "Redis", 8080: "HTTP alt", 8443: "HTTPS alt", 27017: "MongoDB",
}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def build_kpis(doc):
    f = doc["findings"]
    counts = {k: sum(1 for x in f if x["severity"] == k) for k in SEV_ORDER}
    d = doc.get("delta", {})
    new = sum(1 for x in f if x.get("delta") == "new")
    regressed = sum(1 for x in f if x.get("delta") == "regressed")
    fixed = len(d.get("fixed", []))
    incomplete = sum(1 for c in doc.get("checks_run", []) if c["state"] != "ok")
    first_run = not d.get("baseline")

    return [
        {"label": "Findings Open", "num": len(f),
         "sub": f"{len(doc.get('checks_run', []))} checks executed",
         "rail": "var(--grad-brand)"},
        {"label": "Material Consequence", "num": counts["material"],
         "sub": "Real business impact if left open" if counts["material"]
                else "Nothing at this level",
         "rail": "linear-gradient(180deg,#EF4458,#FF7A8A)"},
        {"label": "New This Scan" if not first_run else "Baseline Established",
         "num": new,
         "sub": "Not present in the previous scan" if not first_run
                else "First scan — everything is new by definition",
         "rail": "var(--grad-purple)"},
        {"label": "Regressed", "num": regressed,
         "sub": "Severity or observed value worsened" if not first_run
                else "No baseline to regress from",
         "rail": "var(--grad-orange)"},
        {"label": "Resolved Since Last Scan", "num": fixed,
         "sub": "Confirmed absent and re-tested" if fixed
                else "Nothing closed since the last scan",
         "rail": "var(--grad-green)"},
        {"label": "Checks Incomplete", "num": incomplete,
         "sub": "Unrun — not the same as clean" if incomplete
                else "Every check reached a verdict",
         "rail": "var(--grad-coral)" if incomplete else "var(--grad-green)"},
    ]


def build_changed(doc):
    f = doc["findings"]
    d = doc.get("delta", {})
    first_run = not d.get("baseline")

    def row(x):
        return {"title": x["title"], "severity": x.get("severity", ""),
                "note": x.get("delta_note", "")}

    changed = {
        "new": [row(x) for x in f if x.get("delta") == "new"],
        "regressed": [row(x) for x in f if x.get("delta") == "regressed"],
        "fixed": [row(x) for x in d.get("fixed", [])],
        "not-retested": [row(x) for x in d.get("not_retested", [])],
    }
    if first_run:
        changed["intro"] = (
            "This is the first scan for this target, so there is no baseline to "
            "compare against and every finding is new by definition. The next run "
            "will compare against today and report only what moved.")
        changed["empty_message"] = "No previous scan to compare against."
        changed["new"] = []          # avoid a wall of "new" on run one
    else:
        n = len(changed["new"]) + len(changed["regressed"]) + len(changed["fixed"])
        changed["intro"] = (
            f"Compared against the scan of {d['baseline']}. "
            + (f"{n} item(s) moved." if n else
               "Nothing moved — the posture is identical to the previous scan.")
            + " Findings that carry an <em>Unchanged</em> chip below are the "
              "standing state and need no re-reading unless their disposition "
              "has not yet been decided.")
        changed["empty_message"] = (
            f"Nothing changed since {d['baseline']}. Every finding is in the same "
            "state, nothing new appeared, and nothing was resolved.")
    return changed


def build_ports(doc):
    landlord = ""
    for f in doc["findings"]:
        if f["asset"] == "landlord":
            landlord = "hosting provider"
            break
    rows = []
    for p in doc.get("ports", []):
        port = p["port"]
        banner = (p.get("banner") or "").strip()
        rows.append({
            "port": port,
            "service": PORT_SERVICES.get(port, "—"),
            "state": p["state"],
            "owner": landlord or "target",
            "banner": banner,
            "note": banner.splitlines()[0][:110] if banner else "",
        })
    return rows


def default_methodology(doc):
    scan = doc["scan"]
    doms = ", ".join(d["fqdn"] for d in doc["target"]["domains"])
    tools = scan.get("tools", {})
    incomplete = [c for c in doc.get("checks_run", []) if c["state"] != "ok"]

    m = [
        ("Domains in scope",
         f"{esc(doms)}. A finding is reported against the specific domain it was "
         "observed on. Domains that appear in a certificate SAN list but are not "
         "in the target profile are reported as an informational finding rather "
         "than scanned, because an unscanned sibling domain is a common way for a "
         "missing email-authentication record to stay hidden."),
        ("Date and time",
         f"{esc(scan['started_utc'])} to {esc(scan['finished_utc'])} UTC, "
         f"{esc(scan.get('vantage', 'single vantage point'))}."),
        ("Testing boundary",
         esc(scan.get("boundary", "")) + ". Requests to the target's own vhost "
         "include a fixed list of known-sensitive paths; each is a plain GET that "
         "either finds a world-readable file or receives a 404. Shared "
         "infrastructure is touched only by a TCP connect and a banner read, "
         "because probing a shared host's services reaches other tenants and is "
         "not the target owner's to authorize."),
        ("Techniques",
         "Authoritative DNS queries via <code class=\"mono\">dig</code> against "
         "three independent public resolvers, so an absent record is only "
         "reported when all three agree; HTTP capture via "
         "<code class=\"mono\">curl</code>; X.509 inspection and protocol "
         "negotiation via <code class=\"mono\">openssl s_client</code>; TCP "
         "connect and banner reads via <code class=\"mono\">nc</code>"
         + ("; protocol and cipher enumeration via "
            "<code class=\"mono\">testssl.sh</code> in Docker."
            if tools.get("docker") else ".")),
        ("User-Agent handling",
         "Every request carries a realistic browser User-Agent. Many hosts return "
         "an error to requests without one, and a scanner that reads its own "
         "rejection as a service fault will report a false outage. The no-User-"
         "Agent case is tested exactly once, deliberately, as a WAF fingerprint — "
         "never as an availability signal."),
        ("Version strings are not patch levels",
         "A version read from a banner or a generator tag is a disclosure finding. "
         "It is not evidence that the software is unpatched: distributions backport "
         "security fixes while the advertised version stays fixed. No finding in "
         "this report asserts a vulnerability without a specific CVE or advisory "
         "identifier and a link to it."),
        ("Unrun checks",
         (f"{len(incomplete)} check(s) did not reach a verdict this run: "
          + "; ".join(f"<code class=\"mono\">{esc(c['check'])}</code> on "
                      f"{esc(c['scope'])} ({esc(c['state'])}"
                      + (f" — {esc(c['reason'])}" if c.get("reason") else "") + ")"
                      for c in incomplete[:8])
          + ". An unrun check is not a clean result, and a prior finding whose "
            "check did not complete is reported as not re-tested rather than "
            "resolved.") if incomplete else
         "Every check reached a verdict. No finding in this report rests on an "
         "assumption that something was tested when it was not."),
        ("Not assessed",
         "Authenticated application testing, plugin and theme inventory behind the "
         "admin console, control-panel configuration, mail flow in transit, and "
         "anything requiring credentials. Login rate limiting cannot be confirmed "
         "from outside without submitting credentials, which this scan does not "
         "do — verify it in the platform's own console."),
        ("Reproducing this",
         "Every command in the evidence blocks is copyable and re-runnable from a "
         "shell. Results will change if the hosting provider alters its "
         "configuration or its WAF rule set."),
    ]
    return m


def fallback_narrative(doc):
    """Generated prose so the pipeline runs end to end without model input."""
    f = doc["findings"]
    mat = [x for x in f if x["severity"] == "material"]
    d = doc.get("delta", {})
    org = doc["target"]["org"]
    doms = [x["fqdn"] for x in doc["target"]["domains"]]

    if mat:
        h1 = (f"{len(mat)} finding{'s' if len(mat) > 1 else ''} of material "
              f"consequence across {len(doms)} domain{'s' if len(doms) > 1 else ''}.")
    else:
        h1 = ("No findings of material consequence — the remainder are cheap "
              "hardening and documented acceptances.")

    lede = (f"{len(f)} findings from {len(doc.get('checks_run', []))} checks against "
            f"{', '.join(doms)}. "
            + (f"Compared against the scan of {d['baseline']}. "
               if d.get("baseline") else "First scan for this target — this run "
               "establishes the baseline that future scans measure against. ")
            + "Severity is calibrated against the asset scope below, not against a "
              "generic control baseline.")

    return {
        "title": f"Website Security Posture — {', '.join(doms)}",
        "overline": "Periodic External Posture Scan",
        "h1": h1,
        "lede": lede,
        "scope_html": (
            "<p><strong style=\"color:var(--ink-800)\">No scope statement was "
            "supplied in the target profile.</strong> Severities in this report "
            "therefore use each check's generic default, which is very likely "
            "wrong for this asset in both directions. Add a scope statement to "
            "the profile and re-render before circulating this.</p>"),
        "verdict_overline": "Overall Posture",
        "verdict_h2": ("Where the consequence actually sits" if mat
                       else "Nothing here carries material consequence"),
        "verdict_p": "<p>" + (
            "The findings below are ordered by consequence against the asset as "
            "scoped, not by the severity a generic scanner would assign. "
            + ("The material items are listed first and are the only ones worth "
               "treating as urgent." if mat else
               "Everything open is either cheap hardening or a documented "
               "acceptance.")) + "</p>",
        "context": {
            "tile": "t-orange" if mat else "t-green",
            "icon": '<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/>',
            "title": "Read this before acting on the list",
            "body": "<p style=\"font-size:var(--text-sm)\">This section is "
                    "generated. Replace it with the one thing a reader needs to "
                    "understand before they act — the piece of context that "
                    "changes what the findings mean.</p>",
        },
        "closing_html": (
            '<div class="callout is-info reveal">'
            '<span class="tile t-brand" aria-hidden="true"><svg viewBox="0 0 24 24">'
            '<circle cx="12" cy="12" r="9"/><path d="M12 16v-4M12 8h.01"/></svg></span>'
            '<div><h3>How to read this report</h3>'
            '<p style="margin-bottom:0">Scan output is not an assessment. Severity '
            'here is calibrated to the asset scope recorded in the target profile, '
            f'and is not transferable to any other {esc(org)} system. A clean '
            'result on this host says nothing about systems inside a controlled '
            'boundary, and neither does a poor one.</p></div></div>'),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scan_json")
    ap.add_argument("--template", help="path to report-template.html")
    ap.add_argument("--out", help="output .html (default: sibling of the JSON)")
    args = ap.parse_args()

    with open(args.scan_json, encoding="utf-8") as fh:
        doc = json.load(fh)

    tpl_path = args.template or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets", "report-template.html")
    if not os.path.exists(tpl_path):
        sys.exit(f"error: template not found at {tpl_path}")
    tpl = open(tpl_path, encoding="utf-8").read()

    nar = dict(fallback_narrative(doc))
    nar.update({k: v for k, v in (doc.get("narrative") or {}).items() if v})

    data = {
        "kpis": build_kpis(doc),
        "donut": {
            "segments": [{"label": SEV_LABEL[k], "color": SEV_COLOR[k],
                          "n": sum(1 for x in doc["findings"] if x["severity"] == k)}
                         for k in SEV_ORDER],
            "center_num": len(doc["findings"]),
            "center_label": "Findings",
        },
        "context": nar["context"],
        "changed": build_changed(doc),
        "findings": doc["findings"],
        "ports": build_ports(doc),
        "ports_intro": doc.get("narrative", {}).get("ports_intro") or (
            "TCP connect tests with a banner read where the service responded. No "
            "authentication was attempted and no payload was sent. Where a port is "
            "owned by the hosting provider it is listed for completeness — it is "
            "not closable from the tenant side."),
        "ports_caption": (f"TCP reachability observed {doc['scan']['started_utc']} UTC"
                          + (f" against {doc['facts']['ip']}"
                             if doc.get("facts", {}).get("ip") else "") + "."),
        "remediation": doc.get("remediation") or [],
        "methodology": doc.get("narrative", {}).get("methodology") or default_methodology(doc),
    }

    payload = json.dumps(data, ensure_ascii=False, indent=1)
    # A literal </script> inside a JSON string would close the block early.
    payload = payload.replace("</", "<\\/")

    html = tpl
    for key, val in [
        ("TITLE", esc(nar["title"])),
        ("ORG", esc(doc["target"]["org"])),
        ("TARGET_LABEL", esc(", ".join(d["fqdn"] for d in doc["target"]["domains"]))),
        ("DATE", esc(doc["scan"]["date"])),
        ("OVERLINE", esc(nar["overline"])),
        # h1, lede and verdict_h2 are authored prose, inserted as-is so entities
        # like &nbsp; work — the same treatment verdict_p and scope_html get.
        # Escaping them turned "4&nbsp;August" into visible markup.
        ("H1", nar["h1"]),
        ("LEDE", nar["lede"]),
        ("SCOPE_HTML", nar["scope_html"]),
        ("VERDICT_OVERLINE", esc(nar["verdict_overline"])),
        ("VERDICT_H2", nar["verdict_h2"]),
        ("VERDICT_P", nar["verdict_p"]),
        ("CLOSING_HTML", nar["closing_html"]),
        ("DATA", payload),
    ]:
        html = html.replace(f"@@{key}@@", val)

    left = re.findall(r"@@([A-Z0-9_]+)@@", html)
    if left:
        sys.exit(f"error: unfilled placeholders remain: {sorted(set(left))}")

    out = args.out or os.path.splitext(args.scan_json)[0] + ".html"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)

    used_fallback = not (doc.get("narrative") or {}).get("h1")
    print(json.dumps({
        "html": out, "bytes": len(html),
        "findings": len(doc["findings"]),
        "narrative": "fallback (generated)" if used_fallback else "authored",
        "remediation_items": len(data["remediation"]),
    }))
    if used_fallback:
        print("[!] narrative is generated placeholder text — the model still needs "
              "to write the verdict, context card, scope statement and "
              "remediation before this report is circulated.", file=sys.stderr)


if __name__ == "__main__":
    main()
