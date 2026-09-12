"""Passage index: TF-IDF (word + char n-grams) + LSI + BM25 over windows.

A single message in this corpus is often "haan" or "+1". The unit of
retrieval is a short conversation window, then we point at the most
central message inside that window.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize as sk_normalize

from chatsearch.lexicon import expand_tokens
from chatsearch.textutil import tokenize

WINDOW = 4


@dataclass
class Passage:
    pid: int
    center_id: int
    start_idx: int
    end_idx: int
    sender: str
    ts: str
    text: str
    expanded: str


def load_messages(path: Path) -> list[dict]:
    out = []
    with path.open() as fh:
        for line in fh:
            out.append(json.loads(line))
    return out


def window_text(messages: list[dict], i: int, k: int = WINDOW) -> tuple[str, int, int]:
    lo = max(0, i - k)
    hi = min(len(messages), i + k + 1)
    parts = []
    for j in range(lo, hi):
        m = messages[j]
        mark = ">>" if j == i else "  "
        parts.append(f"{mark} {m['sender']}: {m['text']}")
    return "\n".join(parts), lo, hi


def build_passages(messages: list[dict]) -> list[Passage]:
    passages = []
    pid = 0
    for i, m in enumerate(messages):
        if m.get("kind") == "media_omitted" and not m.get("text"):
            continue
        raw, lo, hi = window_text(messages, i)
        toks = tokenize(raw)
        expanded = " ".join(expand_tokens(toks))
        passages.append(
            Passage(
                pid=pid,
                center_id=int(m["id"]),
                start_idx=lo,
                end_idx=hi,
                sender=m["sender"],
                ts=m["ts"],
                text=raw,
                expanded=expanded + " " + m["sender"].lower(),
            )
        )
        pid += 1
    return passages


class ChatIndex:
    def __init__(self, messages: list[dict]) -> None:
        self.messages = messages
        self.passages = build_passages(messages)
        self.id_to_idx = {m["id"]: i for i, m in enumerate(messages)}
        corpus = [p.expanded for p in self.passages]
        self.word_vec = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            min_df=1,
            max_features=80000,
            sublinear_tf=True,
        )
        self.char_vec = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=2,
            max_features=40000,
            sublinear_tf=True,
        )
        self.X_word = self.word_vec.fit_transform(corpus)
        self.X_char = self.char_vec.fit_transform(corpus)

        # Dense embeddings removed

        print("Running LSI...")
        n_comp = min(128, max(16, self.X_word.shape[0] // 40))
        self.svd = TruncatedSVD(n_components=n_comp, random_state=7)
        self.X_lsi = sk_normalize(self.svd.fit_transform(self.X_word))
        self.ts = [datetime.fromisoformat(m["ts"]) for m in messages]
        self.now = self.ts[-1]

    def encode_query(self, expanded_text: str) -> dict:
        qw = self.word_vec.transform([expanded_text])
        qc = self.char_vec.transform([expanded_text])
        ql = sk_normalize(self.svd.transform(qw))
        return {"word": qw, "char": qc, "lsi": ql}
