<div align="center">

# Website security scan

**A cursory, read-only look at what a website and its email domains expose to the public internet — and an HTML report that says what moved since last time.**

<!-- pd:badges start -->
[![Python 3](https://img.shields.io/badge/Python-3-4A4AE8)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-12142B.svg)](LICENSE)
[![Checks](https://img.shields.io/badge/Checks-catalog-4C5273)](references/check-catalog.md)
[![Skill](https://img.shields.io/badge/Skill-SKILL.md-4C5273)](SKILL.md)
<!-- pd:badges end -->

<!-- pd:viz name="run-pipeline" src=".prettydocs/src/run-pipeline/" facts-hash="d146afaeba00d3b86fa0f21b18ee846b25f9848acf1520fc2bf1d3d8447d324c" src-hash="5e798d8a0e345b73c7e6837526b78c46f3c8be25c637a46c794f0463877ab004" -->
<div align="center">
<img src="docs/assets/run-pipeline.svg" alt="A run in four stages. A target profile under assets/targets supplies the domains and the scope statement; scan.py runs the check catalog and writes findings, per-check execution state and evidence to JSON; a narrative and an exploratory pass add judgment to that JSON; render_report.py turns it into HTML with a delta against the previous run. Ticks along the baseline are the checks, and the one drawn hollow did not run — it is reported as not retested rather than as resolved." width="820" />
</div>
<!-- pd:viz end -->

</div>

> [!IMPORTANT]
> This is a quick outside-in check for common, obvious problems. It is not a
> penetration test, not a vulnerability assessment, and not exhaustive. It never
> logs in and never sends a payload. Treat a clean run as "nothing basic is
> hanging out in the open", not as "this site is secure".

## What this is

A [Claude Code](https://claude.com/claude-code) skill that runs a fixed catalog of
external, read-only checks against a website and the domains carrying its email,
then renders the result as a self-contained HTML report with run-to-run change
tracking.

The whole scan works from outside, the way any stranger sees the site: DNS records,
response headers, certificates, a fixed list of paths that should never be readable,
and the ports answering on the host. Nothing is authenticated. There is no crawl and
no fuzzing. Everything that would need credentials, a payload, or the hosting
provider's permission sits outside the boundary on purpose, and the report names each
of those gaps instead of leaving a reader to assume they were covered.

Where it does spend effort is on not overstating the result. Severity is judged
against what the asset actually is — a brochure site on shared hosting and a system
inside an authorization boundary produce very different consequences from the same
missing header. And a check that failed to complete is recorded as `not-retested`,
never as a pass, because a scan that did not look and a scan that found nothing
produce identical silence.

## What it checks

Eight families, every ID documented in [the check catalog](references/check-catalog.md).

| Family | What it looks at |
| --- | --- |
| `dns.*` | DNSSEC, CAA records, and whether a nameserver answers an unauthenticated zone transfer |
| `email.*` | DMARC, SPF, DKIM, MTA-STS, TLS-RPT and BIMI |
| `tls.*` | Certificate state and expiry, protocol support, legacy protocols via testssl.sh |
| `http.*` | Security headers, HTTP-to-HTTPS redirects, server banners, availability, time to first byte |
| `cms.*` | Generator version disclosure, exposed REST user lists, reachable login form, XML-RPC |
| `exposure.*` | A fixed list of paths that should not be readable, plus directory listings and `security.txt` |
| `port.*` | Reachable ports and service banners on the host's IP |
| `infra.*` | Hosting context, including the WAF User-Agent filter that makes other scanners report a false outage |

After the catalog runs, the model looks over the raw observations for anything the
catalog does not name — an odd header, an SPF include for a service nobody
recognises, a sibling domain in the certificate that was never in scope.

## What it will not do

<!-- pd:viz name="boundary" src=".prettydocs/src/boundary/" facts-hash="21ec687a982113960f3c15b2888ea788c30a80ba034989667f7e0f40fee2c905" src-hash="f1a0aa44bc8fc0cff0946ce1d8e5e77e938f4da461b833590451f1cf98649d42" -->
<div align="center">
<img src="docs/assets/boundary.svg" alt="Two columns. Sent: DNS queries to three public resolvers, HTTP GET and HEAD with a browser User-Agent, TLS handshakes, a fixed path list against the target's own vhost, and TCP connect plus banner reads. Never sent: credentials or any login attempt, payloads, injection, traversal or uploads, directory brute-forcing, and probes of other tenants on a shared IP. No authenticated testing, ever, and every coverage gap is named in the report." width="820" />
</div>
<!-- pd:viz end -->

The split that matters is the target's own vhost versus the landlord's IP. Requests
to the vhost touch only the target. Probing services on a shared IP reaches the
hosting provider's infrastructure and other tenants' listeners, which is not the site
owner's to authorize — so the scan connects to ports and reads banners, and stops
there. Ask it for `nmap -sV`, `nikto` or `wpscan --enumerate` against shared hosting
and it will tell you that needs written permission from the provider.

Seven things are out of scope by decision rather than by oversight, and each one is
printed in the report's methodology so nobody mistakes silence for a clean result.

| Gap | Why |
| --- | --- |
| Login rate limiting | Cannot be confirmed externally without submitting credentials. |
| Plugin and theme inventory | Needs the admin console, or path enumeration well beyond a fixed list. |
| Authenticated application testing | Requires credentials. |
| Injection, XSS, traversal, upload testing | Requires sending payloads. Outside the read-only boundary. |
| Service versions behind provider banners | Patch state is not externally observable and cannot be inferred from a version string. |
| Other tenants on a shared IP | Not the site owner's to authorize, and probing them would reach third-party systems. |
| Mail flow in transit | Requires access to the mail platform. |

## One name, two assets

<!-- pd:viz name="two-assets" src=".prettydocs/src/two-assets/" facts-hash="c043ede778d7f41fefff303d121ea2f286e8b8830435ed7284074b03b311c74c" src-hash="a18a81c3111c01c37d92475f001f94b413ad05cbcaf46c6b06adb01a3a9515d3" -->
<div align="center">
<img src="docs/assets/two-assets.svg" alt="A single domain name fronts two assets with almost nothing in common. The website produces findings about headers, TLS, readable files and CMS disclosure, and what they cost depends on what the site holds. The DNS zone carries DMARC, SPF, DKIM and MTA-STS for corporate mail, where a weakness is aimed at whoever trusts the name. Isolating the website protects the zone from nothing, so email-authentication findings are reported first." width="820" />
</div>
<!-- pd:viz end -->

Pointing a scanner at a hostname hides this. The website and the DNS zone have
different hosting, hold different things, and fail in ways that cost wildly different
amounts. Email authentication lives in the zone, so however isolated the web host is,
it offers the zone no protection at all — and a weak DMARC policy is the one finding
whose damage lands on somebody else who trusted the name. The report keeps the two
apart and puts the email findings first.

## Technology stack

| Area | Choice |
| --- | --- |
| Language | Python 3, standard library only |
| External commands | `dig`, `curl`, `openssl`, `nc` |
| Optional | Docker, for the testssl.sh escalation |
| Output | One self-contained HTML file with inlined CSS |
| Runtime | A Claude Code skill; the scripts also run standalone |

Nothing is installed with a package manager. The scripts shell out to standard
command-line tools so that every evidence block in the report is a command a reader
can paste into their own shell and re-run.

## Project structure

```
website-security-scan/
├── SKILL.md                       the workflow, the boundary, and the honesty rules
├── assets/
│   ├── report-template.html       the report, with the full design system inlined
│   └── targets/example.md         the target-profile template to copy
├── references/
│   └── check-catalog.md           every check ID, its severity, and what it means
├── scripts/
│   ├── scan.py                    runs the catalog, writes findings and evidence
│   ├── render_report.py           scan JSON + template → HTML
│   └── test_delta.py              self-check for the change-tracking logic
└── docs/assets/                   the diagrams on this page
```

## Getting started

### Prerequisites

- Python 3. There is nothing to `pip install`.
- `dig`, `curl`, `openssl` and `nc` on `PATH`.
- Docker, optional. Without it testssl.sh cannot run, and the legacy-protocol check
  reports `tls.legacy.unverified` rather than quietly passing.

### Install

It is a skill directory. Drop it where Claude Code looks for skills:

```bash
cp -R website-security-scan ~/.claude/skills/
```

### Describe the target

Copy the template and fill it in. The JSON block configures the scanner; everything
below it is the scope statement the severities are calibrated against, and it is the
one input nobody can verify from outside, so it carries the owner's name and a date.

```bash
cd ~/.claude/skills/website-security-scan
cp assets/targets/example.md assets/targets/acme.md
```

### Run it

```bash
python3 scripts/scan.py --profile assets/targets/acme.md
python3 scripts/render_report.py <output_dir>/acme-<date>.json
```

`scan.py` writes a dated JSON to the profile's `output_dir` and computes the delta
against the most recent prior JSON there. `render_report.py` writes the HTML beside
it. Useful flags: `--no-docker` skips testssl.sh, `--skip-paths` and `--skip-ports`
narrow the run, `--delay` changes the request interval.

Run standalone you get a mechanically accurate report with generated prose. Asking
Claude to run the skill instead is what adds the exploratory pass and the written
verdict — see [SKILL.md](SKILL.md) for that workflow.

### Testing

One self-check, and it earns its place:

```bash
python3 scripts/test_delta.py
```

It proves a skipped check cannot be reported as resolved. Run it after touching
`compute_delta`, `ran()`, or any `COVERS_*` group in
[`scripts/scan.py`](scripts/scan.py). There are no other automated tests.

## Documentation

- [SKILL.md](SKILL.md) — the workflow end to end, the boundary, and the four honesty
  rules the reports are held to.
- [references/check-catalog.md](references/check-catalog.md) — every check ID, its
  default severity, the deliberate coverage gaps, and how to add a check.
- [assets/targets/example.md](assets/targets/example.md) — the target profile
  template, with the scope statement and calibration rules a reader has to fill in.

## License

Released under the [MIT License](LICENSE).

<!-- pd:footer start -->
<div align="center">
<br/>

**Copyright © 2026 Zerø Effort. Released under the MIT license.**

</div>
<!-- pd:footer end -->
