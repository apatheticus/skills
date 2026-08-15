# Pattern catalog — register-gated

15 of the catalog's 36 patterns, plus personality injection. Each one changes or
switches off depending on the register selected in Step 1 of `SKILL.md`. Applying
them blind is how this skill breaks documents.

The other 21 are always on and live in `patterns-core.md`. Read that file on
every run; read this one only when the gate table below turns at least one
pattern on for the selected register.

Before flagging anything here, read the False positives list in
`patterns-core.md`. A clean human writer trips several of these patterns with no
AI involved, and a single hit proves nothing — look for **clusters**.

Derived from the MIT-licensed `humanizer` skill, Wikipedia's "Signs of AI
writing", and the MIT-licensed `no-ai-slop` skill. See `attribution.md`.

---

## The gate table

| Pattern | E | P | T | R | Why it varies |
| --- | :-: | :-: | :-: | :-: | --- |
| §11 elegant variation | ● | ● | ◑ | ◑ | **Inverts** in Technical and Regulated — one name per thing; cutting repetition is a correctness bug |
| §14 em dash budget | ● | ● | ● | ○ | House style governs in Regulated (GPO, agency guides) |
| §16 inline-header lists | ● | ● | ○ | ○ | Runbooks and compliance docs are legitimately list-shaped |
| §17 title-case headings | ● | ● | ○ | ○ | Project or agency style guide wins |
| §18 emojis | ◐ | ● | ● | ● | Sparingly allowed in Editorial, banned elsewhere |
| §24 excessive hedging | ● | ● | ◐ | ◐ | Calibrated uncertainty is content, not hedging |
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

Two gates deserve spelling out, because getting them backwards is the most
expensive mistake available here. Both are marked ◑ or ◐ above and both are
detailed in their own sections below: **§11** reverses its fix direction in
Technical and Regulated, and **§24** stops being a defect there. The third
expensive gate, §21 speculative gap-filling, is always on and lives in
`patterns-core.md`.

---

## Language and grammar

### §11. Elegant variation (synonym cycling)
**Registers:** E P T R — **inverts in T and R**

Repetition-penalty artifacts produce needless synonym substitution. In Technical
and Regulated this is a correctness bug, not a style issue: a component gets the
same name every time, without exception.

**Before:** The protagonist faces many challenges. The main character must overcome obstacles. The central figure eventually triumphs.

**After:** The protagonist faces many challenges but eventually triumphs.

**The fix direction reverses in Technical and Regulated.** Everywhere else,
cycling synonyms is a repetition-penalty artifact to remove. In a spec or a
filing, "varying" a term is the defect and consistency is the fix. Do not cut
repetition of a technical term to make prose read better.

---

## Style

### §14. Em dash and en dash budget
**Registers:** E P T — **off in R** (house style governs)

A dash is not a tell. A dash used as the default rhythm is. Budget them instead of
banning them: **none in short copy, one or two in a longer draft** where a dash
clearly beats a comma, a period, a colon, or parentheses. Cut the rest, and cut
every cluster and decorative dash first. Catch spaced ` — ` and double hyphens
` -- ` too.

When replacing one, prefer in this order: a period, a comma, a colon,
parentheses, or a restructured sentence. Scan the final draft and count both
characters before returning it. Two dashes on a page is a habit; six is the tell.

An explicit instruction outranks the budget. If the user asks for every dash
removed, remove every dash. Do not enforce a zero count on your own initiative in
Editorial work, where the false-positive list is explicit that heavy em dash use
is ordinary in edited prose.

**Before:** The term is promoted by institutions—not by the people themselves. You don't say "Netherlands, Europe" as an address—yet this continues—even in official documents.

**After:** The term is promoted by institutions, not by the people themselves. You don't say "Netherlands, Europe" as an address, yet this continues in official documents.

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

---

## Filler, hedging, and rhetorical moves

### §24. Excessive hedging
**Registers:** E P — **limited in T and R**

**Before:** It could potentially possibly be argued that the policy might have some effect on outcomes.

**After:** The policy may affect outcomes.

**In Technical and Regulated, distinguish hedging from calibrated uncertainty.**
"This may fail under load" is hedging — cut it. "Throughput degrades above
roughly 4k concurrent connections; we have not tested past 8k" is calibrated
uncertainty, and it is the most valuable sentence on the page. Never cut the
second. The test is whether the qualifier carries information the reader can act
on.

### §26. Hyphenated word-pair overuse
**Registers:** E P — **off in T and R**

**Watch:** third-party, cross-functional, client-facing, data-driven, decision-making, well-known, high-quality, real-time, long-term, end-to-end

Models hyphenate uniformly, including in predicate position. Humans typically
hyphenate attributively and drop it after the noun. Off in Technical and
Regulated, where hyphenation is usually spec- or style-defined.

**Before:** The team is cross-functional, the report is high-quality, and the methodology is data-driven.

**After:** The team is cross functional, the report is high quality, and the methodology is data driven.

### §28. Signposting and announcements
**Registers:** E P T — **off in R** (mandated templates require structural signposting)

**Watch:** let's dive in, let's explore, let's break this down, here's what you need to know, now let's look at, in this section we will

**Before:** Let's dive into how caching works in Next.js. Here's what you need to know.

**After:** Next.js caches data at several layers, including request memoization, the data cache, and the router cache.

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

**Repairing a kicker: delete it, do not improve it.** When the last line exists to
sound deep, do not rewrite it into a better metaphor and do not preserve its
rhythm. Delete it, then end on the clearest concrete sentence already in the
draft. If the ending then feels unfinished, add a plain takeaway or a next action.
Smoothing the kicker into a quieter sentence leaves the piece still ending on a
manufactured closer, which is the failure this pattern names.

### §32. Aphorism formulas
**Registers:** E P — rare in T and R

**Watch:** X is the Y of Z, X becomes a trap, X is not a tool but a mirror, the language of, the currency of, the architecture of

**Before:** Teams kept optimizing the checkout flow until nobody could explain why step four existed. Efficiency becomes a trap. Symmetry is the language of trust.

**After:** Teams kept optimizing the checkout flow until nobody could explain why step four existed.

Delete is the default repair, as in §31. Paraphrasing the aphorism into a plainer
sentence — "symmetric layouts often feel more predictable to users" — keeps the
closer and only lowers its volume. Rewrite instead of deleting in the one case
where the aphorism is the only place a real claim appears; then state that claim
plainly and put it where the argument needs it, not at the end as a flourish.

### §33. Conversational rhetorical openers
**Registers:** E P — **off in T and R**

**Watch:** Honestly?, Look, Here's the thing, Here's what I mean, The thing is, Let's be honest, Let me be clear, I'll be honest, The uncomfortable truth is, Real talk — used as standalone hooks or fake-candid pauses.

**Before:** Is it worth the price? Honestly? It depends on how often you'll use it.

**After:** Whether it's worth the price depends on how often you'll use it.

**Before:** Let me be clear: the migration slipped because we lost two engineers in March.

**After:** The migration slipped because we lost two engineers in March.

On in Professional, not only Editorial. "Let me be clear" and "I'll be honest" are
staples of executive memos, all-hands notes, and internal comms, and they delay
the point there exactly as they do in an essay. Cut the opener and state the
point. Keep "honestly" or "look" mid-sentence, which is ordinary speech — see the
false-positive list in `patterns-core.md`.

### §34. Colon reveals
**Registers:** E P — **off in T and R**

**Watch:** The best part:, The catch:, The result:, The problem:, The detail that makes it work:, Here's the kicker: — a bare noun phrase, a colon, then a lowercase payload.

The colon withholds a short point for a beat of theatre the sentence has not
earned. Rewrite as a plain sentence.

**Before:** The detail that makes it work: a separate agent grades every draft. The best part: it learns from the corrections.

**After:** A separate agent grades every draft, which is what makes it work. It also learns from the corrections.

Colons are correct for lists, labels, quotations, and ratios. The test is whether
the colon **labels** the content or **withholds** it. "Known limits: no cache
warming" is a label. "The tradeoff we are accepting: Vendor A's reporting is
weaker" is a label with substance behind it. "The best part: it learns" is a
reveal. Off in Technical and Regulated, where the labelled colon is the house
pattern and the dramatic one is rare.

Corollary: after a colon, use sentence case unless grammar, a proper noun, a
title, or code requires otherwise.

### §35. Faux-insight setups
**Registers:** E only

**Watch:** here's what nobody tells you, what most people get wrong, the part everyone misses, this is the part most people skip, nobody talks about, few people realize, the part nobody warns you about

The setup flatters the writer as the one person holding the insight, and it does
that whether or not the claim behind it is any good. Cut the setup and let the
claim stand alone. If the claim cannot stand alone, the setup was doing all the
work and the claim needs evidence, not a frame.

**Before:** Here's what nobody tells you about launching a product: distribution is the real moat.

**After:** Distribution is the moat.

Distinct from §27 authority tropes, which inflate the topic ("the real question
is", "at its core"). This one inflates the author. §27 is in `patterns-core.md`.

### §36. Rhetorical setups and self-answered questions
**Registers:** E only

**Watch:** What if I told you, Think about it:, Plot twist:, Here's a thought:, Sound familiar? — plus any question the writer poses and answers in the next breath.

**Before:** What if I told you the eval matters more than the model? Think about it. Why did every team we talked to have the same problem? Because nobody was measuring.

**After:** Every team we talked to had the same problem, and none of them was measuring anything. The eval matters more than the model.

A question answered in the next sentence was never a question; it is a pause for
effect. Ask one only when the reader is meant to sit with it, which in practice is
rare. §28 covers announcement signposting ("let's dive in") and §33 covers
standalone candor openers; this one covers the manufactured question.

---

## PERSONALITY — voice injection
**Registers:** E only

The only register where injecting voice is correct. In Professional, Technical
and Regulated, neutral and plain **is** the human voice, and adding personality is
the most damaging failure this skill can produce — it is not visible to the person
who asked for it.

Editorial voice work is covered in `registers.md`. The rule that keeps it honest:
keep, do not manufacture. An aside you invented is not the writer's voice, it is
generic texture in place of generic polish.
