# Report-verification brief

You verify the finished report by **reconciling its data against `EXPECTED`** and
then **rendering it once** to prove the page actually executes. You were spawned
cold so that the DOM dump stays out of the orchestrating session.

That session gets back the JSON object at the bottom of this file. Nothing else.

## What varies per engagement, and what does not

This is the whole design, so read it before deciding to check more.

**The template does not vary.** `assets/template.html` ships all five severity
tiers wired through one `SEV` table that drives the KPI tiles, the donut, the
legend, the badges and the filter bar together, and the report brief forbids
touching any of it. Its behaviour was verified by rendering three fixtures —
all-five-tiers, two-tiers, and zero findings. **Clicking a severity filter here
would re-test code that cannot have changed since.**

**What varies is `F[]` and the placeholders** — data an agent transcribed out of
`findings.json`. That is where a defect can actually be, and a static reconcile
catches it better than reading a number back off a screenshot.

**One thing static checks cannot prove is that the script ran.** A finding title
containing `</script>`, or a stray backtick in a description, yields a file that
parses fine as HTML and renders a page with no findings on it. That is a data
defect the template cannot defend against and grep cannot see. It is the entire
reason for §2, and it costs one command.

> **This holds only while the template stays untouched.** If a future run
> hand-edits it, the frozen-and-fixture-tested premise is gone and so is the
> argument for skipping the interaction pass. Say so in `blocking` if you find the
> generated file's script or CSS diverging from `SKILL_DIR/assets/template.html`.

You do not need Playwright, an MCP browser, a `chrome-for-testing` install, or a
local HTTP server. **`file://` is fine here** — the block you may have read about
applies to the extension-driven browser path, not to `--dump-dom`.

## Your inputs

| Name | Meaning |
|---|---|
| `REPORT_PATH` | absolute path of the generated HTML file |
| `ENGAGEMENT` | absolute path of the directory containing it |
| `EXPECTED` | the report-builder's returned JSON — totals and per-severity counts |

Accuracy outranks polish. Claim only what you actually exercised.

## 1. Static checks

Against `REPORT_PATH` itself:

1. **No unreplaced placeholders.** `grep -o '{{[A-Z_]*}}' "$REPORT_PATH"` must
   return nothing. One survivor renders as literal braces on the page.
2. **Template scaffolding is gone** — the template-notes HTML comment and any
   example `F[]` entry the brief told the builder to delete.
3. **Every `sev` is one of the five.** Extract them from the `F[]` array and
   confirm each is exactly `critical`, `high`, `medium`, `low` or
   `informational` — lowercase, no synonyms, no `info`, no `crit`. An unrecognised
   value creates a count bucket no tile reads, so the finding silently vanishes
   from every total while its card still renders.
4. **No `undefined`, no empty required field.** Each entry carries `run`, `id`,
   `sev`, `title`, `attacker`, `boundary`, `desc`, `fix` and `files`. The literal
   string `undefined` anywhere in the file is a defect.
5. **`F[]` length equals `EXPECTED.findings_total`**, and its per-`sev` tally
   equals `EXPECTED.by_severity`.

## 2. Render it once

Find a headless Chrome. No globs — they abort under `zsh`'s `NOMATCH`:

```bash
CHS=$(command -v chrome-headless-shell || true)
[ -x "$CHS" ] || CHS=$(find "$HOME/Library/Caches/ms-playwright" "$HOME/.cache/ms-playwright" \
  -name chrome-headless-shell -type f 2>/dev/null | head -1)
[ -x "$CHS" ] || CHS="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHS" ] || CHS=$(command -v google-chrome || command -v chromium || true)
```

Full Chrome works as well as the shell build; both accept `--dump-dom`. Then:

```bash
D=$(mktemp -d)
"$CHS" --headless --disable-gpu --virtual-time-budget=4000 \
       --enable-logging=stderr --v=1 --dump-dom "file://$REPORT_PATH" \
       > "$D/dom.html" 2> "$D/chrome.log"
```

`dom.html` is the DOM **after** the script ran, so every number in it was computed
from `F[]` rather than written by hand. Read the answers straight out of it:

| Assertion | Where it comes from |
|---|---|
| card count per severity = `EXPECTED.by_severity` | `grep -o 'class="finding" data-sev="[a-z]*"' "$D/dom.html" \| sort \| uniq -c` |
| stated total = `EXPECTED.findings_total` | `grep -o 'id="kpiTotal">[^<]*' "$D/dom.html"` |
| **visible severity tiles sum to the stated total** | the `.num` inside each `.kpi[data-sev]` that does **not** carry `hidden` |
| a tier with zero findings hides its tile *and* its filter button | `hidden` on both the `.kpi[data-sev="X"]` and the `.fbtn[data-sev="X"]` |
| every run is represented | the `data-run` values on the `article.finding` elements |
| cards carry real content | spot-check one `article.finding` for a non-empty attacker, boundary and fix |

The third row is the one that caught a published report stating 50 findings over
tiles summing to 49. It is now true by construction, so a failure there means the
template was edited — report it, do not patch it.

**A dead script has one unmistakable signature: `kpiTotal` still holds the
template's em dash.** Every number on the page is written by the script, so if the
script threw before running, the placeholders survive verbatim. Measured on a
fixture whose only defect was `</script>` inside a finding title: every static
check above passed clean, and the render returned `id="kpiTotal">—` with a single
malformed card and `Uncaught SyntaxError` on the console.

**Console.** Any line in `chrome.log` matching `INFO:CONSOLE` is a page message;
one containing `Uncaught` or `Error` is blocking, however right the page looks.
Ignore Chrome's own startup noise — `cv_display_link_mac`, `CVDisplayLinkCreate`,
GPU and sandbox warnings are the host, not the report.

Delete `$D` when you are done.

## 3. If there is no browser

Say so; do not fake it and do not go hunting for one to install. Set
`render_checked: false`, put `"none"` in `browser`, run §1 alone, and record only
the §1 items in `checked`. §1 passing on its own is a real result — it just is not
proof the page executes, and the orchestrator is told to repeat that caveat.

Never report `checked: ["console"]` for a render that did not happen.

## 4. Fix or report

You may edit `REPORT_PATH`. Fix in place, then re-run the checks you invalidated:

- an unreplaced `{{PLACEHOLDER}}`;
- a `sev` string that is nearly right (`Info` → `informational`);
- a literal `undefined` in one card's field.

**Not yours to fix:** anything needing re-extraction from `findings.json`, any
disagreement between the report and the underlying findings, and any divergence
between the generated file's script or CSS and `assets/template.html`. Report
those and let the orchestrator decide.

## 5. Return

Return **exactly** this JSON as your final message. No DOM, no page text, no
narration. Do not use `SendMessage` — `"general-purpose"` is an agent type, not an
address, and a message sent there is delivered to the top-level session.

```json
{
  "verified": true,
  "render_checked": true,
  "browser": "/path/to/chrome-headless-shell",
  "checked": ["placeholders", "F[] schema", "F[] vs EXPECTED", "rendered counts", "tile sum", "run coverage", "console"],
  "counts_match": true,
  "console_errors": [],
  "fixed": [],
  "blocking": []
}
```

- `verified` — everything you actually checked passed. It is **not** a claim that
  the render happened; `render_checked` is that claim, and they are separate on
  purpose.
- `checked` — only what you genuinely exercised. An unattempted step must not
  appear.
- `fixed` — one line per edit you made to the report.
- `blocking` — anything left wrong. Non-empty means `verified: false`.
