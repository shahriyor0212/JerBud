from __future__ import annotations

import re
from typing import Pattern

# A conservative list of common filler tokens/phrases to remove (simple token forms).
FILLER_TOKENS = [
    r"uh+",
    r"um+",
    r"umm+",
    r"uhh+",
    r"like",
    r"you\s+know",
    r"i\s+mean",
]

# Build a regex that captures optional punctuation surrounding the filler token.
_token_alt = "|".join(FILLER_TOKENS)
# Group 1: leading punctuation (commas/semicolons/colons/parentheses/quotes)
# Group 2: trailing punctuation (same set)
_FILLER_RE = re.compile(r"([,;:\(\)\"']*)\s*(?:" + _token_alt + r")\s*([,;:\(\)\"']*)", flags=re.IGNORECASE)


def _collapse_spaces(s: str) -> str:
    # Remove repeated spaces and fix spaces before punctuation
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s+([,.;:!?])", r"\1", s)
    return s.strip()


# Conservative set of common contractions transcribed without apostrophes.
_CONTRACTION_MAP = {
    "cant": "can't",
    "wont": "won't",
    "dont": "don't",
    "im": "I'm",
    "ive": "I've",
    "ill": "I'll",
    "youre": "you're",
    "youll": "you'll",
    "youve": "you've",
    "theyre": "they're",
    "theyll": "they'll",
    "theyve": "they've",
    "theres": "there's",
    "wheres": "where's",
    "heres": "here's",
    "whats": "what's",
    "thats": "that's",
    "didnt": "didn't",
    "doesnt": "doesn't",
    "isnt": "isn't",
    "wasnt": "wasn't",
    "werent": "weren't",
    "arent": "aren't",
    "havent": "haven't",
    "hasnt": "hasn't",
    "couldnt": "couldn't",
    "wouldnt": "wouldn't",
    "shouldnt": "shouldn't",
}

_CONTRACTION_RE = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in _CONTRACTION_MAP) + r")\b",
    flags=re.IGNORECASE,
)

_SENTENCE_BOUNDARY_RE = re.compile(r"([.!?])\s+([a-z])")


def _fix_contraction(m: re.Match) -> str:
    token = m.group(1)
    if token.isupper():
        # Preserve acronyms (e.g. "ID", "IM") instead of rewriting them.
        return token
    return _CONTRACTION_MAP[token.lower()]


def grammar_correct(text: str) -> str:
    """Return text with light, conservative grammar corrections applied.

    Rules applied (rule-based, on-device):
    - Collapse repeated whitespace and fix spacing around punctuation.
    - Restore common apostrophes in contracted words (e.g. "cant" -> "can't").
    - Capitalize standalone "i".
    - Capitalize the first letter of each sentence.
    - Ensure the final sentence ends with a period.

    Note: this is intentionally conservative and deterministic to avoid
    large-scale rewrites or introducing errors.
    """
    if not text:
        return text

    cleaned = _collapse_spaces(text)

    # Restore common contractions (e.g. "cant" -> "can't", "im" -> "I'm")
    cleaned = _CONTRACTION_RE.sub(_fix_contraction, cleaned)

    # Capitalize standalone "i"
    cleaned = re.sub(r"\bi\b", "I", cleaned)

    # Capitalize sentence starts
    cleaned = _SENTENCE_BOUNDARY_RE.sub(lambda m: m.group(1) + " " + m.group(2).upper(), cleaned)

    # Capitalize the first letter of the text
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]

    # Ensure the final sentence has ending punctuation
    if cleaned and not re.search(r"[.!?]\s*$", cleaned):
        cleaned = cleaned.rstrip() + "."

    return cleaned


def remove_fillers(text: str) -> str:
    """Return text with common filler words removed in a conservative way.

    Rules applied:
    - Remove standalone filler tokens/phrases (e.g. "uh", "umm", "you know", "like").
    - Collapse repeated fillers and extra whitespace.
    - Preserve other words and most punctuation.

    Note: this is intentionally conservative and rule-based to avoid large-scale rewrites.
    """
    if not text:
        return text

    # Remove filler tokens while preserving punctuation that belongs to the previous clause.
    def _repl(m: Pattern) -> str:  # pragma: no cover - small helper
        lead = m.group(1) or ""
        trail = m.group(2) or ""
        # If there is leading punctuation (e.g., a comma after the previous word), keep it.
        if re.search(r"[,;:]", lead):
            return lead + " "
        # Otherwise, prefer a single separating space (don't keep trailing punctuation here)
        return " "

    without = _FILLER_RE.sub(_repl, text)

    # Collapse spaces and tidy punctuation
    cleaned = _collapse_spaces(without)

    # Remove duplicate punctuation like ",," -> "," and ", ," -> ","
    cleaned = re.sub(r",\s*,+", ",", cleaned)
    cleaned = re.sub(r";\s*;+", ";", cleaned)

    # Remove leading punctuation leftover (e.g., ", I..." -> "I...")
    cleaned = re.sub(r"^[,;:\.\s]+", "", cleaned)

    # Final space/punctuation tidy
    cleaned = _collapse_spaces(cleaned)

    # Capitalize sentence starts if the original looked sentence-cased
    # (best-effort: if original first char was uppercase, keep it)
    if text and text[0].isupper() and cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]

    return cleaned
