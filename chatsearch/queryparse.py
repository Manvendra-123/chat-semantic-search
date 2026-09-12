"""Split a chat search box into meaning / person / time constraints.

One retriever cannot serve all three well. The router is rule-based on
purpose: it is inspectable in the UI, and it does not need a mocked LLM.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from chatsearch.textutil import normalize, tokenize

IST = ZoneInfo("Asia/Kolkata")

PEOPLE = {
    "rohit": "Rohit",
    "sneha": "Sneha",
    "ankit": "Ankit",
    "devansh": "Devansh",
    "aman": "Aman",
    "priya": "Priya",
    "kritika": "Kritika",
    "ishaan": "Ishaan",
    "she": None,  # resolved later from context; still marks person intent
    "he": None,
}

MONTHS = {
    "jan": 1, "january": 1, "januari": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

HINDI_MONTH = {
    "pichle mahine": "last_month",
    "pichle month": "last_month",
    "last month": "last_month",
    "last week": "last_week",
    "pichle hafte": "last_week",
    "yesterday": "yesterday",
    "kal": None,  # too ambiguous in Hinglish (kal = yesterday OR tomorrow)
}


@dataclass
class ParsedQuery:
    raw: str
    tokens: list[str]
    people: list[str]
    time_start: datetime | None
    time_end: datetime | None
    time_label: str | None
    intents: list[str]

    @property
    def is_person(self) -> bool:
        return "person" in self.intents

    @property
    def is_time(self) -> bool:
        return "time" in self.intents


def _shift_month(dt: datetime, delta: int) -> tuple[int, int]:
    month = dt.month - 1 + delta
    year = dt.year + month // 12
    month = month % 12 + 1
    return year, month


def parse_query(text: str, now: datetime) -> ParsedQuery:
    raw = text.strip()
    norm = normalize(raw)
    tokens = tokenize(norm)
    people: list[str] = []
    for tok in tokens:
        if tok in PEOPLE and PEOPLE[tok]:
            people.append(PEOPLE[tok])
    people = list(dict.fromkeys(people))

    time_start = time_end = None
    time_label = None

    for phrase, kind in HINDI_MONTH.items():
        if phrase and phrase in norm and kind:
            if kind == "last_month":
                y, m = _shift_month(now, -1)
                time_start = datetime(y, m, 1, tzinfo=now.tzinfo)
                ny, nm = _shift_month(time_start, 1)
                time_end = datetime(ny, nm, 1, tzinfo=now.tzinfo)
                time_label = f"{time_start:%B %Y}"
            elif kind == "last_week":
                time_end = now
                time_start = now - timedelta(days=7)
                time_label = "last 7 days"
            elif kind == "yesterday":
                start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                time_start = start
                time_end = start + timedelta(days=1)
                time_label = "yesterday"

    if time_start is None:
        for tok in tokens:
            if tok in MONTHS:
                month = MONTHS[tok]
                year = now.year
                time_start = datetime(year, month, 1, tzinfo=now.tzinfo)
                y, m = _shift_month(time_start, 1)
                time_end = datetime(y, m, 1, tzinfo=now.tzinfo)
                time_label = f"{time_start:%B %Y}"
                break

    intents = ["meaning"]
    if people:
        intents.append("person")
    if time_start is not None:
        intents.append("time")
    if re.search(r"\b(who|kisne|kaun)\b", norm):
        if "person" not in intents:
            intents.append("person")
    return ParsedQuery(
        raw=raw,
        tokens=tokens,
        people=people,
        time_start=time_start,
        time_end=time_end,
        time_label=time_label,
        intents=intents,
    )
