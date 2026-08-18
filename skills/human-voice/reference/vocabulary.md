# Vocabulary

Supports §7. **Do not apply this as one global blacklist.** A flat ban is the
single most damaging thing a humanizing pass can do to a technical or regulated
document, because a dozen of the most AI-coded words are also ordinary terms of
art.

Three tiers. Apply Tier 1 always; add Tier 2 for the selected register; treat
Tier 3 as phrase-level and near-global.

---

## Tier 1 — banned in every register

Statistically overrepresented in model output with no common technical meaning.
Replace on sight.

`delve` · `tapestry` (figurative) · `testament` · `multifaceted` · `myriad` ·
`synergy` · `cognizant` · `garner` · `commence` · `utilize` · `elucidate` ·
`facilitate` · `endeavor` · `intricacies` · `pivotal` · `paramount` · `crucial` ·
`invaluable` · `indispensable` · `groundbreaking` (figurative) · `revolutionary`
(figurative) · `transformative` · `cutting-edge` · `seamless` / `seamlessly` ·
`compelling` · `embrace` (figurative) · `foster` / `fostering` · `enduring` ·
`vibrant` (figurative) · `breathtaking` · `must-visit` · `nestled` · `renowned` ·
`profound` (figurative) · `interplay` · `intriguing` · `remarkable` ·
`noteworthy` · `valuable` · `underscore` (verb) · `showcase` (verb) ·
`furthermore` · `moreover` · `whilst`

**Standard replacements:** *utilize* → use · *commence* → start · *facilitate* →
help, enable · *elucidate* → explain · *myriad* → many · *paramount* → most
important · *crucial* → important, or say why · *garner* → get, receive ·
*showcase* → show · *whilst* → while · *valuable* → say what it is worth ·
*underscore*, *furthermore*, *moreover* → cut, and start the next sentence.

---

## Tier 2 — homonyms: ban the AI sense, keep the real one

Every word here is an AI tell **and** an ordinary term of art. The distinction is
**sense, not register** — "harness the power of Kubernetes" is a tell in a spec
just as much as in a blog post, while "spin up the test harness" is correct
everywhere.

So do not gate these by register. Read the sense, then decide.

| Word | Ban this sense | Never flag this sense |
| --- | --- | --- |
| `harness` | harness the power of | **test harness**, wiring harness |
| `realm` | the realm of possibility | **Kerberos/auth realm**, DNS realm |
| `leverage` (verb) | leverages a framework/strategy | financial leverage, leverage ratio |
| `robust` | a robust solution, robust offering | robustness testing, robust statistics, robust error handling |
| `navigate` | navigate the complexities of | UI navigation, navigating a tree or filesystem |
| `sentinel` | a sentinel of quality | **sentinel value**, Redis Sentinel |
| `key` (adj.) | a key moment, key role | cryptographic key, primary key, key-value |
| `align with` | aligns with our values | memory alignment, text alignment |
| `unlock` / `unleash` | unlock the potential of | unlocking an account, a record, a mutex |
| `enhance` | enhancing its appeal | image enhancement, signal enhancement |
| `illuminate` | illuminates the deeper issue | literal lighting, rendering |
| `intricate` | an intricate tapestry of | genuine structural complexity, described concretely |
| `landscape` | the evolving landscape of | literal geography, landscape orientation |
| `actually` | filler intensifier | actual state vs expected state |
| `scale` / `scalable` | built to scale, infinitely scalable | a measured scaling property, with numbers |

**The carve-out rule.** Before flagging any word in this tier, check whether it
sits inside a code span, an identifier, a file path, an error string, a quoted
source, a proper noun, or a citation. If it does, leave it — the word is being
*used*, not written. This is the fastest way to break a technical document.

**When the sense is ambiguous, look at what the sentence would lose.** Delete the
word and reread. If the sentence still says the same thing, it was a tell. "Our
robust test harness" loses nothing without *robust*; "robust to malformed UTF-8
input" collapses without it.

## Tier 2b — genuinely register-varying

The short list of words where the *same* sense is acceptable in one register and
not another.

| Word | E | P | T | R | Note |
| --- | :-: | :-: | :-: | :-: | --- |
| `hence` / `thereby` / `thereof` | ban | ban | ban | keep | Legal and regulatory drafting convention |
| `subsequently` | ban | ban | keep | keep | Step ordering in a procedure; elsewhere use *then* |
| `additionally` | ban | ban | keep | keep | Enumerating requirements; elsewhere start the sentence |
| `shall` | ban | ban | ban | keep* | Binding obligation in regulated drafting; elsewhere use *must* |
| `pursuant to` | ban | ban | ban | keep | Citation convention; elsewhere use *under* |

Everything else that is banned in one register is banned in all four. If a word
is not in this table and not in Tier 2, it belongs to Tier 1 or Tier 3.

\* **`shall` narrows for government audiences.** The Federal Plain Language
Guidelines require *must* for an obligation, on the grounds that courts have read
`shall` both ways. In a U.S. government document keep `shall` only inside quoted
statutory text or a mandated template, and write *must* everywhere else. Outside
government — clinical, safety and private legal drafting — the `keep` above
stands as written.

---

## Tier 3 — phrases

Near-global. Ban in every register unless a mandated template requires the
wording.

- "In today's ever-evolving world/landscape" — and any opener starting "In today's"
- "It's important to note that" / "It's worth noting that" / "It should be mentioned that"
- "In summary" / "In conclusion" / "In essence"
- "Harness the power of"
- "In the ever-evolving landscape of"
- "As we navigate the complexities of"
- "Unlocking the potential of"
- "Seamlessly integrate"
- "At the forefront of innovation"
- "A game-changing solution"
- "This is a testament to"
- "Empowering users to"
- "It remains to be seen"
- "One might argue that"
- "From a broader perspective"
- "Generally speaking"
- "Shed light on"
- "Valuable insights"
- "Exciting possibilities"
- "Not just X, but Y" (the construction, not the words)
- "In this section we will..." / "Let's explore..." / "Let's dive into..."

---

## Filler substitutions (all registers)

Mechanical and safe. These reinforce plain-language requirements rather than
fighting them.

| Instead of | Write |
| --- | --- |
| in order to | to |
| due to the fact that | because |
| at this point in time | now |
| in the event that | if |
| has the ability to | can |
| it is important to note that X shows | X shows |
| for the purpose of | to |
| in the near future | soon, or give a date |
| a large number of | many, or give the number |
| prior to | before |
| with regard to / regarding | about |
| in spite of the fact that | although |

---

## Verification

Scan the draft before delivering:

```bash
python3 scripts/voice_check.py <file> --register E|P|T|R
```

The checker carries all three tiers plus the register table, and it masks out
fenced blocks, inline code spans, link targets, blockquotes and quoted material
before scanning — so it applies the carve-out rule below by construction rather
than by remembering to. A plain grep does not, which is why one is no longer
printed here: the greps this section used to carry reported every banned word a
document was *quoting*, and the reader had to filter those by eye every time.

Without Python, do the scan by reading and say so in the delivery.

**Government documents take a second pass.** The federal substitution table in
`reference/plain-language.md` carries roughly sixty pairs the tiers here do not,
because they are solely Guideline-derived and wrong to enforce on an essay. The
checker does not carry that table; run it by reading.

A Tier 1 or Tier 3 hit is a defect and the checker exits non-zero on it. A
**Tier 2 hit is a question** — it comes back as `QUERY`, never as a replacement.
Apply the carve-out rule and the delete-and-reread test before touching one.
Treating that tier as a find-and-replace list will break technical documents,
which is the specific failure it exists to prevent, and it is why the checker has
no fix mode at all.

Everything else the checker prints is advisory. The sentence-length and
burstiness numbers in `SKILL.md` are targets rather than gates, and enforcing
them would fight both §24 calibrated uncertainty and Regulated's plain-language
brevity.

**Read the first line of the output.** It reports what was counted, including how
many characters the carve-outs masked. A `PROBLEM nothing-to-check` there means
almost nothing survived masking and the run proved nothing — a clean `0 error(s)`
underneath it would otherwise read as a pass.

**One limit worth knowing before you trust a count.** The carve-outs cover mention
that markdown marks as mention — code, links, blockquotes, quotation. They cannot
cover an unmarked exemplar, because a sentence quoted as an example of bad prose
and a sentence of bad prose are the same characters on the page. A document whose
*subject* is this word list therefore reports itself: `patterns-core.md` returns 23
Tier 1 errors and is correct as written. On ordinary prose the rate is what you
would expect — this skill's own README returns one, and that one is a real defect.
