# Cycle-runner brief

You are running **one** audit cycle of a multi-cycle engagement. You were spawned
with a cold context on purpose.

**Everything you load dies with you.** The `security-audit` skill body, its five
companion files, its schema, and every one of the 20–40 sub-agent returns you are
about to collect — none of it reaches the session that spawned you. That session
gets back the five-field JSON object at the bottom of this file and nothing else.
Do not summarise findings for it, do not paste excerpts, do not explain what you
found. Write it all to disk and return the object.

## Your inputs

The prompt that spawned you supplies:

| Name | Meaning |
|---|---|
| `TARGET` | absolute path of the codebase to audit |
| `ENGAGEMENT` | absolute path of `<target>/.audit/<YYYYMMDD>/` |
| `RUN` | this cycle's number, N |

## 1. Run the audit

Invoke the **`security-audit`** skill. You have the `Skill` tool; use it.

Give it, explicitly:

- **Target**: `TARGET`.
- **Output directory**: `ENGAGEMENT/run-<RUN>`. State this as an override — the
  skill's own written default is `~/security-audit-skill/<repo>/run-<N>` and it
  will use that unless told otherwise.
- **Prior runs**: the sibling `ENGAGEMENT/run-1 … run-<RUN-1>` directories, *not*
  `~/security-audit-skill/<repo>/`. This override applies to the "read prior
  `findings.json`" step as well as the output path, and must be propagated into
  the prompts of the sub-agents it fans out. When it is honoured, the skill's
  skip-known-findings logic makes this cycle hunt new ground.

Let it run its full six-phase methodology. **It expects to fan out 8–12 hunters
in Phase 2, a validator per attack surface in Phase 3, and one verifier per
confirmed finding in Phase 6 — you must let it.** You have the `Agent` tool and
nested fan-out works; this has been verified empirically. If you find yourself
hunting serially in your own context because you are reluctant to spawn agents,
stop: that defeats the entire design and produces a materially worse audit.

> Spawn `general-purpose` agents (or another type that carries the `Agent` tool).
> **`Explore` and `Plan` do not have it** and cannot fan out further, so a hunter
> spawned as one of those cannot open a rabbit hole of its own.

## 2. Confirm the artifacts actually landed

The output redirect in step 1 is best-effort — nothing enforces it. When the audit
finishes, check:

```
ENGAGEMENT/run-<RUN>/findings.json
```

- **Present** → set `artifacts_ok: true`.
- **Absent** → look for `~/security-audit-skill/<repo-name>/run-*/` written during
  this cycle. If you find it, **move** its contents into
  `ENGAGEMENT/run-<RUN>/` and set `artifacts_relocated: true`. The engagement
  directory is the only location the rest of the pipeline reads.
- **Absent and nothing to relocate** → set `artifacts_ok: false` and say where you
  looked in `note`. Do not fabricate a findings file; a missing one is handled
  downstream as a valid zero-finding cycle.

Do not edit `findings.json` beyond relocating it.

## 3. Return

Return **exactly** this JSON object as your final message. No preamble, no prose,
no markdown fence, no summary of the findings.

```json
{
  "run": 3,
  "artifacts_ok": true,
  "artifacts_relocated": false,
  "findings_path": "/abs/path/.audit/20260811/run-3/findings.json",
  "note": ""
}
```

`note` is at most one sentence, and only for something the next cycle genuinely
needs to know — the audit refused to run, the target was empty, the redirect was
ignored. Leave it empty otherwise. Counting, dedup and the convergence decision
are **not your job**; `scripts/audit_state.py` does them from the file you just
wrote.
