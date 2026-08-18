---
name: human-voice
description: Remove signs of AI-generated writing and rewrite prose so it reads as human-authored, adapting to the document's register (editorial, professional, technical, regulated). Use whenever the user wants to humanize, de-AI, or de-slop text; make writing sound natural, human, or less like ChatGPT; strip AI tells, em dashes, or AI words; pass or avoid AI detection (GPTZero, Originality.ai, Turnitin, Copyleaks); or asks "does this sound AI-generated?" Also use when editing, polishing, or reviewing drafted prose for voice, tone, and readability, including blog posts, articles, thought leadership, marketing copy, memos, policies, reports, specs, technical docs, and proposals. For anything a U.S. federal, state, or local government agency, evaluator, or auditor reads, apply the regulated register inside the Plain Writing Act and Federal Plain Language Guidelines envelope in plain-language.md.
when_to_use: Also use it as a detector rather than an editor — audit, scan, or flag a draft for AI tells without rewriting it. Trigger on a request naming one specific tell — hedging, passive voice, filler, fluff, buzzwords, corporate speak, jargon, sycophancy, boldface overuse, emojis, curly quotes, title-case headings, signposting, rule of three, negative parallelism ("not just X, but Y"), self-answered rhetorical questions, aphorisms, manufactured kickers, synonym cycling, or promotional language. Genres also include cover letters, email, LinkedIn and social posts, grant narratives, executive summaries, runbooks, ADRs, and release notes.
license: MIT
version: 1.3.0
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, AskUserQuestion
---

# human-voice

Rewrite text so it reads as written by a person, in the register the document
actually calls for. A travel essay and a system security plan both fail when
they sound machine-generated, but they fail *differently* and the fixes are not
interchangeable. This skill picks the register first, then applies only the
patterns that register wants.

Do **not** use this for drafting from nothing — it is an editing pass over prose
that already exists. Do **not** use it as a style guide for code, config, or
commit messages. For documents written for a government reader, see
[Government documents](#government-documents) below: the plain-language envelope
constrains the rewrite, it does not replace it.

## When to use

- The user asks to humanize, de-AI, de-slop, or "make this sound human"
- The user asks whether something reads as AI-generated
- A draft needs a voice, tone, or readability pass before it ships
- Content must survive an AI detector (GPTZero, Originality.ai, Turnitin, Copyleaks)
- Any prose deliverable is about to be handed to a reader who did not ask for it

## Step 1 — Select the register

**Do this before reading a single pattern.** Every downstream decision depends on
it. If the genre is genuinely ambiguous, ask with AskUserQuestion rather than
guessing. The bad outcome this one question prevents: a spec or a policy handed
back with an essayist's voice injected into it, which the person who asked will
not notice and cannot easily undo.

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

**Ask once per document set, not once per file.** When a register has already been
established for this body of work — the user named it, an earlier file in the same
pass settled it, or the surrounding documents obviously share a genre — reuse it
and say which one you are reusing in the delivery. Re-asking on every file of a
docs directory trains the user to answer without reading, which is the one time
the question would have mattered.

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

The catalog is 36 patterns, split across two files by whether the register can
switch them off. Load the one the register asks for:

| File | Contents | Read it |
| --- | --- | --- |
| `reference/patterns-core.md` | The 21 always-on patterns, plus the false-positive list and the signs-of-human-writing list | Every run |
| `reference/patterns-gated.md` | The 15 register-gated patterns, plus personality injection and the gate table | Only when the register turns at least one on |

Every register turns on something in the gated file, so in practice both load for
Editorial and Professional work. Technical and Regulated turn on a handful — §11,
§24 and §30 for Technical, §11, §18, §24 and §30 for Regulated — so read the gate
table and those sections rather than the whole file.

Vocabulary lists live separately in `reference/vocabulary.md` because they are
register-scoped, and Step 4 explains when to open them.

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

**Register-gated.** The 15 that change or switch off, plus personality injection,
are tabled with their reasons in `reference/patterns-gated.md`. Applying one blind
is how this skill breaks documents, so read that table before touching any of
them.

Three gates deserve calling out here, because getting them backwards is the most
expensive mistake available and the fix runs opposite to the obvious one:

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

## Government documents

When the audience is a U.S. federal, state, or local government agency,
evaluator, or auditor — proposals, RFP/RFI responses, user manuals, ConOps, SSPs,
ATO packages, public-facing agency content — select the Regulated register and
add the plain-language envelope in `reference/plain-language.md`. That file is
government-scoped and loads for nothing else.

**What the statute actually requires.** The Plain Writing Act of 2010
(Pub. L. 111-274) obliges agencies to write *covered documents* — the material a
member of the public needs to obtain a benefit, comply with a requirement, or
file taxes — in plain writing. Regulations are excluded by definition, and §6
forecloses judicial review, so there is no compliance finding to certify against.
The defensible claim in a delivery is "written to the Federal Plain Language
Guidelines". "Plain Writing Act compliant" is not a claim anyone can make, and
this skill never makes it.

Do not skip the humanizing pass because the document is governmental — an
evaluator scoring narrative quality is exactly the reader most likely to notice
machine-written prose, and a full bail-out leaves the highest-stakes document
with zero cleanup. Roughly two-thirds of the catalog still applies, and much of
it (§23 filler, §13 passive voice, §7 vocabulary) *reinforces* plain language
rather than fighting it.

Where the envelope collides with a pattern, the mandated template or the agency's
own style guide wins without argument. The specific collisions are §14, §16, §17,
§26, §28, the burstiness thresholds, and contractions — all already marked ○ for
Regulated above.

**Do not improvise the rest of federal compliance.** Section 508, the GPO Style
Manual, agency voice guides, and mandated section structures are outside this
skill entirely. Apply the register and the envelope, then tell the user plainly
which checks you did *not* perform. `reference/plain-language.md` names them, and
`reference/registers.md` carries the condensed floor.

## Step 4 — Self-check

Run every step. This is mandatory, not advisory. Thresholds are register-scoped
because burstiness and plain-language brevity genuinely want opposite things.

**Steps 1 through 3 are countable, so count them rather than eyeballing them.**
`scripts/voice_check.py` does the arithmetic — vocabulary tiers, sentence-length
distribution, opener repetition, dash and quote and emoji counts, boldface
density, heading case — and skips code spans, fenced blocks, link targets and
quoted material so a banned word inside a `code span` is never reported:

```bash
python3 scripts/voice_check.py <file> --register E|P|T|R
```

The checker is optional. It is an accelerator for the three mechanical steps
below, not a gate on the skill: without Python, do those steps by reading, and say
in the delivery that you counted by hand. What it cannot do is judge — every
Tier-2 hit comes back as a `QUERY`, never a replacement, for the reason
`reference/vocabulary.md` gives.

1. **Vocabulary scan.** Tier 1 and Tier 3 are mechanical and every hit is a
   defect; replace with plainer, more specific alternatives. Open
   `reference/vocabulary.md` when the checker returns a `QUERY` (Tier 2 — apply
   the carve-out rule and the delete-and-reread test) or a Tier 2b hit, where the
   same sense is legal in one register and not another. **For a government
   audience,** also run the federal substitution table in
   `reference/plain-language.md`; it carries pairs the global tiers do not.
2. **Sentence length audit.** Check against the register's targets:

   | | Editorial | Professional | Technical | Regulated |
   | --- | --- | --- | --- | --- |
   | Max consecutive similar-length sentences | 3 | 4 | 4 | no limit |
   | Sentences under 8 words | ≥2 per paragraph | ≥1 per section | as useful | as useful |
   | Long sentences | ≥1 over 30 words per page | occasional | occasional | **cap at 30 words** |
   | Average target | wide variance | 15–25 words | 15–25 words | **≤20 words** |

   The Regulated column's ≤20 average and 30-word cap come from the Federal Plain
   Language Guidelines and are written for a government reader. In non-government
   Regulated work — clinical, legal, safety — treat them as targets rather than
   the hard cap they are for an agency document.

3. **Opener diversity.** Read the first word of every sentence. If any word opens
   more than twice in a section, rewrite one.
4. **Structure.** Does it preview itself? Does the conclusion restate the
   introduction? Both are AI tells in every register. Restructure. Then read the
   last line on its own: if it exists to sound deep, delete it and end on the
   clearest concrete sentence already in the draft (§31), or add a plain takeaway
   or next action. Do not rewrite it into a better version of itself. **For a
   government audience,** also apply §G4 in `reference/plain-language.md` — the
   main idea comes before its exceptions and conditions, never after them.
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

1. The **register** chosen, in one line, with the reason. For a government
   document, say that the plain-language envelope was applied and name the checks
   that were not performed — Section 508, GPO style, agency style guides,
   mandated section structures, and testing with real readers.
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
  in `reference/patterns-core.md` before flagging anything — a clean human writer
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
  absent, or a compliance area sits outside this skill, say so in the delivery.

## Reference

- `reference/registers.md` — the four register profiles in full, plus the
  condensed plain-language floor for Regulated
- `reference/plain-language.md` — **government audiences only.** The Plain Writing
  Act, the Federal Plain Language Guidelines, §G1–§G7, the federal substitution
  table, and what this skill does not cover
- `reference/patterns-core.md` — the 21 always-on patterns with before/after,
  plus the false-positive and signs-of-human-writing lists. Read every run
- `reference/patterns-gated.md` — the 15 register-gated patterns, personality
  injection, and the gate table. Read when the register turns one on
- `reference/vocabulary.md` — global and register-scoped word and phrase lists,
  with the technical-term carve-outs
- `reference/examples.md` — one full worked rewrite per register
- `reference/attribution.md` — provenance of the derived material
- `scripts/voice_check.py` — optional checker for the countable half of Step 4;
  `scripts/test_voice_check.py` is its test suite

## Attribution

The pattern catalog derives from the MIT-licensed
[`humanizer`](https://github.com/blader/humanizer) skill (© 2025 Siqi Chen) and,
through it, from [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
(CC BY-SA 4.0), maintained by WikiProject AI Cleanup. Patterns §34–§36, the kicker
repair procedure, and the em dash budget derive from the MIT-licensed
[`no-ai-slop`](https://github.com/petergyang/no-ai-slop) skill (© 2026 Peter Yang).
Full provenance and license terms: `reference/attribution.md`.
