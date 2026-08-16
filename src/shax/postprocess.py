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
