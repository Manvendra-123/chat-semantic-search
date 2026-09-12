# Search a Group Chat Properly

Semantic search for a messy, Hinglish group chat. The goal is to find the right message even when the query and the message share no words.

Example:

```text
Query:   When did we lock the hill station?
Message: chalo manali fix h 14 ko nikalte h
```

## What It Demonstrates

- **Meaning search:** TF-IDF, character n-grams, LSI, and a small Hinglish concept lexicon work together.
- **Intent routing:** Meaning, person, and time queries receive different ranking boosts.
- **Conversation context:** Every result includes nearby messages instead of showing an isolated sentence.
- **Messy text handling:** Typos, Hinglish, short replies, forwarded text, and omitted media are part of the corpus.

## Quick Start

Requirements: Python 3.10 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The generated corpus and evaluation files are already included. To regenerate them:

```bash
python -m chatsearch.generate
python -m chatsearch.eval
```

Start the web demo:

```bash
python -m chatsearch.serve
```

Open http://127.0.0.1:8000. The first search builds the local LSI index and may take a few seconds.

## Demo Queries

Try these in the web UI:

```text
When did we lock the hill station?
What did Priya say about the fest money?
pichle mahine internship ki baat hui thi
```

The first query is a hard zero-overlap example. The expected Manali decision message is:

```text
Rohit: chalo manali fix h 14 ko nikalte h
```

## Synthetic Data

No real chat data is used. Everything is deterministic and generated locally from the seed in `chatsearch/generate.py`.

- 4,000+ messages across approximately 6 months
- 8 mocked participants: Rohit, Sneha, Ankit, Devansh, Aman, Priya, Kritika, and Ishaan
- Hinglish, typos, one-word replies, forwarded messages, and media placeholders
- Three decision threads: the Manali trip, the tech fest budget, and a major project

## Evaluation

The test set contains 40 labeled queries:

- **Hard 8:** The query shares no words with the target message.
- **Warm-up 32:** More direct queries used as a baseline.

Run the evaluator with:

```bash
python -m chatsearch.eval
```

It reports `hit@1`, `hit@5`, and `mrr@5` for all 40 queries, the hard 8, and the warm-up 32. The hard-query result is the most important measure of semantic retrieval quality.

## Project Layout

```text
chatsearch/generate.py   Synthetic corpus and query generation
chatsearch/index.py      TF-IDF, character, and LSI indexes
chatsearch/queryparse.py Meaning/person/time intent parsing
chatsearch/retrieve.py   Hybrid ranking and context windows
chatsearch/serve.py      FastAPI server
static/                  Browser UI
data/                    Corpus, labels, and evaluation output
```

## Public Repository

https://github.com/Manvendra-123/chat-semantic-search