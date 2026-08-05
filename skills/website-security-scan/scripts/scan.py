#!/usr/bin/env python3
"""
scan.py — external, read-only security posture scan for a set of related domains.

Emits a JSON document describing every finding, every check that ran, and the raw
evidence each finding rests on. The JSON is the contract consumed by
render_report.py and by the model that writes the narrative.

Design constraints that matter (see references/check-catalog.md for the why):

  * Stdlib only. Shells out to dig / curl / openssl / nc / docker so the evidence
    blocks in the report are literally re-runnable commands, not paraphrases.

  * A check that did not run must never look like a clean result. Every check
    records its own execution state (ok / unverified / error / skipped) in
    `checks_run`, and the delta logic refuses to call a finding FIXED unless the
    check that would have found it actually completed this time.

  * Read-only on the target's own vhost; TCP connect + banner read only on a
    shared IP. No authentication, no credentials, no payloads, no fuzzing.

  * Always send a realistic User-Agent. The host WAF returns 406 to requests
    without one, and reading that rejection as an outage is exactly the mistake
    that produced two bogus "critical" findings in the assessment this skill
    exists to replace. The no-UA case is tested deliberately, once, as a WAF
    fingerprint — never as an availability signal.

Usage:
    scan.py --profile <path/to/target.md> [--out <path.json>] [--no-docker]
            [--skip-ports] [--skip-paths] [--delay 0.4]
"""

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " \
     "(KHTML, like Gecko) Chrome/128.0 Safari/537.36"

RESOLVERS = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]

# Severity ordering, worst first. Used for delta direction and report sorting.
SEVERITY_RANK = {"material": 0, "low": 1, "informational": 2, "accepted": 3}

# ---------------------------------------------------------------------------
# Sensitive paths. All plain GETs against the target's own vhost. Nothing here
# sends a payload or attempts authentication — a request for /.env either finds
# a file the world can already read, or it 404s.
# ---------------------------------------------------------------------------
SENSITIVE_PATHS = [
    # version control
    ".git/HEAD", ".git/config", ".git/logs/HEAD", ".svn/entries", ".hg/store/00manifest.i",
    # environment and secrets
    ".env", ".env.local", ".env.bak", ".env.production", ".env.save",
    ".aws/credentials", ".ssh/id_rsa", "id_rsa", ".npmrc", ".netrc",
    # WordPress config leftovers
    "wp-config.php.bak", "wp-config.php.save", "wp-config.php.old",
    "wp-config.php.orig", "wp-config.php~", "wp-config.txt", "wp-config.php.swp",
    # backups and dumps
    "backup.zip", "backup.tar.gz", "site.zip", "website.zip", "wordpress.zip",
    "public_html.zip", "backup.sql", "database.sql", "dump.sql", "db.sql",
    # debug and info disclosure
    "phpinfo.php", "info.php", "test.php", "error_log", "wp-content/debug.log",
    "server-status", "server-info", ".DS_Store", ".htpasswd", ".htaccess.bak",
    "web.config", ".vscode/sftp.json", "config.php.bak", "settings.php.bak",
    # dependency manifests
    "composer.json", "composer.lock", "package.json", "yarn.lock", ".gitignore",
    # admin surfaces
    "adminer.php", "phpmyadmin/", "pma/", "wp-admin/install.php",
    # WordPress surfaces worth knowing about (findings, not necessarily problems)
    "wp-login.php", "xmlrpc.php", "wp-cron.php", "readme.html", "license.txt",
    "wp-json/wp/v2/users", "wp-content/uploads/", "wp-content/plugins/",
    "wp-content/themes/", "wp-includes/",
    # good-practice presence checks
    ".well-known/security.txt", "robots.txt", "sitemap.xml",
]

# Paths that get their own dedicated finding further down, so the generic
# exposure.path.* finding is suppressed for them. Without this, a listable
# directory produces two findings for one condition and inflates the count.
PATHS_REPORTED_ELSEWHERE = {
    # expected to exist; presence is context, not exposure
    "robots.txt", "sitemap.xml", ".well-known/security.txt",
    # each has a purpose-built finding below
    "wp-login.php", "xmlrpc.php", "wp-cron.php", "wp-json/wp/v2/users",
    "wp-content/uploads/", "wp-content/plugins/", "wp-content/themes/",
    "wp-includes/",
}

DKIM_SELECTORS = ["selector1", "selector2", "default", "google", "k1", "k2",
                  "mail", "dkim", "s1", "s2", "pm", "everlytickey1", "zoho",
                  "mandrill", "sendgrid", "protonmail", "mimecast20220101"]

SECURITY_HEADERS = {
    "strict-transport-security": ("http.hsts.missing", "Strict-Transport-Security"),
    "content-security-policy": ("http.csp.missing", "Content-Security-Policy"),
    "x-frame-options": ("http.xfo.missing", "X-Frame-Options"),
    "x-content-type-options": ("http.xcto.missing", "X-Content-Type-Options"),
    "referrer-policy": ("http.referrer-policy.missing", "Referrer-Policy"),
    "permissions-policy": ("http.permissions-policy.missing", "Permissions-Policy"),
}


COVERS_HEADERS_FULL = ["http.hsts", "http.csp", "http.xfo", "http.xcto",
                       "http.referrer-policy", "http.permissions-policy",
                       "http.banner"]
COVERS_HEADERS_REDIRECT = ["http.hsts"]
COVERS_TLS_CERT = ["tls.cert", "tls.handshake", "infra.related-domain"]
COVERS_TLS_LEGACY = ["tls.protocol", "tls.legacy", "tls.vuln"]
COVERS_PATHS = ["exposure.path", "exposure.dirlisting", "cms.rest-users",
                "cms.login", "cms.xmlrpc", "web.securitytxt"]


# ---------------------------------------------------------------------------
# Plumbing
# ---------------------------------------------------------------------------

def sh(cmd, timeout=25, stdin_devnull=False):
    """Run a shell command, never raise. Returns (rc, stdout, stderr)."""
    try:
        p = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout,
            stdin=subprocess.DEVNULL if stdin_devnull else None,
        )
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out after {timeout}s"
    except Exception as e:                                    # pragma: no cover
        return 1, "", str(e)


class Scan:
    def __init__(self, profile, cfg, args):
        self.profile_path = profile
        self.cfg = cfg
        self.args = args
        self.findings = []
        self.checks = []
        self.ports = []
        self.facts = {}
        self.http_calls = 0
        self._last_http = 0.0
        self.overrides = cfg.get("severity_overrides", {})
        self._once = set()

    # -- rate-limited HTTP ---------------------------------------------------
    def curl(self, url, method="HEAD", ua=UA, timeout=25, extra=""):
        """One rate-limited curl. Returns (cmd, rc, out) with headers+body marker."""
        if self.http_calls >= self.args.max_requests:
            return ("(request cap reached)", 1, "")
        gap = time.time() - self._last_http
        if gap < self.args.delay:
            time.sleep(self.args.delay - gap)
        self._last_http = time.time()
        self.http_calls += 1

        flag = "-I" if method == "HEAD" else "-i"
        ua_part = "-H 'User-Agent:'" if ua is None else f"-A '{ua}'"
        cmd = (f"curl -sS {flag} --http2 {ua_part} {extra} "
               f"--max-time {timeout} '{url}'")
        rc, out, err = sh(cmd, timeout=timeout + 8)
        return (cmd, rc, out or err)

    def head_status(self, url, ua=UA):
        cmd = (f"curl -sS -o /dev/null -A '{ua}' --max-time 25 "
               f"-w '%{{http_code}} %{{time_total}} %{{size_download}} %{{redirect_url}}' '{url}'")
        if self.http_calls >= self.args.max_requests:
            return None
        gap = time.time() - self._last_http
        if gap < self.args.delay:
            time.sleep(self.args.delay - gap)
        self._last_http = time.time()
        self.http_calls += 1
        rc, out, _ = sh(cmd, timeout=35)
        parts = out.split()
        if rc != 0 or len(parts) < 3:
            return None
        return {"cmd": cmd, "code": parts[0], "time": float(parts[1]),
                "size": int(parts[2]), "redirect": parts[3] if len(parts) > 3 else ""}

    # -- recording -----------------------------------------------------------
    def ran(self, check, scope, state="ok", reason="", covers=None):
        # `covers` lists the finding-ID prefixes this execution is evidence for.
        # It exists because a check's name and the IDs it emits often diverge —
        # one "http.headers" execution decides six http.*.missing findings. The
        # delta logic uses it to tell "absent because fixed" from "absent because
        # nobody looked", so an incomplete covers list silently reports unrun
        # checks as resolved.
        self.checks.append({"check": check, "scope": scope, "state": state,
                            "reason": reason, "covers": covers or [check]})

    def add(self, check, scope, asset, title, severity, summary,
            value="", evidence=None, refs=None, once_key=None):
        # Several facts are properties of shared infrastructure rather than of a
        # domain — one WAF, one certificate, one server serving several hostnames.
        # once_key reports those a single time instead of once per domain, which
        # would pad the finding count with duplicates of the same fact.
        if once_key is not None:
            if (check, once_key) in self._once:
                return
            self._once.add((check, once_key))
        for pat, sev in self.overrides.items():
            if fnmatch.fnmatch(check, pat):
                severity = sev
                break
        # The report inserts evidence output as raw HTML so highlight spans work.
        # Captured command output therefore has to be escaped here, or literal
        # markup in a real response — a WordPress `link:` header, a generator meta
        # tag — is parsed as HTML and silently vanishes from the evidence block.
        ev = []
        for e in (evidence or []):
            ev.append(dict(e, out=(str(e.get("out", ""))
                                   .replace("&", "&amp;")
                                   .replace("<", "&lt;")
                                   .replace(">", "&gt;"))))
        self.findings.append({
            "id": f"{check}@{scope}",
            "check": check, "scope": scope, "asset": asset, "title": title,
            "severity": severity, "value": value, "summary": summary,
            "evidence": ev, "refs": refs or [],
        })

    # -- DNS -----------------------------------------------------------------
    def dig(self, name, rtype, resolver=RESOLVERS[0], short=True):
        s = "+short " if short else ""
        cmd = f"dig {s}@{resolver} {name} {rtype}"
        rc, out, _ = sh(cmd, timeout=20)
        return cmd, [l for l in out.splitlines() if l.strip()]

    def dig_consensus(self, name, rtype):
        """Query every resolver. Absence is only believed when all agree."""
        results, cmds = {}, []
        for r in RESOLVERS:
            cmd, vals = self.dig(name, rtype, r)
            cmds.append(cmd)
            results[r] = vals
        present = [r for r, v in results.items() if v]
        any_vals = next((v for v in results.values() if v), [])
        return {"cmds": cmds, "results": results, "values": any_vals,
                "unanimous_absent": not present,
                "split": bool(present) and len(present) < len(RESOLVERS)}


# ---------------------------------------------------------------------------
# Check families
# ---------------------------------------------------------------------------

def check_dns_zone(s, dom):
    """DNSSEC, CAA, zone transfer, nameservers."""
    fqdn = dom["fqdn"]

    cmd, ds = s.dig(fqdn, "DS")
    cmd2, dnskey = s.dig(fqdn, "DNSKEY")
    s.ran("dns.dnssec.missing", fqdn)
    if not ds and not dnskey:
        s.add("dns.dnssec.missing", fqdn, "dns",
              f"DNSSEC not enabled on {fqdn}", "informational",
              "No DS record at the parent and no DNSKEY in the zone. DNSSEC "
              "addresses resolver cache poisoning, which major public resolvers "
              "already mitigate by other means.", value="absent",
              evidence=[{"cmd": f"{cmd}; {cmd2}",
                         "out": "(empty — no DS record)\n(empty — no DNSKEY)"}])

    caa = s.dig_consensus(fqdn, "CAA")
    s.ran("dns.caa", fqdn)
    if caa["unanimous_absent"]:
        s.add("dns.caa.missing", fqdn, "dns",
              f"No CAA record on {fqdn}", "low",
              "Any certificate authority may issue certificates for this domain "
              "and every hostname under it, including the mail hostnames. A CAA "
              "record is a single DNS entry that constrains issuance.",
              value="absent",
              evidence=[{"cmd": caa["cmds"][0], "out": "(empty — no CAA record)"}],
              refs=[{"label": "RFC 8659 — DNS CAA", "url": "https://www.rfc-editor.org/rfc/rfc8659"}])
    else:
        val = " ".join(caa["values"])
        if "iodef" not in val:
            s.add("dns.caa.no-iodef", fqdn, "dns",
                  f"CAA record on {fqdn} has no iodef contact", "informational",
                  "CAA is published but carries no iodef reporting address, so a "
                  "CA that blocks a misissuance attempt has nowhere to report it.",
                  value=val,
                  evidence=[{"cmd": caa["cmds"][0], "out": val}])

    cmd, ns = s.dig(fqdn, "NS")
    s.facts.setdefault("nameservers", {})[fqdn] = ns

    # AXFR: read-only, and a zone transfer that succeeds is a genuine finding.
    s.ran("dns.axfr.open", fqdn)
    leaked = []
    for nsname in ns[:3]:
        rc, out, _ = sh(f"dig +noall +answer @{nsname.rstrip('.')} {fqdn} AXFR",
                        timeout=20)
        if out and "Transfer failed" not in out and len(out.splitlines()) > 2:
            leaked.append((nsname, out))
    if leaked:
        nsname, out = leaked[0]
        s.add("dns.axfr.open", fqdn, "dns",
              f"Zone transfer permitted by {nsname}", "material",
              "The nameserver answered an unauthenticated AXFR, disclosing the "
              "full DNS zone including internal hostnames.", value="permitted",
              evidence=[{"cmd": f"dig +noall +answer @{nsname.rstrip('.')} {fqdn} AXFR",
                         "out": "\n".join(out.splitlines()[:12])}])


def check_email_auth(s, dom):
    """DMARC, SPF, DKIM, MTA-STS, TLSRPT, BIMI. The highest-value family."""
    fqdn = dom["fqdn"]
    mail_asset = "email"

    cmd_mx, mx = s.dig(fqdn, "MX")
    has_mail = bool(mx) or "mail" in dom.get("roles", [])
    s.facts.setdefault("mx", {})[fqdn] = mx

    # ---- DMARC ----
    d = s.dig_consensus(f"_dmarc.{fqdn}", "TXT")
    s.ran("email.dmarc", fqdn)
    rec = next((v.strip('"') for v in d["values"] if "DMARC1" in v), "")

    if not rec:
        rcode_cmd = f"dig @{RESOLVERS[0]} _dmarc.{fqdn} TXT"
        rc, rcode_out, _ = sh(rcode_cmd + " +noall +comment", timeout=15)
        status = "NXDOMAIN" if "NXDOMAIN" in rcode_out else "no TXT answer"
        sev = "material" if has_mail else "low"
        s.add("email.dmarc.missing", fqdn, mail_asset,
              f"No DMARC record published for {fqdn}", sev,
              f"Lookup returns {status} on all three public resolvers — no DMARC "
              "policy of any kind. Receivers have no published instruction for "
              "mail that fails authentication, and no alignment requirement ties "
              "the visible From: header to an authenticated identifier. An SPF "
              "record ending in -all does not substitute: SPF authenticates the "
              "envelope sender, not the From: header a recipient reads."
              + (" This domain has live MX records, so it is a usable spoofing "
                 "target, not a parked name." if mx else ""),
              value=status,
              evidence=[{"cmd": "; ".join(d["cmds"]),
                         "out": f"1.1.1.1  ({status})\n8.8.8.8  ({status})\n"
                                f"9.9.9.9  ({status})\n\n# Unanimous. No DMARC record exists."},
                        {"cmd": cmd_mx, "out": "\n".join(mx) or "(no MX)"}],
              refs=[{"label": "RFC 7489 — DMARC", "url": "https://www.rfc-editor.org/rfc/rfc7489"}])
    else:
        tags = dict(re.findall(r"(\w+)\s*=\s*([^;]+)", rec))
        tags = {k.lower(): v.strip() for k, v in tags.items()}
        p = tags.get("p", "none").lower()
        sp = tags.get("sp", "").lower()
        ev = [{"cmd": d["cmds"][0], "out": rec}]

        if p != "reject":
            sev = "material" if p == "none" else "low"
            s.add("email.dmarc.policy-weak", fqdn, mail_asset,
                  f"DMARC policy on {fqdn} is p={p}, not reject", sev,
                  ("p=none monitors only — failing mail is delivered normally."
                   if p == "none" else
                   "p=quarantine sends failing mail to spam rather than rejecting "
                   "it, so a portion still reaches inboxes."),
                  value=f"p={p}", evidence=ev)

        # An absent sp inherits p, so it is only a finding when sp is explicitly
        # published AND weaker than the apex policy.
        strength = {"none": 0, "quarantine": 1, "reject": 2}
        if sp and strength.get(sp, 0) < strength.get(p, 0):
            s.add("email.dmarc.subdomain-weak", fqdn, mail_asset,
                  f"DMARC subdomain policy on {fqdn} is sp={sp}, weaker than p={p}",
                  "material" if sp == "none" else "low",
                  f"The apex is on p={p} but every subdomain is explicitly set to "
                  f"sp={sp}."
                  + (" That is no enforcement at all on subdomains, regardless of "
                     "the apex policy — frequently the weakest part of an "
                     "otherwise reasonable record, and easy to miss when a record "
                     "is transcribed rather than read."
                     if sp == "none" else ""),
                  value=f"sp={sp}", evidence=ev)
        elif sp == "none" and p == "none":
            pass          # already reported as policy-weak; not a second finding

        pct = tags.get("pct", "100")
        if pct != "100":
            s.add("email.dmarc.pct-partial", fqdn, mail_asset,
                  f"DMARC applies to only {pct}% of mail on {fqdn}", "low",
                  f"pct={pct} means the policy is sampled, not enforced.",
                  value=f"pct={pct}", evidence=ev)

        if not tags.get("rua"):
            s.add("email.dmarc.no-rua", fqdn, mail_asset,
                  f"DMARC on {fqdn} requests no aggregate reports", "low",
                  "Without a rua address there is no visibility into who is "
                  "sending as this domain, which makes tightening the policy "
                  "a guess rather than a measured change.", value="no rua",
                  evidence=ev)

    # ---- SPF ----
    cmd, txts = s.dig(fqdn, "TXT")
    spf = next((t.strip('"') for t in txts if t.strip('"').lower().startswith("v=spf1")), "")
    s.ran("email.spf", fqdn)
    if not spf:
        if has_mail:
            s.add("email.spf.missing", fqdn, mail_asset,
                  f"No SPF record on {fqdn}", "material",
                  "No sender policy is published, so no receiver can distinguish "
                  "authorized senders from forgeries at the envelope level.",
                  value="absent", evidence=[{"cmd": cmd, "out": "(no v=spf1 record)"}])
    else:
        ev = [{"cmd": f"{cmd} | grep spf", "out": spf}]
        m = re.search(r"([~\-?+])all\s*$", spf.strip())
        qual = m.group(1) if m else None
        if qual == "~":
            s.add("email.spf.softfail", fqdn, mail_asset,
                  f"SPF on {fqdn} ends in ~all (softfail)", "low",
                  "Unauthorized senders are marked rather than rejected. Move to "
                  "-all once the authorized sender list is confirmed against "
                  "DMARC aggregate reports.", value="~all", evidence=ev)
        elif qual in ("?", "+"):
            s.add("email.spf.permissive", fqdn, mail_asset,
                  f"SPF on {fqdn} ends in {qual}all", "material",
                  f"{qual}all instructs receivers to accept mail from any source, "
                  "which is worse than publishing no SPF record at all.",
                  value=f"{qual}all", evidence=ev)
        elif qual is None:
            s.add("email.spf.no-all", fqdn, mail_asset,
                  f"SPF on {fqdn} has no terminating all mechanism", "low",
                  "Without a trailing all, receivers apply a neutral default to "
                  "unmatched senders.", value="no all", evidence=ev)

        lookups = len(re.findall(r"\b(?:include|a|mx|ptr|exists|redirect)[:=]", spf))
        if lookups > 10:
            s.add("email.spf.lookup-limit", fqdn, mail_asset,
                  f"SPF on {fqdn} needs {lookups} DNS lookups (limit is 10)",
                  "material",
                  "Exceeding ten mechanisms causes a permerror, and many "
                  "receivers treat permerror as no SPF at all — so the record "
                  "silently stops working.", value=f"{lookups} lookups",
                  evidence=ev,
                  refs=[{"label": "RFC 7208 §4.6.4",
                         "url": "https://www.rfc-editor.org/rfc/rfc7208#section-4.6.4"}])
        s.facts.setdefault("spf", {})[fqdn] = spf

    # ---- DKIM (selector probe) ----
    s.ran("email.dkim", fqdn)
    found = []
    for sel in DKIM_SELECTORS:
        _, vals = s.dig(f"{sel}._domainkey.{fqdn}", "TXT")
        _, cn = s.dig(f"{sel}._domainkey.{fqdn}", "CNAME")
        if vals or cn:
            found.append(sel)
    if has_mail and not found:
        s.add("email.dkim.none-found", fqdn, mail_asset,
              f"No DKIM selector found on {fqdn}", "low",
              "Probed " + str(len(DKIM_SELECTORS)) + " common selector names and "
              "found none. DKIM may still exist under a private selector name, so "
              "confirm in the mail platform before treating this as absent — "
              "DMARC alignment needs at least one working selector.",
              value="none of " + str(len(DKIM_SELECTORS)) + " probed",
              evidence=[{"cmd": f"for s in {' '.join(DKIM_SELECTORS[:6])}; do "
                                f"dig +short $s._domainkey.{fqdn} TXT; done",
                         "out": "(no selector responded)"}])
    else:
        s.facts.setdefault("dkim", {})[fqdn] = found

    # ---- MTA-STS / TLSRPT / BIMI ----
    for sub, check, label, sev, why in [
        (f"_mta-sts.{fqdn}", "email.mtasts.missing", "MTA-STS", "low",
         "Without MTA-STS a sending server will fall back to cleartext if a "
         "downgrade is forced, because STARTTLS is opportunistic by default."),
        (f"_smtp._tls.{fqdn}", "email.tlsrpt.missing", "TLSRPT", "informational",
         "No reporting address for TLS negotiation failures, so a downgrade "
         "attack against inbound mail would leave no trace."),
        (f"default._bimi.{fqdn}", "email.bimi.missing", "BIMI", "informational",
         "BIMI is brand display in supporting mail clients and requires a "
         "Verified Mark Certificate. It is not a security control and should "
         "not be rated as one."),
    ]:
        _, vals = s.dig(sub, "TXT")
        s.ran(check, fqdn)
        if not vals and has_mail:
            s.add(check, fqdn, mail_asset, f"{label} not published for {fqdn}",
                  sev, why, value="absent",
                  evidence=[{"cmd": f"dig +short {sub} TXT",
                             "out": f"(empty — no {label} record)"}])


def check_tls(s, dom):
    """Certificate state, protocol support, and the testssl.sh escalation."""
    fqdn = dom["fqdn"]
    s.ran("tls.cert", fqdn, covers=COVERS_TLS_CERT)

    cmd = (f"echo | openssl s_client -connect {fqdn}:443 -servername {fqdn} 2>/dev/null "
           f"| openssl x509 -noout -subject -issuer -dates -ext subjectAltName")
    rc, out, _ = sh(cmd, timeout=30)
    if rc != 0 or not out:
        s.ran("tls.cert", fqdn, "error", "TLS handshake produced no certificate",
              covers=COVERS_TLS_CERT)
        s.add("tls.handshake.failed", fqdn, "web",
              f"Could not complete a TLS handshake with {fqdn}", "material",
              "openssl s_client returned no certificate. Confirm by hand before "
              "acting — a handshake failure from one vantage point is not proof "
              "the service is down.", value="no certificate",
              evidence=[{"cmd": cmd, "out": "(no output)"}])
        return

    s.facts.setdefault("cert", {})[fqdn] = out
    subj = re.search(r"subject=.*?CN\s*=\s*([^\s,/]+)", out)
    cn = subj.group(1) if subj else ""
    sans = re.findall(r"DNS:([^\s,]+)", out)
    if cn and fqdn not in (cn, cn.lstrip("*.")) and fqdn in sans:
        s.add("tls.cert.cn-mismatch", fqdn, "web",
              f"Certificate common name is {cn}, not {fqdn}", "informational",
              f"Validity for this host comes from the SAN list rather than the "
              f"CN. Harmless, but it costs the next reviewer time and is the kind "
              f"of detail a scanner may misreport.", value=f"CN={cn}",
              evidence=[{"cmd": cmd, "out": out}], once_key=cn)

    exp = re.search(r"notAfter=(.+)", out)
    if exp:
        try:
            when = datetime.strptime(exp.group(1).strip(), "%b %d %H:%M:%S %Y %Z")
            days = (when.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)).days
            s.facts.setdefault("cert_days", {})[fqdn] = days
            if days < 0:
                s.add("tls.cert.expired", fqdn, "web",
                      f"Certificate for {fqdn} expired {abs(days)} days ago",
                      "material", "Browsers will refuse the connection.",
                      value=f"{days}d", evidence=[{"cmd": cmd, "out": out}])
            elif days < 14:
                s.add("tls.cert.expiry-near", fqdn, "web",
                      f"Certificate for {fqdn} expires in {days} days", "low",
                      "Confirm automated renewal is working.", value=f"{days}d",
                      evidence=[{"cmd": cmd, "out": out}])
        except ValueError:
            pass

    # New domains surfaced by the SAN list. Decision 10: these should announce
    # themselves rather than wait for someone to think of adding a profile.
    known = {d["fqdn"] for d in s.cfg["domains"]}
    known |= {"www." + d for d in known}
    extra = sorted({x.lstrip("*.") for x in sans} - known)
    extra = [x for x in extra if not any(x.endswith("." + k) for k in known)]
    if extra:
        s.add("infra.related-domain.unprofiled", fqdn, "dns",
              f"Certificate names {len(extra)} domain(s) absent from the profile",
              "informational",
              "These appear in the certificate SAN list but are not in this "
              "target's domain set, so their DNS and email authentication were "
              "not checked: " + ", ".join(extra) + ". Add them to the profile if "
              "they belong to the organization — an unscanned sibling domain is "
              "exactly how a missing DMARC record stays hidden.",
              value=", ".join(extra),
              evidence=[{"cmd": cmd, "out": "SANs: " + ", ".join(sans)}])

    # Protocol negotiation with the local OpenSSL.
    s.ran("tls.protocol.modern", fqdn, covers=["tls.tls13"])
    proto = {}
    for flag, name in [("-tls1_2", "TLS 1.2"), ("-tls1_3", "TLS 1.3")]:
        rc, out2, _ = sh(f"echo | openssl s_client -connect {fqdn}:443 "
                         f"-servername {fqdn} {flag} 2>/dev/null | grep -E 'Protocol|Cipher'",
                         timeout=25)
        proto[name] = out2 or "not negotiated"
    s.facts.setdefault("protocols", {})[fqdn] = proto
    if "not negotiated" in proto["TLS 1.3"]:
        s.add("tls.tls13.absent", fqdn, "web",
              f"{fqdn} does not negotiate TLS 1.3", "informational",
              "TLS 1.2 remains acceptable; 1.3 is faster and drops legacy "
              "primitives. On shared hosting this is the provider's decision.",
              value="1.3 unavailable",
              evidence=[{"cmd": f"openssl s_client -connect {fqdn}:443 -tls1_3",
                         "out": proto["TLS 1.3"]}])

    # Legacy protocols: local OpenSSL cannot test these, so escalate to
    # testssl.sh in Docker or record an explicit unverified state.
    legacy_check = "tls.protocol.legacy-enabled"
    if s.args.no_docker or not shutil.which("docker"):
        s.ran(legacy_check, fqdn, "unverified",
              "docker unavailable; local OpenSSL has TLS 1.0/1.1 compiled out", covers=COVERS_TLS_LEGACY)
        s.add("tls.legacy.unverified", fqdn, "web",
              f"TLS 1.0/1.1 support on {fqdn} was not tested", "informational",
              "The local OpenSSL build has both protocols compiled out, so a "
              "negotiation attempt fails client-side and proves nothing about "
              "the server. This is an unrun check, not a clean result. Install "
              "or start Docker so testssl.sh can run, or confirm with an "
              "independent scanner such as Qualys SSL Labs.",
              value="[UNVERIFIED — no testssl.sh available]",
              evidence=[{"cmd": "openssl version; docker info",
                         "out": "OpenSSL has no -tls1/-tls1_1 support in this build\n"
                                "docker: unavailable"}], once_key="toolchain")
        return

    rc, _, _ = sh("docker info", timeout=25)
    if rc != 0:
        s.ran(legacy_check, fqdn, "unverified", "docker daemon not running", covers=COVERS_TLS_LEGACY)
        s.add("tls.legacy.unverified", fqdn, "web",
              f"TLS 1.0/1.1 support on {fqdn} was not tested", "informational",
              "Docker is installed but its daemon is not running, so testssl.sh "
              "could not execute. Treat this as an unrun check rather than a "
              "pass, start Docker, and re-run.",
              value="[UNVERIFIED — docker daemon down]",
              evidence=[{"cmd": "docker info", "out": "Cannot connect to the Docker daemon"}],
              once_key="toolchain")
        return

    tcmd = (f"docker run --rm drwetter/testssl.sh --quiet --color 0 "
            f"-p -U --severity HIGH {fqdn}")
    rc, out, err = sh(tcmd, timeout=600)
    if rc != 0 and not out:
        s.ran(legacy_check, fqdn, "error", f"testssl.sh failed: {err[:180]}", covers=COVERS_TLS_LEGACY)
        s.add("tls.legacy.unverified", fqdn, "web",
              f"TLS 1.0/1.1 support on {fqdn} was not tested", "informational",
              "testssl.sh was available but did not complete. Unrun, not clean. "
              f"Error: {err[:180]}", value="[UNVERIFIED — testssl.sh error]",
              evidence=[{"cmd": tcmd, "out": (err or "(no output)")[:600]}],
              once_key="toolchain")
        return

    s.ran(legacy_check, fqdn, covers=COVERS_TLS_LEGACY)
    s.facts.setdefault("testssl", {})[fqdn] = out[:6000]

    # Labels must match testssl's actual output, which prints "TLS 1" and
    # "TLS 1.1" with a space. A pattern that never matches yields no finding,
    # which is indistinguishable from a clean result — the exact failure this
    # skill exists to prevent, so verify against real output when editing these.
    for label, cid, sev in [(r"SSLv2", "sslv2", "material"),
                            (r"SSLv3", "sslv3", "material"),
                            (r"TLS 1", "tls1", "low"),
                            (r"TLS 1\.1", "tls1_1", "low")]:
        m = re.search(rf"^\s*{label}\s{{2,}}(.+)$", out, re.M)
        if not m:
            continue
        verdict = m.group(1).strip()
        if "not offered" in verdict.lower() or "offered" not in verdict.lower():
            continue
        s.add(f"tls.protocol.{cid}-offered", fqdn, "web",
              f"{fqdn} still offers {label.replace(chr(92), '')}", sev,
              "A deprecated protocol being offered lets a client be negotiated "
              "down to obsolete cryptography. On shared hosting the protocol set "
              "is the provider's configuration, so confirm who can change it "
              "before assigning the remediation.", value="offered",
              evidence=[{"cmd": tcmd, "out": m.group(0).strip()}])

    # testssl also names CVE-identified weaknesses. Capturing them is the whole
    # point of running it — and each arrives with its own advisory ID, which is
    # what a vulnerability claim needs in order to be a finding rather than a guess.
    for line in out.splitlines():
        if not re.search(r"\bVULNERABLE\b|potentially NOT ok", line):
            continue
        cves = re.findall(r"CVE-\d{4}-\d{4,7}", line)
        name = re.split(r"\s*\(CVE|\s{2,}", line.strip())[0].strip(" ,")
        if not name:
            continue
        potential = "potentially" in line.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40]
        s.add(f"tls.vuln.{slug}", fqdn, "web",
              f"{name} on {fqdn}"
              + (f" ({', '.join(cves)})" if cves else ""),
              "informational" if potential else "low",
              (("testssl.sh reports this as potentially vulnerable, which means "
                "the precondition is present but exploitability depends on the "
                "content served. ") if potential else
               "testssl.sh reports this as vulnerable. ")
              + "This is a cipher-suite or TLS-configuration weakness; on shared "
                "hosting it is the provider's configuration and is closed by them "
                "or by migrating. "
              + (f"Advisories: {', '.join(cves)}." if cves else
                 "No CVE was named on this line — treat the label as a "
                 "configuration observation, not a vulnerability claim, until an "
                 "advisory is identified."),
              value=("potentially vulnerable" if potential else "vulnerable"),
              evidence=[{"cmd": tcmd, "out": line.strip()}],
              refs=[{"label": c, "url": f"https://nvd.nist.gov/vuln/detail/{c}"}
                    for c in cves])


def check_http(s, dom):
    """Headers, redirect behaviour, WAF fingerprint, availability, banners."""
    fqdn = dom["fqdn"]
    base = f"https://{fqdn}/"

    # WAF fingerprint FIRST, so nothing downstream misreads a block as an outage.
    s.ran("infra.waf", fqdn)
    cmd_noua, _, out_noua = s.curl(base, ua=None)
    code_noua = re.search(r"HTTP/[\d.]+ (\d{3})", out_noua)
    cmd_ua, _, out_ua = s.curl(base)
    code_ua = re.search(r"HTTP/[\d.]+ (\d{3})", out_ua)
    waf = bool(code_noua and code_ua and code_noua.group(1) != code_ua.group(1))
    s.facts["waf_blocks_no_ua"] = waf
    if waf:
        s.add("infra.waf.ua-filter", fqdn, "web",
              f"{fqdn} returns HTTP {code_noua.group(1)} to requests without a "
              f"User-Agent, {code_ua.group(1)} to a browser", "informational",
              "A WAF rule is rejecting atypical clients. This is not a defect, "
              "but it is the single most common cause of false 'site down' and "
              "'TLS unavailable' findings in automated assessments — a scanner "
              "records its own rejection as a service fault. Any availability "
              "claim about this host must be re-tested with a browser "
              "User-Agent before it is believed.",
              value=f"{code_noua.group(1)} vs {code_ua.group(1)}",
              evidence=[{"cmd": cmd_noua, "out": out_noua[:400]},
                        {"cmd": cmd_ua, "out": out_ua[:400]}],
              # Keyed on the rejection code alone: the same WAF fronting several
              # vhosts is one fact, and the allowed-response code differs per
              # host (200 on the primary, 301 on a redirect) without changing it.
              once_key=code_noua.group(1))

    if not out_ua:
        s.ran("http.headers", fqdn, "error", "no response with browser UA",
              covers=COVERS_HEADERS_FULL)
        return

    headers = {}
    for line in out_ua.splitlines():
        if ":" in line and not line.startswith("HTTP/"):
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    s.facts.setdefault("headers", {})[fqdn] = headers

    # A host that only redirects never renders a document, so CSP, X-Frame-Options,
    # X-Content-Type-Options, Referrer-Policy and Permissions-Policy have nothing
    # to act on there. HSTS still matters — it is what stops that hostname being
    # downgraded before the redirect is ever followed.
    serves_content = "web-primary" in dom.get("roles", []) or not dom.get("roles")
    applicable = SECURITY_HEADERS if serves_content else {
        "strict-transport-security": SECURITY_HEADERS["strict-transport-security"]}
    s.ran("http.headers", fqdn,
          reason="" if serves_content else
                 "redirect-only host: only HSTS is applicable",
          covers=COVERS_HEADERS_FULL if serves_content else COVERS_HEADERS_REDIRECT)

    missing = []
    for hdr, (check, label) in applicable.items():
        if hdr in headers:
            continue
        if hdr == "x-frame-options" and "frame-ancestors" in headers.get("content-security-policy", ""):
            continue
        missing.append(label)
        s.add(check, fqdn, "web", f"{label} header absent on {fqdn}", "low",
              f"Not present on the response. Add it on the vhost or in "
              f".htaccess — these are a single configuration block, and their "
              f"absence is the most visible criticism any external scanner can "
              f"make of a public site."
              + (" Start Content-Security-Policy in report-only mode on a "
                 "page-builder site: a strict policy will break inline styles "
                 "and third-party fonts until it is tuned."
                 if hdr == "content-security-policy" else ""),
              value="absent",
              evidence=[{"cmd": cmd_ua,
                         "out": out_ua[:500] + f"\n\n# absent: {hdr}"}])
    s.facts.setdefault("missing_headers", {})[fqdn] = missing

    if "strict-transport-security" in headers:
        m = re.search(r"max-age=(\d+)", headers["strict-transport-security"])
        if m and int(m.group(1)) < 15552000:
            s.add("http.hsts.short", fqdn, "web",
                  f"HSTS max-age on {fqdn} is {m.group(1)}s", "low",
                  "Below the 180-day floor that preload requires and that makes "
                  "the protection durable across infrequent visits.",
                  value=f"max-age={m.group(1)}",
                  evidence=[{"cmd": cmd_ua, "out": headers["strict-transport-security"]}])

    for hdr, check in [("server", "http.banner.server"), ("x-powered-by", "http.banner.powered-by")]:
        v = headers.get(hdr, "")
        if re.search(r"\d+\.\d+", v):
            s.add(check, fqdn, "web",
                  f"{hdr} header on {fqdn} discloses a version: {v}",
                  "informational",
                  "Version disclosure does not create a vulnerability but it "
                  "removes the attacker's need to fingerprint. Suppress it if "
                  "the platform allows.", value=v,
                  evidence=[{"cmd": cmd_ua, "out": f"{hdr}: {v}"}])

    # HTTP -> HTTPS
    s.ran("http.redirect", fqdn)
    r = s.head_status(f"http://{fqdn}/")
    if r:
        if r["code"].startswith("2"):
            s.add("http.redirect.missing", fqdn, "web",
                  f"Plain HTTP on {fqdn} serves content instead of redirecting",
                  "low", "A cleartext response means a first-contact visitor can "
                  "be served over HTTP indefinitely.", value=f"HTTP {r['code']}",
                  evidence=[{"cmd": r["cmd"], "out": f"{r['code']} (no redirect)"}])
        elif r["code"].startswith("3"):
            s.facts.setdefault("http_redirect", {})[fqdn] = r["redirect"]

    # Availability + timing. Multi-sample, browser UA, so a WAF block or a single
    # transient cannot masquerade as a standing outage.
    s.ran("http.availability", fqdn, covers=["http.availability", "http.perf"])
    samples = []
    for _ in range(int(s.args.samples)):
        st = s.head_status(base)
        if st:
            samples.append(st)
    if samples:
        codes = [x["code"] for x in samples]
        times = [x["time"] for x in samples]
        s.facts.setdefault("availability", {})[fqdn] = {"codes": codes, "times": times}
        bad = [c for c in codes if not c.startswith(("2", "3"))]
        ev = [{"cmd": samples[0]["cmd"],
               "out": "\n".join(f"try{i+1}: {x['code']}  {x['time']:.3f}s"
                                for i, x in enumerate(samples))}]
        if bad:
            s.add("http.availability.errors", fqdn, "web",
                  f"{len(bad)} of {len(codes)} requests to {fqdn} failed", "material",
                  f"Codes observed: {', '.join(codes)}. All requests used a "
                  "browser User-Agent, so this is not the WAF filter."
                  + (" Note that this host does filter atypical User-Agents, so "
                     "compare against that behaviour before escalating." if waf else ""),
                  value=f"{len(bad)}/{len(codes)} failed", evidence=ev)
        avg = sum(times) / len(times)
        if avg > 1.5 and serves_content:
            s.add("http.perf.slow-ttfb", fqdn, "web",
                  f"{fqdn} averages {avg:.2f}s to complete", "informational",
                  "Slow for a static marketing page. This is a performance and "
                  "user-experience defect with a plausible bounce-rate cost, not "
                  "a security finding — recorded here because availability-"
                  "adjacent claims are often made without measuring it.",
                  value=f"{avg:.2f}s", evidence=ev)


def check_cms_and_paths(s, dom):
    """CMS fingerprint plus the fixed sensitive-path list, soft-404 aware."""
    fqdn = dom["fqdn"]
    if dom.get("roles") and "web-primary" not in dom["roles"]:
        s.ran("cms.fingerprint", fqdn, "skipped", "not the primary web host",
                  covers=["cms.version"])
        return
    base = f"https://{fqdn}/"

    _, _, body = s.curl(base, method="GET", timeout=30)
    s.ran("cms.fingerprint", fqdn, covers=["cms.version"])
    gens = re.findall(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)', body, re.I)
    s.facts.setdefault("generators", {})[fqdn] = gens
    for g in gens:
        s.add("cms.version.disclosed", fqdn, "web",
              f"Page source advertises {g}", "low",
              f"A generator meta tag names the exact software version to any "
              f"visitor, removing the need to fingerprint it. Remove the tag. "
              f"Note this is a disclosure finding — it is not evidence that the "
              f"software is unpatched, and asserting a vulnerability from a "
              f"version string without a specific advisory is not a finding.",
              value=g, evidence=[{"cmd": f"curl -sS -A '<browser UA>' {base} | "
                                         f"grep -i 'name=\"generator\"'",
                                  "out": f'<meta name="generator" content="{g}" />'}])

    if s.args.skip_paths:
        s.ran("exposure.path", fqdn, "skipped", "--skip-paths", covers=COVERS_PATHS)
        return

    # Soft-404 fingerprint: WordPress commonly answers 200 for missing paths, so
    # a bare status code would produce a page of false positives.
    probe = "zz-" + hashlib.sha1(fqdn.encode()).hexdigest()[:12] + "-nonexistent"
    ref = s.head_status(base + probe)
    soft404 = None
    if ref and ref["code"] == "200":
        soft404 = ref["size"]
        s.facts["soft_404_size"] = soft404

    s.ran("exposure.path", fqdn, covers=COVERS_PATHS)
    hits = []
    for path in SENSITIVE_PATHS:
        st = s.head_status(base + path)
        if not st:
            continue
        code, size = st["code"], st["size"]
        real = code == "200" and not (soft404 is not None and abs(size - soft404) < 512)
        if not real:
            continue
        hits.append({"path": path, "code": code, "size": size})

        if path in PATHS_REPORTED_ELSEWHERE:
            continue
        sev = "material" if any(k in path for k in (
            ".git", ".env", "wp-config", ".sql", "credentials", "id_rsa",
            ".htpasswd", "adminer", ".npmrc", ".netrc")) else "low"
        s.add(f"exposure.path.{path.strip('/').replace('/', '-')}", fqdn, "web",
              f"Publicly readable: /{path}", sev,
              "Returned HTTP 200 with content distinct from the site's 404 page. "
              + ("Files of this kind commonly contain credentials or database "
                 "connection details. Retrieve it, confirm what it exposes, "
                 "remove it, and rotate anything it revealed."
                 if sev == "material" else
                 "Confirm whether the content is sensitive and remove it if not "
                 "needed."), value=f"HTTP {code}, {size} bytes",
              evidence=[{"cmd": f"curl -sSI -A '<browser UA>' {base}{path}",
                         "out": f"HTTP/2 {code}\ncontent-length: {size}\n\n"
                                f"# soft-404 baseline for this site: "
                                f"{soft404 if soft404 is not None else 'returns 404 correctly'}"}])

    s.facts.setdefault("path_hits", {})[fqdn] = hits
    found_paths = {h["path"] for h in hits}

    if "wp-json/wp/v2/users" in found_paths:
        s.add("cms.rest-users.exposed", fqdn, "web",
              "WordPress REST API lists user accounts without authentication",
              "low", "/wp-json/wp/v2/users returns 200, disclosing usernames and "
              "author slugs. Combined with a reachable login form this supplies "
              "the username half of a credential-stuffing attempt. Restrict the "
              "endpoint or require authentication.", value="HTTP 200",
              evidence=[{"cmd": f"curl -sSI -A '<browser UA>' {base}wp-json/wp/v2/users",
                         "out": "HTTP/2 200"}])

    if "wp-login.php" in found_paths:
        s.add("cms.login.exposed", fqdn, "web",
              "wp-login.php is reachable from the public internet", "low",
              "A standard credential-stuffing target. Rate limiting cannot be "
              "confirmed from outside without submitting credentials, which this "
              "scan does not do — verify in the admin console that a limiting "
              "plugin, IP restriction or CAPTCHA is active.",
              value="HTTP 200",
              evidence=[{"cmd": f"curl -sSI -A '<browser UA>' {base}wp-login.php",
                         "out": "HTTP/2 200"}])

    if "xmlrpc.php" in found_paths:
        s.add("cms.xmlrpc.enabled", fqdn, "web",
              "xmlrpc.php responds", "low",
              "XML-RPC supports request batching, which historically enabled "
              "amplified password guessing and pingback-based reflection. Disable "
              "it unless a specific integration needs it.", value="reachable",
              evidence=[{"cmd": f"curl -sSI -A '<browser UA>' {base}xmlrpc.php",
                         "out": "HTTP/2 200"}])

    for d in ("wp-content/uploads/", "wp-content/plugins/", "wp-content/themes/", "wp-includes/"):
        if d in found_paths:
            s.add(f"exposure.dirlisting.{d.strip('/').replace('/', '-')}", fqdn, "web",
                  f"Directory listing enabled on /{d}", "low",
                  "An index of files discloses the installed plugin and theme "
                  "inventory, which turns version-specific advisories into a "
                  "targeting list. Add an index guard or disable Options "
                  "+Indexes.", value="listing enabled",
                  evidence=[{"cmd": f"curl -sSI -A '<browser UA>' {base}{d}",
                             "out": "HTTP/2 200 (index page)"}])

    if ".well-known/security.txt" not in found_paths:
        s.add("web.securitytxt.missing", fqdn, "web",
              "No /.well-known/security.txt", "informational",
              "A finder with something to report has no documented channel. One "
              "static file, and it is the cheapest way to keep an unsolicited "
              "report out of a sales inbox.", value="absent",
              evidence=[{"cmd": f"curl -sSI -A '<browser UA>' {base}.well-known/security.txt",
                         "out": "HTTP/2 404"}],
              refs=[{"label": "RFC 9116 — security.txt",
                     "url": "https://www.rfc-editor.org/rfc/rfc9116"}])


def check_ports(s):
    """TCP connect + banner read against the resolved IP. Landlord-aware."""
    pc = s.cfg.get("port_scan", {})
    if s.args.skip_ports or not pc.get("enabled"):
        s.ran("port", "-", "skipped", "--skip-ports or disabled in profile")
        return

    primary = next((d["fqdn"] for d in s.cfg["domains"]
                    if "web-primary" in d.get("roles", [])), s.cfg["domains"][0]["fqdn"])
    try:
        ip = socket.gethostbyname(primary)
    except OSError as e:
        s.ran("port", primary, "error", str(e))
        return

    rc, rdns, _ = sh(f"dig +short -x {ip}", timeout=15)
    s.facts["ip"] = ip
    s.facts["rdns"] = rdns
    landlord = s.cfg.get("landlord", {})
    provider_owned = bool(landlord.get("owns_ports"))

    s.ran("port", ip)
    open_ports, states = [], []
    for p in pc.get("ports", []):
        rc, _, _ = sh(f"nc -z -w 4 {ip} {p}", timeout=12, stdin_devnull=True)
        is_open = rc == 0
        states.append({"port": p, "state": "open" if is_open else "closed"})
        if is_open:
            open_ports.append(p)

    banners = {}
    for p in open_ports:
        if p in (80, 443):
            continue
        rc, out, _ = sh(f"nc -w 5 {ip} {p} < /dev/null | strings | head -4",
                        timeout=14, stdin_devnull=True)
        if out:
            banners[p] = out
    s.ports = [dict(x, banner=banners.get(x["port"], "")) for x in states]

    if open_ports:
        sev = "accepted" if provider_owned else "low"
        note = ""
        if provider_owned:
            note = (f" These are {landlord.get('provider', 'the hosting provider')}'s "
                    f"listening services on infrastructure shared with other "
                    f"tenants. There is no firewall, no root access and no way to "
                    f"close them from the tenant side: remediation is a migration "
                    f"decision, not a configuration change. Reverse DNS resolves "
                    f"to {rdns or 'the provider'}, which is the evidence for this.")
        s.add("port.inventory", ip, "landlord" if provider_owned else "web",
              f"{len(open_ports)} TCP ports reachable on {ip}", sev,
              f"Open: {', '.join(str(p) for p in open_ports)}.{note}",
              value=",".join(str(p) for p in open_ports),
              evidence=[{"cmd": f"for p in {' '.join(str(p) for p in pc['ports'])}; "
                                f"do nc -z -w 4 {ip} $p; done",
                         "out": "\n".join(f"port {x['port']} {x['state'].upper()}"
                                          for x in states)}]
                       + ([{"cmd": f"nc -w 5 {ip} {p} < /dev/null",
                            "out": banners[p]} for p in sorted(banners)][:4]))

    # A version banner is a disclosure fact, never a vulnerability claim.
    # Wire-protocol versions are not software versions: an "HTTP/1.1 301" status
    # line says nothing about what is serving it, and reporting it as a disclosed
    # version is a false positive that erodes trust in the whole list.
    PROTOCOL_NAMES = {"http", "https", "sip", "rtsp", "ftp", "smtp", "imap", "pop3"}
    for p, b in banners.items():
        m = re.search(r"([A-Za-z][\w\-]*)[/_ ]v?(\d+\.\d[\w.\-]*)", b)
        if m and m.group(1).lower() in PROTOCOL_NAMES:
            m = re.search(r"([A-Za-z][\w\-]{2,})[/_ ]v?(\d+\.\d[\w.\-]*)",
                          re.sub(r"\b(?:HTTP|RTSP|SIP)/\d[\d.]*", "", b, flags=re.I))
        if m and m.group(1).lower() not in PROTOCOL_NAMES:
            s.add(f"port.{p}.version-disclosed", ip,
                  "landlord" if provider_owned else "web",
                  f"Port {p} discloses {m.group(1)} {m.group(2)} in its banner",
                  "accepted" if provider_owned else "informational",
                  f"The service volunteers its version to any client that "
                  f"connects. A banner is not a patch level — distributions "
                  f"backport fixes while the advertised version stays fixed — so "
                  f"this does not establish that the software is vulnerable. "
                  f"Any vulnerability claim here needs a specific CVE plus "
                  f"evidence of exploitability against this host.",
                  value=f"{m.group(1)} {m.group(2)}",
                  evidence=[{"cmd": f"nc -w 5 {ip} {p} < /dev/null | strings | head -3",
                             "out": b}])


# ---------------------------------------------------------------------------
# Profile loading and delta
# ---------------------------------------------------------------------------

def load_profile(path):
    """Profile is Markdown for humans with one fenced ```json block for machines."""
    text = open(path, encoding="utf-8").read()
    m = re.search(r"```json\s*\n(.*?)\n```", text, re.S)
    if not m:
        sys.exit(f"error: no ```json config block found in {path}")
    try:
        cfg = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        sys.exit(f"error: config block in {path} is not valid JSON: {e}")
    for key in ("slug", "domains"):
        if key not in cfg:
            sys.exit(f"error: profile {path} is missing required key '{key}'")
    return cfg, text


def _covers(entry, finding_check):
    """True when this check execution is evidence about `finding_check`."""
    for c in entry.get("covers") or [entry.get("check", "")]:
        if finding_check == c or finding_check.startswith(c + "."):
            return True
    return False


def compute_delta(current, baseline):
    """
    Classify each finding against the previous scan.

    The load-bearing rule: FIXED requires that the check which would have found
    the issue actually completed this run. A check that was skipped, errored, or
    could not reach a verdict leaves its findings as 'not-retested' — because a
    scan that did not look is indistinguishable from a scan that found nothing,
    and only one of those is good news.
    """
    if not baseline:
        for f in current["findings"]:
            f["delta"] = "new"
            f["delta_note"] = "First scan — no baseline to compare against."
        return {"baseline": None, "fixed": [], "not_retested": []}

    old = {f["id"]: f for f in baseline.get("findings", [])}

    for f in current["findings"]:
        prev = old.get(f["id"])
        if not prev:
            f["delta"] = "new"
            f["delta_note"] = f"Not present in the {baseline['scan']['date']} scan."
            continue
        now_r = SEVERITY_RANK.get(f["severity"], 9)
        was_r = SEVERITY_RANK.get(prev.get("severity", ""), 9)
        if now_r < was_r:
            f["delta"] = "regressed"
            f["delta_note"] = (f"Severity worsened from {prev['severity']} to "
                               f"{f['severity']} since {baseline['scan']['date']}.")
        elif f.get("value") and prev.get("value") and f["value"] != prev["value"]:
            f["delta"] = "regressed" if now_r <= was_r else "unchanged"
            f["delta_note"] = (f"Observed value changed: was {prev['value']}, "
                               f"now {f['value']}.")
        else:
            f["delta"] = "unchanged"
            f["delta_note"] = f"Also present on {baseline['scan']['date']}."

    now_ids = {f["id"] for f in current["findings"]}
    fixed, not_retested = [], []
    for fid, prev in old.items():
        if fid in now_ids:
            continue
        retested = any(
            c["state"] == "ok" and c["scope"] == prev.get("scope", "")
            and _covers(c, prev.get("check", ""))
            for c in current.get("checks_run", []))
        entry = dict(prev, delta="fixed" if retested else "not-retested")
        if retested:
            entry["delta_note"] = (f"Present on {baseline['scan']['date']}, absent "
                                   f"now, and the check completed this run.")
            fixed.append(entry)
        else:
            entry["delta_note"] = (f"Present on {baseline['scan']['date']}. The "
                                   f"check did not complete this run, so this is "
                                   f"NOT confirmed fixed — it was not re-tested.")
            not_retested.append(entry)
    return {"baseline": baseline["scan"]["date"], "fixed": fixed,
            "not_retested": not_retested}


def find_baseline(outdir, current_name):
    if not os.path.isdir(outdir):
        return None
    cands = sorted(f for f in os.listdir(outdir)
                   if f.endswith(".json") and f != current_name)
    if not cands:
        return None
    try:
        with open(os.path.join(outdir, cands[-1]), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profile", required=True, help="path to target profile .md")
    ap.add_argument("--out", help="output JSON path (default: derived from profile)")
    ap.add_argument("--outdir", help="directory for reports (default from profile)")
    ap.add_argument("--no-docker", action="store_true", help="skip testssl.sh")
    ap.add_argument("--skip-ports", action="store_true")
    ap.add_argument("--skip-paths", action="store_true")
    ap.add_argument("--delay", type=float, default=0.4,
                    help="seconds between HTTP requests (default 0.4)")
    ap.add_argument("--samples", type=int, default=6,
                    help="availability samples per host (default 6)")
    ap.add_argument("--max-requests", type=int, default=400)
    args = ap.parse_args()

    cfg, profile_text = load_profile(args.profile)
    started = datetime.now(timezone.utc)
    s = Scan(args.profile, cfg, args)

    for dom in cfg["domains"]:
        print(f"[*] {dom['fqdn']} — DNS zone", file=sys.stderr)
        check_dns_zone(s, dom)
        print(f"[*] {dom['fqdn']} — email authentication", file=sys.stderr)
        check_email_auth(s, dom)
        print(f"[*] {dom['fqdn']} — TLS", file=sys.stderr)
        check_tls(s, dom)
        print(f"[*] {dom['fqdn']} — HTTP", file=sys.stderr)
        check_http(s, dom)
        print(f"[*] {dom['fqdn']} — CMS and exposed paths", file=sys.stderr)
        check_cms_and_paths(s, dom)
    print("[*] TCP ports", file=sys.stderr)
    check_ports(s)

    finished = datetime.now(timezone.utc)
    outdir = args.outdir or cfg.get("output_dir") or f"Outputs/website-scans/{cfg['slug']}"
    outdir = os.path.expanduser(outdir)
    name = args.out or f"{cfg['slug']}-{started:%Y%m%d}.json"
    name = os.path.basename(name)

    _, ov, _ = sh("openssl version", timeout=10)
    doc = {
        "schema": 1,
        "target": {"slug": cfg["slug"], "org": cfg.get("org", cfg["slug"]),
                   "domains": cfg["domains"]},
        "scan": {
            "date": f"{started:%Y-%m-%d}",
            "started_utc": started.isoformat(timespec="seconds"),
            "finished_utc": finished.isoformat(timespec="seconds"),
            "vantage": cfg.get("vantage", "single vantage point, commercial ISP"),
            "profile": os.path.abspath(args.profile),
            "tools": {"openssl": ov, "docker": bool(shutil.which("docker")) and not args.no_docker},
            "http_requests": s.http_calls,
            "boundary": "read-only on target vhosts; TCP connect and banner read "
                        "only on shared infrastructure; no authentication, "
                        "credentials, payloads or fuzzing",
        },
        "findings": sorted(s.findings,
                           key=lambda f: (SEVERITY_RANK.get(f["severity"], 9), f["id"])),
        "checks_run": s.checks,
        "ports": s.ports,
        "facts": s.facts,
        "narrative": {},
        "remediation": [],
    }

    baseline = find_baseline(outdir, name)
    doc["delta"] = compute_delta(doc, baseline)

    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2)

    counts = {}
    for f in doc["findings"]:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    unrun = [c for c in s.checks if c["state"] != "ok"]
    print(f"\n[+] {path}", file=sys.stderr)
    print(f"[+] {len(doc['findings'])} findings: "
          + ", ".join(f"{v} {k}" for k, v in sorted(
              counts.items(), key=lambda kv: SEVERITY_RANK.get(kv[0], 9))),
          file=sys.stderr)
    print(f"[+] {len(s.checks) - len(unrun)}/{len(s.checks)} checks completed; "
          f"{len(unrun)} did not", file=sys.stderr)
    if doc["delta"]["not_retested"]:
        print(f"[!] {len(doc['delta']['not_retested'])} prior finding(s) could not "
              f"be re-tested — NOT confirmed fixed", file=sys.stderr)
    print(json.dumps({"json": path, "findings": len(doc["findings"]),
                      "severity_counts": counts,
                      "checks_incomplete": len(unrun),
                      "baseline": doc["delta"]["baseline"]}))


if __name__ == "__main__":
    main()
