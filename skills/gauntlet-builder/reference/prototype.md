# prototype — make something rough to react to

Some questions cannot be talked out. "How should this look," "how should this feel to
use," "does this flow make sense" — the user does not know until they see something.
Asking harder does not help; building something rough does.

It also solves the hardest problem in the whole method: **what do you compare against
when there is no famous thing to point at?** Most work has no Stripe to hold up beside
it. So you build a rough version, the user reacts to it, and **the thing you built
becomes the reference** — a real, openable artifact where before there was only an
adjective.

## Build it rough, and mean it

1. **Throwaway from the first line, and obviously so.** Name it so nobody mistakes it
   for the real thing.
2. **One command or one double-click to run.** If the user has to think about how to
   start it, the prototype has already failed.
3. **No persistence, no tests, no error handling, no abstractions.** You are buying a
   reaction, not building a foundation.
4. **Several variations, not one.** One version gets you "yeah, fine." Three genuinely
   different versions get you "that one, but the header from the second." Make them
   differ in the thing actually being decided, not in colour.
5. **Make switching between them trivial** — a toggle, a URL parameter, tabs. The user
   should be able to flip back and forth in a second.

## The user picks

Show the variations and do not choose. Do not narrow to a favourite and present it as
the outcome. Do not say "I went with the second one because it is cleaner."

Picking is the decision, the decision is the user's, and an agent that builds three
options and quietly selects one has replaced the interview with its own taste — which
is the exact thing this skill exists to prevent.

Ask which one, and why. The *why* matters as much as the pick, because it is usually a
general principle in disguise, and general principles produce more checks than a single
answer does.

## Parking it as a reference

Once the user has picked:

1. **Keep the chosen prototype in a form that still opens.** Do not delete it when the
   decision is folded in — it is now a **reference**, and a reference that cannot be
   opened is worth nothing.

   This is stricter than it sounds. Whoever grades the finished work is a stranger in a
   fresh session, possibly weeks later, with no idea how this project runs. A prototype
   that needs `pnpm dev`, a scratch database, and the right branch checked out is not a
   reference to that person — it is a dead link.

   So park it as **one of two things**:
   - **a single self-contained file that opens on a double-click** — one HTML file with
     everything inlined, no build step, no server, no dependencies; or
   - **a screenshot**, if what was decided is purely how it looks.

   If the chosen prototype is not already one of those, convert it before recording the
   decision. Inline the styles, stub the data, save the file.

2. **Save it inside the engagement folder** — `.gauntlet/<slug>/refs/<name>.html` or
   `.png` — and record that exact relative path in the answer. The linter resolves
   every `A/B pick` reference as a real path, so a reference parked outside the folder
   or recorded with the wrong name reds the build rather than dying quietly at judging
   time.

3. **Write the answer** into the map: what was picked, why (the user's words, not your
   summary of them), and the check.

4. **The check for a prototype question is almost always `A/B pick`**, with this
   prototype as the reference. That is the point of having built it.

Occasionally the reaction produces a hard rule — "the empty state must always tell you
what to do next." That is a `run it` check, and it is better than the A/B. Take it when
it appears.

## When the prototype changes the question

A prototype often reveals that you were asking the wrong thing. The user sees it and
says "actually, none of these — the whole flow is wrong."

That is a success, not a wasted round. Rewrite the question, re-order the list, and say
plainly what changed. Finding this out now is worth more than the prototype cost.

## Gates

1. Did the **user** pick, in their own words?
2. Is the chosen prototype parked as one double-clickable file or one image, inside
   `.gauntlet/<slug>/refs/`?
3. Does the recorded reference path resolve? Run the linter — a dead reference is the
   failure mode this whole section exists to prevent.
