"""Hybrid retrieval: lexical + LSI + person filter + time filter + RRF.

Returning a naked message is useless in this corpus. Hits are always
expanded to the surrounding thread.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from chatsearch.index import WINDOW, ChatIndex
from chatsearch.lexicon import expand_tokens
from chatsearch.queryparse import ParsedQuery, parse_query
from chatsearch.textutil import tokenize

DECISION_HINTS = {
    "lock", "fix", "fixed", "pakka", "final", "done", "confirm", "decided", "settled"
}


@dataclass
class Hit:
    message_id: int
    score: float
    sender: str
    ts: str
    text: str
    why: list[str]
    context: list[dict]


def _sparse_scores(X, q) -> np.ndarray:
    # X is csr, q is 1 x V
    return (X @ q.T).toarray().ravel()


def _rrf(rank_lists: list[list[int]], k: int = 60) -> dict[int, float]:
    scores: dict[int, float] = {}
    for ranks in rank_lists:
        for r, pid in enumerate(ranks):
            scores[pid] = scores.get(pid, 0.0) + 1.0 / (k + r + 1)
    return scores


def _top_ids(scores: np.ndarray, n: int) -> list[int]:
    if len(scores) == 0:
        return []
    n = min(n, len(scores))
    idx = np.argpartition(scores, -n)[-n:]
    idx = idx[np.argsort(scores[idx])[::-1]]
    return [int(i) for i in idx]


def search(index: ChatIndex, query: str, k: int = 8) -> tuple[ParsedQuery, list[Hit]]:
    parsed = parse_query(query, index.now)
    expanded = " ".join(expand_tokens(parsed.tokens))
    qv = index.encode_query(expanded)

    word_s = _sparse_scores(index.X_word, qv["word"])
    char_s = _sparse_scores(index.X_char, qv["char"])
    lsi_s = cosine_similarity(qv["lsi"], index.X_lsi).ravel()

    # Structured gates as multiplicative boosts, not hard filters —
    # a hard filter on the wrong parse would hide the gold message.
    person_boost = np.ones(len(index.passages))
    time_boost = np.ones(len(index.passages))
    decision_boost = np.ones(len(index.passages))
    query_concepts = {
        token for token in expand_tokens(parsed.tokens) if token.startswith("concept:")
    }
    concept_boost = np.ones(len(index.passages))

    for i, p in enumerate(index.passages):
        if parsed.people:
            if p.sender in parsed.people:
                person_boost[i] = 1.55
            elif any(name.lower() in p.text.lower() for name in parsed.people):
                person_boost[i] = 1.15
            else:
                person_boost[i] = 0.72
        if parsed.time_start and parsed.time_end:
            ts = index.ts[index.id_to_idx[p.center_id]]
            if parsed.time_start <= ts < parsed.time_end:
                time_boost[i] = 1.7
            else:
                time_boost[i] = 0.55
        center = index.messages[index.id_to_idx[p.center_id]]
        ctoks = set(tokenize(center["text"]))
        if ctoks & DECISION_HINTS:
            decision_boost[i] = 1.25
        # Prefer substantive centers over "haan"
        if len(center["text"]) < 8:
            decision_boost[i] *= 0.65
        if query_concepts:
            center_concepts = {
                token
                for token in expand_tokens(tokenize(center["text"]))
                if token.startswith("concept:")
            }
            coverage = len(query_concepts & center_concepts) / len(query_concepts)
            concept_boost[i] = 1.0 + 8.0 * coverage

    fused = (
        0.42 * _z(word_s)
        + 0.18 * _z(char_s)
        + 0.22 * _z(lsi_s)
    ) * concept_boost
    fused *= person_boost * time_boost * decision_boost

    word_top = _top_ids(word_s * person_boost * time_boost * concept_boost, 80)
    lsi_top = _top_ids(lsi_s * person_boost * time_boost * concept_boost, 80)
    fused_top = _top_ids(fused, 80)
    rrf = _rrf([word_top, lsi_top, fused_top])
    ranked = _top_ids(fused, len(fused))

    hits: list[Hit] = []
    seen_centers: set[int] = set()
    for pid in ranked:
        p = index.passages[pid]
        if p.center_id in seen_centers:
            continue
        seen_centers.add(p.center_id)
        why = []
        if parsed.people and p.sender in parsed.people:
            why.append(f"person:{p.sender}")
        if parsed.time_label:
            ts = index.ts[index.id_to_idx[p.center_id]]
            if parsed.time_start <= ts < parsed.time_end:
                why.append(f"time:{parsed.time_label}")
        if "concept:" in p.expanded and any(t.startswith("concept:") for t in expand_tokens(parsed.tokens)):
            why.append("meaning:concept-overlap")
        why.append("hybrid:tfidf+lsi+rrf")
        best_msg_id = p.center_id
        best_score = 0.0

        for j in range(p.start_idx, p.end_idx):
            m = index.messages[j]
            msg_v = index.word_vec.transform([m["text"]])
            score = (msg_v @ qv["word"].T).toarray()[0, 0]
            if score > best_score:
                best_score = score
                best_msg_id = m["id"]

        ctx = []
        for j in range(p.start_idx, p.end_idx):
            m = index.messages[j]
            ctx.append(
                {
                    "id": m["id"],
                    "sender": m["sender"],
                    "ts": m["ts"],
                    "text": m["text"],
                    "kind": m["kind"],
                    "is_hit": m["id"] == best_msg_id,
                }
            )
        best_msg = index.messages[index.id_to_idx[best_msg_id]]
        hits.append(
            Hit(
                message_id=best_msg_id,
                score=float(rrf[pid]),
                sender=best_msg["sender"],
                ts=best_msg["ts"],
                text=best_msg["text"],
                why=why,
                context=ctx,
            )
        )
        if len(hits) >= k:
            break
    return parsed, hits


def _z(x: np.ndarray) -> np.ndarray:
    s = x.std()
    if s < 1e-9:
        return np.zeros_like(x)
    return (x - x.mean()) / s


def context_for_id(index: ChatIndex, message_id: int, k: int = WINDOW) -> list[dict]:
    i = index.id_to_idx[message_id]
    lo = max(0, i - k)
    hi = min(len(index.messages), i + k + 1)
    out = []
    for j in range(lo, hi):
        m = index.messages[j]
        out.append({**m, "is_hit": m["id"] == message_id})
    return out
