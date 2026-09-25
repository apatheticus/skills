# Registers

Five profiles. Pick one in Step 1 of `SKILL.md` before reading any pattern.

The register is not a style preference — it decides which of the 36 patterns run,
which vocabulary tier applies, and what "sounds human" even means for this
document. A spec that reads like an essay has failed just as badly as an essay
that reads like a spec.

---

## Editorial

**Genres.** Blog posts, essays, articles, thought leadership, marketing copy,
newsletters, personal writing, social posts.

| Field | Value |
| --- | --- |
| Personality | **On** — this is the only register where voice injection is correct |
| Specificity currency | Lived experience: anecdote, scene, sensory detail, the thing that actually happened |
| Stance | Opinionated. Take a position and defend it |
| Person | First person freely |
| Contractions | Yes |
| Lists | Avoid. Prose carries analysis; bullets fragment it |
| Opening | A specific, unexpected hook. Never a broad generalization about the state of an industry |
| Closing | The strongest concrete thing in the piece. Never a summary of what was just said, and never a manufactured aphorism (§31, §32) |
| Sentence policy | Widest variance of any register. Fragments are allowed. One-sentence paragraphs land hard |

**Voice work.** Avoiding AI patterns is only half the job here — sterile,
voiceless prose is just as detectable as slop. Signs a draft is clean but dead:
every sentence the same length, no opinions, no acknowledged uncertainty, no
humor or edge, reads like a press release.

Fixes: react to facts rather than reporting them; vary rhythm deliberately
(short punchy sentence, then a longer one that takes its time getting where it is
going); keep the mess the writer already put there — tangents, asides, and
half-formed thoughts are human, and smoothing them out is what makes structure
read as algorithmic.

Keep, do not manufacture. An aside you invented is not the writer's voice, it is
generic texture in place of generic polish. Step 2 of `SKILL.md` names three to
five signals out of the draft itself for exactly this reason: the material to
preserve is already on the page.

**Characteristic failure mode.** Over-compression. The first rewrite strips the
AI tells *and* the texture, returning something clean, short, and lifeless. Cover
everything the original covered.

---

## Professional

**Genres.** Memos, policies, reports, briefs, internal comms, executive
summaries, board material. A proposal or anything else a client could hold you
to is **Commercial**, not Professional.

| Field | Value |
| --- | --- |
| Personality | **Off**. Neutral and plain *is* the human voice here |
| Specificity currency | Institutional fact: dates, names, roles, quantities, decisions, owners |
| Stance | Directive. Recommend firmly; hedged recommendations are not recommendations |
| Person | "We" for the organization. First-person singular rarely |
| Contractions | Sparingly. Never in formal policy |
| Lists | Only for genuine enumerations — steps, requirements, options. Never for analysis |
| Opening | State the purpose in the first sentence. No executive-summary throat-clearing |
| Closing | A decision, an ask, or an owner and a date. Not a restatement |
| Sentence policy | 15–25 word average, moderate variance, at least one short sentence per section |

**§33 and §34 apply here, not only in Editorial.** "Let me be clear" and "I'll be
honest" are memo and all-hands staples, and a colon reveal in an executive summary
is the same withholding trick it is in an essay. Cut both. A colon that labels
content — "Next steps:", "Decision needed:" — stays.

**Elevate §21 (speculative gap-filling) to a blocker.** An unsourced claim in an
essay is a style problem. The same sentence in a policy or a proposal is a
fabricated assertion attributed to the organization. If the source is missing,
write what is not known or cut the sentence.

**Characteristic failure mode.** Diplomatic mush. Every recommendation softened
until the document commits to nothing. Reads as machine-written because
equivocation is the model default.

---

## Technical

**Genres.** Specs, architecture docs, runbooks, API documentation, RFCs, ADRs,
design docs, incident write-ups, README bodies.

| Field | Value |
| --- | --- |
| Personality | **Off** |
| Specificity currency | Reproducible artifact: versions, config values, error strings, commands, file paths, measured numbers |
| Stance | Candid. Name the tradeoff, the limit, the thing that does not work |
| Person | Second person for instructions ("run", "set"). Imperative mood for procedures |
| Contractions | Match the project's existing docs |
| Lists | **Freely.** Procedures, parameters, and requirements are legitimately list-shaped — §16 and §17 are off |
| Opening | The thing itself. No preamble about why the topic matters |
| Closing | Stop when the last step is documented |
| Sentence policy | 15–25 word average. Precision beats variance; do not manufacture burstiness at the cost of clarity |

**Terminology consistency inverts §11.** Elegant variation is bad everywhere, but
here it is a correctness bug: the same component gets the same name every single
time. Never cycle synonyms for a technical term to avoid repetition.

**Elevate §30 (diff-anchored writing).** The most common AI tell in technical
docs is prose that narrates a change rather than describing the system: "this
function was added to replace the previous approach". Unless the document is
version-scoped (changelog, migration guide, release notes), it must read
coherently to someone who has never seen the prior version.

**§24 is limited, not off.** "This may fail under load" is hedging — cut it.
"Throughput degrades above roughly 4k concurrent connections; untested past 8k"
is calibrated uncertainty and is the most valuable sentence on the page. The test
is whether the qualifier carries information.

**Characteristic failure mode.** Confident vagueness. Fluent prose that never
names a version, a number, or a failure condition, and would apply to any system
if you swapped the nouns.

---

## Regulated

**Genres.** Federal documentation, legal filings, clinical and safety
documentation, compliance and audit material, regulatory submissions.

| Field | Value |
| --- | --- |
| Personality | **Off** |
| Specificity currency | Cited authority: statute, standard, control ID, section reference |
| Stance | Precise. Claim only what is sourced |
| Person | Per the governing style guide |
| Contractions | Per the governing style guide. In a U.S. government document the Federal Plain Language Guidelines affirmatively recommend them; an agency style guide may still override |
| Lists | **Required** where they aid comprehension. §16 and §17 are off |
| Opening | Per the mandated template |
| Closing | Per the mandated template |
| Sentence policy | **Cap any sentence at 30 words; target ≤20 average.** Plain-language brevity outranks burstiness here — this is the one register where the anti-detection goal loses |

**Government audiences take an extra file.** Regulated is wider than government
work — clinical, legal and safety documents live here too. When the reader *is* a
U.S. federal, state or local government one, load
`reference/plain-language.md` alongside this profile. It carries the Plain
Writing Act frame, §G1–§G7, and the federal substitution table. See "Government
documents" in `SKILL.md`.

**Off in this register:** §14 (em dashes), §16 (inline-header lists), §17 (title
case), §26 (hyphenated pairs), §28 (signposting — mandated templates require
structural signposting), personality injection, and the burstiness thresholds.
Everything else in the always-on set still applies and mostly reinforces plain
language.

**Elevate §21 to a blocker,** for the same reason as Professional, with higher
stakes: a fabricated citation in a regulatory document is a finding, not a typo.

**Characteristic failure mode.** Two opposite ones. Either the humanizing pass
strips a mandated structure, or it is skipped entirely and an evaluator reads
obviously machine-written narrative. Both are avoidable; neither is rare.

### Plain-language floor (government audiences)

Apply this floor whenever the reader is a U.S. federal, state or local government
one, then tell the user explicitly which checks you did not perform. It is the
condensed form of `reference/plain-language.md`; load that file for the full
envelope and the worked examples.

- **Active voice.** "The agency reviews the application", not "The application is
  reviewed by the agency". Passive is acceptable only when the actor is genuinely
  unknown or irrelevant.
- **Common words.** *help* not *facilitate*; *use* not *utilize*; *show* not
  *demonstrate*; *start* not *commence*; *about* not *regarding*.
- **Short sentences.** ≤20 word average, hard cap 30. Break embedded lists out of
  prose into real lists.
- **Address the reader.** "You" for the reader, "we" for the organization, rather
  than "the applicant" where "you" works.
- **Concrete examples.** Every abstract requirement gets an example nearby.
- **Define once.** Spell out each acronym on first use.

Five more, each covered in full in `reference/plain-language.md` — pointers
rather than restatements, because the examples are what make them usable:

- **§G1 hidden verbs.** *decide*, not *make a determination*.
- **§G2 noun strings.** Break any run of three or more stacked nouns.
- **§G3 positive language.** No double negatives, no exceptions to exceptions.
- **§G4 main idea first.** The rule comes before its conditions and exceptions.
- **`must`, not `shall`.** Keep `shall` only inside quoted statutory text or a
  mandated template.

This is a floor, not a substitute. It covers none of Section 508, none of the GPO
Style Manual, no agency style guide, none of the mandated section structures, and
no testing with real readers. Say so.

---

## Commercial

**Genres.** Client-facing commercial documents: proposals, pitch and capability
material, RFP, RFI, DDQ and PEP responses, case studies, one-pagers, statements
of work, work orders, task orders, engagement letters, MSA schedules, term
sheets, letters of intent, and amendments to any of these.

| Field | Value |
| --- | --- |
| Personality | **Off** |
| Specificity currency | Commercial fact: the party, the quantity, the period, the named artefact, the date, the price, the acceptance test. For an outcome figure, the client, the measurement basis and its approval for external use |
| Stance | Definite. Commit to exactly what is priced — no wider (overselling, open-ended duties) and no narrower (self-deprecating framing, bare disclaimers) |
| Person | The named party in every obligation: "Supplier will…", "Client will…". Never "we" or "you" in operative text. First person only in a cover note |
| Contractions | No |
| Lists | Numbered enumerations, freely. Never three bolded lead-ins (§16), which read as a pitch deck |
| Opening | Brief factual background, the business problem in one sentence, then the purpose: "This Document covers…". Where the client has stated the problem in their own request, restate it from their document and cite it. No section opens on a value proposition. A scope summary is a flat run of declaratives naming the performing party ("Supplier will design… Client will provide…") that closes on the outcome stated plainly |
| Closing | The mechanism and its timer, stated flatly: effective date, acceptance, change control. Never a summary or a value line |
| Sentence policy | 15–30 words per sentence, one obligation or claim per sentence, and no subordinate clause chained across a scope boundary. Over 30 words is a rewrite candidate everywhere; the ~35-word split for the scope summary is a cap for that section, not a licence elsewhere. No burstiness target: flat, even, definite prose is the human voice here |

**Load `reference/commercial.md` with this profile, every run.** It carries the
split between operative and non-operative text, which decides how strictly every
other rule applies, plus §C1–§C16 and the Commercial word lists. The profile
above is the summary; that file is the rule set.

**Three skill-wide rules change here.**

- **"Rewrite, do not delete" narrows to "relocate, never delete a disclosure".**
  Every exclusion, assumption, dependency, cap and risk statement survives, moved
  if needed. Methodology narration and a limit restated in a second place are
  cut, because in a contract the repetition is a second term that can disagree
  with the first.
- **Step 2 calibration is skipped.** The client's paper and the house template set
  the voice, not an individual writer.
- **§21 is a blocker,** as in Professional, with a commercial edge: an outcome
  figure without its client, basis and approval status is an unsupported claim
  the evaluator will score down or the client will quote back.

**Government buyers.** A commercial document addressed to a U.S. federal, state
or local agency — a proposal, an RFP or RFI response — stays **Commercial** and
also takes the plain-language envelope in `reference/plain-language.md`. Where
they collide, Commercial wins on who owes what (named party, will/may/must) and
on person throughout the Document, so the envelope's "you" and "we" apply only
where `commercial.md` §1 allows first person; the envelope governs the rest, and the solicitation's mandated
format (Section L, page limits, volume structure) wins on layout. Government
documents that are not commercial — user manuals, ConOps, SSPs, ATO packages,
public-facing agency content — stay Regulated.

**Characteristic failure mode.** Two opposite ones, both common. Overselling:
intensifiers, unquantified benefits and pitch-deck rhythm that read as a promise
nobody priced. Self-sabotage: every limit kept, but worded so the document is
honest and framed to lose money. §C10–§C16 exist for the second one, which no
other register guards against.

**Outside this skill.** Deliverables tables, acceptance-test mapping, pricing and
milestone tables that foot, checks on the rendered PDF or Word file, and the
audit of the pricing model behind every number. A separate contracts review
covers them. When none ran, say in the delivery that these checks were not
performed.
