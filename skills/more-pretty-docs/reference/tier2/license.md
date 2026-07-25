# LICENSE spec (Tier 2)

Legal text. The governing rule: **reproduce, never author, and never choose.**

## Visual budget: none, ever

**LICENSE is an official legal document. It gets ZERO visuals, zero banners, zero
badges, zero markers, and zero formatting beyond the verbatim legal text.** No
`mpd:viz` embed, no `mpd:footer`, no `mpd:badges`, no attention banner, no design-system
styling — nothing. The file is the canonical license text and the single filled
copyright line, and nothing else. **Any `mpd:` marker or image in this file is a hard
quality-gate violation** (house-style → Quality gates 3 and 10).

## Rules

- **Don't pick a license for the user.** License selection is an ownership decision.
  Derive the SPDX id from the manifest `license` field if present; otherwise **ask**.
  Never default to one.
- **If a `LICENSE` already exists, treat it as truth.** Extract its SPDX id and the
  holder/year. Don't rewrite the body — only reconcile the copyright line's holder and
  year (and the badge/footer references *in the other docs*, never inside LICENSE) to
  match `docsmeta`.
- **When creating, reproduce the exact canonical text.** Fill only the copyright line
  (`Copyright © <year> <holder>`) from `docsmeta`. Don't paraphrase, summarize, or
  trim a license.
- **Source the canonical text from an authoritative source** at runtime (SPDX,
  `choosealicense.com`, or the steward's site). For the ubiquitous fixed-text licenses
  (MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC) the text is well-known and safe to
  reproduce. **If you can't obtain authoritative text and aren't certain of it, ask —
  don't approximate.**
- **Holder = organisation/entity**, per the house identity guardrail. Never the user's
  personal git/OS identity unless they explicitly state they are the individual holder.

## Apache-2.0 note

Apache-2.0 expects a companion **NOTICE** file — create/maintain it too (see
`notice.md`). The Apache license body itself is not customized except the
appendix's copyright line.

## Consistency

After writing LICENSE, the SPDX id must match: the manifest `license` field, the
README license badge and License section, and `docsmeta.license`. The cross-doc truth
gate checks this.
