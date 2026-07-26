# Issue templates spec (Tier 2)

GitHub issue forms/templates, generated from a standard skeleton adapted to the
project. On-demand only. Location follows host detection (GitHub: `.github/ISSUE_TEMPLATE/`).

These are forms, not prose docs: they carry **no visuals, banners, badges, or `pd:`
markers** — just the template fields.

## What to create

A small, sensible default set — don't over-engineer:

- **`bug_report.md`** (or `.yml` form) — what happened, expected vs actual, steps to
  reproduce, environment, and the project-relevant state to capture (mirror what
  SUPPORT.md's bug section asks for, so they agree).
- **`feature_request.md`** — the problem, the proposed change, alternatives considered.
- **`config.yml`** — set `blank_issues_enabled` per the project's preference and add
  `contact_links` routing security reports to the SECURITY process and questions to
  Discussions (only if enabled) — so the templates reinforce the SECURITY/SUPPORT
  routing rather than contradict it.

## Rules

- **Adapt fields to the project.** A web app's bug form asks for route/viewport; a CLI's
  asks for command/flags/OS. Pull the relevant axes from the evidence pass.
- **Keep routing consistent** with SECURITY.md (vulnerabilities never go to a public
  bug issue) and SUPPORT.md (questions → the configured channel).
- **Forge-specific.** Issue forms are a GitHub feature. On other forges, create the
  equivalent (e.g. GitLab issue templates under `.gitlab/issue_templates/`) or skip
  with a noted reason if the forge doesn't support them.
- Don't add a CODE_OF_CONDUCT checkbox or DCO unless the project actually uses one.
