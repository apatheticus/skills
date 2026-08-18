# Worked examples

One full rewrite per register, each showing the delivery format from Step 5 of
`SKILL.md`: register, draft, audit, final. Note how the *same* source failure —
fluent, confident, unspecific prose — gets a different fix in each register.

---

## Editorial

**Register:** Editorial. Personal blog post; author's own experience; voice is
the product.

### Before

> Learning to sail has been a truly transformative journey that has taught me
> invaluable lessons about patience, humility, and resilience. From the moment I
> first stepped aboard, I knew I was embarking on something special.
>
> Sailing is not just a sport — it's a profound conversation with the natural
> world, one that underscores our deep connection to forces far greater than
> ourselves. The learning curve is steep, but every challenge rewards you with
> hard-won confidence and a renewed appreciation for the sea.
>
> Despite these challenges, the journey has been incredibly rewarding. If you're
> considering taking up sailing, I wholeheartedly encourage you to take the
> plunge. You won't regret it! ⛵

### Audit

- §1 significance inflation ("transformative journey", "forces far greater than ourselves")
- §10 rule of three, twice ("patience, humility, and resilience")
- §9 negative parallelism ("not just a sport — it's a...")
- §6 formulaic "Despite these challenges" pivot
- §25 generic positive conclusion; §18 emoji; §14 one em dash in three paragraphs
  of short copy, where the budget is none — and it sits inside the §9 construction,
  so it goes with that rewrite
- Tier 1 vocabulary: *transformative*, *invaluable*, *profound*, *underscores*
- No specific detail anywhere. Nothing here happened to a particular person on a
  particular day.

### After

> I have been learning to sail for about eight months and I am still bad at it.
>
> Most of it is waiting. You rig the boat,
> you check the forecast, you drive forty minutes to the marina, and then the wind
> dies and you sit there. My instructor calls this "sailing." I called it
> something else for the first two months.
>
> What changed my mind was a Tuesday in March when the wind came up while I was
> still fumbling the mainsheet, and for about ninety seconds the boat did exactly
> what it was supposed to and I did not have to think about any of it. Then I
> oversteered and we rounded up into the wind and my instructor laughed at me.
> That is apparently the whole thing. Ninety good seconds, then you fix what you
> broke.
>
> I would tell you to try it, but honestly it depends on whether you can tolerate
> being bad at something in front of a stranger for a year.

Personality **on**: an opinion, a specific Tuesday, an unresolved feeling, a
sentence fragment, wide length variance, a closing that refuses the upbeat
ending. "Most of it is waiting" states the claim without the §35 setup ("the part
nobody warns you about") that would have flattered the writer for knowing it.

---

## Professional

**Register:** Professional. Internal recommendation memo to a decision-maker.

### Before

> Our team has conducted a comprehensive evaluation of the vendor landscape and
> is pleased to share several valuable insights. It's important to note that each
> option presents a unique set of tradeoffs.
>
> Vendor A offers a robust, scalable, and cost-effective solution that could
> potentially deliver significant value. Vendor B, meanwhile, boasts a more
> mature feature set, underscoring its position as an industry leader. Experts
> generally agree that both are strong contenders.
>
> Ultimately, the decision will depend on organizational priorities. We look
> forward to continuing this important conversation.

### Audit

- §5 vague attribution ("experts generally agree")
- §24 hedging stacked ("could potentially deliver")
- §8 copula avoidance ("boasts", "offers")
- §10 rule of three ("robust, scalable, and cost-effective")
- §25 generic conclusion that makes no recommendation
- Tier 3 phrases: "valuable insights", "it's important to note that"
- **Stance failure.** A recommendation memo that recommends nothing. This is the
  register's characteristic failure mode.
- No institutional fact anywhere: no price, no date, no owner.

### After

> We evaluated four vendors against our three must-have requirements. We
> recommend Vendor A, with a decision needed by 14 March to hit the Q3 rollout.
>
> Vendor A meets all three requirements at $48k/year. Vendor B meets all three
> and has a better reporting module, but quoted $131k/year and could not commit
> to a SOC 2 report before Q4, which puts our own audit at risk. Vendors C and D
> failed the SSO requirement outright.
>
> The tradeoff we are accepting: Vendor A's reporting is weaker, and two teams
> will keep exporting to spreadsheets for roughly six months until their Q4
> release ships. We think that is worth $83k.
>
> If you want to proceed, Dana will start the security review this week. If you
> would rather revisit Vendor B, we need to know by 7 March to keep the timeline.

Personality **off**. Stance **directive**: a named recommendation, a named
tradeoff, a price, a date, an owner, and the cost of delay.

The colon in "The tradeoff we are accepting:" stays. §34 catches the colon that
withholds a short payload for drama, not the one that labels substance — the test
is in that entry, and this is the boundary case it describes.

---

## Technical

**Register:** Technical. Architecture decision record.

### Before

> We have implemented a robust caching layer that seamlessly integrates with our
> existing infrastructure, significantly enhancing performance across the board.
>
> This change was made to replace the previous approach, which was causing
> performance issues under load. The new implementation leverages a
> multi-layered strategy that ensures optimal response times while maintaining
> data consistency.
>
> **Benefits:** Improved latency, better scalability, and reduced database load.

### Audit

- §30 diff-anchored writing — "was made to replace the previous approach" tells a
  reader nothing about what the system *is*. Elevated pattern for this register.
- §3 superficial -ing ("ensuring optimal response times")
- §10 rule of three in the benefits line
- §4 promotional ("seamlessly integrates", "across the board")
- §15/§16 bolded inline header doing analysis work
- Zero reproducible artifacts: no TTL, no cache name, no measured number, no
  invalidation semantics. Confident vagueness, the register's failure mode.
- Note *robust* and *leverages* here: Tier 2 says **keep** `robust` in Technical
  when it means robustness. It does not mean that here, so it goes.

### After

> Read-heavy endpoints now serve from a two-tier cache: an in-process LRU
> (10k entries, 30s TTL) in front of Redis (15m TTL).
>
> On a cache miss both tiers are populated. Writes invalidate by key prefix
> through a Redis pub/sub channel; the in-process tier subscribes on boot, so a
> pod that misses an invalidation message can serve stale data for up to 30s.
> That window is acceptable for the catalog endpoints and is not acceptable for
> pricing, which bypasses the cache entirely.
>
> Measured on the 2024-11 load test: p99 on `GET /catalog/items` fell from 840ms
> to 95ms, and read queries against Postgres dropped about 70%.
>
> Known limits: no cache warming, so the first request after a deploy pays full
> latency. Redis is a single point of failure for this path; if it is unavailable
> the service falls back to direct queries and p99 returns to roughly 840ms.

Specificity currency **reproducible artifact**. Stance **candid** — the stale
window, the SPOF, and the missing warm-up are stated, not buried.

---

## Regulated

**Register:** Regulated. User manual section for a federal customer.

> **Scope note.** The reader here is a government one, so the rewrite runs the
> Regulated register inside the plain-language envelope in
> `reference/plain-language.md`. It shows the voice pass only. Section 508, GPO
> style, agency style guides and mandated section structures are outside this
> skill and were not checked.

### Before

> In order to facilitate the submission of your application, it is important to
> note that applicants must ensure that all required documentation has been
> uploaded prior to the deadline.
>
> The system leverages a robust validation framework — ensuring that submissions
> are processed accurately and efficiently. In the event that an application is
> found to be incomplete, a notification will be sent to the applicant.
>
> **Next Steps:** Applicants should review their submission carefully.

### Audit

- §13 passive voice throughout ("a notification will be sent") — hard rule here
- §23 filler: "in order to", "prior to", "in the event that", "it is important to note that"
- Tier 1/2: *facilitate*, *leverages*, *robust* (not robustness), *ensuring*
- §3 superficial -ing
- Sentence 1 is 34 words — over the 30-word cap
- Does not address the reader. "The applicant" where "you" works
- §17 title case and §14 em dash are **off** in this register; leave to house
  style rather than "fixing" them here

### After

> Upload all required documents before the deadline. You cannot submit an
> incomplete application.
>
> The system checks your documents when you submit. If anything is missing, the
> system sends you an email within one business day listing what to add. You can
> then upload the missing documents and submit again.
>
> Before you submit, check that each document opens correctly and matches the
> name on your application.

Active voice, second person, every sentence under 30 words, filler removed,
Tier 1 and Tier 2 words replaced. The mandated heading structure and any agency
style rules stay untouched — those belong to the compliance skill, not this one.

---

## What the four have in common

Every "before" above is fluent, grammatical, and confident. None is
*wrong* in a way a spellchecker would catch. What each lacks is the thing its
register uses as evidence that a person wrote it:

| Register | Evidence of a human |
| --- | --- |
| Editorial | A specific Tuesday, an unresolved feeling |
| Professional | A price, a date, an owner, a stated tradeoff |
| Technical | A TTL, a p99, a named failure mode |
| Regulated | A direct instruction the reader can act on |

If the rewrite adds none of these, it has removed AI tells without adding a human
voice, and it will still read as machine-written.
