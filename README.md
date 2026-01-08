# Hadith Search v2

Semantic search engine for Sahih al-Bukhari and Sahih Muslim hadiths.

## Quick Start

### 1. Setup

```bash
cd hadith-search_v2
conda activate hadith-app
```

### 2. Build Indices (First Time Only)

```bash
python scripts/ingest.py
```

This will:
- Convert 14,736 hadiths from JSON to search format (~5 seconds)
- Build vector embeddings (~3-5 minutes)
- Build keyword index (~10 seconds)

### 3. Start Server

```bash
uvicorn src.api.main:app --reload
```

### 4. Open Browser

Navigate to: http://localhost:8000

## What's Inside?

- **14,736 hadiths** (Bukhari: 7,277 + Muslim: 7,459)
- **Hybrid search**: Semantic (ChromaDB) + Keywords (BM25)
- **Smart ranking**: RRF fusion + Cross-encoder reranking
- **Fast**: 30-60ms per search, <1ms if cached

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.

## API Examples

### Search

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "prayer", "top_k": 5}'
```

### Health Check

```bash
curl "http://localhost:8000/api/health"
```

## Project Structure

```
hadith-search_v2/
├── raw_data/           # Source JSON files (from GitHub)
├── data/               # Processed data & indices
├── src/
│   ├── ingestion/      # Convert JSON & build indices
│   ├── search/         # Search pipeline
│   ├── api/            # FastAPI server
│   └── ui/             # Gradio web interface
└── scripts/
    └── ingest.py       # Run ingestion pipeline
```

## Key Technologies

- **ChromaDB**: Vector embeddings for semantic search
- **BM25**: Traditional keyword search
- **RRF**: Combine both search methods
- **Cross-encoder**: Rerank top results for accuracy
- **FastAPI**: REST API
- **Gradio**: Web UI

## Why v2?

v1 used PDF extraction which had:
- 60-70% accuracy
- ~12,000 hadiths extracted
- Garbled text and numbering errors

v2 uses verified JSON from GitHub:
- ✅ 100% accuracy
- ✅ 14,736 hadiths
- ✅ Perfect metadata
- ✅ Ready in 1 hour vs days
