# Pattern catalog

33 patterns. Each carries its register tags: **E**ditorial, **P**rofessional,
**T**echnical, **R**egulated. A pattern with no tag for the selected register is
off — do not apply it.

Read [False positives](#false-positives) before flagging anything. Most of these
patterns are tripped occasionally by clean human writers; a single hit proves
nothing. Look for **clusters**.

Derived from the MIT-licensed `humanizer` skill and Wikipedia's "Signs of AI
writing". See `attribution.md`.

---

## Content patterns

### §1. Undue emphasis on significance, legacy, and broader trends
**Registers:** E P T R

**Watch:** stands/serves as, is a testament/reminder, a vital/significant/crucial/pivotal/key role/moment, underscores its importance, reflects broader, symbolizing its enduring, contributing to the, setting the stage for, marking a shift, key turning point, evolving landscape, focal point, indelible mark, deeply rooted

Models puff up importance by asserting that an arbitrary detail represents some
broader trend.

**Before:** The Statistical Institute of Catalonia was officially established in 1989, marking a pivotal moment in the evolution of regional statistics in Spain. This initiative was part of a broader movement to decentralize administrative functions.

**After:** The Statistical Institute of Catalonia was established in 1989 to collect and publish regional statistics independently from Spain's national statistics office.

### §2. Undue emphasis on notability and coverage
**Registers:** E P T R

**Watch:** independent coverage, national media outlets, written by a leading expert, active social media presence

**Before:** Her views have been cited in The New York Times, BBC, Financial Times, and The Hindu. She maintains an active social media presence with over 500,000 followers.

**After:** In a 2024 New York Times interview, she argued that AI regulation should focus on outcomes rather than methods.

### §3. Superficial analyses with -ing endings
**Registers:** E P T R

**Watch:** highlighting, underscoring, emphasizing, ensuring, reflecting, symbolizing, contributing to, fostering, encompassing, showcasing

Present-participle phrases tacked onto a sentence to simulate depth.

**Before:** The temple's palette of blue, green, and gold resonates with the region's natural beauty, symbolizing Texas bluebonnets and the Gulf of Mexico, reflecting the community's deep connection to the land.

**After:** The temple uses blue, green, and gold. The architect said these reference local bluebonnets and the Gulf coast.

### §4. Promotional and advertisement-like language
**Registers:** E P T R

**Watch:** boasts a, vibrant, rich (figurative), profound, enhancing its, showcasing, exemplifies, commitment to, nestled, in the heart of, groundbreaking, renowned, breathtaking, must-visit, stunning

**Before:** Nestled within the breathtaking region of Gonder, Alamata Raya Kobo stands as a vibrant town with a rich cultural heritage and stunning natural beauty.

**After:** Alamata Raya Kobo is a town in the Gonder region of Ethiopia, known for its weekly market and 18th-century church.

### §5. Vague attribution and weasel words
**Registers:** E P T R — elevate in P and R

**Watch:** industry reports, observers have cited, experts argue, some critics argue, several sources

**Before:** Due to its unique characteristics, the Haolai River is of interest to researchers. Experts believe it plays a crucial role in the regional ecosystem.

**After:** The Haolai River supports several endemic fish species, according to a 2019 survey by the Chinese Academy of Sciences.

### §6. Formulaic "Challenges and Future Prospects" sections
**Registers:** E P T R

**Watch:** Despite its... faces several challenges, Despite these challenges, Challenges and Legacy, Future Outlook

**Before:** Despite its industrial prosperity, Korattur faces challenges typical of urban areas. Despite these challenges, with its strategic location and ongoing initiatives, Korattur continues to thrive.

**After:** Traffic congestion increased after 2015 when three IT parks opened. The municipal corporation began a stormwater drainage project in 2022.

---

## Language and grammar

### §7. Overused AI vocabulary
**Registers:** E P T R — **list is register-scoped**, see `vocabulary.md`

Do not apply a global blacklist. Words like *robust*, *leverage*, *harness*,
*realm*, and *navigate* are terms of art in technical writing and banning them
breaks documents. `vocabulary.md` splits the list into a globally safe tier and
register-scoped tiers with carve-outs.

**Before:** Additionally, an enduring testament to Italian colonial influence is the widespread adoption of pasta in the local culinary landscape, showcasing how these dishes have integrated into the traditional diet.

**After:** Pasta dishes, introduced during Italian colonization, remain common, especially in the south.

### §8. Copula avoidance
**Registers:** E P T R

**Watch:** serves as, stands as, marks, represents, boasts, features, offers — where "is" or "has" would do.

**Before:** Gallery 825 serves as LAAA's exhibition space. The gallery features four separate spaces and boasts over 3,000 square feet.

**After:** Gallery 825 is LAAA's exhibition space. It has four rooms totaling 3,000 square feet.

### §9. Negative parallelism and tailing negation
**Registers:** E P T R

"Not only... but...", "It's not just X, it's Y", plus clipped fragments like "no
guessing" or "no wasted motion" bolted onto a sentence.

**Before:** It's not just about the beat riding under the vocals; it's part of the aggression. It's not merely a song, it's a statement.

**After:** The heavy beat adds to the aggressive tone.

**Before:** The options come from the selected item, no guessing.

**After:** The options come from the selected item, so the user does not have to guess.

### §10. Rule of three
**Registers:** E P T R

**Before:** The event features keynote sessions, panel discussions, and networking opportunities. Attendees can expect innovation, inspiration, and industry insights.

**After:** The event includes talks and panels, with time for informal networking between sessions.

### §11. Elegant variation (synonym cycling)
**Registers:** E P T R — **inverts in T and R**

Repetition-penalty artifacts produce needless synonym substitution. In Technical
and Regulated this is a correctness bug, not a style issue: a component gets the
same name every time, without exception.

**Before:** The protagonist faces many challenges. The main character must overcome obstacles. The central figure eventually triumphs.

**After:** The protagonist faces many challenges but eventually triumphs.

### §12. False ranges
**Registers:** E P T R

"From X to Y" where X and Y are not endpoints of any real scale.

**Before:** Our journey has taken us from the singularity of the Big Bang to the grand cosmic web, from the birth of stars to the enigmatic dance of dark matter.

**After:** The book covers the Big Bang, star formation, and current theories about dark matter.

### §13. Passive voice and subjectless fragments
**Registers:** E P T R — hard rule in R

**Before:** No configuration file needed. The results are preserved automatically.

**After:** You do not need a configuration file. The system preserves the results automatically.

---

## Style

### §14. Em dashes and en dashes
**Registers:** E P T — **off in R** (house style governs)

Replace every `—` and `–`, in rough order of preference: a period, a comma, a
colon, parentheses, or a restructured sentence. Catch spaced ` — ` and double
hyphens ` -- ` too. Scan the final draft for both characters before returning it.

**Before:** The term is promoted by institutions—not by the people themselves. You don't say "Netherlands, Europe" as an address—yet this continues—even in official documents.

**After:** The term is promoted by institutions, not by the people themselves. You don't say "Netherlands, Europe" as an address, yet this continues in official documents.

### §15. Boldface overuse
**Registers:** E P T R

**Before:** It blends **OKRs (Objectives and Key Results)**, **KPIs**, and tools such as the **Business Model Canvas (BMC)**.

**After:** It blends OKRs, KPIs, and visual strategy tools like the Business Model Canvas.

### §16. Inline-header vertical lists
**Registers:** E P — **off in T and R**

Bulleted items that open with a bolded header and a colon, where prose would
carry the analysis better. Off in Technical and Regulated, where procedures,
parameters, and requirements are legitimately list-shaped and plain-language
guidance actively calls for lists.

**Before:**
> - **User Experience:** The experience has been significantly improved with a new interface.
> - **Performance:** Performance has been enhanced through optimized algorithms.

**After:** The update improves the interface and speeds up load times through optimized algorithms.

### §17. Title case in headings
**Registers:** E P — **off in T and R** (project or agency style guide wins)

**Before:** `## Strategic Negotiations And Global Partnerships`

**After:** `## Strategic negotiations and global partnerships`

### §18. Emojis
**Registers:** E (sparingly) — banned in P T R

**Before:** 🚀 **Launch Phase:** The product launches in Q3

**After:** The product launches in Q3.

### §19. Curly quotation marks
**Registers:** E P T R

Straight quotes over `“ ”`. Weak signal alone — most editors auto-curl — but it
counts inside a cluster. In Technical, never alter quotes inside code spans.

### §20. Chatbot correspondence artifacts
**Registers:** E P T R

**Watch:** I hope this helps, Of course!, Certainly!, You're absolutely right, Would you like..., Want me to...?, Should I continue?, let me know, here is a...

**Before:** Here is an overview of the French Revolution. I hope this helps! Let me know if you'd like me to expand on any section.

**After:** The French Revolution began in 1789 when financial crisis and food shortages led to widespread unrest.

### §21. Knowledge-cutoff disclaimers and speculative gap-filling
**Registers:** E P T R — **blocker in P and R**

**Watch:** as of [date], up to my last training update, while specific details are limited, based on available information, not publicly available, maintains a low profile, keeps personal details private, likely [grew up/studied], it is believed that

Two tells. Models leave hard cutoff disclaimers in the text, and when a source is
missing they write a paragraph *about* the missing source and then invent
plausible filler. Say what is not known, or cut the sentence.

**Before:** Information about her early life is not publicly available, suggesting she maintains a low profile. She likely grew up in a middle-class household, which shaped her later interest in education reform.

**After:** Her early life is not documented in the available sources.

### §22. Sycophantic tone
**Registers:** E P T R

**Before:** Great question! You're absolutely right that this is complex. That's an excellent point about the economic factors.

**After:** The economic factors you mentioned are relevant here.

---

## Filler and hedging

### §23. Filler phrases
**Registers:** E P T R — reinforces plain language

- "In order to achieve this goal" → "To achieve this"
- "Due to the fact that it was raining" → "Because it was raining"
- "At this point in time" → "Now"
- "In the event that you need help" → "If you need help"
- "The system has the ability to process" → "The system can process"
- "It is important to note that the data shows" → "The data shows"

### §24. Excessive hedging
**Registers:** E P — **limited in T and R**

**Before:** It could potentially possibly be argued that the policy might have some effect on outcomes.

**After:** The policy may affect outcomes.

In Technical and Regulated, distinguish hedging from calibrated uncertainty. "This
may fail under load" is hedging. "Throughput degrades above roughly 4k concurrent
connections; untested past 8k" carries information and stays. The test is whether
the qualifier tells the reader something actionable.

### §25. Generic positive conclusions
**Registers:** E P T R

**Before:** The future looks bright for the company. Exciting times lie ahead as they continue their journey toward excellence.

**After:** The company plans to open two more locations next year.

### §26. Hyphenated word-pair overuse
**Registers:** E P — **off in T and R**

**Watch:** third-party, cross-functional, client-facing, data-driven, decision-making, well-known, high-quality, real-time, long-term, end-to-end

Models hyphenate uniformly, including in predicate position. Humans typically
hyphenate attributively and drop it after the noun. Off in Technical and
Regulated, where hyphenation is usually spec- or style-defined.

**Before:** The team is cross-functional, the report is high-quality, and the methodology is data-driven.

**After:** The team is cross functional, the report is high quality, and the methodology is data driven.

### §27. Persuasive authority tropes
**Registers:** E P T R — rare outside E

**Watch:** the real question is, at its core, in reality, what really matters, fundamentally, the deeper issue, the heart of the matter

**Before:** The real question is whether teams can adapt. At its core, what really matters is organizational readiness.

**After:** The question is whether teams can adapt. That mostly depends on whether the organization is ready to change its habits.

### §28. Signposting and announcements
**Registers:** E P T — **off in R** (mandated templates require structural signposting)

**Watch:** let's dive in, let's explore, let's break this down, here's what you need to know, now let's look at, in this section we will

**Before:** Let's dive into how caching works in Next.js. Here's what you need to know.

**After:** Next.js caches data at several layers, including request memoization, the data cache, and the router cache.

### §29. Fragmented headers
**Registers:** E P T R

A heading followed by a one-line paragraph restating the heading before the real
content starts.

**Before:**
> ## Performance
>
> Speed matters.
>
> When users hit a slow page, they leave.

**After:**
> ## Performance
>
> When users hit a slow page, they leave.

### §30. Diff-anchored writing
**Registers:** E P R — **elevated in T**

Prose that narrates a change rather than describing the thing. Unless the
document is version-scoped (changelog, release notes, migration guide), it must
read coherently without knowing what changed last commit.

**Before:** This function was added to replace the previous approach of iterating through all items, which caused O(n²) performance.

**After:** This function uses a hash map for O(1) lookups, avoiding the O(n²) cost of naive iteration.

### §31. Manufactured punchlines and staccato drama
**Registers:** E only

Every sentence landing like a quotable closer, then short declarative fragments
stacked to manufacture drama. One short sentence for emphasis is fine; a run of
them sounds engineered.

**Before:** Then AlphaEvolve arrived. It had no preference for symmetry. No aesthetic prior. No nostalgia for human taste. The old rules were gone.

**After:** AlphaEvolve changed the search because it did not favor symmetry or human-looking designs, which made some older assumptions less useful.

### §32. Aphorism formulas
**Registers:** E P — rare in T and R

**Watch:** X is the Y of Z, X becomes a trap, X is not a tool but a mirror, the language of, the currency of, the architecture of

**Before:** Symmetry is the language of trust. Efficiency becomes a trap when teams forget the human layer.

**After:** Symmetric layouts often feel more predictable to users. Teams can over-optimize workflows and miss how people actually use them.

### §33. Conversational rhetorical openers
**Registers:** E only

**Watch:** Honestly?, Look, Here's the thing, The thing is, Let's be honest, Real talk — used as standalone hooks or fake-candid pauses.

**Before:** Is it worth the price? Honestly? It depends on how often you'll use it.

**After:** Whether it's worth the price depends on how often you'll use it.

---

## False positives

A clean human writer hits several patterns above with no AI involved. None of
these is a reliable indicator on its own:

- **Perfect grammar and consistent style.** Many writers are professionals or
  have been edited. Polish is not evidence.
- **Mixed casual and formal registers.** Often signals a person in a technical
  field, a young writer, or particular prose habits — not a chatbot.
- **Bland or robotic prose.** AI prose has *specific* tells. Generic dryness
  without them is just dry writing.
- **Formal or academic vocabulary.** Models overuse *specific* fancy words, not
  all fancy words. Do not flatten "ostensibly" or "constituent".
- **Common transition words in isolation.** *Additionally*, *moreover*,
  *consequently* are tells only when piled up. One *however* is nothing.
- **Curly quotes alone.** macOS, Word, and most CMSes auto-curl by default.
- **Em dashes alone.** Editors and journalists use them heavily. Evidence only
  when paired with formulaic, sales-y rhythm.
- **One short emphatic sentence.** Humans use clipped sentences to land a point.
  Flag staccato drama only for a run of them.
- **"Honestly" or "look" mid-sentence.** Ordinary in casual writing. The tell is
  the standalone theatrical opener.
- **Unsourced claims.** Most writing is unsourced. It proves nothing on its own.
- **Correct, complex formatting.** Templates and visual editors produce clean
  output with no AI involved.
- **Secondhand text.** Never rewrite a watched phrase inside a quotation, title,
  proper name, code identifier, error string, or an example where the phrase is
  being discussed rather than used.

A single em dash means nothing. Em dashes plus rule-of-three plus *vibrant
tapestry* plus a "Conclusion" section is a confession.

## Signs of human writing — preserve these

When these appear, lean toward leaving the prose alone. Over-editing destroys
exactly what makes a piece sound human:

- **Specific, hard-to-fabricate detail.** A real address, a weird quote, "the
  lawyer who used to work upstairs from my dentist". Models round off specifics;
  people hoard them.
- **Mixed feelings and unresolved tension.** "I think this is mostly good, but it
  bothers me and I can't fully explain why."
- **Dated, era-bound references.** Slang and in-jokes that map to a specific year
  and subculture.
- **Editorial choices the writer can defend.** If they can explain why they made
  a cut, that is a strong human signal.
- **Variety in sentence length.** Real writing alternates; models tend toward an
  even mid-length cadence.
- **Genuine asides and self-corrections.** "(I keep wanting to say 'almost' here,
  but it really was certain.)" Models rarely interrupt themselves.
