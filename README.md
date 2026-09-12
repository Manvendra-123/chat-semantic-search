# chat-semantic-search

Semantic search over messy Hinglish group chats. This project provides a fast, multi-strategy search engine for group chat conversations with support for both semantic and lexical retrieval.

## Features

- **Hybrid Search**: Combines TF-IDF, BM25, and semantic search (LSI) for comprehensive results
- **Window-based Retrieval**: Groups related messages into context windows for better understanding
- **Hinglish Support**: Built to handle code-mixed Hindi-English text
- **Fast Indexing**: Lazy-loaded index built on first request
- **Web UI**: Simple, responsive interface for searching chat history
- **Evaluation Framework**: Built-in evaluation metrics for search quality
- **API**: RESTful API for programmatic access

## Installation

### Prerequisites
- Python 3.10+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Manvendra-123/chat-semantic-search.git
cd chat-semantic-search
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Usage

### Running the Server

Start the local demo server:
```bash
python -m chatsearch.serve
```

Then open http://localhost:8000 in your browser.

### API Endpoints

- **GET `/`** - Web UI
- **GET `/api/meta`** - Get corpus metadata and evaluation results
- **GET `/api/search?q=<query>`** - Search the chat index
  - Query parameter: `q` (string) - Search query
  - Returns: Ranked results with metadata

### Indexing Data

Place your chat data in `data/corpus.jsonl`:

```json
{"id": 0, "text": "Namaste! How are you?", "timestamp": "2024-01-01T10:00:00", "author": "Alice"}
{"id": 1, "text": "Main bilkul theek hoon", "timestamp": "2024-01-01T10:01:00", "author": "Bob"}
```

Create metadata in `data/corpus_meta.json`:
```json
{
  "num_messages": 1000,
  "date_range": "2024-01-01 to 2024-03-31"
}
```

## Architecture

### Core Modules

- **`index.py`** - Passage indexing with TF-IDF, LSI, and BM25 scoring over context windows
- **`retrieve.py`** - Search and ranking logic
- **`queryparse.py`** - Query parsing and preprocessing
- **`lexicon.py`** - Token expansion for Hinglish text
- **`textutil.py`** - Text preprocessing utilities
- **`serve.py`** - FastAPI server and web interface
- **`eval.py`** - Evaluation metrics and benchmarking
- **`generate.py`** - Data generation and corpus building

### Retrieval Strategy

Messages are grouped into sliding windows (default: 4 messages) with a center message designation. This provides context without overwhelming the index. The search uses a fused score combining:
- TF-IDF similarity
- BM25 ranking
- LSI (Latent Semantic Indexing) semantic similarity

## Project Structure

```
chat-semantic-search/
├── chatsearch/           # Main package
│   ├── index.py         # Indexing engine
│   ├── retrieve.py      # Search & ranking
│   ├── serve.py         # FastAPI server
│   ├── eval.py          # Evaluation
│   └── ...
├── data/                # Data directory
│   ├── corpus.jsonl     # Chat messages
│   ├── queries.json     # Test queries
│   └── eval_results.json # Evaluation results
├── static/              # Frontend assets
│   ├── index.html
│   ├── app.js
│   └── style.css
├── pyproject.toml       # Project configuration
└── README.md            # This file
```

## Development

### Running Tests

```bash
pytest
```

### Evaluating Search Quality

```bash
python -m chatsearch.eval
```

This runs the search against test queries and generates `data/eval_results.json`.

## License

MIT

## Author

Manvendra Singh