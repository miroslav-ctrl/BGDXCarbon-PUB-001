"""Validate document metadata without guessing a document's language."""

import re
import unicodedata

_LANGUAGE = re.compile(
    r"[A-Za-z]{2,3}(?:-[A-Za-z]{4})?(?:-(?:[A-Za-z]{2}|[0-9]{3}))?"
    r"(?P<variants>(?:-(?:[A-Za-z0-9]{5,8}|[0-9][A-Za-z0-9]{3}))*)"
)


def validate_title(value: str) -> str:
    """Require visible single-line text; retain punctuation and Unicode."""
    if not value.strip() or any(
        unicodedata.category(character) == "Cc" or character in "\u2028\u2029"
        for character in value
    ):
        raise ValueError("Title must be non-empty text without control characters.")
    return value


def validate_language(value: str) -> str:
    """Accept language, optional script/region and variants; no registry lookup."""
    match = _LANGUAGE.fullmatch(value)
    if match is None:
        raise ValueError(
            "Language must use language[-Script][-REGION][-variant] syntax."
        )
    variants = match.group("variants").lower().split("-")[1:]
    if len(variants) != len(set(variants)):
        raise ValueError("Language variants must not repeat (case-insensitive).")
    return value
