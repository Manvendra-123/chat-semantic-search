"""Check which hard-8 queries truly have zero word overlap with their gold text,
and which ones the keyword baseline retrieves correctly (and why)."""

import json
from pathlib import Path
from chatsearch.textutil import tokenize, word_set

DATA = Path("data")

# --- 1. Zero-overlap check ---
queries = json.loads((DATA / "queries.json").read_text())
hard = [q for q in queries if q.get("hard")]

# Also load corpus so we can look at what keyword actually retrieves
corpus = []
with open(DATA / "corpus.jsonl") as f:
    for line in f:
        corpus.append(json.loads(line))

# Build id -> message lookup
id_to_msg = {m["id"]: m for m in corpus}

print("=" * 80)
print("STEP 1: Zero-overlap check on all 8 hard queries")
print("=" * 80)

STOP_WORDS = {"a", "an", "the", "is", "are", "was", "were", "do", "does", "did",
              "in", "on", "at", "to", "for", "of", "and", "or", "but", "not",
              "we", "i", "me", "my", "you", "he", "she", "it", "they", "them",
              "this", "that", "what", "when", "where", "who", "which", "how",
              "each", "should", "much", "about", "her", "his"}

for q in hard:
    q_tokens = word_set(q["query"])
    g_tokens = word_set(q["gold_text"])
    overlap = q_tokens & g_tokens
    # Also check with stopwords removed
    content_overlap = overlap - STOP_WORDS

    status = "✅ ZERO OVERLAP" if len(content_overlap) == 0 else "❌ HAS OVERLAP"
    print(f"\n{q['id']}: {status}")
    print(f"  Query:     {q['query']}")
    print(f"  Gold text: {q['gold_text']}")
    print(f"  Q tokens:  {sorted(q_tokens)}")
    print(f"  G tokens:  {sorted(g_tokens)}")
    if overlap:
        print(f"  ALL overlap:     {sorted(overlap)}")
        print(f"  CONTENT overlap: {sorted(content_overlap)}")
    else:
        print(f"  Overlap:   (none)")

print("\n" + "=" * 80)
print("STEP 2: Run keyword baseline on hard 8 and identify which it gets right")
print("=" * 80)

from chatsearch.index import ChatIndex, load_messages
from chatsearch.retrieve import search

messages = load_messages(DATA / "corpus.jsonl")
index = ChatIndex(messages)

for q in hard:
    _parsed, hits = search(index, q["query"], k=5, mode="keyword")
    ids = [h.message_id for h in hits]
    rank = ids.index(q["gold_id"]) + 1 if q["gold_id"] in ids else None

    status = f"RANK {rank}" if rank else "MISS"
    print(f"\n{q['id']}: {status}")
    print(f"  Query:     {q['query']}")
    print(f"  Gold:      [{q['gold_id']}] {q['gold_text']}")
    if rank:
        print(f"  *** KEYWORD FOUND IT — investigating why ***")
        # Show what the parsed query looks like
        print(f"  Parsed tokens: {_parsed.tokens}")
        # Check the gold text tokens vs expanded query tokens
        from chatsearch.lexicon import expand_tokens
        expanded_q = expand_tokens(_parsed.tokens)
        gold_tokens = set(tokenize(q["gold_text"]))
        expanded_overlap = set(expanded_q) & gold_tokens
        print(f"  Expanded query tokens: {sorted(set(expanded_q))}")
        print(f"  Gold text tokens:      {sorted(gold_tokens)}")
        print(f"  Overlap after expansion: {sorted(expanded_overlap)}")
    print(f"  Top 3 hits:")
    for i, h in enumerate(hits[:3]):
        print(f"    {i+1}. [{h.message_id}] {h.text[:100]}...")
