from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from chatsearch.textutil import zero_overlap

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

def load_jsonl(path: Path) -> list[dict]:
    with path.open() as fh:
        return [json.loads(line) for line in fh]

def load_json(path: Path) -> list[dict]:
    with path.open() as fh:
        return json.load(fh)

def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value)

def main() -> None:
    print("Running validation...")
    corpus = load_jsonl(DATA / "corpus.jsonl")
    queries = load_json(DATA / "queries.json")

    errors = []

    # Check 1: IDs unique and strictly increasing; timestamps chronological
    last_id = -1
    last_ts = None
    for msg in corpus:
        if msg["id"] <= last_id:
            errors.append(f"ID not strictly increasing at id {msg['id']}")
        last_id = msg["id"]

        ts = parse_ts(msg["ts"])
        if last_ts and ts < last_ts:
            errors.append(f"Timestamp not chronological at id {msg['id']}")
        last_ts = ts

    # Check 2: No text starts with its own sender
    for msg in corpus:
        if msg["text"].startswith(f"{msg['sender']}:"):
            errors.append(f"Text starts with sender prefix at id {msg['id']}")

    # Check 3: Substantive-line uniqueness >= 95%
    substantive_lines = [msg["text"] for msg in corpus if len(msg["text"]) > 12]
    unique_substantive = set(substantive_lines)
    if not substantive_lines:
        errors.append("No substantive lines found")
    else:
        uniqueness = len(unique_substantive) / len(substantive_lines)
        if uniqueness < 0.95:
            errors.append(f"Substantive-line uniqueness too low: {uniqueness:.2%} (< 95%)")
        else:
            print(f"Substantive-line uniqueness: {uniqueness:.2%}")

    # Check 7: All 8 participants present; >= 4,000 messages; span >= 5 months
    if len(corpus) < 4000:
        errors.append(f"Corpus size too small: {len(corpus)} (< 4000)")

    participants = {msg["sender"] for msg in corpus}
    if len(participants) != 8:
        errors.append(f"Expected 8 participants, found {len(participants)}: {participants}")

    start_ts = parse_ts(corpus[0]["ts"])
    end_ts = parse_ts(corpus[-1]["ts"])
    span_days = (end_ts - start_ts).days
    if span_days < 150:
        errors.append(f"Time span too short: {span_days} days (< 5 months)")

    # Queries checks
    corpus_ids = {msg["id"]: msg for msg in corpus}
    gold_ids_seen = set()

    # Check unique gold ids
    gold_counts = {}
    for q in queries:
        gold_counts[q["gold_id"]] = gold_counts.get(q["gold_id"], 0) + 1

    for gid, count in gold_counts.items():
        if count > 1:
            errors.append(f"gold_id {gid} used by multiple queries")

    hard_overlap_survivors = 0

    for q in queries:
        gold_id = q["gold_id"]

        # Check 4: Every gold_id exists
        if gold_id not in corpus_ids:
            errors.append(f"Query {q['id']} references missing gold_id {gold_id}")
            continue

        # Check 6: zero_overlap recomputed
        gold_msg = corpus_ids[gold_id]
        actual_overlap = zero_overlap(q["query"], gold_msg["text"])
        q["zero_overlap"] = actual_overlap
        if q["hard"] and actual_overlap:
            hard_overlap_survivors += 1

    if hard_overlap_survivors < 8:
        errors.append(f"Only {hard_overlap_survivors} hard queries survive zero_overlap check (< 8)")

    # Write back queries to overwrite the hand-written flag
    (DATA / "queries.json").write_text(json.dumps(queries, indent=2, ensure_ascii=False))

    if errors:
        print("\\nValidation failed with errors:")
        for err in errors:
            print(f"- {err}")
        import sys
        sys.exit(1)

    print("Validation passed!")

if __name__ == "__main__":
    main()
