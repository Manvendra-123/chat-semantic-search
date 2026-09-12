from __future__ import annotations

import re
import unicodedata

WORD_RE = re.compile(r"[a-zA-Z0-9]+", re.UNICODE)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = text.lower().replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    return WORD_RE.findall(normalize(text))


def word_set(text: str) -> set[str]:
    return set(tokenize(text))


def zero_overlap(query: str, message: str) -> bool:
    q = word_set(query)
    m = word_set(message)
    return q.isdisjoint(m)


def overlap_tokens(query: str, message: str) -> set[str]:
    return word_set(query) & word_set(message)
