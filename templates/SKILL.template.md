---
name: skill-name
description: <What the skill does, concretely, in one clause>. Use when <trigger>, <trigger>, or the user says "<literal phrase>".
# Optional — delete what you do not need:
# allowed-tools: Read, Grep, Glob, Bash
# disable-model-invocation: true      # only runs when the user types /skill-name
# argument-hint: <pr-number>
# version: 0.1.0
---

# Skill Name

One or two sentences on what this does and what the user gets at the end.

## When to use

- <situation that should trigger this>
- <another situation>

Do **not** use this for <the adjacent thing it gets confused with> — use <alternative> instead.

## Steps

### 1. <First action>

Imperative instructions to the agent. Name exact commands, files, and flags.

```bash
<command>
```

### 2. <Second action>

Say what "done" looks like and how to verify it against reality, not against
assumptions.

### 3. Report back

What to tell the user: paths touched, commands run, output to quote.

## Rules

- <a hard constraint the agent must not violate>
- <a failure mode seen before, and what to do instead>

## Reference

Move anything long here and link it, so it loads only when needed:

- `reference/<topic>.md` — <what is in it>
