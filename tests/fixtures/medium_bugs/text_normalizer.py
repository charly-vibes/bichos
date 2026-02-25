"""Text normalization utilities.

Provides functions for cleaning, normalizing, and tokenizing text strings.
Used in search indexing, NLP preprocessing, and data import pipelines.
"""

from __future__ import annotations

import re
import unicodedata


_WHITESPACE_RE = re.compile(r"\s+")
_NON_ALPHANUMERIC_RE = re.compile(r"[^\w\s-]", flags=re.UNICODE)
_REPEATED_PUNCT_RE = re.compile(r"([^\w\s])\1+")
_URL_RE = re.compile(
    r"https?://[^\s]+",
    flags=re.IGNORECASE,
)
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")


def normalize_unicode(text: str) -> str:
    """Decompose and recompose Unicode to NFC form."""
    return unicodedata.normalize("NFC", text)


def strip_accents(text: str) -> str:
    """Remove diacritics by decomposing to NFD and dropping combining marks."""
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def collapse_whitespace(text: str) -> str:
    """Replace any run of whitespace with a single space and strip ends."""
    return _WHITESPACE_RE.sub(" ", text).strip()


def remove_urls(text: str, placeholder: str = "") -> str:
    """Replace all HTTP/HTTPS URLs with placeholder."""
    return _URL_RE.sub(placeholder, text)


def remove_emails(text: str, placeholder: str = "") -> str:
    """Replace all email-like tokens with placeholder."""
    return _EMAIL_RE.sub(placeholder, text)


def slugify(text: str, separator: str = "-", max_length: int = 100) -> str:
    """Convert text to a URL-safe slug.

    Steps: lowercase → strip accents → remove non-alphanumeric → collapse
    whitespace → replace spaces with separator → truncate.
    """
    text = text.lower()
    text = strip_accents(text)
    text = _NON_ALPHANUMERIC_RE.sub(" ", text)
    text = collapse_whitespace(text)
    text = text.replace(" ", separator)
    return text[:max_length]


def truncate(text: str, max_chars: int, ellipsis: str = "...") -> str:
    """Truncate text to at most max_chars, appending ellipsis if cut."""
    if len(text) <= max_chars:
        return text
    cutoff = max_chars - len(ellipsis)
    if cutoff <= 0:
        return ellipsis[:max_chars]
    return text[:cutoff] + ellipsis


def word_count(text: str) -> int:
    """Return the number of whitespace-delimited tokens in text."""
    return len(text.split())


def tokenize(text: str, lowercase: bool = True) -> list[str]:
    """Split text into cleaned tokens, optionally lowercased."""
    if lowercase:
        text = text.lower()
    text = strip_accents(text)
    text = _NON_ALPHANUMERIC_RE.sub(" ", text)
    tokens = text.split()
    return [t for t in tokens if t]


def sentence_split(text: str) -> list[str]:
    """Naively split text into sentences by terminal punctuation."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]
