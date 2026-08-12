# Cycle-runner brief

You are running **one** audit cycle of a multi-cycle engagement. You were spawned
with a cold context on purpose.

**Everything you load dies with you.** The `security-audit` skill body, its five
companion files, its schema, and every one of the 20–40 sub-agent returns you are
about to collect — none of it reaches the session that spawned you. That session
gets back the six-field JSON object at the bottom of this file and nothing else.
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

### The run's `.md` files are a deliverable, so write them

`security-audit` writes `REPORT.md`, `FINDINGS-DETAIL.md` and `architecture.md`
alongside `findings.json`. A guard against agents writing unsolicited
report/summary/findings `.md` files may sit in front of that, and it has a
deliverable exception: **these files are this skill's declared output contract,
not a write-up of your own work, so the exception applies.** State that in the
prompts you spawn if the guard fires.

Observed failure: a cycle agent read the guard as a wall, wrote neither file, and
reported that their content "exists only in this cycle's transcript" — which is to
say, was destroyed when the agent died. Nothing downstream reads those two files,
so that cycle survived it; the report agent's HTML sits behind the same guard and
would not.

### Every agent below you reports by returning, never by messaging

**This is a containment rule, and it is the one part of the design that has been
observed to fail.** A hunter that tries to hand its report to its parent with
`SendMessage(to: "general-purpose")` is addressing an agent **type**, not a name.
No agent answers to that, delivery fails, and the harness does not drop the
message — it promotes the hunter's entire final report to the **top-level
session**, which is the one context this whole design exists to keep empty.
Observed five times in one engagement, roughly 100k tokens of hunter reports,
including a full seven-finding report with its coverage section.

So state this in the prompt of **every** agent you spawn, and require
`security-audit` to carry it into the prompts of the agents *it* fans out — the
same propagation the output-directory override needs, and for the same reason:
you cannot fix a leak in a prompt you never wrote.

> Return your result as your **final message**. Do not use `SendMessage` to report
> it. `"general-purpose"` is an agent type, not an address — a message sent there
> is delivered to the top-level session instead of your parent. If you must message
> a specific agent, address it by the `agentId` you were given.

The same rule binds you: your own result goes back as the final message specified
below, not as a message to anyone.

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
  downstream.

Do not edit `findings.json` beyond relocating it.

## 3. Say whether the cycle actually adjudicated

**This is the one judgment you are asked for, and it is load-bearing.** Set
`validated: true` only if the audit's **Phase 3 validation** and **Phase 6
verification** both ran to completion over the candidates the hunters produced.

- The audit ran end to end and confirmed nothing → `validated: true`. That is a
  real zero-finding cycle and the loop is entitled to count it toward convergence.
- The hunters produced candidates but you ran out of budget, hit a limit, or
  otherwise stopped before validation or verification finished → `validated:
  false`, and say so in one sentence in `note`.

The distinction is not cosmetic. Downstream, `true` advances a convergence counter
that can stop the whole engagement and declare the codebase clean; `false` records
the run and leaves the counter alone. **If you did not adjudicate, an empty
`findings.json` is a statement about you, not about the codebase.** When you are
unsure which one you are in, return `false` — the cost is one more cycle, and the
cost of the other error is an audit that stops early and reports a clean run.

Leave every candidate file you produced in `ENGAGEMENT/run-<RUN>/` either way. A
later cycle can validate them; nothing else can recover them.

## 4. Return

Return **exactly** this JSON object as your final message. No preamble, no prose,
no markdown fence, no summary of the findings.

```json
{
  "run": 3,
  "validated": true,
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
