# Semantic Chat Search

This repository contains a submission for the IT Geeks assessment (Problem #2 "Search a Group Chat Properly"). The brief requires searching a synthetic Hinglish group chat (4,000+ messages, 8 participants, 6 months) and retrieving the correct message for 40 queries, including 8 queries with zero word overlap with the answer.

## Layout

```
chatsearch/          retrieval pipeline, corpus builder, eval, demo server
static/              local demo UI
data/                generated corpus, queries, seed transcripts
```

| Path | Role |
|---|---|
| `chatsearch/build_corpus.py` | Build the 4,000+ message archive and 40 labeled queries |
| `chatsearch/index.py` | Windowed TF-IDF + LSI index |
| `chatsearch/retrieve.py` | Hybrid / keyword search |
| `chatsearch/queryparse.py` | Meaning / person / time intents |
| `chatsearch/eval.py` | Hit@1 / Hit@3 / MRR on all 40 and the hard 8 |
| `chatsearch/serve.py` | Local demo at `http://127.0.0.1:8000` |
| `chatsearch/bank.py` | Hand-authored Hinglish filler |
| `data/raw_1.jsonl`, `data/raw_2.jsonl` | Seed transcript used by the corpus builder |

## The Honest Result

The stated result of this project is the large gap between the warmup queries (where keyword overlap exists) and the hard 8 queries (zero word overlap). The pipeline is a hybrid lexical/sparse retriever (TF-IDF word + char n-grams, LSI, BM25 over conversation windows). 

| Split | n | Keyword (BM25/Lexical) Hit@1 | Hit@3 | MRR | Full Hybrid (TF-IDF + LSI) Hit@1 | Hit@3 | MRR |
|---|---|---|---|---|---|---|---|
| Overall | 40 | 0.525 | 0.625 | 0.582 | 0.525 | 0.575 | 0.555 |
| Warmup | 32 | 0.656 | 0.781 | 0.728 | 0.656 | 0.719 | 0.694 |
| Hard | 8 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

*The gap is stark: 0.656 on warmup vs 0.000 on hard queries.*

### Per-Shape Breakdown
| Shape | n | Hit@1 |
|---|---|---|
| Meaning | 20 | 0.600 |
| Person | 10 | 0.500 |
| Time | 10 | 0.200 |

*Time-based queries are the weakest, likely because relative expressions like "last month" must resolve against the chat's final timestamp rather than today's date.*

## Measurement Findings

The following findings came from actual measurement and ablation, not guesswork.

**1. Corpus was 83% duplicate**
An early version of the synthetic corpus contained 4,120 messages but only 698 distinct strings. As a result, every query had roughly eight identical correct answers spread throughout the timeline, making evaluation meaningless.

**2. Intra-window tie-break bug**
Retrieval is window-based, but returning a naked message from within a window was initially arbitrary. Adding intra-window scoring moved warmup hit@1 from **0.28 → 0.656**, while the hard-8 stayed completely flat at **0.125** (measured before the lexicon concept table was removed — see Finding 5). This flatness was the evidence that the tie-break fix leaked nothing: it breaks ties on term overlap, and genuinely zero-overlap queries have no terms to break on.

**3. Unique ≠ meaningful**
After fixing the duplicates, the corpus passed a 97.1% uniqueness check but was effectively useless "slot-salad" generated from 13 templates (e.g., "aaj parking me garmi bahot h", "CR cancel kar diya parking next week"). With no meaningful semantics to retrieve, all channels scored near zero. Replacing this with a bank of 406 hand-written Hinglish sentences moved warmup hit@1 from **0.125 → 0.781** (measured before the lexicon concept table was removed — see Finding 5). The corpus validator was updated to recognize that uniqueness does not imply semantic value.

**4. Two multilingual models fail on romanized Hinglish**
We tested two off-the-shelf embedding models on a 5-candidate ranking task (Query: "When did we lock the hill station?", Gold: "chalo manali fix h 14 ko nikalte h", Distractor: "aaj parking me garmi bahot h").
- `paraphrase-multilingual-MiniLM-L12-v2`: Gold scored 0.367, Distractor 0.475. Gold loses.
- `intfloat/multilingual-e5-base`: Gold scored 0.746, Distractor 0.754. Gold loses (all candidates clumped between 0.70 and 0.75).
Both models can handle Devanagari Hindi but fail on Roman-script Hinglish. The neural/dense channel was deliberately dropped based on this evidence.

**5. The Lexicon Cheat**
Earlier numbers on the hard-8 were non-zero only because a hand-written concept table mapped query phrases directly to literal strings from the gold answers (e.g., "lock" → 14, "chip in" → 450, "stay" → snowview, "bus" → 10:40). We removed this entirely because it was answering the test rather than solving the problem. The honest number on the hard 8 is 0.000.

**6. LSI adds noise**
The hybrid pipeline scores lower than the keyword baseline on hit@3 (0.575 vs 0.625 overall, 0.719 vs 0.781 warmup). A hybrid containing the keyword channel should not lose to it. Without valid semantic overlap, the LSI channel introduces noise and pushes good keyword hits down.

## Why hard-8 is 0.000, and what would fix it

Sparse retrieval (TF-IDF, BM25) cannot bridge zero word overlap by construction. Because the off-the-shelf multilingual embedding models we tested do not understand romanized Hinglish, there is no semantic bridge available in the current architecture.

**What would actually work:**
- A Hinglish-specific embedding model.
- Fine-tuning an existing model on code-mixed Hinglish query-passage pairs.

Neither approach was reachable in the time available for this assessment, so the honest 0.000 score stands.

## Generated vs Hand-Authored (What is Mocked)

Per the brief, the corpus is entirely synthetic. No real chat data is used, no external APIs are called, and all retrieval runs locally. The generation process mixes scripted assembly with hand-written content:
- **Hand-authored:** 3 decision threads containing the gold answers, and a 406-sentence filler bank.
- **Generated:** The final chronological assembly of the messages and conversational filler is completely scripted.

## How to Run

1. Clone the repository.
2. Use **Python 3.12**.
3. Create and activate a virtual environment, then install dependencies:
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
4. Generate the dataset, evaluate, and open the demo:
```bash
PYTHONPATH=. python -m chatsearch.build_corpus
PYTHONPATH=. python -m chatsearch.eval
PYTHONPATH=. python -m chatsearch.serve
```
The demo is at `http://127.0.0.1:8000`. Optional: `PYTHONPATH=. python -m chatsearch.validate` checks corpus constraints.
