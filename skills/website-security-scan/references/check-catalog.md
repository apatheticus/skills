# Check catalog

Every check `scan.py` performs, its stable ID, and its default severity. Read this
when you need to know what a finding ID means, whether a gap in coverage is
deliberate, or how to add a check.

**Contents**
- [Why IDs are stable](#why-ids-are-stable)
- [Severity model](#severity-model)
- [dns.* — zone hygiene](#dns--zone-hygiene)
- [email.* — authentication](#email--authentication)
- [tls.* — transport](#tls--transport)
- [http.* — response and behaviour](#http--response-and-behaviour)
- [cms.* — content management](#cms--content-management)
- [exposure.* — readable files](#exposure--readable-files)
- [port.* — network reachability](#port--network-reachability)
- [infra.* — hosting context](#infra--hosting-context)
- [Deliberate coverage gaps](#deliberate-coverage-gaps)
- [Adding a check](#adding-a-check)

## Why IDs are stable

A finding's identity is `<check-id>@<scope>`, assigned by the catalog and never
derived from prose. "Missing CAA record" has to be recognisably the same finding
in October as in August or the delta is meaningless — every run would report
everything as new, and a real regression would be invisible in the noise.

Two consequences worth internalising:

- **Never reword a check ID to improve a report.** The ID is a database key. Change
  the title, the summary, the severity — those are all data. Changing the ID
  silently orphans every historical record of that finding.
- **A check that does not run emits no finding, and that is not the same as a pass.**
  Each check records its own state in `checks_run`. `compute_delta` refuses to call
  a prior finding FIXED unless the relevant check completed this run; otherwise it
  is reported as `not-retested`, which the report surfaces in its own warning
  block. A scan that did not look and a scan that found nothing produce identical
  silence, and only one of them is good news.

### `covers` — how a check vouches for a finding

A check's name and the finding IDs it emits frequently diverge: one `http.headers`
execution decides six `http.*.missing` findings. So `s.ran()` takes a `covers`
list of ID prefixes the execution is evidence about, defaulting to the check name
itself, matched exactly or as a dotted prefix. `compute_delta` uses it to decide
whether an absent finding was actually re-tested.

Get this wrong in the incomplete direction and findings are perpetually reported
as not-retested — annoying but safe. Get it wrong in the over-broad direction and
the report announces that problems were resolved when nothing looked for them,
which is the failure this whole design exists to prevent. `scripts/test_delta.py`
covers both directions; run it after touching a `COVERS_*` group.

### Changing the catalog creates phantom deltas

The first run after you add, remove, rename or split a check will report movement
that did not happen: a removed check's findings look resolved, a renamed one looks
like a brand-new problem. This is unavoidable — the ID is the identity — but it is
also invisible unless someone says so. When you change the catalog, note it in the
target profile's history and say plainly in that run's report that the movement is
a scanner change rather than a posture change. A silent phantom regression will be
chased by somebody.

## Severity model

Four levels. They describe **consequence against the specific asset**, not CVSS
and not a scanner's colour.

| Level | Meaning |
|---|---|
| `material` | Real business consequence if left open. Reserve it. On a data-free marketing site this is usually an email-authentication weakness, a leaked credential file, or the site genuinely being unreachable. |
| `low` | Worth fixing, usually cheap, but the consequence is bounded. Most header and DNS-record findings live here. The honest justification is often cost, not risk — say so. |
| `informational` | A fact worth recording that needs no action. Version disclosure, WAF behaviour, performance. |
| `accepted` | Nothing to remediate, because the fix is not the target owner's to make. Provider-owned infrastructure. Needs a documented risk acceptance, not an engineering ticket. |

A target profile may override any check's severity via `severity_overrides`
(fnmatch patterns against the check ID). Landlord-owned ports are forced to
`accepted` automatically when the profile declares `landlord.owns_ports`.

## dns.* — zone hygiene

| ID | Default | What it means |
|---|---|---|
| `dns.dnssec.missing` | informational | No DS at the parent and no DNSKEY in the zone. Addresses resolver cache poisoning, which major public resolvers already mitigate by other means — genuine hardening, rarely urgent. |
| `dns.caa.missing` | low | Any CA may issue for the domain and every hostname under it, including mail hostnames. One DNS record to fix. |
| `dns.caa.no-iodef` | informational | CAA published without a reporting address, so a CA that blocks a misissuance has nowhere to report it. |
| `dns.axfr.open` | material | A nameserver answered an unauthenticated zone transfer, disclosing the whole zone. Read-only to test, genuinely serious when true. |

Absence is only reported when **all three** public resolvers agree. A split result
is recorded rather than asserted, because one resolver's stale cache is not
evidence that a record does not exist.

## email.* — authentication

The highest-value family. These records live in the DNS zone, which means a
website's isolation gives them no protection whatsoever — and they are the only
findings whose weakness can be turned against a third party who trusts the
domain's name.

| ID | Default | What it means |
|---|---|---|
| `email.dmarc.missing` | material (if MX present) | No DMARC record at all. No alignment requirement, no published policy. An SPF `-all` does **not** substitute: SPF authenticates the envelope sender, not the `From:` header a person reads. |
| `email.dmarc.policy-weak` | material if `p=none`, low if `p=quarantine` | `p=none` monitors only. `p=quarantine` sends failing mail to spam, so a portion still lands. |
| `email.dmarc.subdomain-weak` | material if `sp=none`, else low | Only emitted when `sp` is explicitly published **and** weaker than `p`. An absent `sp` inherits `p` and is not a finding. |
| `email.dmarc.pct-partial` | low | `pct<100` samples the policy instead of enforcing it. |
| `email.dmarc.no-rua` | low | No aggregate reporting, so tightening the policy is a guess rather than a measured change. |
| `email.spf.missing` | material (if MX present) | No sender policy published. |
| `email.spf.softfail` | low | Terminates in `~all`. Unauthorized senders are marked, not rejected. |
| `email.spf.permissive` | material | Terminates in `?all` or `+all` — worse than publishing nothing. |
| `email.spf.no-all` | low | No terminating mechanism; receivers apply a neutral default. |
| `email.spf.lookup-limit` | material | More than ten DNS-lookup mechanisms causes a permerror, and many receivers treat permerror as no SPF — the record silently stops working. |
| `email.dkim.none-found` | low | None of ~17 common selector names responded. DKIM may exist under a private selector, so this is a prompt to confirm in the mail platform, not proof of absence. |
| `email.mtasts.missing` | low | STARTTLS is opportunistic by default; without MTA-STS a sender falls back to cleartext under a forced downgrade. |
| `email.tlsrpt.missing` | informational | No reporting address for TLS negotiation failures. |
| `email.bimi.missing` | informational | **Not a security control.** Brand display in supporting clients, requires a Verified Mark Certificate. Recorded so that a report which rates it as critical can be contradicted with evidence. |

## tls.* — transport

| ID | Default | What it means |
|---|---|---|
| `tls.handshake.failed` | material | No certificate returned. Confirm by hand — a failure from one vantage point is not proof the service is down. |
| `tls.cert.expired` | material | Browsers will refuse the connection. |
| `tls.cert.expiry-near` | low | Under 14 days. Confirm renewal automation works. |
| `tls.cert.cn-mismatch` | informational | CN names a different host; validity comes from the SAN list. Cosmetic, but it costs the next reviewer time. Deduplicated per certificate. |
| `tls.tls13.absent` | informational | 1.2 remains acceptable. On shared hosting this is the provider's decision. |
| `tls.protocol.tls1-offered`, `tls.protocol.tls1_1-offered` | low | Deprecated protocols still offered. Requires testssl.sh. |
| `tls.protocol.sslv3-offered`, `tls.protocol.sslv2-offered` | material | Obsolete and broken. Requires testssl.sh. |
| `tls.legacy.unverified` | informational | **The check did not run.** Emitted when Docker is unavailable, its daemon is down, or testssl.sh errored. Carries an explicit `[UNVERIFIED — reason]` value so it cannot be mistaken for a pass. Deduplicated to once per run, because it is a limitation of the scanning host rather than a property of the target. |
| `infra.related-domain.unprofiled` | informational | The certificate names domains that are not in the target profile, so their DNS and email authentication were **not checked**. Scoping to one hostname is how a sibling domain's missing DMARC stays hidden. |

Legacy protocols cannot be tested with a modern local OpenSSL — the protocols are
compiled out, so the handshake fails client-side and proves nothing about the
server. That is why the escalation to testssl.sh exists, and why its absence
produces a finding rather than silence.

## http.* — response and behaviour

| ID | Default | What it means |
|---|---|---|
| `http.hsts.missing` | low | Checked on every hostname, including redirect-only ones — HSTS is what stops that hostname being downgraded before the redirect is followed. |
| `http.hsts.short` | low | `max-age` below 180 days. |
| `http.csp.missing`, `http.xfo.missing`, `http.xcto.missing`, `http.referrer-policy.missing`, `http.permissions-policy.missing` | low | Checked only on hosts that serve content. A redirect-only host never renders a document, so these have nothing to act on there. `X-Frame-Options` is skipped when CSP already sets `frame-ancestors`. |
| `http.redirect.missing` | low | Plain HTTP serves content rather than redirecting. |
| `http.banner.server`, `http.banner.powered-by` | informational | A version in a response header. Disclosure, not vulnerability. |
| `http.availability.errors` | material | Non-2xx/3xx across multiple samples, all sent **with** a browser User-Agent. |
| `http.perf.slow-ttfb` | informational | Mean completion over 1.5s on a content-serving host. A performance defect with a plausible bounce-rate cost — reported plainly as that, never dressed as security. |

## cms.* — content management

| ID | Default | What it means |
|---|---|---|
| `cms.version.disclosed` | low | A generator meta tag naming exact software versions. A **disclosure** finding. It is not evidence the software is unpatched. |
| `cms.rest-users.exposed` | low | `/wp-json/wp/v2/users` returns 200, disclosing usernames. Supplies the username half of credential stuffing. |
| `cms.login.exposed` | low | The login form is publicly reachable. Rate limiting cannot be confirmed from outside without submitting credentials, which this scan does not do — verify in the platform console. |
| `cms.xmlrpc.enabled` | low | XML-RPC supports request batching, historically enabling amplified password guessing and pingback reflection. |

## exposure.* — readable files

`exposure.path.<slug>` — one per path found readable, from a fixed ~60-entry list.
`material` for `.git`, `.env`, `wp-config` leftovers, `.sql` dumps, `id_rsa`,
`.htpasswd`, `.npmrc`, `.netrc` and `adminer`; `low` otherwise.

`exposure.dirlisting.<slug>` (low) — a directory index discloses the installed
plugin and theme inventory, turning version-specific advisories into a targeting
list.

`web.securitytxt.missing` (informational) — no `/.well-known/security.txt`, so a
finder with something to report has no documented channel.

**Log files must be read before they are rated.** `error_log`, `wp-content/debug.log`
and friends default to `low`, because their contents decide everything and the
scanner cannot judge them. A log holding one repeated deprecation notice is
housekeeping; a log holding stack traces with query fragments, absolute paths or
connection strings is a credential disclosure. Retrieve it during the exploratory
pass, see what is actually in it, and set the severity from that. Do not let the
default stand unexamined in either direction.

**Soft-404 handling.** Many CMSes answer 200 for missing paths, so a bare status
code would produce a page of false positives. The scanner first requests a
random path to fingerprint the site's not-found response, then treats a 200 as
real only when the body size diverges from that baseline by more than 512 bytes.
If a target ever produces obvious false positives here, that threshold is the
thing to look at first.

## port.* — network reachability

`port.inventory` — one finding listing every reachable port, not one per port. On
a shared host the individual ports are not independently actionable, and 12
separate findings would drown the list.

`port.<n>.version-disclosed` — a version string in a service banner.

Both are forced to `accepted` when the profile declares `landlord.owns_ports`,
with wording that names who owns the fix. The accurate framing is never "the
target exposed MySQL" but "the target's site is a tenant on a host that exposes
MySQL to its tenants" — the remedy is a migration decision, not a firewall rule.

**A banner is not a patch level.** Distributions backport security fixes while the
advertised version never moves; an OpenSSH 8.0 banner on a RHEL-family host does
not mean OpenSSH 8.0's unpatched behaviour. No `port.*` finding asserts
exploitability, and none should be edited to.

## infra.* — hosting context

`infra.waf.ua-filter` (informational) — the host returns a different status to a
request with no User-Agent than to a browser.

This one earns its place. A WAF that rejects atypical clients is not a defect, but
it is the single most common cause of false "site down" and "TLS unavailable"
findings in automated assessments: the scanner records its own rejection as a
service fault. Recording the behaviour explicitly means any availability claim
about the host can be checked against it. Deduplicated on the rejection code, so
one WAF fronting several vhosts is one finding.

## Deliberate coverage gaps

Not oversights. Each is out of scope by decision, and each is stated in the
report's methodology so a reader knows it was not tested.

| Gap | Why |
|---|---|
| Login rate limiting | Cannot be confirmed externally without submitting credentials. |
| Plugin and theme inventory | Needs the admin console, or enumeration that would probe paths far beyond a fixed list. |
| Authenticated application testing | Requires credentials. |
| Injection, XSS, traversal, upload testing | Requires sending payloads. Outside the read-only boundary. |
| Service versions behind provider banners | Patch state is not externally observable and cannot be inferred from a version string. |
| Other tenants on a shared IP | Not the target owner's to authorize, and probing them would reach third-party systems. |
| Mail flow in transit | Requires access to the mail platform. |

## Adding a check

1. Pick an ID in an existing family. Lowercase, dot-separated, describing the
   condition rather than the remedy — `email.dmarc.missing`, not
   `email.add-dmarc`.
2. Call `s.ran(check, scope)` **whether or not** it produces a finding. This is
   what lets `compute_delta` distinguish resolved from not-tested. Pass
   `state="unverified"` or `"error"` with a reason when it could not conclude.
3. Call `s.add(...)` only on a genuine finding, with at least one evidence entry
   whose `cmd` is a command a reader can paste into a shell and re-run.
4. Set a default severity that reflects consequence, and let target profiles
   override it. If a check is only ever material for one target, that belongs in
   that profile's `severity_overrides`, not in the default.
5. Use `once_key` for facts about shared infrastructure — one certificate, one
   WAF, one toolchain limitation — so they report once instead of once per domain.
6. Add a row to the relevant table above. An undocumented check is one nobody can
   interpret six months later.

### Promoting an exploratory finding

The model's exploratory pass exists because a fixed catalog can only find what it
already names. When the same exploratory finding appears in two consecutive runs
of the same target, add it to the catalog: it has stopped being a discovery and
become a condition worth tracking, and only a catalogued check gets a stable ID
and therefore a delta. Note the promotion in the target profile's history.
