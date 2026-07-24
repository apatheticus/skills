# Attribution and provenance

This skill is a derivative work. Recording what came from where, because two of
the three sources carry license terms.

## Pattern catalog (§1–§33)

Derived from the **`humanizer`** Claude Code skill.

- Repository: <https://github.com/blader/humanizer>
- Author: blader (<https://github.com/blader>)
- License: MIT, © 2025 Siqi Chen
- Version this skill derived from: **2.8.2**

Retained: the 33-pattern taxonomy, the "words to watch" lists, most before/after
example pairs, the false-positive list, the signs-of-human-writing list, and the
draft → audit → final process.

Changed: every pattern carries register tags and several are now conditional or
off by register; the vocabulary list is split into tiers with technical
carve-outs; the personality section became one register profile rather than a
global mode with an inline exception; a federal routing rule was added; the
em dash ban became register-scoped rather than absolute.

MIT permits this reuse with attribution. The license text is reproduced in the
upstream repository.

## Underlying source

`humanizer` is itself based on **[Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)**,
maintained by WikiProject AI Cleanup, which is licensed **CC BY-SA 4.0**.

The pattern observations, and some example text that passed through `humanizer`,
originate there. CC BY-SA carries a share-alike obligation on substantial
reuse of the original expression. This skill reuses the *taxonomy and
observations* rather than Wikipedia prose verbatim, and most examples here were
rewritten, but the lineage is real and is recorded here rather than dropped.

**If you redistribute this skill,** keep this file and the attribution block at
the bottom of `SKILL.md`. If you extend it with verbatim Wikipedia text, review
the share-alike terms.

## Register model

The four-register model, the detector-mechanics framing (perplexity and
burstiness), the numeric sentence-length thresholds, and the vocabulary
blacklist seed list derive from a private, unversioned `human-voice` skill not
published anywhere. No license terms attach.

Substantially reworked here: the original had three content-type playbooks with
no ending guidance for two of them and a flat global blacklist. This version has
four registers, gates the pattern catalog by register, resolves the original's
conflicts with plain-language guidance, and adds the technical-term carve-outs
that a flat blacklist breaks.

## Plain-language floor

The floor in `registers.md` paraphrases publicly published U.S. federal
guidance: the Plain Writing Act of 2010 (Pub. L. 111-274) and the Federal Plain
Language Guidelines at <https://plainlanguage.gov>. U.S. government works are
not subject to copyright. It is a floor for the case where no compliance skill is
installed, not a compliance implementation.
