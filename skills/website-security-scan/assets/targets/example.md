# Target profile — Example Co public web presence

Machine configuration for `scan.py` is the fenced JSON block. Everything below it
is for the model writing the report: it is the scope statement that determines
what each finding actually means, and it is the reason severities in these reports
do not match what a generic scanner would output.

Copy this file to `<slug>.md` and replace every value with the target's own.

```json
{
  "slug": "example-co",
  "org": "Example Co",
  "output_dir": "~/scratch/Outputs/website-scans/example-co",
  "vantage": "macOS host, commercial ISP, single vantage point",
  "domains": [
    {
      "fqdn": "example.com",
      "roles": ["web-primary", "mail"],
      "asset_class": "web-marketing-disposable",
      "note": "Primary marketing site. Also carries email authentication records for corporate mail."
    },
    {
      "fqdn": "example.net",
      "roles": ["web-redirect", "mail"],
      "asset_class": "web-marketing-disposable",
      "note": "301s to the primary site. Separately provisioned mail domain with its own MX."
    }
  ],
  "landlord": {
    "provider": "Shared hosting provider name",
    "evidence": "reverse-DNS name of the shared IP",
    "owns_ports": true
  },
  "port_scan": {
    "enabled": true,
    "connect_only": true,
    "ports": [21, 22, 25, 80, 110, 143, 443, 465, 587, 993, 995,
              2082, 2083, 2086, 2087, 2095, 2096, 2222, 3306]
  },
  "severity_overrides": {}
}
```

## Scope statement

Asserted by the system owner, with a name and a date — this is the one input you
cannot verify externally, and the owner is the correct authority for it.

State plainly what the site is and is not: what data it holds, whether any network
or credentialed path reaches internal systems, whether hosting is shared or
dedicated, and which compliance or authorization boundaries it sits inside or
outside. Then state the worst realistic outcome of a compromise.

## Two assets share these domain names

**The website** — where most findings land. Describe the realistic worst outcome
and the recovery path.

**The email domain** — corporate mail with real senders and real counterparties.
Findings here are the only ones whose weakness can be turned against a third party
who trusts the org's name, and they are independent of where the site is hosted.

Consequence: **email-authentication findings outrank website findings** unless the
website itself holds data or reaches internal systems. Report them in that order.

## Calibration rules

1. **Severity means consequence against this asset, not CVSS.** Reserve `material`
   for something with real business consequence given the scope above.

2. **Never cite a control baseline as applicable** unless the asset is genuinely
   inside that boundary. If a control reference is useful as an analogy, say so
   explicitly.

3. **No dollar-loss estimates** unless the figure has a cited source and a stated
   methodology scoped to this asset.

4. **Landlord findings say who owns the fix.** Ports and banners on a shared IP
   belong to the provider. Phrase them as tenancy facts, not as the org exposing a
   service it cannot close.

5. **Version strings are disclosure, not vulnerability.** Asserting exploitability
   requires a specific CVE or advisory ID plus a link. Distributions backport fixes
   without moving the advertised version.

6. **Availability findings are business impact, not security.** Report a slow or
   failing site as a performance defect, and do not let a WAF block masquerade as
   an outage.

## Known standing conditions

Things already understood about this target. Report them if they change; do not
present them as discoveries.

| Condition | State as of YYYY-MM-DD |
|---|---|
| _e.g._ WAF User-Agent filter | Host returns 406 with no User-Agent, 200 to a browser. |

## History

- **YYYY-MM-DD** — Profile created. Note what prompted it.
