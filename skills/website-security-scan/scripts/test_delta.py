#!/usr/bin/env python3
"""
Self-check for the delta logic. Run it after touching compute_delta, ran(), or
any COVERS_* group:

    python3 scripts/test_delta.py

The case that matters most is `absent_but_check_skipped`. Every other branch
being wrong produces a visibly odd report; that one produces a report which
cheerfully says a problem was resolved when nobody looked for it.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan import compute_delta, _covers                       # noqa: E402


def finding(fid, check, scope="example.com", severity="low", value="v1"):
    return {"id": fid, "check": check, "scope": scope, "asset": "web",
            "title": fid, "severity": severity, "value": value,
            "summary": "", "evidence": [], "refs": []}


def ran(check, scope="example.com", state="ok", covers=None):
    return {"check": check, "scope": scope, "state": state, "reason": "",
            "covers": covers or [check]}


def doc(findings, checks):
    return {"scan": {"date": "2026-09-01"}, "findings": findings,
            "checks_run": checks}


def base(findings):
    return {"scan": {"date": "2026-08-04"}, "findings": findings,
            "checks_run": []}


fails = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ok    {name}")
    else:
        print(f"  FAIL  {name} {detail}")
        fails.append(name)


print("covers matching")
check("exact match", _covers(ran("dns.caa"), "dns.caa"))
check("dotted prefix", _covers(ran("dns.caa"), "dns.caa.missing"))
check("not a bare string prefix",
      not _covers(ran("http.hsts"), "http.hstsx.missing"),
      "'http.hsts' must not cover 'http.hstsx.missing'")
check("explicit covers list",
      _covers(ran("http.headers", covers=["http.csp", "http.hsts"]),
              "http.csp.missing"))
check("outside explicit covers",
      not _covers(ran("http.headers", covers=["http.hsts"]), "http.csp.missing"),
      "redirect-only host checked HSTS only; CSP is not covered")

print("\nfirst run, no baseline")
cur = doc([finding("a", "dns.caa")], [ran("dns.caa")])
d = compute_delta(cur, None)
check("everything is new", cur["findings"][0]["delta"] == "new")
check("no fixed list", d["fixed"] == [])
check("no not_retested list", d["not_retested"] == [])
check("baseline is None", d["baseline"] is None)

print("\nunchanged")
cur = doc([finding("a", "dns.caa")], [ran("dns.caa")])
compute_delta(cur, base([finding("a", "dns.caa")]))
check("same id and value is unchanged", cur["findings"][0]["delta"] == "unchanged")

print("\nnew finding against an existing baseline")
cur = doc([finding("a", "dns.caa"), finding("b", "email.spf")],
          [ran("dns.caa"), ran("email.spf")])
compute_delta(cur, base([finding("a", "dns.caa")]))
check("unseen id is new",
      [f["delta"] for f in cur["findings"]] == ["unchanged", "new"])

print("\nregression by severity")
cur = doc([finding("a", "email.dmarc", severity="material")], [ran("email.dmarc")])
compute_delta(cur, base([finding("a", "email.dmarc", severity="low")]))
check("low -> material is regressed", cur["findings"][0]["delta"] == "regressed")
check("note records both severities",
      "low" in cur["findings"][0]["delta_note"]
      and "material" in cur["findings"][0]["delta_note"])

print("\nregression by observed value")
cur = doc([finding("a", "email.dmarc", value="p=none")], [ran("email.dmarc")])
compute_delta(cur, base([finding("a", "email.dmarc", value="p=quarantine")]))
check("changed value at same severity is regressed",
      cur["findings"][0]["delta"] == "regressed")
check("note records old and new value",
      "p=quarantine" in cur["findings"][0]["delta_note"]
      and "p=none" in cur["findings"][0]["delta_note"])

print("\nseverity improvement while still open")
cur = doc([finding("a", "email.dmarc", severity="informational")], [ran("email.dmarc")])
compute_delta(cur, base([finding("a", "email.dmarc", severity="material")]))
check("material -> informational is not a regression",
      cur["findings"][0]["delta"] == "unchanged")

print("\nabsent and the check completed")
cur = doc([], [ran("dns.caa")])
d = compute_delta(cur, base([finding("a", "dns.caa.missing")]))
check("reported fixed", [f["delta"] for f in d["fixed"]] == ["fixed"])
check("not in not_retested", d["not_retested"] == [])

print("\nabsent but the check was skipped  <-- the one that matters")
cur = doc([], [ran("dns.caa", state="skipped")])
d = compute_delta(cur, base([finding("a", "dns.caa.missing")]))
check("NOT reported fixed", d["fixed"] == [],
      "a skipped check must never produce a 'fixed' verdict")
check("reported not-retested",
      [f["delta"] for f in d["not_retested"]] == ["not-retested"])
check("note says not confirmed fixed",
      "NOT confirmed fixed" in d["not_retested"][0]["delta_note"])

print("\nabsent but the check errored")
cur = doc([], [ran("tls.cert", state="error", covers=["tls.cert"])])
d = compute_delta(cur, base([finding("a", "tls.cert.expired")]))
check("errored check does not mean fixed", d["fixed"] == [])
check("reported not-retested", len(d["not_retested"]) == 1)

print("\nabsent and no check touched it at all")
cur = doc([], [ran("email.spf")])
d = compute_delta(cur, base([finding("a", "http.csp.missing")]))
check("unrelated check does not vouch for it", d["fixed"] == [])
check("reported not-retested", len(d["not_retested"]) == 1)

print("\nheader finding vouched for by the http.headers execution")
cur = doc([], [ran("http.headers", covers=["http.csp", "http.hsts"])])
d = compute_delta(cur, base([finding("a", "http.csp.missing")]))
check("covers list makes it fixed", len(d["fixed"]) == 1)

print("\nscope isolation")
cur = doc([], [ran("dns.caa", scope="other.com")])
d = compute_delta(cur, base([finding("a", "dns.caa.missing", scope="example.com")]))
check("a check on another domain does not vouch for this one",
      d["fixed"] == [] and len(d["not_retested"]) == 1)

print()
if fails:
    print(f"{len(fails)} FAILED: {', '.join(fails)}")
    sys.exit(1)
print("all delta checks passed")
