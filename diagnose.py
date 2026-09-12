import json
import os
import numpy as np
from pathlib import Path

from chatsearch.index import ChatIndex, load_messages
from chatsearch.retrieve import search, parse_query, expand_tokens, _top_ids, _sparse_scores
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

def calc_metrics(rows, k: int) -> dict:
    hits = [r["rank"] for r in rows if r["rank"] is not None]
    return {
        "n": len(rows),
        "hit@1": sum(1 for r in hits if r == 1) / len(rows) if rows else 0,
        "hit@3": sum(1 for r in hits if r <= 3) / len(rows) if rows else 0,
        "mrr": sum(1.0 / r for r in hits if r <= k) / len(rows) if rows else 0
    }

def run_diagnostics():
    print("--- 3. CACHE ALIGNMENT ---")
    corpus_time = os.path.getmtime(DATA / "corpus.jsonl")
    dense_time = os.path.getmtime(DATA / "dense.npy") if (DATA / "dense.npy").exists() else 0
    print(f"corpus.jsonl modified: {corpus_time}")
    print(f"dense.npy modified:    {dense_time}")
    print(f"Is dense.npy newer than corpus? {dense_time > corpus_time}")

    messages = load_messages(DATA / "corpus.jsonl")
    queries = json.loads((DATA / "queries.json").read_text())
    index = ChatIndex(messages)

    print(f"\nX_dense shape: {index.X_dense.shape}")
    print(f"Number of passages (windows): {len(index.passages)}")
    if index.X_dense.shape[0] != len(index.passages):
        print("MISMATCH! Cache is stale or misaligned.")
    else:
        print("Row count matches.")

    print("\n--- 1 & 2. CHANNEL EVALUATIONS ---")

    modes = {
        "tf-idf + lsi (no dense)": lambda qs, zs, ls, ds: qs + ls,
        "word-only": lambda qs, zs, ls, ds: qs,
        "char-only": lambda qs, zs, ls, ds: zs,
        "lsi-only": lambda qs, zs, ls, ds: ls,
        "dense-only": lambda qs, zs, ls, ds: ds
    }

    # We will compute scores directly to avoid retrieve.py's RRF and mode flags for this diagnostic
    results = {m: {"all": [], "warm": [], "hard": []} for m in modes}

    for q in queries:
        parsed = parse_query(q["query"], index.now)
        expanded = " ".join(expand_tokens(parsed.tokens))
        qv = index.encode_query(expanded)

        # We don't apply the z-score norm or boosts here to see RAW channel performance.
        # Actually, TF-IDF+LSI needs some scaling. Let's just use raw values for relative ranking.
        word_s = _sparse_scores(index.X_word, qv["word"])
        char_s = _sparse_scores(index.X_char, qv["char"])
        lsi_s = cosine_similarity(qv["lsi"], index.X_lsi).ravel()
        dense_msg_s = cosine_similarity(qv["dense"], index.X_dense).ravel()
        dense_s = np.zeros(len(index.passages))
        for i, score in enumerate(dense_msg_s):
            dense_s[index.dense_msg_ids[i]] = score

        for m, func in modes.items():
            scores = func(word_s, char_s, lsi_s, dense_s)
            ranked = _top_ids(scores, len(scores))

            # intra-window selection logic
            hits = []
            seen = set()
            for pid in ranked:
                p = index.passages[pid]
                best_msg_id = p.center_id
                # simple selection: just center id for diagnostic
                if best_msg_id not in seen:
                    seen.add(best_msg_id)
                    hits.append(best_msg_id)
                if len(hits) == 5:
                    break

            rank = hits.index(q["gold_id"]) + 1 if q["gold_id"] in hits else None
            row = {"id": q["id"], "rank": rank}
            results[m]["all"].append(row)
            if q["hard"]:
                results[m]["hard"].append(row)
            else:
                results[m]["warm"].append(row)

    for m in modes:
        print(f"\nMode: {m}")
        kw = calc_metrics(results[m]["all"], 5)
        kw_w = calc_metrics(results[m]["warm"], 5)
        kw_h = calc_metrics(results[m]["hard"], 5)
        print(f"  Overall 40: hit@1={kw['hit@1']:.3f}")
        print(f"  Warmup 32:  hit@1={kw_w['hit@1']:.3f}")
        print(f"  Hard 8:     hit@1={kw_h['hit@1']:.3f}")

    print("\n--- 4. TOP-5 FOR HARD QUERY (DENSE-ONLY) ---")
    hard_q = [q for q in queries if q["hard"]][0]
    print(f"Query: '{hard_q['query']}'")
    print(f"Gold text: '{hard_q['gold_text']}'\n")

    parsed = parse_query(hard_q["query"], index.now)
    expanded = " ".join(expand_tokens(parsed.tokens))
    qv = index.encode_query(expanded)
    dense_msg_s = cosine_similarity(qv["dense"], index.X_dense).ravel()
    dense_s = np.zeros(len(index.passages))
    for i, score in enumerate(dense_msg_s):
        dense_s[index.dense_msg_ids[i]] = score

    ranked = _top_ids(dense_s, len(dense_s))
    hits = []
    seen = set()
    for pid in ranked:
        p = index.passages[pid]
        best_msg_id = p.center_id
        if best_msg_id not in seen:
            seen.add(best_msg_id)
            hits.append((best_msg_id, p, pid))
        if len(hits) == 5:
            break

    for i, (msg_id, p, pid) in enumerate(hits):
        center_text = index.messages[index.id_to_idx[msg_id]]["text"]
        print(f"Rank {i+1} (score {dense_s[pid]:.3f}): '{center_text}'")

if __name__ == "__main__":
    run_diagnostics()
