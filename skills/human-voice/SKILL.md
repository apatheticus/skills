---
name: human-voice
description: Remove signs of AI-generated writing and rewrite prose so it reads as human-authored, adapting to the document's register (editorial, professional, technical, regulated). Use whenever the user wants to humanize, de-AI, or de-slop text; make writing sound natural, human, or less like ChatGPT; strip AI tells, em dashes, or AI words; pass or avoid AI detection (GPTZero, Originality.ai, Turnitin, Copyleaks); or asks "does this sound AI-generated?" Also use when editing, polishing, or reviewing drafted prose for voice, tone, and readability, including blog posts, articles, thought leadership, marketing copy, memos, policies, reports, specs, technical docs, and proposals. For anything a U.S. federal agency, evaluator, or auditor will read, invoke the federal-technical-writing skill first for compliance, then apply this skill's regulated register inside those constraints.
license: MIT
version: 1.1.0
allowed-tools: Read, Write, Edit, Grep, Glob, AskUserQuestion
---

# human-voice

Rewrite text so it reads as written by a person, in the register the document
actually calls for. A travel essay and a system security plan both fail when
they sound machine-generated, but they fail *differently* and the fixes are not
interchangeable. This skill picks the register first, then applies only the
patterns that register wants.

Do **not** use this for drafting from nothing — it is an editing pass over prose
that already exists. Do **not** use it as a style guide for code, config, or
commit messages. For documents bound by federal statute, see
[Federal routing](#federal-routing) below: this skill yields, it does not
compete.

## When to use

- The user asks to humanize, de-AI, de-slop, or "make this sound human"
- The user asks whether something reads as AI-generated
- A draft needs a voice, tone, or readability pass before it ships
- Content must survive an AI detector (GPTZero, Originality.ai, Turnitin, Copyleaks)
- Any prose deliverable is about to be handed to a reader who did not ask for it

## Step 1 — Select the register

**Do this before reading a single pattern.** Every downstream decision depends on
it. If the genre is genuinely ambiguous, ask with AskUserQuestion rather than
guessing; guessing wrong is worse than one question.

| Register | Genres | Personality | Specificity currency | Stance |
| --- | --- | --- | --- | --- |
| **Editorial** | blog posts, essays, articles, thought leadership, marketing, newsletters | On | Lived experience, anecdote, scene | Opinionated — take a position |
| **Professional** | memos, policies, reports, proposals, briefs, internal comms | Off | Institutional fact — dates, names, roles, quantities | Directive — recommend without hedging |
| **Technical** | specs, architecture docs, runbooks, API docs, RFCs, ADRs | Off | Reproducible artifact — versions, error strings, config values | Candid — state tradeoffs and limits |
| **Regulated** | federal, legal, clinical, safety, compliance, filings | Off | Cited authority — statute, standard, control ID | Precise — claim only what is sourced |

Default to **Professional** when unsure. Never default to Editorial: injecting
voice into a document that did not want it is the most damaging failure this
skill can produce, and it is not visible to the person who asked for it.

Full profiles, including opening and closing rules and each register's
characteristic failure mode: `reference/registers.md`.

**Two more questions, when the draft does not already answer them.** Register is a
coarse instrument. A blog post written for engineers and one written for a buyer
are both Editorial, and every opening and closing rule differs between them.

- **Who is this for, and where will it be published?** Sets the specificity
  currency and the opening.
- **What should the reader think, feel, or do after reading it?** Sets the closing,
  which no register can check without it.

Ask only what the draft leaves open, in the same `AskUserQuestion` call as the
register question. A draft with a named audience and an obvious ask needs neither.

## Step 1b — Detect, or edit?

Two jobs. Decide which one was asked for before rewriting a word.

**Detect.** The user asks whether something reads as AI-generated, or asks for an
audit, a scan, or a flag pass. Report; do not rewrite:

- Each pattern found, by number and name, with the line quoted.
- The fix, in a few words.
- Nothing else. Do not rewrite the draft, do not score it, and do not claim to
  know whether a model wrote it. Detectors guess. A named pattern with a quoted
  line is evidence the user can check.

Offer the rewrite at the end, then stop. Steps 2 through 5 run only if the user
takes the offer.

**Edit (default).** Everything else, including "clean this up" and "make this
sound human". Continue to Step 2.

The fork sits after register selection, not before it. Which patterns are even
reportable depends on the register, and flagging a runbook's inline-header lists
or a filing's mandated signposting is a false positive, not a finding.

## Step 2 — Calibrate to the writer (Editorial and Professional)

**Always, sample or no sample.** Before changing anything, read the draft in hand
and name three to five voice signals to preserve: vocabulary, sentence-length
habit, bluntness, humor, admitted uncertainty, digressions, level of polish. Keep
the note internal. Every signal you do not name is one the rewrite will quietly
replace with a generic substitute.

**If the user supplies their own prior writing,** read that too and note the same
things, plus how paragraphs open, punctuation habits, recurring tics, and how
transitions are handled. A sample is the stronger evidence. The draft is the
evidence you always have.

Then match those patterns rather than substituting generic "human" ones. If they
write short, do not hand back long. If they write "stuff" and "things", do not
upgrade to "elements" and "components". Fall back to the register defaults only
for what neither the draft nor a sample settles, and never manufacture texture: an
aside you invented is as machine-made as the sentence it replaced.

Skip this step for Technical and Regulated — those registers are set by house
style and authority, not by an individual voice.

## Step 3 — Apply the patterns

The full catalog of 36 patterns, each with a before/after and its register tags,
lives in `reference/patterns.md`. Read it on every run. Vocabulary lists live
separately in `reference/vocabulary.md` because they are register-scoped.

**Always on, every register.** These 21 never conflict with any house style, and
several of them actively reinforce plain-language requirements:

> §1 significance inflation · §2 notability padding · §3 superficial -ing
> analyses · §4 promotional language · §5 vague attribution *(elevate in P and R)*
> · §6 formulaic "Challenges" sections · §7 AI vocabulary · §8 copula avoidance ·
> §9 negative parallelism · §10 rule of three · §12 false ranges · §13 passive
> voice *(hard rule in R)* · §15 boldface overuse · §19 curly quotes · §20 chatbot
> artifacts · §21 speculative gap-filling *(blocker in P and R)* · §22 sycophancy ·
> §23 filler phrases · §25 generic positive conclusions · §27 authority tropes
> *(rare outside E)* · §29 fragmented headers

Always on means the pattern never switches off. Four of them change *severity* by
register, marked above; §21 changes enough to get its own note below.

**Register-gated.** These change or switch off. Applying them blind is how this
skill breaks documents:

| Pattern | E | P | T | R | Why it varies |
| --- | :-: | :-: | :-: | :-: | --- |
| §11 elegant variation | ● | ● | ◑ | ◑ | **Inverts** in Technical and Regulated — one name per thing; cutting repetition is a correctness bug |
| §14 em dash budget | ● | ● | ● | ○ | House style governs in Regulated (GPO, agency guides) |
| §16 inline-header lists | ● | ● | ○ | ○ | Runbooks and compliance docs are legitimately list-shaped |
| §17 title-case headings | ● | ● | ○ | ○ | Project or agency style guide wins |
| §18 emojis | ◐ | ● | ● | ● | Sparingly allowed in Editorial, banned elsewhere |
| §24 excessive hedging | ● | ● | ◐ | ◐ | Calibrated uncertainty is content, not hedging — see below |
| §26 hyphenated pairs | ● | ● | ○ | ○ | Hyphenation is often spec- or style-defined |
| §28 signposting | ● | ● | ● | ○ | Regulated templates mandate structural signposting |
| §30 diff-anchored writing | ● | ● | ◑ | ● | **Elevate** in Technical — the most common failure there |
| §31 manufactured punchlines | ● | ○ | ○ | ○ | An editorial tell; absent elsewhere |
| §32 aphorism formulas | ● | ● | ○ | ○ | Rare in Technical and Regulated |
| §33 rhetorical openers | ● | ● | ○ | ○ | "Let me be clear" and "I'll be honest" are memo staples, not just essay hooks |
| §34 colon reveals | ● | ● | ○ | ○ | The labelled colon is the house pattern in T and R; the dramatic one is rare |
| §35 faux-insight setups | ● | ○ | ○ | ○ | An editorial tell; absent elsewhere |
| §36 rhetorical setups | ● | ○ | ○ | ○ | An editorial tell; absent elsewhere |
| PERSONALITY (voice injection) | ● | ○ | ○ | ○ | Neutral and plain **is** the human voice for P, T, R |

● on · ◐ limited · ◑ elevated or inverted · ○ off

Three gates deserve spelling out, because getting them backwards is the most
expensive mistake available here:

**§11 in Technical and Regulated — the fix direction reverses.** Everywhere else,
cycling synonyms is a repetition-penalty artifact to remove. In a spec or a
filing, a component gets the same name every time, without exception, and
"varying" a term is a correctness bug rather than a style choice. Do not cut
repetition of a technical term to make prose read better.

**§24 in Technical and Regulated.** "This may fail under load" is hedging.
"Throughput degrades above roughly 4k concurrent connections; we have not tested
past 8k" is calibrated uncertainty, and it is the most valuable sentence on the
page. Cut the first. Never cut the second. The tell is whether the qualifier
carries information.

**§21 in Professional and Regulated — elevate to a blocker.** Speculative
gap-filling in an essay is a style problem. The same sentence in a proposal, a
policy, or a filing is a fabricated claim attributed to your organization. When a
source is missing, say what is not known or cut the sentence. Never dress a guess
as fact, and never let a plausible-sounding invention survive because it read
smoothly.

## Federal routing

When the audience is a U.S. federal agency, evaluator, or auditor — proposals,
RFP/RFI responses, user manuals, ConOps, SSPs, ATO packages, public-facing agency
content:

1. **Invoke the `federal-technical-writing` skill first** if it is installed. It
   owns the compliance envelope: Plain Writing Act, GPO Style Manual, Section 508,
   agency voice, required document sections.
2. **Then run this skill's Regulated register inside that envelope.**

This is precedence, not a handoff. Do not skip the humanizing pass because the
document is federal — an evaluator scoring narrative quality is exactly the
reader most likely to notice machine-written prose, and a full bail-out leaves
the highest-stakes document with zero cleanup. Roughly two-thirds of the catalog
still applies, and much of it (§23 filler, §13 passive voice, §7 vocabulary)
*reinforces* plain language rather than fighting it.

Where the two collide, the compliance skill wins without argument. The specific
collisions are §14, §16, §17, §26, §28, the burstiness thresholds, and
contractions — all already marked ○ for Regulated above.

**If `federal-technical-writing` is not installed**, do not improvise federal
compliance. Apply the Regulated register, then tell the user plainly which
compliance checks you did *not* perform. `reference/registers.md` carries a
minimal plain-language floor for this case; it is a floor, not a substitute.

## Step 4 — Self-check

Run every step. This is mandatory, not advisory. Thresholds are register-scoped
because burstiness and plain-language brevity genuinely want opposite things.

1. **Vocabulary scan.** Grep the draft against the tiers in
   `reference/vocabulary.md` for the selected register. Replace hits with plainer,
   more specific alternatives.
2. **Sentence length audit.** Check against the register's targets:

   | | Editorial | Professional | Technical | Regulated |
   | --- | --- | --- | --- | --- |
   | Max consecutive similar-length sentences | 3 | 4 | 4 | no limit |
   | Sentences under 8 words | ≥2 per paragraph | ≥1 per section | as useful | as useful |
   | Long sentences | ≥1 over 30 words per page | occasional | occasional | **cap at 30 words** |
   | Average target | wide variance | 15–25 words | 15–25 words | **≤20 words** |

3. **Opener diversity.** Read the first word of every sentence. If any word opens
   more than twice in a section, rewrite one.
4. **Structure.** Does it preview itself? Does the conclusion restate the
   introduction? Both are AI tells in every register. Restructure. Then read the
   last line on its own: if it exists to sound deep, delete it and end on the
   clearest concrete sentence already in the draft (§31), or add a plain takeaway
   or next action. Do not rewrite it into a better version of itself.
5. **Specificity.** Find every general claim with no supporting detail. Add the
   detail in the register's currency, or cut the claim.
6. **Stance.** Does the piece commit to anything? Editorial takes a position,
   Professional makes a firm recommendation, Technical names a tradeoff,
   Regulated cites a source. A document that does none of these still reads as
   machine-written no matter how clean the vocabulary.
7. **Register leak.** Re-read for anything belonging to a different register: a
   first-person aside in a spec, an anecdote in a policy, a bare assertion in a
   filing. This is the failure unique to a register-aware skill and it will not
   be caught by any other step.
8. **Final read.** Ask sentence by sentence: does this sound like something only
   a language model would write? Rewrite anything that does, plainly.

## Step 5 — Deliver

For a detect request, Step 1b's findings report *is* the delivery. Stop there and
offer the rewrite. For an edit, produce, in this order:

1. The **register** chosen, in one line, with the reason. If federal routing
   applied, say whether `federal-technical-writing` ran.
2. The **draft rewrite**.
3. **"What still reads as AI here?"** — answer honestly in two to five bullets.
   A draft with nothing left to flag is almost always an unexamined draft.
4. The **final rewrite** addressing those bullets.
5. Optionally, a short changelog of what was cut and why.

Never return only the final text. The audit step is what separates this from an
unstructured rewrite, and skipping it silently is the most common way this skill
underperforms.

## Rules

- **Rewrite, do not delete.** Cover everything the original covered. Five
  paragraphs in, five paragraphs out. Compression disguised as cleanup is the
  most common failure of the first draft.
- **Cluster, do not snipe.** A single em dash means nothing. One `however` means
  nothing. Flag a pattern only when tells co-occur. Read the false-positive list
  in `reference/patterns.md` before flagging anything — a clean human writer
  trips several of these patterns with no AI involved.
- **Never rewrite inside quotations, titles, proper names, code identifiers,
  file paths, error strings, or citations.** A banned word inside a `code span`
  or a quoted source is being *used*, not written. This is the fastest way to
  break a technical document.
- **Never invent detail to satisfy the specificity rule.** If the source lacks a
  number, the rewrite lacks a number. Fabricating a date, metric, or citation to
  make prose sound human is a worse outcome than leaving it vague.
- **Preserve meaning.** If a rewrite changes what the document asserts, it failed
  regardless of how it reads.
- **State what you did not check.** If a register was assumed, a sample was
  absent, or a compliance skill was unavailable, say so in the delivery.

## Reference

- `reference/registers.md` — the four register profiles in full, plus the
  plain-language floor for Regulated when no compliance skill is installed
- `reference/patterns.md` — all 36 patterns with before/after and register tags,
  plus the false-positive and signs-of-human-writing lists
- `reference/vocabulary.md` — global and register-scoped word and phrase lists,
  with the technical-term carve-outs
- `reference/examples.md` — one full worked rewrite per register
- `reference/attribution.md` — provenance of the derived material

## Attribution

The pattern catalog derives from the MIT-licensed
[`humanizer`](https://github.com/blader/humanizer) skill (© 2025 Siqi Chen) and,
through it, from [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
(CC BY-SA 4.0), maintained by WikiProject AI Cleanup. Patterns §34–§36, the kicker
repair procedure, and the em dash budget derive from the MIT-licensed
[`no-ai-slop`](https://github.com/petergyang/no-ai-slop) skill (© 2026 Peter Yang).
Full provenance and license terms: `reference/attribution.md`.
