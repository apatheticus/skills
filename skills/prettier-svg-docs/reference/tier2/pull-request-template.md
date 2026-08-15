# Pull request template spec (Tier 2)

A `PULL_REQUEST_TEMPLATE.md` (GitHub: repo root or `.github/`), generated from the
project's real review gates. On-demand only.

This is a form, not a prose doc: it carries **no visuals, banners, badges, or `pd:`
markers** — just the template fields.

## Content

- **Summary** — what changed and why (prompt for the *why*, matching the commit
  convention in CONTRIBUTING).
- **Linked issue** — `Closes #…`.
- **Checklist** — the project's genuine pre-merge gates, **reused from CONTRIBUTING.md's
  PR checklist** so the two never diverge. If CONTRIBUTING lists determinism /
  typecheck / no-new-deps gates, mirror exactly those.
- **Notes for reviewers** — optional, for context that doesn't fit the summary.

## Rules

- **Single source of truth for the checklist is CONTRIBUTING.md.** This template
  restates it in checkable form; it must not introduce gates that aren't real.
- Keep it short — a wall of checkboxes gets ignored. Five real gates beat fifteen
  aspirational ones.
- Adapt the forge vocabulary (PR vs MR) and location per host detection.
