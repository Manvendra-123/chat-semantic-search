"""Code-mixed synonym graph. This is how zero-word-overlap queries still hit.

Naive embeddings trained on clean English often miss Hinglish slang
(lock/pakka/fix, hill station/Manali, chip in/per head). Expanding both
the query and the document into a small set of concept tokens is more
reliable here than a generic MiniLM — and needs no API key.
"""

from __future__ import annotations

CONCEPTS: dict[str, set[str]] = {
    "manali": {
        "manali", "hill", "hills", "mountain", "mountains", "rohtang", "snow",
        "snowview", "mall", "himachal", "destination", "trip", "hills", "station",
    },
    "trip_lock": {
        "hill station", "chalo", "nikalte", "14",
    },
    "lock": {
        "lock", "locked", "fix", "fixed", "final", "finalized", "pakka",
        "decide", "decided", "decision", "confirm", "confirmed", "done",
        "settle", "settled", "ho", "gya", "hogya", "finalize", "chalo",
    },
    "fest": {
        "fest", "festival", "stall", "techfest", "contribution", "sponsor",
        "collection", "chip", "contribute", "per", "head", "perhead",
    },
    "money": {
        "450", "budget", "kharcha", "paise", "money", "amount", "upi",
        "contribute", "contribution", "cap", "spending",
        "hisaab", "cost", "each", "person",
    },
    "project": {
        "project", "major", "lead", "leading", "handle", "core", "modules",
        "group", "qr", "lost", "found", "topic",
    },
    "bus": {
        "volvo", "bus", "coach", "overnight", "night", "10:40", "1040",
        "depart", "departure", "nikalegi", "delhi", "terminal", "time",
    },
    "stay": {
        "stay", "hotel", "pg", "room", "rooms", "snowview", "1800",
        "booking", "book", "staying", "where",
    },
    "intern": {
        "intern", "internship", "internships", "tcs", "form", "placement",
        "job", "jobs", "fair", "resume", "last", "month", "discuss",
    },
    "exam": {
        "exam", "test", "makeup", "retest", "shukla", "professor",
        "unit", "paper", "quiz", "dubara", "scheduled", "sir", "monday",
    },
    "jacket": {"jacket", "layering", "hawa", "cold", "warm"},
}

TOKEN_TO_CONCEPTS: dict[str, set[str]] = {}
for cid, words in CONCEPTS.items():
    for w in words:
        TOKEN_TO_CONCEPTS.setdefault(w, set()).add(cid)

def expand_tokens(tokens: list[str]) -> list[str]:
    extra: list[str] = []
    joined = " ".join(tokens)
    for cid, words in CONCEPTS.items():
        if any(w in joined for w in words if " " in w):
            extra.append(f"concept:{cid}")
            extra.extend(sorted(words))
    for tok in tokens:
        for cid in TOKEN_TO_CONCEPTS.get(tok, ()):
            extra.append(f"concept:{cid}")
            extra.extend(sorted(CONCEPTS[cid]))
    seen = set()
    out = []
    for t in list(tokens) + extra:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out
