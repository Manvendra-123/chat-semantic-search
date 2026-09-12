"""Detailed eval showing per-query results for warmup and hard, plus shape breakdown."""
import json
from pathlib import Path
from chatsearch.index import ChatIndex, load_messages
from chatsearch.retrieve import search

DATA = Path("data")
messages = load_messages(DATA / "corpus.jsonl")
queries = json.loads((DATA / "queries.json").read_text())
index = ChatIndex(messages)

print("=" * 100)
print("PER-QUERY RESULTS (Hybrid)")
print("=" * 100)

shape_results = {"meaning": [], "person": [], "time": []}

for q in queries:
    _parsed, hits = search(index, q["query"], k=5, mode="hybrid")
    ids = [h.message_id for h in hits]
    rank = ids.index(q["gold_id"]) + 1 if q["gold_id"] in ids else None

    status = f"✅ rank={rank}" if rank and rank <= 3 else f"❌ rank={rank}" if rank else "❌ MISS"
    hit1 = 1 if rank == 1 else 0
    hit3 = 1 if rank and rank <= 3 else 0

    shape_results[q["intent"]].append({"hit1": hit1, "hit3": hit3, "rank": rank})

    if q["hard"] or not (rank and rank <= 1):
        print(f"  {q['id']:>4} [{q['intent']:>7}] {status:>15}  {q['query'][:50]}")
        if not (rank and rank <= 3):
            print(f"       Gold: [{q['gold_id']}] {q['gold_text'][:60]}")
            if hits:
                print(f"       Got:  [{hits[0].message_id}] {hits[0].text[:60]}")

print("\n" + "=" * 100)
print("PER-SHAPE BREAKDOWN (Hybrid)")
print("=" * 100)
print(f"{'Shape':>10} | {'n':>3} | {'Hit@1':>8} | {'Hit@3':>8} | {'MRR':>8}")
print("-" * 50)
for shape in ["meaning", "person", "time"]:
    rows = shape_results[shape]
    n = len(rows)
    h1 = sum(r["hit1"] for r in rows) / n if n else 0
    h3 = sum(r["hit3"] for r in rows) / n if n else 0
    mrr = sum(1.0/r["rank"] for r in rows if r["rank"]) / n if n else 0
    print(f"{shape:>10} | {n:>3} | {h1:>8.3f} | {h3:>8.3f} | {mrr:>8.3f}")
