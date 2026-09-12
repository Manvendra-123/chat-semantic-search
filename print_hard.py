import json
with open("data/queries.json") as f:
    queries = json.load(f)
for q in queries:
    if q["hard"]:
        print(f"Query: {q['query']}, Gold ID: {q['gold_id']}")
        print(f"Gold text: {q['gold_text']}")
