"""Local demo server. No API keys. First request builds the index (a few seconds)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from chatsearch.index import ChatIndex, load_messages
from chatsearch.retrieve import search

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
STATIC = ROOT / "static"

app = FastAPI(title="Search a Group Chat Properly", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@lru_cache(maxsize=1)
def get_index() -> ChatIndex:
    return ChatIndex(load_messages(DATA / "corpus.jsonl"))


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


@app.get("/api/meta")
def meta():
    meta = json.loads((DATA / "corpus_meta.json").read_text())
    eval_path = DATA / "eval_results.json"
    eval_results = json.loads(eval_path.read_text()) if eval_path.exists() else None
    queries = json.loads((DATA / "queries.json").read_text())
    return {
        "corpus": meta,
        "eval": None
        if not eval_results
        else {k: eval_results[k] for k in ("all_40", "hard_8", "warmup_32", "note")},
        "examples": [
            {"query": q["query"], "hard": q["hard"], "intent": q["intent"]}
            for q in queries
            if q["id"] in {"H1", "H2", "H6", "W01", "W10", "W16"}
        ],
    }


@app.get("/api/search")
def api_search(q: str = Query(..., min_length=2), k: int = 8):
    index = get_index()
    parsed, hits = search(index, q, k=k)
    return {
        "query": q,
        "parsed": {
            "intents": parsed.intents,
            "people": parsed.people,
            "time_label": parsed.time_label,
            "tokens": parsed.tokens,
        },
        "hits": [
            {
                "message_id": h.message_id,
                "score": round(h.score, 5),
                "sender": h.sender,
                "ts": h.ts,
                "text": h.text,
                "why": h.why,
                "context": h.context,
            }
            for h in hits
        ],
    }


def main() -> None:
    import uvicorn

    uvicorn.run("chatsearch.serve:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
