# grill — the interview

Interview the user until you reach a shared understanding. This is where the answer
key actually comes from: the checks are not generated at the end, they are extracted
here, one at a time, while the decision is still fresh.

The decisions belong to the user. An interview where you supply both sides has
produced nothing — it is your opinion with extra steps, and it will read as a
standard on camera while being a guess underneath.

SKILL.md holds the two check forms, the no-score rule, the reference rule, and the
two-strangers test. They are not restated here; this file is the mechanics of getting
to them.

## The design tree

Map the space as a **design tree**: every decision branches into the decisions that
hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites
are already settled — the questions you can ask *now* without guessing at answers you
have not heard yet. Ask the whole frontier in one round, then wait.

A question whose answer depends on another question still open in this round belongs
to a *later* round, not this one.

Format each question like this:

```
❓ **Q1** — **<short title>**: <the question, in plain language. Offer concrete
options where there are some.>

➡️ <your recommended answer, and one line on why>
```

Give a recommendation every time. A question with no recommendation makes the user do
all the work, and the point is to make deciding fast, not to hand them a blank form.

Each round of answers reshapes the tree — settled decisions push the frontier
outward. Recompute and ask the next round.

## Finding facts is your job, never the user's

When a question needs a fact — how something currently behaves, what a service
charges, what is already in the project — go and get it. Dispatch a background agent
against primary sources rather than asking the user something you could look up.

Do not block on it. A running lookup is an unsettled prerequisite, so only the
questions downstream of it wait. Ask the rest of the frontier now.

Two things follow when the lookup returns. A found fact usually makes a `run it`
check, because the fact *is* the check. And if the research does not settle it — "the
docs do not say," "it depends how you configure it" — do not decide for the user:
convert it into a grilling question and put it in the running order. If the honest
finding is "you would only know by running it," that is an Unknown.

## The follow-up that produces the bar

After the user settles a question, ask one more thing before moving on:

> **"How would you know if this came out wrong?"**

Push until the answer is something a stranger could act on. The ladder:

- **Too vague:** "the billing should work properly"
- **Still too vague:** "upgrades should charge the right amount"
- **Usable:** "upgrading to annual mid-month charges only the difference, prorated by
  days remaining" → **run it**
- **Usable:** "the checkout reads as trustworthy at a glance" → **A/B pick** against
  Stripe's checkout page

If the honest answer is "you would only know by running it with real users" — say so
and mark it. That is a genuine unknown, and it belongs in the answer key's Unknown
section, where it does more good than a fabricated check.

## Two modes

**Naming the destination** (first, before any question exists). Narrow until you have
one or two sentences describing what done looks like. Then ask the scope question
explicitly:

> *"What would you consider out of bounds here — things that would make this worse if
> someone added them?"*

Those seed **Out of scope**, and they are the only defence against a critic that tries
to win by piling on features.

**Charting breadth-first** (right after). Fan out across the *whole* space rather than
going deep on any one thread. You are looking for the shape of what is unknown, not
for answers. Two things come out:

- questions you can phrase sharply now → **Open questions**
- things you can tell are coming but cannot phrase sharply → **Not yet specified**

## Gates

Answer these before leaving the interview. A no is a reason to keep going, not a
finding to note and move past.

1. Has every question in this round been answered by the **user**, rather than by you
   on their behalf?
2. Does every answered question carry a check, a `judged by`, and a reference (or `—`)?
3. Is the frontier empty — every branch visited, nothing silently assumed?
4. **Did anything land in the fog?** If **Not yet specified** is empty after charting,
   stop and tell the user the effort is small enough to just do. Do not write a map.
   This gate exists to prevent a padded answer key: manufacturing questions to look
   thorough produces a document that looks like a standard while being filler, and
   filler on a bar is worse than no bar, because a critic will grade against it.
5. Has the user confirmed you have reached a shared understanding? Do not act on any
   of it until they have.
