# Report-verification brief

You verify the finished report **against the real rendered pixels**, then report
what you exercised. You were spawned cold so that screenshots and console dumps
stay out of the orchestrating session.

A green build is not proof. The only evidence that counts is what the live page did
when you drove it.

## Before your first browser call

Load the **`browser-verification`** skill. It carries the gotchas for this
environment — `file://` being blocked, which browser binaries exist, how tabs and
scroll positions behave — and reading it after a failure costs more than reading it
first. Load **`visual-output-verification`** too; it is the checklist this brief is
an instance of.

## Your inputs

| Name | Meaning |
|---|---|
| `REPORT_PATH` | absolute path of the generated HTML file |
| `ENGAGEMENT` | absolute path of the directory containing it |
| `EXPECTED` | the report-builder's returned JSON — totals and per-severity counts |

## 1. Serve it

Browsers block `file://`, so serve the directory rather than opening the file:

```bash
python3 -m http.server 8771 --directory "<ENGAGEMENT>" &
# then open http://localhost:8771/<basename of REPORT_PATH>
```

Kill the server when you are done: `lsof -ti:8771 | xargs kill`. Do this even if
you fail partway — a stranded server holds the port for the next engagement.

## 2. Exercise it

Not "look at it". Drive it, and record what each step actually produced:

1. **Hero, KPIs, donut** — screenshot the top of the page. Do the KPI numbers match
   `EXPECTED.findings_total` and `EXPECTED.by_severity`? The template computes them
   from `F[]` at runtime, so a mismatch means the array is wrong, not the CSS.
2. **Findings list** — scroll to it. Is every run represented? Count the cards
   against `EXPECTED.findings_total`.
3. **Expand one card** — confirm the detail (attacker, boundary, fix, file refs)
   renders and is not empty or `undefined`.
4. **Click a severity filter** — confirm the visible card count updates and the
   surviving cards are all of that severity. This is the one interaction most
   likely to be silently broken, because it depends on `F[]` field names matching
   what the template's script expects.
5. **Click a run filter**, if more than one run — same check, by run.
6. **Console** — read it. Any error means the page is not trustworthy, however
   right it looks.

> Screenshots freeze CSS animation, so never measure motion from one. If something
> animated needs checking, query it from the page instead of inferring it from a
> still.

## 3. Fix or report

Small, unambiguous defects in the generated HTML — a wrong count, a broken filter
attribute, an `undefined` in a card — fix in place and re-verify. You are allowed
to edit `REPORT_PATH`.

Anything that would require re-extracting findings, or any disagreement with the
underlying `findings.json`, is **not** yours to fix. Report it and let the
orchestrator decide.

## 4. Return

Return **exactly** this JSON. No screenshots, no page text, no narration.

```json
{
  "verified": true,
  "checked": ["hero+KPIs", "donut", "findings list", "expanded card", "severity filter", "run filter", "console"],
  "counts_match": true,
  "console_errors": [],
  "fixed": [],
  "blocking": []
}
```

- `checked` — only what you genuinely exercised. An unattempted step must not
  appear here.
- `fixed` — one line per edit you made to the report.
- `blocking` — anything left wrong. Non-empty means `verified: false`.
