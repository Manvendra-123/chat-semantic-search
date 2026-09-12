"""Accuracy on the 40 labeled queries, with the hard 8 reported separately."""

from __future__ import annotations

import json
from pathlib import Path

from chatsearch.index import ChatIndex, load_messages
from chatsearch.retrieve import search

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def evaluate(k: int = 5) -> dict:
    messages = load_messages(DATA / "corpus.jsonl")
    queries = json.loads((DATA / "queries.json").read_text())
    index = ChatIndex(messages)
    rows = []
    for q in queries:
        _parsed, hits = search(index, q["query"], k=k)
        ids = [h.message_id for h in hits]
        rank = ids.index(q["gold_id"]) + 1 if q["gold_id"] in ids else None
        rows.append(
            {
                "id": q["id"],
                "query": q["query"],
                "gold_id": q["gold_id"],
                "hard": q["hard"],
                "intent": q["intent"],
                "zero_overlap": q["zero_overlap"],
                "hit@1": ids[:1] == [q["gold_id"]],
                "hit@5": q["gold_id"] in ids[:5],
                "rank": rank,
                "top": ids[:5],
            }
        )

    def agg(subset: list[dict]) -> dict:
        n = len(subset)
        hit1 = sum(r["hit@1"] for r in subset) / n
        hit5 = sum(r["hit@5"] for r in subset) / n
        mrr = sum((1 / r["rank"]) if r["rank"] else 0.0 for r in subset) / n
        return {"n": n, "hit@1": round(hit1, 4), "hit@5": round(hit5, 4), "mrr@5": round(mrr, 4)}

    all_rows = rows
    hard = [r for r in rows if r["hard"]]
    warm = [r for r in rows if not r["hard"]]
    report = {
        "all_40": agg(all_rows),
        "hard_8": agg(hard),
        "warmup_32": agg(warm),
        "note": (
            "Hit@1 is the number that matters. The gap between all-40 and hard-8 "
            "is the actual result of this project."
        ),
        "rows": rows,
    }
    (DATA / "eval_results.json").write_text(json.dumps(report, indent=2))
    print("all 40 ", report["all_40"])
    print("hard 8 ", report["hard_8"])
    print("warm 32", report["warmup_32"])
    missed = [r for r in rows if not r["hit@5"]]
    if missed:
        print("missed@5:")
        for r in missed:
            print(f"  {r['id']} {r['query']!r} gold={r['gold_id']} top={r['top']}")
    return report


def main() -> None:
    evaluate()


if __name__ == "__main__":
    main()
