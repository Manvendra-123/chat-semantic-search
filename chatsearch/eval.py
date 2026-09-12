"""Accuracy on the 40 labeled queries, with the hard 8 reported separately."""

from __future__ import annotations

import json
from pathlib import Path

from chatsearch.index import ChatIndex, load_messages
from chatsearch.retrieve import search

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

def calc_metrics(rows, k: int) -> dict:
    hits = [r["rank"] for r in rows if r["rank"] is not None]
    return {
        "n": len(rows),
        "hit@1": sum(1 for r in hits if r == 1) / len(rows) if rows else 0,
        "hit@3": sum(1 for r in hits if r <= 3) / len(rows) if rows else 0,
        "mrr": sum(1.0 / r for r in hits if r <= k) / len(rows) if rows else 0
    }

def evaluate(k: int = 5) -> None:
    messages = load_messages(DATA / "corpus.jsonl")
    queries = json.loads((DATA / "queries.json").read_text())
    index = ChatIndex(messages)
    
    results = {"hybrid": {"all": [], "hard": [], "warm": []}, 
               "keyword": {"all": [], "hard": [], "warm": []}}

    for mode in ["keyword", "hybrid"]:
        for q in queries:
            _parsed, hits = search(index, q["query"], k=k, mode=mode)
            ids = [h.message_id for h in hits]
            rank = ids.index(q["gold_id"]) + 1 if q["gold_id"] in ids else None
            
            row = {"id": q["id"], "rank": rank}
            results[mode]["all"].append(row)
            if q["hard"]:
                results[mode]["hard"].append(row)
            else:
                results[mode]["warm"].append(row)

    print(f"{'Split':<10} | {'Count':<5} | {'Keyword (BM25/Lexical) Baseline':<35} | {'Full Hybrid (TF-IDF + LSI)':<35}")
    print(f"{'':<10} | {'':<5} | {'Hit@1':<8} {'Hit@3':<8} {'MRR':<8} | {'Hit@1':<8} {'Hit@3':<8} {'MRR':<8}")
    print("-" * 105)
    
    for split in ["all", "warm", "hard"]:
        count = len(results["hybrid"][split])
        kw = calc_metrics(results["keyword"][split], k)
        hy = calc_metrics(results["hybrid"][split], k)
        
        kw_str = f"{kw['hit@1']:<8.3f} {kw['hit@3']:<8.3f} {kw['mrr']:<8.4f}"
        hy_str = f"{hy['hit@1']:<8.3f} {hy['hit@3']:<8.3f} {hy['mrr']:<8.4f}"
        
        split_name = {"all": "Overall 40", "hard": "Hard 8", "warm": "Warmup 32"}[split]
        print(f"{split_name:<10} | {count:<5} | {kw_str:<35} | {hy_str:<35}")

    print("\n" + "=" * 105)
    print("PER-SHAPE BREAKDOWN (Hybrid)")
    print("=" * 105)
    print(f"{'Shape':<10} | {'Count':<5} | {'Hit@1':<8} {'MRR':<8}")
    print("-" * 50)
    
    shape_results = {"meaning": [], "person": [], "time": []}
    for q in queries:
        ids = [h.message_id for _parsed, hits in [search(index, q["query"], k=k, mode="hybrid")] for h in hits]
        rank = ids.index(q["gold_id"]) + 1 if q["gold_id"] in ids else None
        shape_results[q["intent"]].append({"rank": rank})
        
    for shape in ["meaning", "person", "time"]:
        rows = shape_results[shape]
        count = len(rows)
        hy = calc_metrics(rows, k)
        print(f"{shape.capitalize():<10} | {count:<5} | {hy['hit@1']:<8.3f} {hy['mrr']:<8.4f}")

if __name__ == "__main__":
    evaluate(k=5)
