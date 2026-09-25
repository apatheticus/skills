# Commercial — client-facing commercial documents

**Load this file whenever the register is Commercial,** and for nothing else.
It sits alongside the Commercial profile in `reference/registers.md`, which
carries the summary. Nothing here replaces a pattern in the catalog: the 36
patterns still run, gated by the Commercial column of the gate table in
`patterns-gated.md`. This file adds the operative/non-operative split, sixteen
Commercial-only rules (§C1–§C16), the Commercial word lists, and the extra
self-check.

The reader these rules are written for: an evaluator or procurement reviewer
looking for ambiguity to price against the supplier, and later a delivery lead
looking for what was actually promised. Every rule below keeps the prose from
creating obligations nobody intended, or hiding obligations everyone assumed.

**Four hard limits, above every rule in this file.**

1. **Never delete a disclosure.** Every exclusion, assumption, dependency, rate,
   cap and risk statement survives the edit. Rewording and relocating are
   allowed; removal is not.
2. **Never change a number.** A fee, rate, date, duration, headcount, threshold
   or volume belongs to the pricing model or the technical baseline, not to the
   prose. If an edit seems to need a different number, stop and ask the deal
   owner.
3. **Flag, never silently override.** If the user's instruction conflicts with a
   rule here, say so and ask. In a commercial document a silent override becomes
   an obligation.
4. **The client's mandated template wins on layout,** section order and page
   limits. These rules still govern the prose inside it. Note the conflict and
   the accommodation in the delivery.

---

## 1 — Operative and non-operative text

*The Document* is whatever client-facing commercial artefact is being edited.

**Operative text** can become binding: scope, deliverables, acceptance criteria,
pricing, fees, rates, milestones, assumptions, dependencies, exclusions, change
control, service levels and warranties. Every word of a statement of work, work
order, task order, engagement letter, MSA schedule, term sheet or amendment is
operative. In a proposal or RFP response, the scope, pricing, delivery-plan,
assumptions and exclusions sections are operative even though the Document is
not yet a contract.

**Non-operative text** is cover notes, executive summaries, capability
statements, track-record and case-study sections, architecture commentary and
client references.

How the split applies:

- Every rule in this file, and every pattern the gate table turns on, applies in
  full to operative text.
- **§C10–§C16 apply in full to non-operative text too.** An open-ended commitment
  in an executive summary is as dangerous as one in a scope clause, because
  non-operative sections are routinely incorporated by reference or quoted back
  in negotiation.
- **Two relaxations in non-operative text, and only two.** A benefit claim is
  allowed when it carries its number, its source and its scope, or is
  attributed to the client's own stated analysis (§C5). First person is allowed
  in a cover note (§C1). Everything else — pivots, triads, slogans,
  intensifiers, metaphors, the defensive register, methodology narration — is
  banned everywhere in the Document.

Mark the boundary in your working notes before editing, and re-read each section
against the rules that govern it. Where you cannot tell whether a section is
operative, treat it as operative and say so in the delivery.

---

## 2 — Coverage map

Most of the no-hype half of this register is already in the catalog under
another number. Read this table before adding a rule here; it exists to stop the
same rule being written twice.

| Commercial rule | Where it lives |
| --- | --- |
| Em-dash chains | §14, tightened in C to one per section, appositive definitions only |
| The pivot ("not a proof of concept — a production build") | §9 negative parallelism |
| Triadic drama ("It integrates. It scales. It pays back.") | §10 rule of three, §31 staccato drama (on in C) |
| Aphoristic titles and slogan openers ("From Data to Decisions") | §32 aphorisms, §29 fragmented headers, §31 manufactured punchlines |
| Intensifier and value adverbs | §4 promotional language, Tier 1, and the Commercial list in §4 below |
| Rhetorical inversion ("A well-scoped pilot, in our experience, needs no rework") | §27 authority tropes, §24 hedging. Fix: actor, obligation, object |
| Bare passive ("the data will be provided") | §13, a hard rule in C, plus §C1 |
| Hedged obligations ("should", "aims to") | §24, elevated in C, plus §C2 |
| One name per party, system and deliverable | §11, inverted in C |
| Rhetorical questions stacked | §36 rhetorical setups (on in C) |
| "The real question is", "here's what matters" | §27, §35 (on in C), plus §C7 |
| Bold or italic for emphasis in operative prose | §15, plus §C8 |
| Speculative gap-filling | §21, a blocker in C |
| **New here** | §C1–§C16 below |

---

## 3 — §C1 to §C16

The `C` prefix is deliberate, like the `G` on the government set: these load
only for the Commercial register. Detect mode may cite them by number.

### Voice

#### §C1 — Name the party in every obligation

Every obligation sentence names who performs it: "Supplier will…", "Client
will…". Never "we" or "you" in operative text. First person belongs in a cover
note, and in an executive summary only where the client's own paper uses it and
no sentence in it states a commitment. One obligation or claim per sentence, and
never a chain of subordinate clauses that crosses a scope boundary.

**Before:** We will make sure the data is provided on time so that you can start testing.

**After:** Client will provide the test data extract by 3 March. Supplier will begin testing within two business days of receipt.

#### §C2 — Modal discipline

*Will* for obligations, *may* for options, *must* only where a hard gate is
intended. Never *should*, *aims to*, *endeavours to*, *strives to*, *works
toward* or *is expected to* in an operative sentence. Each is unenforceable in
one direction and quotable in the other.

**Before:** Supplier aims to complete the migration by the end of Q2 and should be able to support cutover.

**After:** Supplier will complete the migration by 30 June. Supplier will provide cutover support as set out in D6.

#### §C3 — Plain reading beside every technical detail, and the delivery register

Every architecture, model or integration detail gets a sentence saying what the
Client gets from it and how they will know it works. Every delivery sentence
states what is delivered, in what form, to whom, and by when.

**Before:** The pipeline leverages a retrieval step prior to generation.

**After:** The pipeline runs a *retrieval step*: it selects the policy documents most likely to answer the query before any answer is generated. Client can check this in the evaluation notebook, which shows the documents retrieved for each test query.

**Delivery register:** "Supplier will deliver the trained model, the evaluation
notebook and a written accuracy report to Client's nominated technical owner by
the end of Sprint 4."

#### §C4 — Exact references, one spelling, terms defined once

Cite every prior document by exact title, date and version: "This Document is
issued under the Master Services Agreement between the parties dated 14 March
2026." Cite the client's RFP, RFI, DDQ or PEP by exact title, date and section.
Use the client's spelling variant (British or American) with zero mixing. Define
each term once, at first use or in the definitions section, and then use it
identically everywhere: "A *Use Case* is a single scoped business workflow with
its own acceptance criteria."

**Connective stock.** "For the avoidance of doubt", "Subject to", "Provided
that", "Except as set out in", "Note that", "Where", "In addition to". Use them
sparingly, and never to smuggle in a new obligation: a "For the avoidance of
doubt" sentence that adds a duty the scope does not state is a new term hiding
in a clarification.

### No hype

#### §C5 — Unquantified benefit claims

In operative text, a benefit claim either becomes a number with a test (and so a
measurable acceptance criterion) or moves out. "Will significantly reduce
handling time" is a performance obligation with no test. In non-operative text a
benefit claim is allowed only with its number, its source and its scope —
"reduced cycle time from 40 to 12 minutes at Client A, on a 14-week engagement" —
or attributed to the client's own stated analysis. A bare superlative is banned
in both. Never invent the number to satisfy this rule; §21 applies.

**Evidence register for track record.** Every outcome figure names the client,
the measurement basis and its approval status for external use. Mark an
unapproved figure in place rather than implying approval. Every capability table
keeps what exists in production today separate from what is new work.

#### §C6 — Structural, journey, partnership and war metaphors

Never call a workstream, assumption, dependency or milestone "load-bearing",
"the linchpin", "the cornerstone", "the backbone" or "doing the heavy lifting".
No "journey", "trusted partner", "north star", "single throat to choke", "war
room", "swim lanes" (say workstreams) or "land and expand". No sports and
finance metaphors: "wins", "unlocks", "payoff", "quick wins". Say what the thing
does and who owes what.

**Before:** The data-access dependency is load-bearing for the whole programme.

**After:** The data-access dependency sets the Sprint 2 start date.

#### §C7 — Significance clefts

"The reason this matters is…", "This is the difference between an hour and a
week", "What this buys you is…", "The number is important, but the reusability
more so." These announce significance instead of showing it. State the fact and
let it carry.

**Before:** What this buys you is a pipeline you never have to rebuild.

**After:** Client can add a new document type by adding a configuration file; no code change is required.

#### §C8 — Stacked parentheses, footnotes and emphasis

At most one parenthetical per sentence, and one per paragraph in scope and
delivery prose; move the rest into their own sentences, into Assumptions, or
into Exclusions. No footnotes: a footnote in a commercial document is an
obligation nobody read. No bold or italic for emphasis in operative prose.
Reserve them for defined terms and headings.

#### §C9 — Defensive register and methodology narration

Two kinds of text that argue instead of stating. **Defensive:** runs of clipped
sentences, and pre-emption of objections nobody raised — "To be clear, Supplier
does not warrant…", "This is not to say that…", "Nothing in this section
implies…". State each limit once, in Exclusions or Assumptions, as a full
declarative sentence. **Narration:** re-arguing how the estimate was built or why
the scope was split — "Having considered a single-phase approach, we separated
Phase 1 and Phase 2 so that…". The reasoning belongs in the approach section, at
most one clause. Symptoms: a paragraph that recaps the previous section; the same
assumption restated two or three ways; a mechanism re-explained when it already
sits in the deliverables table. Also cut fronted-participle openers ("Built this
way, …", "Delivered iteratively, …").

**Measured corrections are allowed** when they earn their place and carry their
reason: "A larger initial data extract appears to increase cost. In practice it
lowers total cost, because it removes the second extract cycle currently priced
into Phase 2." That is a fact the reader would get wrong without it. A staged
reversal for effect is still §9.

### No self-sabotage

§C5–§C9 forbid overselling. §C10–§C16 forbid the two opposite errors: **wording
the obligation wider than the deal**, and **wording the value narrower than the
evidence**. The failure mode is a Document that is honest and framed to lose
money. These rules govern wording only. Disclosure is non-negotiable (hard limit
1).

#### §C10 — Open-ended obligation verbs

Any verb without a quantity, a period or a named artefact is a blank cheque.
Ban "as required", "as needed", "to Client's satisfaction", "including but not
limited to" and "best efforts" in scope sentences, and "ongoing" anywhere,
including executive summaries and capability statements.

**Before:** Supplier will support Client's adoption of the platform on an ongoing basis as required.

**After:** Supplier will provide up to 40 hours of post-deployment support during the 30 days following Acceptance.

#### §C11 — Self-deprecating framing and casual understatement

A deliberately bounded phase is "Phase 1, covering X and Y", not "a limited
initial phase", "only a first cut" or "a lightweight proof of concept". A pilot
with production-grade engineering is not "just a pilot". A reference cited for
one criterion is not "only a second data point". Where the fact is stronger
stated precisely, state it precisely: "production data and a completed security
review", not "real data and real security review".

#### §C12 — Limits as design, rights not motives

A designed boundary is stated as the boundary: "Production hosting remains on
Client infrastructure and is managed by Client", not "Supplier does not provide
hosting". Prefer a statement of rights to a statement of intent: "Supplier makes
no ownership claim over the data, integration or governance substrate", not
"Supplier has no interest in owning the substrate". Mirror the client's own
language where their request uses it.

#### §C13 — Scope every concession; one general disclaimer

Bind each concession to where it holds, in the same clause: a warranty applies
"on the environment configuration recorded at Acceptance", not everywhere. At
most one broad "Supplier does not warrant" or "Supplier is not responsible for"
formulation in the whole Document, after the positive statement. Convert every
other self-limiting sentence into a neutral allocation that keeps the substance.

**Before:** Supplier cannot guarantee data quality.

**After:** Data quality in the source systems is Client's responsibility. Supplier will report defects it identifies during ingestion.

#### §C14 — Do not hedge a committed number

A contracted accuracy, uptime or throughput figure is a commitment. Do not also
call it "indicative", "target" or "aspirational" in the same clause. Keep the
precise qualifier once (the test set, the measurement window, the exclusions)
and drop the vague adjective. A number that is genuinely not being contracted
stays in non-operative text, marked as not contracted.

#### §C15 — Guard the high-read positions

The executive summary, scope summary, deliverables table, pricing section and
acceptance criteria are what get read. Lead with the committed outcome, then the
scoped boundary. Never open or close one of these on a limitation stated more
starkly than the commercial position requires — and never open any section on a
value proposition either. Titles name the phase, the workstream and the
deliverable, plainly.

**Before:** Supplier is not responsible for hosting, change management or data quality.

**After:** Supplier will deliver a deployed extraction service meeting the accuracy thresholds in Table 4. Production hosting and Client-side change management sit with Client.

#### §C16 — The stop rule

Rephrase any sentence a reviewer could quote to cut the price or widen the
obligation, when a neutral rewording defuses it **without changing a single
commercial term**. If the rewording would need an exclusion dropped, a cap
softened or a dependency hidden, stop: keep the honest version and raise it with
the deal owner. This is where §C10–§C16 end and hard limit 1 begins.

---

## 4 — Commercial word lists

`scripts/voice_check.py --register C` counts these. Every hit is an ERROR,
because the justified count outside quoted client language is zero. Quotation
is masked, so the client's own words in quotes are never reported.

- **Unbounded obligation (§C10):** as required · as needed · ongoing · to
  Client's satisfaction · including but not limited to · best efforts
- **Hedged modals (§C2):** should · aims to · endeavour / endeavor · strives to ·
  works toward(s) · is expected to
- **Metaphors (§C6):** load-bearing · linchpin · cornerstone · heavy lifting ·
  backbone of · this / our / your journey · trusted partner · north star · single throat to choke ·
  war room · swim lanes · land and expand · quick wins
- **Intensifiers (§4, Commercial scope):** turnkey · world-class · best-in-class
  · bespoke · holistic / holistically · synergistic · robustly ·
  transformational · proven · industry-leading · market-leading · a / the
  leading (as an adjective: "a leading provider")
- **Significance clefts (§C7):** what this buys · the reason this matters ·
  this is the difference between · that is the difference between

Two more counts, both WARN: more than one broad disclaimer in the Document
(§C13), and a sentence carrying more than one parenthetical (§C8). A parenthesis
holding only a quoted defined term — `("Supplier")` in a preamble — is not
counted. Markdown
footnotes (`[^1]`) and first person (`we`, `our`, `you`, `your`) are WARN too;
first person is legitimate in a cover note, so a human adjudicates.

`end-to-end` is not on the list: it is correct when the endpoints are named.
Nor is a bare `journey` (a customer journey map is a real deliverable, so
"journey map" and "journey mapping" never fire) or a bare `the difference between` (the
difference between two quotes is a fact). Judge them in the semantic pass.

---

## 5 — Self-check additions

Run these in Step 4 of `SKILL.md`, after the register-wide steps. Report the
outcome of each one, pass or fail, before calling the draft finished.

1. **Checker.** `python3 scripts/voice_check.py <file> --register C`. Add `--gov`
   for a government buyer. The checker reads text or Markdown only: convert a
   Word file or PDF to text first (`textutil -convert txt`, `pandoc`,
   `pdftotext`, or the docx or pdf skill).
2. **Summary read-aloud.** Read the executive summary and the scope summary
   aloud. Split any sentence that needs a breath in the middle.
3. **Disclaimers.** Count the broad forms. More than one: keep the best-placed
   one and convert the rest to named exclusions or neutral allocations (§C13).
4. **Parentheses in scope and delivery sections.** Each is deletable, or shows
   the sentence is doing two jobs, or belongs in Assumptions (§C8).
5. **Banned constructions, two stages, both mandatory.** (a) Mechanical: the
   checker, or the §4 lists by hand. (b) Semantic: a fresh read of every
   sentence, **every heading, every table caption, every diagram label, and
   every schedule and appendix**, against §C5–§C9 and the gate table. Use a
   fresh-context reviewer or subagent where one is available, given the full
   Document and told to return line-referenced violations with flat rewrites.
   Never report this item as passed on the strength of stage (a) alone.
   Calibration: the recurring failure greps clean and still contains a section
   titled "Accelerating Your Underwriting Transformation", an architecture
   diagram with "seamless integration" on an arrow, and one sentence in an
   appendix committing to "ongoing support as required".
6. **Terminology.** One spelling variant, one name per party, system and
   deliverable, one capitalisation convention for defined terms, and every
   defined term both defined and used. First person only where §1 permits it.
7. **Self-sabotage sweep.** Re-read the five high-read positions (§C15) for any
   obligation stated wider, or value stated narrower, than the position
   requires. Flag any limit stated in more than one place; keep it in exactly
   one, with its consequence attached. **Confirm no exclusion, dependency, cap
   or number was removed or changed** — compare against the original, item by
   item.
8. **Two read-aloud tests.** Any sentence that sounds like a pitch slide, a
   LinkedIn post or ad copy is rewritten flat. Any sentence a procurement
   reviewer could hold up as a promise nobody priced is rewritten, quantified,
   or moved to non-operative text where §1 allows it.

In the Step 5 delivery, add the operative/non-operative map after the register
line, and change the audit question to **"What still reads as AI, or as a
promise nobody priced?"**

---

## 6 — Out of scope, named

This file governs wording. It does not check the Document's structure or its
numbers. Say so in every Commercial delivery, naming each of these as not
performed unless a separate contracts review ran them:

- **Structure:** the numbered deliverables list, one acceptance test and one
  price per deliverable, the ≤200-word scope summary, and assumptions,
  dependencies and exclusions consolidated with their consequences attached.
- **Numbers:** totals that foot, and fee, milestone and payment tables that
  reconcile to the penny and to the same dates.
- **The rendered file:** numbering, cross-references, split tables, leftover
  placeholders, a previous client's name, signature blocks.
- **The pricing model:** the adversarial audit of the model behind every fee,
  date and threshold.
- **Legal and deal-desk review.** Nothing in this skill replaces either.
