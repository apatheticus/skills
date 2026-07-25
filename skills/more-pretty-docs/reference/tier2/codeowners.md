# CODEOWNERS spec (Tier 2)

A `CODEOWNERS` file (GitHub: `.github/CODEOWNERS`) mapping paths to review owners.
On-demand only, and it **always requires asking** — owners can't be safely inferred.

This is a config file, not a prose doc: it carries **no visuals, banners, badges, or
`mpd:` markers** — just the path→owner rules (and any `# TODO:` comment).

## Rules

- **Never guess owners.** Do not derive owners from git commit authors, blame, or the
  repo owner's identity. An incorrect CODEOWNERS silently misroutes reviews. Ask the
  user for the path→owner mapping (teams or handles), and write only what they confirm.
- **Respect the identity guardrail.** Owners here are whatever the user specifies
  (often `@org/team` handles). Don't insert the user's personal identity as a default
  owner.
- **Validate the syntax** — glob patterns, one rule per line, last-match-wins ordering.
  Owners must be valid handles/teams the user gave you.
- If the user wants CODEOWNERS but can't yet supply the mapping, write a minimal file
  with a clear `# TODO:` comment rather than fabricated assignments.
- **Forge-specific.** CODEOWNERS is GitHub/GitLab syntax; on unsupported forges, skip
  and note why.
