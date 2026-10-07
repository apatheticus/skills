# Extraction guide — signals, schemas, batching

How the Workflow's extractor/cluster/decide stages should behave. The SKILL.md
pipeline references this file; read it before authoring the workflow script.

## Contents

- **Transcript anatomy** — which JSONL events matter, and how to read huge files.
- **Signal families** — friction, repetition, wins, environment gaps.
- **Extractor output schema (per batch)** — the JSON every extractor returns.
- **Batching** — group by project, size by priority.
- **Clustering & decision stage** — mechanical then semantic merge; verdicts.
- **Workflow return value** — the one object the script returns, which
  `scripts/assemble.py` reads.

## Transcript anatomy (what extractors will see)

Each `~/.claude/projects/<project-dir>/<session-id>.jsonl` line is a JSON
event. The ones that matter:

- `{"type":"user","message":{...}}` — user turns. Real prompts, corrections,
  interruptions. Slash commands appear as `<command-name>/foo</command-name>`.
  Lines whose content starts with `[Request interrupted` mark user
  interruptions.
- `{"type":"assistant","message":{...}}` — model turns incl. tool_use blocks.
- Tool results ride on user-role events (`tool_result` content); errors have
  `is_error: true`.
- `{"type":"permission-mode",...}`, `{"type":"attachment","attachment":{"type":"hook_..."}}`
  — environment context (permission mode, hook output/failures).
- `isSidechain: true` — sub-agent traffic; usually skim-only.
- Header-ish events (`last-prompt`, `mode`, `bridge-session`,
  `file-history-snapshot`) — ignore.

Transcripts can be tens of MB. Extractors should use `grep`/`jq` to locate
user turns, errors, and interruptions first, then Read the surrounding
context — never read a huge file end-to-end.

## Signal families (extract all four)

1. **friction** — user corrections and re-prompts ("no, I meant…", repeated
   rephrasings), abandoned/failed tasks, failed commands and retry loops,
   permission-prompt interruptions, context exhaustion/compaction mid-task,
   misunderstood intent, hook failures, tool errors with user-visible impact.
2. **repetition** — the same task shape appearing across sessions, boilerplate
   prompt fragments the user retypes, manual multi-step routines a skill/
   hook/automation could absorb, installed-but-unused skills that would have
   applied (compare against `ls ~/.claude/skills`).
3. **wins** — prompts, phrasings, and setups that worked notably well; skills
   or workflows that paid off; habits worth codifying so the report is a
   playbook, not just a defect list.
4. **environment** — setup gaps: missing permissions/allowlist entries causing
   prompt fatigue, absent CLAUDE.md context the user keeps supplying by hand,
   model/effort mismatches, MCP servers erroring, hooks misfiring.

## Extractor output schema (per batch)

```json
{
  "type": "object",
  "required": ["signals"],
  "properties": {
    "signals": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["family", "session_id", "project", "summary", "evidence"],
        "properties": {
          "family": {"enum": ["friction", "repetition", "wins", "environment"]},
          "session_id": {"type": "string"},
          "project": {"type": "string"},
          "summary": {"type": "string", "description": "One sentence, concrete"},
          "evidence": {"type": "string", "description": "Verbatim quote from the transcript (user or assistant text, or the failing command+error)"},
          "severity": {"enum": ["high", "medium", "low"]},
          "suggested_theme": {"type": "string", "description": "Short kebab-case cluster hint, e.g. permission-fatigue, html-report-styling"}
        }
      }
    },
    "sessions_unreadable": {"type": "array", "items": {"type": "string"}}
  }
}
```

Extractor prompt must include: the file paths in its batch, the four family
definitions above, the focus term (if any) with instruction to dig deeper on
matches, the anatomy notes, and: "Return 0–8 signals per session; only
signals a reasonable person would act on. Verbatim evidence required — no
paraphrase. Report unreadable files, never skip silently."

## Batching

- Group by project dir first (cross-session repetition within a project is
  the strongest skill signal), then split so a batch stays under ~10 MB of
  transcript: high-priority sessions (from Phase 2 triage) ~5 per batch,
  medium ~10, low/skim ~15.
- Pass triage scores into the prompt so the agent budgets its reading.

## Clustering & decision stage

- Mechanical pass (plain JS in the workflow): group signals by
  `suggested_theme` + family.
- Semantic pass (one agent, all groups): merge synonymous themes, split
  overloaded ones. Output clusters with: theme, family, session_ids
  (deduped), representative evidence (best 2–4 quotes), recurrence count.
- Decision agent per cluster returns:

```json
{
  "type": "object",
  "required": ["verdict", "rationale", "concrete_example", "effort", "leverage"],
  "properties": {
    "verdict": {"enum": ["new-skill", "automation", "fix", "keep-doing", "nothing"]},
    "rationale": {"type": "string", "description": "Recurrence vs build cost, in 2-3 sentences"},
    "concrete_example": {"type": "string", "description": "The actual artifact: draft skill description, exact settings.json line, hook config, improved prompt text, CLAUDE.md addition, etc."},
    "effort": {"enum": ["minutes", "hour", "day"]},
    "leverage": {"type": "integer", "minimum": 1, "maximum": 10}
  }
}
```

Thresholds, ranking, Trend and the `limit` cap all happen in
`scripts/assemble.py`, after the workflow: the workflow returns clusters and
decisions unranked and unfiltered.

## Workflow return value

The script's `return`, exactly this shape. The Workflow tool writes it under
`result` in the output file the task notification names; `assemble.py` reads
that file directly.

```json
{
  "signals_count": 0,
  "unreadable": ["session ids an extractor could not read"],
  "failed_batches": ["labels of batches whose agent failed"],
  "clusters": [{
    "id": "kebab-case slug: the prior edition's id when it is the same issue",
    "title": "...", "family": "friction|repetition|wins|environment",
    "summary": "...", "session_ids": ["..."],
    "evidence": [{"quote": "verbatim", "summary": "...", "session_id": "...",
                  "project": "...", "date": "YYYY-MM-DD", "severity": "high|medium|low"}]
  }],
  "decisions": [{
    "id": "the cluster's id", "verdict": "new-skill|automation|fix|keep-doing|nothing",
    "rationale": "...", "example": "the decision's concrete_example", "example_lang": "json|bash|markdown|text",
    "effort": "minutes|hour|day", "leverage": 1
  }],
  "consolidation": {
    "corroboration": [{"id": "...", "corroborated": true, "note": "what /insights says, one sentence"}],
    "additions": ["a cluster object merged with its decision, for what only /insights surfaced"]
  }
}
```

One decision per cluster, matched by `id`; a cluster with no decision is
skipped and named in `assemble.py`'s output. Keep `evidence` quotes verbatim
and unlabelled (no `User:` prefix, no narration): `verify_quotes.py` drops any
quote it cannot find in the session it cites.
