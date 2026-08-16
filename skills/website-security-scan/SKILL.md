---
name: website-security-scan
description: Run a periodic external security posture scan of a website and the email domains that share its name, then produce an interactive SaaS Pro styled HTML report that tracks what changed since the last scan. Use this whenever someone wants to scan, audit, re-check or monitor a public website or domain for vulnerabilities — missing security headers, DNS or email authentication gaps (DMARC, SPF, DKIM, CAA, MTA-STS, DNSSEC), TLS and certificate problems, publicly readable files like .env or .git, exposed CMS versions, or open ports. Also use it to validate, sanity-check or push back on a third-party security assessment, vendor scan, or security scorecard rating of their own site. Trigger on requests like "scan our website", "run the monthly security check", "what changed since last month's scan", "a vendor sent us these findings, are they real", or any request to re-run a prior scan of a domain. This is for externally observable posture of a live site — for auditing source code, use the security-audit skill instead.
disable-model-invocation: true
---

# Website security scan

Runs a fixed catalog of external, read-only checks against a target's domains,
adds a model-led exploratory pass, then renders the result into the interactive
HTML report format in `assets/report-template.html` with run-to-run delta
tracking.

Two things distinguish this from pointing a scanner at a hostname, and both exist
because a real third-party assessment got them wrong on this exact target:

1. **Severity means consequence against a specific asset.** A scanner has no idea
   whether it is looking at a data-free brochure site on rented shared hosting or
   a system inside an authorization boundary. The target profile supplies that,
   and every severity is calibrated against it.
2. **A domain is not a system.** One domain name usually fronts at least two
   assets with almost nothing in common: a website, and the DNS zone carrying
   corporate email authentication. They have different hosting, different data and
   radically different consequences. Report them separately.

## The boundary — not negotiable

Everything this skill does is read-only or connect-only, and the distinction that
matters is **the target's own vhost versus the landlord's IP**.

Permitted:
- DNS queries; HTTP GET/HEAD with a realistic User-Agent; TLS handshakes.
- GETs of a fixed list of known-sensitive paths against the target's own vhost.
  Each either finds a file the world can already read, or gets a 404.
- TCP connect and banner read on a shared IP.

Never, regardless of who asks or how the request is framed:
- Authentication attempts, credential submission, or password guessing.
- Payloads, injection strings, traversal attempts, fuzzing, or uploads.
- Directory brute-forcing beyond the fixed path list.
- Service probing or enumeration of other tenants on shared infrastructure.

That last one is the reason the split exists. HTTP requests to the target's own
vhost touch only the target. Port-scanning or service-probing a shared IP is
probing the hosting provider's infrastructure and, at the service level, other
tenants' listeners — which is not the target owner's to authorize, and worse when
a recurring job does it unattended. If someone asks for `nmap -sV`, `nikto`, or
`wpscan --enumerate` against shared hosting, say plainly that it needs written
authorization from the provider and offer the read-only equivalent.

## Workflow

### 1. Resolve the target profile

Profiles live in `assets/targets/<slug>.md`. Each holds a fenced `json` config
block for `scan.py` and, below it, the scope statement and calibration rules that
determine what findings actually mean.

```bash
ls ~/.claude/skills/website-security-scan/assets/targets/
```

If a profile exists, **read all of it** before interpreting any finding — the
calibration rules and the standing-conditions table are what stop you re-reporting
known context as a discovery.

If no profile exists for the requested target, you need six things before scanning.
Ask for them together, once, and then write the profile so it is never asked
again:

- Which domains belong to this target, and each one's role (primary website,
  redirect, mail).
- What the site actually is, and what it holds. Any data? Customer data?
- Is there any network or credentialed path from it to anything internal?
- Who hosts it, and is it shared or dedicated? Can the owner close ports?
- Does the domain carry corporate email, and on what platform?
- Does it sit inside any compliance or authorization boundary?

Use `assets/targets/example.md` as the shape to copy. The scope statement
is asserted by the system owner and should say so with a date — it is the one
input you cannot verify externally, and the owner is the correct authority for it.

### 2. Run the scan

```bash
python3 ~/.claude/skills/website-security-scan/scripts/scan.py \
  --profile ~/.claude/skills/website-security-scan/assets/targets/<slug>.md
```

Writes `<slug>-YYYYMMDD.json` to the profile's `output_dir`, using the most recent
prior JSON there as the baseline. Useful flags: `--no-docker` skips testssl.sh,
`--skip-paths` and `--skip-ports` narrow the run, `--delay` adjusts the request
interval (default 0.4s), `--samples` sets availability samples (default 6).

Expect several minutes when testssl.sh runs. It is worth the wait: without it the
legacy-TLS check is permanently unverifiable, and a check that can never run is
one people learn to ignore.

If you changed anything in the scanner, run the delta self-check first — it takes
a second and it is the only thing standing between a skipped check and a report
that claims a problem was resolved:

```bash
python3 ~/.claude/skills/website-security-scan/scripts/test_delta.py
```

Read the JSON before writing anything. Pay attention to three things:

- `checks_run` — anything not `ok`. These are gaps in this run's coverage and the
  report must say so.
- `delta.not_retested` — prior findings whose check did not complete. These are
  **not** resolved. Never describe them as fixed.
- `facts` — the raw observations. Often the interesting story is here rather than
  in the findings list.

### 3. Exploratory pass

The catalog is what makes runs comparable; it is also, by construction, blind to
anything it does not already name. This step is where discovery happens, and it is
not optional — on the assessment that motivated this skill, every one of the six
most consequential findings came from looking around rather than from a checklist.

Work from what the scan surfaced and stay inside the boundary above:

- Follow up on odd `facts`. An unexpected header, a redirect chain, a hostname in
  a certificate that nobody mentioned, an SPF include for a service the
  organization does not obviously use.
- Fingerprinted software versions: look up each against current advisories and the
  vendor's release notes. Cite or do not claim — see the honesty rules.
- Check whether related domains named in certificate SANs are in the profile. The
  `infra.related-domain.unprofiled` finding flags them; act on it, because a
  sibling domain's absent DMARC record is exactly what single-hostname scoping
  hides.
- Ask what a reader would want to know that no check covers.

Add what you find to the JSON's `findings` array with an `exploratory.` ID prefix
and the same shape as the rest. When the same exploratory finding shows up in two
consecutive runs, promote it into the catalog per
`references/check-catalog.md#promoting-an-exploratory-finding`.

### 4. Write the narrative

Edit the scan JSON in place. Three places take model-authored content:

**`narrative`** — an object:

| Key | What goes in it |
|---|---|
| `title` | Browser title. |
| `overline`, `h1`, `lede` | `h1` is a sentence stating the actual conclusion, not a label. "Two of seven claims touch an asset with real business consequence" beats "Scan Results". `h1` and `lede` are inserted as HTML, so `&nbsp;` works — use it to stop dates and version numbers breaking across lines. `overline` is escaped. |
| `scope_html` | The scope statement as HTML paragraphs, attributed and dated. Drawn from the profile. |
| `verdict_overline`, `verdict_h2`, `verdict_p` | The overall read. `verdict_p` is HTML. |
| `context` | `{tile, icon, title, body}` — the one piece of context a reader needs before acting on the list. Tiles: `t-brand`, `t-green`, `t-coral`, `t-orange`, `t-purple`. `icon` is inner SVG path markup on a 24×24 viewBox. |
| `closing_html` | Closing callout. Use `<div class="callout is-info">`, or `is-warn` / `is-bad` / `is-good`. |
| `ports_intro` | Optional. |
| `methodology` | Optional `[[term, html], ...]`. Omit it and a thorough default is generated from the scan record — prefer the default and add to it rather than replacing it. |

**`remediation`** — an array, each `{grp, t, m, tags}` where `grp` is `"do"` or
`"accept"`, `t` is the action, `m` is the reasoning, and `tags` is a list of
`[badge-class, label]` pairs. Badge classes: `b-confirmed` (red), `b-partial`
(orange), `b-missed` (indigo), `b-refuted` (green), `b-unsupported` (purple),
`b-neutral` (grey).

The two groups matter. `accept` items need no engineering work at all — they need
a one-paragraph risk acceptance and a closed ticket. Sorting a finding into
`accept` is a real answer, not a deferral, and saying so protects the reader from
spending a sprint on a landlord's port configuration.

**`findings[].body_html`** — per-finding prose. Without it the report falls back
to the generated `summary`, which is accurate but flat. Write `body_html` for
every material finding and every finding whose disposition is not obvious. Use
`<h4>` subheadings, and include a "Risk in context" heading that states the honest
severity and the honest justification. When something is cheap and low-risk, say
the justification is cost rather than risk — that sentence is what stops a reader
treating a low finding as urgent.

Leave `evidence` alone. It is the scanner's record and the reason the report is
checkable.

### 5. Render, verify, deliver

```bash
python3 ~/.claude/skills/website-security-scan/scripts/render_report.py \
  <path/to/scan.json>
```

Writes the HTML beside the JSON. It exits non-zero on an unfilled placeholder, and
warns on stderr if the narrative is still the generated fallback.

Then verify the rendered artifact, not the code — per the
`visual-output-verification` skill. At minimum: open it, confirm the findings list
renders and the severity tabs filter, confirm the search box matches text you
know is present, expand a card and check the evidence block, and confirm the
console is clean. If you changed the template, re-check contrast and heading
order; the six deliberate deviations from the design system's spec are commented
in the CSS and each one fixes a real WCAG AA failure, so do not "correct" them
back.

Report what you verified against the rendered page, and state plainly anything you
did not check.

## Honesty rules

These are the four failure modes that made a real paid assessment of this exact
target worse than useless. They are the point of the skill.

**1. An unrun check is not a pass.** If a check did not complete, the report says
so, in the finding and in the methodology. A prior finding whose check did not run
is `not-retested`, never `fixed`. `compute_delta` enforces this and the report
gives it a dedicated warning block — do not undo either.

**2. Cite the advisory or do not claim the vulnerability.** A version from a banner
or a generator tag is a **disclosure** finding. Distributions backport security
fixes while the advertised version never moves, so a banner is not a patch level.
To assert a vulnerability you need a specific CVE or advisory ID and a link, and
you need to check the affected version range actually contains the observed
version. Absent that, the honest finding is "version N is behind current release
M; changelog not reviewed," which is still actionable. The assessment that
prompted this skill claimed "known vulnerabilities" for two components, cited
nothing, and had the affected range backwards on one of them.

**3. No dollar-loss estimates.** Not unless the figure carries a cited source and a
methodology scoped to this asset. Repeating an unsupported loss estimate in a
federal contracting context manufactures a problem that does not otherwise exist,
and it will be quoted back from a risk register long after everyone has forgotten
where it came from.

**4. Do not cite a control baseline that does not apply.** If the target is outside
FISMA, NIST SP 800-53, 800-171, HIPAA or ARS scope, say so and cite nothing. An
invented control mapping creates a compliance finding out of thin air. If a
control is a useful analogy, label it explicitly as an analogy and name the
boundary the asset sits outside of.

One more, less a rule than a reflex: **a WAF block is not an outage.** Many hosts
answer non-2xx to requests without a browser User-Agent. A scanner that reads its
own rejection as a service fault will report a false outage and a false TLS
failure from the same root cause. `scan.py` fingerprints this before anything
else and records it as `infra.waf.ua-filter`; check that finding before believing
any availability claim, including your own.

## Scheduling

Run it manually first and confirm the report is right. The first run establishes
the baseline every future delta is measured against, so a partial or misconfigured
first run quietly poisons every comparison after it.

Once a couple of manual runs look correct, monthly suits a static marketing site —
DNS, TLS and header posture move slowly, and CMS core patches land roughly
monthly. Add to `crontab -e`:

```bash
0 6 1 * * cd "$HOME/scratch" && claude -p "Read the website-security-scan skill at ~/.claude/skills/website-security-scan/SKILL.md and run a full scan of the <slug> target, writing the report and narrative as documented." --allowedTools "Bash,Read,Write,Edit,Glob,Grep" > /tmp/website-scan.log 2>&1
```

Confirm before installing a cron — it is persistent configuration. For unattended
runs also read the `unattended-runs` skill: nothing can prompt for approval, so
every command must be non-interactive and writes must go where they are allowed.

## Files

| Path | Role |
|---|---|
| `scripts/scan.py` | Runs the catalog. Emits findings, per-check execution state, evidence, and the delta against the previous run. |
| `scripts/render_report.py` | Scan JSON + template → HTML. Derives KPI tiles, severity donut, change lists, port rows and methodology so the model only supplies judgment. |
| `scripts/test_delta.py` | Self-check for the change-tracking logic. Run it after touching `compute_delta`, `ran()`, or any `COVERS_*` group — it is what proves a skipped check cannot be reported as resolved. |
| `assets/report-template.html` | The report. Full inlined CSS from the SaaS Pro design system including six deliberate corrections to real WCAG AA failures in the DS itself, each commented. |
| `assets/targets/<slug>.md` | Per-target config, scope statement, calibration rules, standing conditions, history. |
| `references/check-catalog.md` | Every check ID, default severity, meaning; deliberate coverage gaps; how to add or promote a check. Read when you need to know what a finding ID means. |
