# gauntlet — emit the runnable prompt

Write `.gauntlet/<slug>/GAUNTLET.md`: one fenced block a person can paste into a fresh
Claude Code session, plus up to three bullets flagging what you had to derive.

The answer key is the floor. This file is what makes the floor run.

## What the loop is

```
CONTRACT   the lead writes a delegation contract for one piece:
           what to build, what evidence to produce, what it may not touch
     |
     v
BUILD      a builder subagent produces the artifact and the evidence
           (screenshot, test output, rendered page, running binary, draft)
     |
     v
AUDIT      a fresh critic subagent receives: goal, answer key, artifact, evidence
           NOT: builder rationale, prior critic notes
     |
     +--> WIN or TIE ---> passed, log the evidence
     |
     +--> LOSS ---------> one gap, back to CONTRACT as the new brief
```

Five things hold it up. Break any one and it collapses into an ordinary "do it well and
check your work" prompt, which fails predictably.

1. **Goal, not implementation.** State the destination. Do not prescribe the
   architecture, the module list, or the technology inside the stack. Real constraints
   the user actually named stay; incidental architecture goes.
2. **A bar a critic can open.** "Amazing," "production-ready" and "keep improving it"
   are not bars. The answer key is the bar precisely because every row of it is
   openable, runnable, or viewable.
3. **The lead decides the split.** Not you, not the user. The prompt says *split it*;
   it never lists the pieces.
4. **The builder never grades itself.** Separate agent, fresh context, no builder
   reasoning, a new one per retry.
5. **No round count.** Not three passes, not "iterate twice." The human is the brake.

And a sixth, for anything that is not a toy: **human gates outrank the loop.** "Keep
going until perfect" must never be able to self-approve a sign-off, a deploy, a send, or
a spend.

## The template

Copy `assets/GAUNTLET.template.md` and fill in the four angle-bracket slots — the goal,
the ceiling reference, the hard stops, and the derived bullets. That file is the only
copy of the prompt text; do not retype it here or anywhere else, because a second copy
drifts and the one people paste is whichever they found first.

Target under 300 words inside the fence. The template ships at 253, which leaves room
for a real goal and a real list of stops and not much else — that is the intended
squeeze. Length is not control here, and every sentence of prescribed implementation is
a sentence of the lead's judgment thrown away.

Copy `reference/critic-contract.md` into `.gauntlet/<slug>/critic-contract.md` when you
write this file, so the pasted prompt points at something that exists in the engagement
folder rather than inside an installed skill the next session may not have.

## Harness verbs

Claude Code only. The three that matter:

- **Subagents** run in their own context window. This is the mechanical basis for the
  blind critic — everything else is convention, this one is enforcement.
- **`/loop`** re-runs a prompt on an interval, or self-paced against a stop condition.
- **`ultracode`** fans substantive tasks across parallel subagents without being asked.

Name them as activation phrases in the prompt only when they earn their words: *fan out
subagents*, *a separate harsh critic subagent per piece*, *use ultracode*. Harness verbs
change often enough that a prompt pinned to a specific command ages badly — confirm
against the current documentation before writing one in, and prefer the plain
description (*a separate subagent in fresh context*) which does not go stale.

Two cautions worth passing to the user in a sentence: `ultracode` applies to every
substantive task in the session, including routine edits, and token cost on a long run
is open-ended with no hard per-goal cap.

## Compose-only

The default is compose-only: write `GAUNTLET.md` and stop. The user pastes it wherever
they want it run — often a different session, often a different day.

Run it here only if the user asks. Even then, the loop does not finish on its own and
the user is the stop condition; say that out loud rather than leaving them watching.

## What this skill does not build

The method is prompt-level. Do not build a harness, a state machine, a scoring
framework, a capture suite, or a runner around it. The prompt *is* the method, and every
agent asked to produce one reflexively reaches for scaffolding it does not need.

## Self-check before writing the file

Answer all ten. Any no is a rewrite, not a note.

1. Is the mission a destination rather than a plan, and bound to the answer key?
2. Is the bar named concretely — the answer key for the floor, one openable thing for
   the ceiling — with a reachable/unreachable flag on the ceiling?
3. Is the lead explicitly forbidden from implementing?
4. Is the cycle stated as contract → build → blind audit → one gap → repeat, with a
   fresh critic per retry?
5. Does the fan-out instruction delegate the decomposition to the lead, and does it ask
   for the parallel-versus-gated split?
6. Are the harness verbs the minimum that activates the harness, and nothing more?
7. Is there a live ledger requirement?
8. Are hard stops and human gates stated as superior to the loop?
9. Is "done" defined — every bar check critic-verified, a smoothing pass over the
   assembled whole, every pending human gate listed?
10. Is the runnable block under 300 words?

Then reject and rewrite if the draft contains any of:

- a prescribed architecture, module list, or technology decision the user did not name
- a number of rounds, iterations, or passes — anywhere in the text
- a bar that is an adjective rather than an artifact
- any instruction that lets one agent both build and judge
- missing hard stops when the work can touch production, spend money, send
  communications, or alter records
