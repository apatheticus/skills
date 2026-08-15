# GAUNTLET — <thing>

Paste the block below into a fresh Claude Code session at the repository root. It will
not finish on its own — you are the stop condition.

```
GOAL
<one sentence: the destination, no architecture>

FLOOR — what it has to clear
Read .gauntlet/<slug>/ANSWER-KEY.md. That is the standard, and it is the
only standard. Judge nothing that is not on it. Items under Unknown may
not be judged: work that touches one stops and hands back to me.

CEILING — what it is aiming at
<named reference>. Deliberately out of reach. Losing to it never fails
the work; it supplies the next thing to close once the floor is clean.

HOW TO RUN IT
You are the lead. You do not implement anything yourself.
Split the goal into the smallest pieces that can be built and judged on
their own, and decide that split yourself. Say which pieces are safely
parallel and which are gated behind another.
Per piece: a builder subagent produces the artifact and its evidence.
Then a separate subagent, fresh context, audits it under
.gauntlet/<slug>/critic-contract.md — artifact and answer key only,
never the builder's reasoning. A new critic on every retry.
Win or tie passes. A loss returns one gap, and that gap is the next
brief. Keep looping. There is no round count.
Keep .gauntlet/<slug>/LEDGER.md current: piece, round, verdict,
evidence, and what is parallel versus gated.
Done means every bar check critic-verified, one smoothing pass over the
assembled whole, and every pending human gate listed for me.

STOPS THAT OUTRANK THIS LOOP
<hard stops: approvals, irreversible actions, spend, external sends>
BLOCKED on any Unknown ends the loop and hands back to me.
I am the stop condition.
```

## Derived — confirm before running

<!-- Up to three. Anything inferred rather than heard, any ambiguous gate, any
     assumption worth a yes before a long run starts. Delete the section if empty. -->

- **DERIVED** — <what was inferred, and what it was inferred from>
