#!/usr/bin/env python3
"""Count the mechanical half of human-voice's Step 4 self-check.

    python3 voice_check.py <file.md> --register E|P|T|R [--gov]

Reports, never rewrites. Tier 1 and Tier 3 vocabulary hits are defects and exit
non-zero; everything else is advisory, because the register tables in SKILL.md
are targets rather than gates and treating them as gates fights both §24
calibrated uncertainty and Regulated's plain-language brevity.

A Tier 2 hit comes back as QUERY and never as a replacement. Running that tier as
a find-and-replace breaks technical documents, which is the specific failure the
tier exists to prevent (reference/vocabulary.md).

Carve-outs are applied before any check runs -- fenced blocks, inline code spans,
link targets, blockquoted lines and quoted material are masked out, so a banned
word being *used* rather than written is never reported. Masking preserves offsets
so reported line numbers stay true.

Known limit, stated rather than papered over: a document *about* AI tells reports
its own examples. The carve-outs cover mention that markdown marks as such -- code,
links, blockquotes, quotation -- and nothing distinguishes an unmarked exemplar of
bad prose from bad prose, because on the page they are the same characters. This
skill's own reference/patterns-core.md returns 23 tier-1 errors for exactly that
reason and is correct as written. No carve-out was added for single-word emphasis
(`*facilitate*`): the span is identical whether the word is being mentioned or
emphatically used, so suppressing it would trade real tier-1 detections for a
lower false-positive rate on the rare document whose subject is the word list.

--gov adds two government-scoped checks from reference/plain-language.md, and is
rejected outside --register R because those rules are written for a U.S.
government audience and are wrong on an essay. It covers SSG1 hidden verbs and
SSG3 stacked negations, both WARN.

There is deliberately **no SSG2 noun-string check**. Telling "laboratory animal
facility management plan" from "New York City Department of Transportation"
needs part-of-speech tagging, and a regex over capitalisation would flag every
proper name in a federal document. Do not read a clean --gov run as evidence
that noun strings were checked; they were not. Nor are the substitution table,
SSG4, SSG5, SSG6 or SSG7 -- all of those need judgment and stay with the reader.
"""

import argparse
import re
import sys
from collections import Counter

# --- register configuration -------------------------------------------------
# Thresholds come from SKILL.md Step 4.2; gates from reference/patterns-gated.md.
# Kept inline rather than in a JSON sibling: it is a 4x4 table of numbers and a
# second file would not earn its maintenance.

REGISTERS = {
    "E": {
        "name": "Editorial",
        "max_similar_run": 3,      # max consecutive similar-length sentences
        "avg_range": None,          # wide variance is correct here
        "sentence_hard_cap": None,
        "dash": True,               # SS14 on
        "title_case": True,         # SS17 on
        "hyphen_pairs": True,       # SS26 on
        "emoji": "sparing",         # SS18 limited
    },
    "P": {
        "name": "Professional",
        "max_similar_run": 4,
        "avg_range": (15, 25),
        "sentence_hard_cap": None,
        "dash": True,
        "title_case": True,
        "hyphen_pairs": True,
        "emoji": "banned",
    },
    "T": {
        "name": "Technical",
        "max_similar_run": 4,
        "avg_range": (15, 25),
        "sentence_hard_cap": None,
        "dash": True,
        "title_case": False,
        "hyphen_pairs": False,
        "emoji": "banned",
    },
    "R": {
        "name": "Regulated",
        "max_similar_run": None,    # no limit; brevity outranks burstiness
        "avg_range": (0, 20),
        "sentence_hard_cap": 30,    # hard cap, an ERROR
        "dash": False,              # SS14 off, house style governs
        "title_case": False,
        "hyphen_pairs": False,
        "emoji": "banned",
    },
}

# Two sentences count as "similar length" when their word counts sit within this
# many words of each other. Reported in the NOTE line so the number is legible.
SIMILAR_BAND = 3

# --- word lists (reference/vocabulary.md) -----------------------------------

TIER1 = [
    "delve", "tapestry", "testament", "multifaceted", "myriad", "synergy",
    "cognizant", "garner", "commence", "utilize", "elucidate", "facilitate",
    "endeavor", "intricacies", "pivotal", "paramount", "crucial", "invaluable",
    "indispensable", "groundbreaking", "revolutionary", "transformative",
    "cutting-edge", "seamless", "seamlessly", "compelling", "embrace", "foster",
    "fostering", "enduring", "vibrant", "breathtaking", "must-visit", "nestled",
    "renowned", "profound", "interplay", "intriguing", "remarkable", "noteworthy",
    "valuable", "underscore", "showcase", "furthermore", "moreover", "whilst",
]

TIER2 = [
    "harness", "realm", "leverage", "robust", "navigate", "sentinel", "key",
    "align with", "unlock", "unleash", "enhance", "illuminate", "intricate",
    "landscape", "actually", "scale", "scalable",
]

# Same sense, legal in some registers and not others. Value is the set of
# registers where the word is allowed.
TIER2B = {
    "hence": {"R"},
    "thereby": {"R"},
    "thereof": {"R"},
    "subsequently": {"T", "R"},
    "additionally": {"T", "R"},
    "shall": {"R"},
    "pursuant to": {"R"},
}

TIER3 = [
    "in today's", "it's important to note that", "it is important to note that",
    "it's worth noting that", "it should be mentioned that", "in summary",
    "in conclusion", "in essence", "harness the power of",
    "in the ever-evolving landscape of", "as we navigate the complexities of",
    "unlocking the potential of", "seamlessly integrate",
    "at the forefront of innovation", "a game-changing solution",
    "this is a testament to", "empowering users to", "it remains to be seen",
    "one might argue that", "from a broader perspective", "generally speaking",
    "shed light on", "valuable insights", "exciting possibilities",
    "in this section we will", "let's explore", "let's dive into",
]

FILLER = {
    "in order to": "to",
    "due to the fact that": "because",
    "at this point in time": "now",
    "in the event that": "if",
    "has the ability to": "can",
    "for the purpose of": "to",
    "in the near future": "soon, or give a date",
    "a large number of": "many, or give the number",
    "prior to": "before",
    "with regard to": "about",
    "in spite of the fact that": "although",
}

HYPHEN_PAIRS = [
    "third-party", "cross-functional", "client-facing", "data-driven",
    "decision-making", "well-known", "high-quality", "real-time", "long-term",
    "end-to-end",
]

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002700-\U000027BF\U0001F1E6-\U0001F1FF"
    "\U00002600-\U000026FF\U0001F900-\U0001F9FF\U0000FE0F\U00002B00-\U00002BFF]"
)

# Words that legitimately open many sentences and carry no style signal.
OPENER_EXEMPT = {"a", "an", "the", "it", "if", "in", "to", "for", "and", "but"}

# --- government-scoped patterns (--gov, Regulated only) ---------------------
# reference/plain-language.md SSG1 and SSG3. Deliberately narrow: these fire only
# for a U.S. government audience and would be wrong on an essay.

# SSG1 hidden verbs. A weak verb propping up a nominalization. Catches the common
# "make a determination" / "provide notification" shape, and nothing subtler --
# an untagged regex cannot tell "provide a solution" (fine) from "provide
# notification" (not), so both come back as WARN and a human adjudicates.
HIDDEN_VERB = re.compile(
    r"\b(?:mak\w+|made|tak\w+|took|giv\w+|gave|provid\w+|conduct\w*|perform\w*|"
    r"achiev\w+|effect\w*|undertak\w+|undertook|is|are|was|were)\s+"
    r"(?:a|an|the|in)?\s*"
    r"\w{4,}(?:tion|sion|ment|ance|ence|ity|ancy|ency)\b",
    re.I)

# SSG3 positive language. Two or more negations in one sentence, counted rather
# than parsed. "not ... unless ... except" is the shape that costs the reader an
# inversion per hop.
NEGATION = re.compile(
    r"\b(?:not|no|never|none|nor|cannot|can't|don't|doesn't|won't|shouldn't|"
    r"unless|except|excluding|other than|fails? to|failed to|failure to|"
    r"notwithstanding|absent|unable|ineligible|unlawful|prohibited|"
    r"disallowed|denied)\b",
    re.I)


class Finding:
    def __init__(self, sev, line, code, msg):
        self.sev, self.line, self.code, self.msg = sev, line, code, msg

    def __str__(self):
        # Quoted spans can straddle a line break; keep every finding on one line.
        msg = " ".join(self.msg.split())
        return f"{self.sev:<7} {self.code}: {msg} (L{self.line})"


# --- carve-outs -------------------------------------------------------------

def _blank(match):
    """Replace a span with spaces, keeping newlines so offsets and lines hold."""
    return "".join("\n" if c == "\n" else " " for c in match.group(0))


def mask(text):
    """Mask everything the skill forbids rewriting inside.

    Returns (masked_text, masked_char_count). Order matters: fenced blocks first,
    so a stray backtick or quote inside one cannot desynchronise later passes.
    """
    original_visible = sum(1 for c in text if not c.isspace())

    # Fenced code blocks (``` or ~~~), including unterminated ones at EOF.
    text = re.sub(r"^([`~]{3,})[^\n]*\n.*?^\1[^\n]*$", _blank, text,
                  flags=re.S | re.M)
    text = re.sub(r"^([`~]{3,})[^\n]*\n.*\Z", _blank, text, flags=re.S | re.M)

    # Indented code blocks (four spaces at line start, after a blank line).
    text = re.sub(r"(?<=\n\n)(?: {4}[^\n]*\n)+", _blank, text)

    # Inline code spans, longest delimiter run first.
    text = re.sub(r"(`{1,3})(?:(?!\1).)*?\1", _blank, text, flags=re.S)

    # Link and image targets, plus bare autolinks. Link *text* stays visible.
    text = re.sub(r"\]\([^)\n]*\)", _blank, text)
    text = re.sub(r"^\s*\[[^\]\n]+\]:[^\n]*$", _blank, text, flags=re.M)
    text = re.sub(r"<[^>\s]+>", _blank, text)

    # Blockquoted lines -- quoted from somewhere else by definition.
    text = re.sub(r"^\s*>[^\n]*$", _blank, text, flags=re.M)

    # Quoted material, straight and curly. Bounded to one line so an apostrophe
    # cannot swallow the rest of the document.
    text = re.sub(r"\"[^\"\n]{0,300}\"", _blank, text)
    text = re.sub(r"“[^”\n]{0,300}”", _blank, text)

    masked_visible = sum(1 for c in text if not c.isspace())
    return text, original_visible - masked_visible


# --- text structure ---------------------------------------------------------

def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


SENTENCE_END = re.compile(r"[.!?](?=[\s\"”)\]]|$)")
ABBREV = re.compile(r"\b(?:e\.g|i\.e|etc|vs|cf|Dr|Mr|Mrs|Ms|St|approx|No)\.$")


def sentences(text):
    """Yield (start_offset, sentence_text) over prose only.

    Headings, list markers, table rows and metadata lines are dropped -- they are
    not sentences and counting them wrecks every length statistic.
    """
    out = []
    for para_start, para in paragraphs(text):
        pos = 0
        for m in SENTENCE_END.finditer(para):
            chunk = para[pos:m.end()]
            if ABBREV.search(chunk.rstrip()):
                continue
            if chunk.strip():
                out.append((para_start + pos, chunk.strip()))
            pos = m.end()
        tail = para[pos:]
        if tail.strip():
            out.append((para_start + pos, tail.strip()))
    return out


def prose_lines(text):
    """Line indices (0-based) that carry prose rather than structure."""
    keep = []
    for i, line in enumerate(text.split("\n")):
        s = line.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith("|") or s.startswith("---"):
            continue
        if re.match(r"^[-*+]\s", s) or re.match(r"^\d+[.)]\s", s):
            continue
        keep.append(i)
    return keep


def paragraphs(text):
    """Yield (offset, text) for each run of consecutive prose lines."""
    lines = text.split("\n")
    starts, off = [], 0
    for line in lines:
        starts.append(off)
        off += len(line) + 1

    keep = set(prose_lines(text))
    out, cur, cur_start = [], [], None
    for i, line in enumerate(lines):
        if i in keep:
            if cur_start is None:
                cur_start = starts[i]
            cur.append(line)
        else:
            if cur:
                out.append((cur_start, " ".join(cur)))
            cur, cur_start = [], None
    if cur:
        out.append((cur_start, " ".join(cur)))
    return out


def words(s):
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'’-]*", s)


def sections(text):
    """Yield (heading_line_index, start_offset, end_offset) per ## section."""
    marks = [(m.start(), line_of(text, m.start()))
             for m in re.finditer(r"^#{1,6}\s", text, flags=re.M)]
    bounds = []
    for i, (start, _) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        bounds.append((start, end))
    return bounds or [(0, len(text))]


# --- checks -----------------------------------------------------------------

def check_vocabulary(masked, reg, findings):
    for w in TIER1:
        for m in re.finditer(r"\b" + re.escape(w) + r"\b", masked, re.I):
            findings.append(Finding("ERROR", line_of(masked, m.start()),
                                    "tier-1", f"'{m.group(0)}' — replace on sight"))
    for p in TIER3:
        for m in re.finditer(re.escape(p), masked, re.I):
            findings.append(Finding("ERROR", line_of(masked, m.start()),
                                    "tier-3", f"'{m.group(0)}'"))
    for w in TIER2:
        for m in re.finditer(r"\b" + re.escape(w) + r"\b", masked, re.I):
            findings.append(Finding(
                "QUERY", line_of(masked, m.start()), "tier-2",
                f"'{m.group(0)}' — carve-out? delete-and-reread? never auto-replace"))
    for w, allowed in TIER2B.items():
        if reg in allowed:
            continue
        for m in re.finditer(r"\b" + re.escape(w) + r"\b", masked, re.I):
            findings.append(Finding(
                "WARN", line_of(masked, m.start()), "tier-2b",
                f"'{m.group(0)}' is not carried in {REGISTERS[reg]['name']}"))
    for phrase, repl in FILLER.items():
        for m in re.finditer(re.escape(phrase), masked, re.I):
            findings.append(Finding("WARN", line_of(masked, m.start()),
                                    "filler", f"'{m.group(0)}' → {repl}"))


def check_sentences(masked, reg, findings, stats):
    cfg = REGISTERS[reg]
    sents = sentences(masked)
    counts = [len(words(s)) for _, s in sents]
    stats["sentences"] = len(sents)
    if not counts:
        return
    avg = sum(counts) / len(counts)
    stats["avg"] = avg

    if cfg["avg_range"]:
        lo, hi = cfg["avg_range"]
        if not (lo <= avg <= hi):
            findings.append(Finding(
                "WARN", 1, "length",
                f"average {avg:.1f} words, target {lo}-{hi}"))

    if cfg["sentence_hard_cap"]:
        cap = cfg["sentence_hard_cap"]
        for off, s in sents:
            n = len(words(s))
            if n > cap:
                findings.append(Finding(
                    "ERROR", line_of(masked, off), "length-cap",
                    f"{n} words, hard cap {cap} in {cfg['name']}"))

    if cfg["max_similar_run"]:
        limit = cfg["max_similar_run"]
        run_start, run = 0, [counts[0]]
        for i in range(1, len(counts)):
            if max(run + [counts[i]]) - min(run + [counts[i]]) <= SIMILAR_BAND:
                run.append(counts[i])
            else:
                if len(run) > limit:
                    findings.append(Finding(
                        "WARN", line_of(masked, sents[run_start][0]), "burstiness",
                        f"{len(run)} consecutive sentences within {SIMILAR_BAND} "
                        f"words of each other, limit {limit}"))
                run_start, run = i, [counts[i]]
        if len(run) > limit:
            findings.append(Finding(
                "WARN", line_of(masked, sents[run_start][0]), "burstiness",
                f"{len(run)} consecutive sentences within {SIMILAR_BAND} "
                f"words of each other, limit {limit}"))


def check_openers(masked, findings):
    for start, end in sections(masked):
        chunk = masked[start:end]
        first = []
        for off, s in sentences(chunk):
            w = words(s)
            if w:
                first.append((w[0].lower(), start + off))
        tally = Counter(w for w, _ in first)
        for word, n in tally.items():
            if n > 2 and word not in OPENER_EXEMPT:
                off = next(o for w, o in first if w == word)
                findings.append(Finding(
                    "WARN", line_of(masked, off), "openers",
                    f"'{word}' opens {n} sentences in this section, limit 2"))


def check_gov(masked, findings):
    """Government-scoped checks. Only runs under --gov, only in Regulated.

    Both are WARN. They are heuristics over a regex, not a parse, and a WARN that
    a reader dismisses costs less than a rule that silently stops firing.
    """
    for m in HIDDEN_VERB.finditer(masked):
        findings.append(Finding(
            "WARN", line_of(masked, m.start()), "gov-hidden-verb",
            f"'{' '.join(m.group(0).split())}' — hidden verb (§G1), use the verb itself"))

    for off, s in sentences(masked):
        hits = [m.group(0).lower() for m in NEGATION.finditer(s)]
        if len(hits) >= 2:
            findings.append(Finding(
                "WARN", line_of(masked, off), "gov-negation",
                f"{len(hits)} negations in one sentence ({', '.join(hits)}) — "
                f"state it positively (§G3)"))


def check_style(masked, reg, findings, stats):
    cfg = REGISTERS[reg]

    if cfg["dash"]:
        hits = list(re.finditer(r"[—–]|(?<=\s)--(?=\s)", masked))
        stats["dashes"] = len(hits)
        if len(hits) > 2:
            findings.append(Finding(
                "WARN", line_of(masked, hits[0].start()), "dashes",
                f"{len(hits)} em/en dashes — budget is one or two in a long draft"))

    curly = list(re.finditer(r"[“”‘’]", masked))
    if curly:
        findings.append(Finding(
            "WARN", line_of(masked, curly[0].start()), "curly-quotes",
            f"{len(curly)} curly quotes — weak alone, counts inside a cluster"))

    emoji = list(EMOJI.finditer(masked))
    if emoji:
        if cfg["emoji"] == "banned":
            findings.append(Finding(
                "WARN", line_of(masked, emoji[0].start()), "emoji",
                f"{len(emoji)} emoji, banned in {cfg['name']}"))
        elif len(emoji) > 2:
            findings.append(Finding(
                "WARN", line_of(masked, emoji[0].start()), "emoji",
                f"{len(emoji)} emoji — Editorial allows them sparingly"))

    bold = list(re.finditer(r"\*\*[^*\n]+\*\*", masked))
    total_words = len(words(masked))
    stats["bold"] = len(bold)
    if bold and total_words and len(bold) / total_words > 0.01:
        findings.append(Finding(
            "WARN", line_of(masked, bold[0].start()), "boldface",
            f"{len(bold)} bold spans in {total_words} words — over 1 per 100"))

    if cfg["title_case"]:
        for m in re.finditer(r"^#{1,6}\s+(.+)$", masked, flags=re.M):
            head = m.group(1).strip()
            ws = [w for w in words(head) if len(w) > 3]
            if len(ws) >= 3:
                caps = sum(1 for w in ws[1:] if w[0].isupper() and not w.isupper())
                if caps >= max(2, int(0.6 * (len(ws) - 1))):
                    findings.append(Finding(
                        "WARN", line_of(masked, m.start()), "title-case",
                        f"'{head}' — sentence case unless a style guide says otherwise"))

    if cfg["hyphen_pairs"]:
        for w in HYPHEN_PAIRS:
            for m in re.finditer(r"\bis\s+" + re.escape(w) + r"\b", masked, re.I):
                findings.append(Finding(
                    "WARN", line_of(masked, m.start()), "hyphen-pair",
                    f"'{m.group(0)}' — humans drop the hyphen after the noun"))


# --- driver -----------------------------------------------------------------

SEV_ORDER = {"PROBLEM": 0, "ERROR": 1, "WARN": 2, "QUERY": 3}


def run(text, reg, gov=False):
    """Pure function on a string. Returns (findings, stats).

    gov=True adds the government-scoped checks. It is meaningless outside
    Regulated and main() rejects the combination before getting here.
    """
    masked, masked_chars = mask(text)
    findings, stats = [], {"masked_chars": masked_chars}

    visible = sum(1 for c in masked if not c.isspace())
    stats["visible_chars"] = visible
    stats["words"] = len(words(masked))

    # Vacuous-pass guard. A document that is substantially all code or all
    # quotation has nothing left to check, and reporting "0 error(s)" there reads
    # as a pass when nothing was examined.
    # The ratio is the whole guard. A short draft is still checkable, so there is
    # no word floor beyond "nothing at all survived" -- a floor set any higher
    # reports a legitimate one-paragraph note as unchecked.
    total = visible + masked_chars
    if stats["words"] == 0 or (total and visible / total < 0.4):
        findings.append(Finding(
            "PROBLEM", 1, "nothing-to-check",
            f"only {visible} of {total} visible characters survived the carve-outs "
            f"({stats['words']} words) — too little prose to check, treat this "
            f"run as not performed"))
        return findings, stats

    check_vocabulary(masked, reg, findings)
    check_sentences(masked, reg, findings, stats)
    check_openers(masked, findings)
    check_style(masked, reg, findings, stats)
    if gov:
        check_gov(masked, findings)

    findings.sort(key=lambda f: (SEV_ORDER[f.sev], f.line))
    return findings, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("--register", required=True, choices=sorted(REGISTERS))
    ap.add_argument("--gov", action="store_true",
                    help="add the government-scoped checks from "
                         "reference/plain-language.md (Regulated only)")
    args = ap.parse_args()

    if args.gov and args.register != "R":
        ap.error("--gov applies only to --register R; the plain-language rules "
                 "are written for a U.S. government audience")

    try:
        text = open(args.file, encoding="utf-8").read()
    except OSError as exc:
        print(f"PROBLEM nothing-to-check: {exc}")
        return 1

    findings, stats = run(text, args.register, gov=args.gov)
    cfg = REGISTERS[args.register]

    note = (f"NOTE    {cfg['name']} register{' · government-scoped' if args.gov else ''} · "
            f"{stats['words']} words · "
            f"{stats.get('sentences', 0)} sentences · "
            f"{stats['masked_chars']} chars masked as code, links or quotation")
    if "avg" in stats:
        note += f" · avg {stats['avg']:.1f} words/sentence"
    note += f" · similar-length band ±{SIMILAR_BAND}"
    print(note)

    for f in findings:
        print(f)

    counts = Counter(f.sev for f in findings)
    print(f"{counts['ERROR']} error(s), {counts['WARN']} warning(s), "
          f"{counts['QUERY']} query(s), {counts['PROBLEM']} problem(s)")
    return 1 if counts["ERROR"] or counts["PROBLEM"] else 0


if __name__ == "__main__":
    sys.exit(main())
