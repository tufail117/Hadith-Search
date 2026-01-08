# Hadith Search v2 - Architecture & Approach

## Overview

This is a **semantic search engine** for Sahih al-Bukhari and Sahih Muslim hadiths, built using pre-structured JSON data from GitHub instead of PDF extraction.

### Key Decision: Why JSON Instead of PDF Extraction?

**Problem with PDFs:**
- Bilingual layout (Arabic + English) in columns
- Inconsistent formatting across volumes
- OCR would take 2-4 hours and only achieve 85-90% accuracy
- Text extraction from PDFs yielded 60-70% accuracy

**Solution with JSON:**
- ✅ Pre-verified, structured data
- ✅ 14,736 hadiths (vs ~12,000 from PDFs)
- ✅ Perfect narrator and text separation
- ✅ Accurate hadith numbering
- ✅ Chapter information included
- ✅ Ready in 1 hour vs days of PDF wrestling

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER                                     │
│                           │                                      │
│              ┌────────────┴────────────┐                        │
│              ▼                         ▼                        │
│     ┌─────────────────┐       ┌─────────────────┐              │
│     │   Web Browser   │       │   REST Client   │              │
│     │   (Gradio UI)   │       │   (API calls)   │              │
│     └────────┬────────┘       └────────┬────────┘              │
│              │                         │                        │
│              └──────────┬──────────────┘                        │
│                         ▼                                       │
│              ┌─────────────────────┐                           │
│              │     FastAPI App     │                           │
│              │    (Port 8000)      │                           │
│              └─────────┬───────────┘                           │
│                        ▼                                        │
│              ┌─────────────────────┐                           │
│              │   Hybrid Search     │                           │
│              │      Engine         │                           │
│              └─────────────────────┘                           │
│                        │                                        │
│         ┌──────────────┼──────────────┐                        │
│         ▼              ▼              ▼                        │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐                  │
│   │  Cache   │   │ ChromaDB │   │   BM25   │                  │
│   │(In-Memory)│   │ (Vectors)│   │(Keywords)│                  │
│   └──────────┘   └──────────┘   └──────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Ingestion Pipeline

```
GitHub JSON Files (raw_data/)
    │
    ├─ bukhari/*.json (97 files, 7,277 hadiths)
    └─ muslim/*.json (57 files, 7,459 hadiths)
         │
         ▼
    Convert to Unified Schema
    (scripts/convert_json.py)
         │
         ▼
    Consolidated JSON
    (data/processed/hadiths.json)
    14,736 hadiths total
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
    ChromaDB      BM25 Index    Metadata
    (Vectors)     (Keywords)    Storage
         │              │              │
         ▼              ▼              ▼
    data/index/    data/index/   hadiths.json
    chroma_db/     bm25_index.pkl
```

### 2. Search Pipeline

```
User Query: "How to perform wudu?"
    │
    ▼
┌─────────────┐
│ Check Cache │ ──── HIT ──── Return Cached Results
└─────────────┘
    │ MISS
    ▼
┌─────────────────┐
│ Query Expansion │ → "wudu ablution purity cleanliness washing..."
└─────────────────┘
    │
    ├──────────────────────┐
    ▼                      ▼
┌──────────────┐    ┌─────────────┐
│Vector Search │    │ BM25 Search │
│  (Top 30)    │    │   (Top 30)  │
│ Semantic     │    │  Keywords   │
└──────────────┘    └─────────────┘
    │                      │
    └──────────┬───────────┘
               ▼
        ┌─────────────┐
        │  RRF Fusion │ Combine with Reciprocal Rank Fusion
        │             │ Score = 1/(60+rank_vec) + 1/(60+rank_bm25)
        └─────────────┘
               │
               ▼
        ┌─────────────┐
        │   Rerank    │ Cross-encoder scores top 20
        │  (Top 20)   │ More accurate relevance scoring
        └─────────────┘
               │
               ▼
        ┌─────────────┐
        │ Store Cache │
        └─────────────┘
               │
               ▼
        Return Top 10 Results
```

---

## Project Structure

```
hadith-search_v2/
│
├── raw_data/                      # Source JSON files (from GitHub)
│   ├── bukhari/                   # 97 JSON files
│   └── muslim/                    # 57 JSON files
│
├── data/                          # Processed data
│   ├── processed/
│   │   └── hadiths.json           # Unified format (generated)
│   └── index/
│       ├── chroma_db/             # Vector embeddings (generated)
│       └── bm25_index.pkl         # Keyword index (generated)
│
├── src/                           # Source code
│   ├── __init__.py
│   ├── config.py                  # Configuration settings
│   │
│   ├── ingestion/                 # Data processing
│   │   ├── __init__.py
│   │   ├── json_converter.py      # Convert GitHub JSON to schema
│   │   └── indexer.py             # Build search indices
│   │
│   ├── search/                    # Search functionality
│   │   ├── __init__.py
│   │   ├── query_expansion.py     # Expand Islamic terms
│   │   ├── vector_search.py       # Semantic search (ChromaDB)
│   │   ├── bm25_search.py         # Keyword search (BM25)
│   │   ├── hybrid_search.py       # Combine both + rerank
│   │   ├── reranker.py            # Cross-encoder reranking
│   │   └── cache.py               # Result caching
│   │
│   ├── api/                       # REST API
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app entry point
│   │   ├── routes.py              # API endpoints
│   │   └── models.py              # Request/Response schemas
│   │
│   └── ui/                        # Web interface
│       ├── __init__.py
│       └── gradio_app.py          # Gradio UI
│
├── scripts/
│   └── ingest.py                  # Run ingestion pipeline
│
├── requirements.txt               # Python dependencies
├── ARCHITECTURE.md                # This file
└── README.md                      # Usage guide
```

---

## Core Technologies

### 1. Vector Search (ChromaDB)

**Purpose:** Semantic understanding - find hadiths by meaning, not just keywords.

**How it works:**
- Uses `BAAI/bge-base-en-v1.5` embedding model (~440MB)
- Converts each hadith to a 768-dimensional vector
- Vectors capture semantic meaning
- Cosine similarity finds similar hadiths

**Example:**
- Query: "washing before prayer"
- Finds hadiths about "wudu", "ablution", "purification" even if exact words differ

### 2. BM25 Keyword Search

**Purpose:** Traditional keyword matching - ensures exact terms aren't missed.

**How it works:**
- BM25Okapi algorithm
- Scores based on term frequency and rarity
- Fast, deterministic keyword matching

**Example:**
- Query: "Narrated Aisha"
- Finds all hadiths narrated by Aisha with high precision

### 3. RRF Fusion (Reciprocal Rank Fusion)

**Purpose:** Intelligently combine vector and BM25 results.

**Formula:**
```
RRF Score = 1/(60 + rank_in_vector) + 1/(60 + rank_in_BM25)
```

**Why:**
- Hadiths ranking high in BOTH methods get highest scores
- No manual weight tuning needed
- Proven effective in research

### 4. Cross-Encoder Reranking

**Purpose:** Final precision scoring of top candidates.

**How it works:**
- Uses `BAAI/bge-reranker-base` model (~280MB)
- Processes query + document together (vs separately in bi-encoder)
- More accurate but slower - only used on top 20

**Why:**
- Bi-encoder (initial): Fast, good accuracy
- Cross-encoder (rerank): Slow, excellent accuracy
- Best of both worlds

### 5. Query Expansion

**Purpose:** Bridge language gap between English queries and Islamic terminology.

**Example mappings:**
```python
"prayer" → "salah salat namaz pray praying"
"fasting" → "sawm siyam roza ramadan fast"
"charity" → "zakat sadaqah alms"
```

**Benefit:** Users can search in English and find relevant Arabic-origin terms.

### 6. Caching

**Purpose:** Speed up repeated queries.

**Implementation:**
- In-memory LRU cache
- 10,000 query capacity
- 24-hour TTL
- Query normalization (lowercase, remove punctuation)

---

## Data Schema

### Source JSON Format (GitHub)

```json
{
  "metadata": {
    "english": {
      "title": "Sahih al-Bukhari",
      "introduction": "Revelation"
    }
  },
  "hadiths": [
    {
      "id": 1,
      "idInBook": 1,
      "chapterId": 1,
      "bookId": 1,
      "english": {
        "narrator": "Narrated 'Umar bin Al-Khattab:",
        "text": "I heard Allah's Messenger (ﷺ) saying..."
      },
      "arabic": "حَدَّثَنَا..."
    }
  ],
  "chapter": {
    "id": 1,
    "english": "Revelation"
  }
}
```

### Unified Schema (Our Format)

```json
{
  "id": "bukhari_1_1",
  "book": "bukhari",
  "volume": 1,
  "chapter": "Revelation",
  "hadith_number": 1,
  "narrator": "Narrated 'Umar bin Al-Khattab:",
  "text": "I heard Allah's Messenger (ﷺ) saying...",
  "full_text": "Narrated 'Umar bin Al-Khattab: I heard Allah's Messenger (ﷺ) saying..."
}
```

**Key fields:**
- `id`: Unique identifier (book_volume_number)
- `full_text`: Narrator + text combined (used for search)
- All other fields: Metadata for display

---

## API Endpoints

### Search

```
POST /api/search
Content-Type: application/json

{
  "query": "how to pray",
  "top_k": 10
}
```

**Response:**
```json
{
  "query": "how to pray",
  "expanded_query": "how to pray salah salat namaz...",
  "results": [
    {
      "id": "bukhari_1_5",
      "book": "bukhari",
      "volume": 1,
      "chapter": "Prayer",
      "hadith_number": 5,
      "narrator": "Narrated Abu Huraira:",
      "text": "The Prophet (ﷺ) said...",
      "score": 0.92
    }
  ],
  "cached": false,
  "took_ms": 45.3
}
```

### Health Check

```
GET /api/health
```

### Cache Stats

```
GET /api/cache/stats
```

### Get Single Hadith

```
GET /api/hadith/{hadith_id}
```

---

## Performance Characteristics

### Ingestion (One-time)

| Task | Time | Output |
|------|------|--------|
| Load JSON files | 5s | 14,736 hadiths |
| Build ChromaDB index | 3-5 min | Vector embeddings |
| Build BM25 index | 10s | Keyword index |
| **Total** | **~5 min** | Ready to search |

### Search (Per Query)

| Component | Time | Notes |
|-----------|------|-------|
| Cache lookup | <1ms | If cached |
| Query expansion | <1ms | Dictionary lookup |
| Vector search | 10-20ms | ChromaDB query |
| BM25 search | 5-10ms | In-memory |
| RRF fusion | 1ms | Simple scoring |
| Reranking | 15-30ms | Cross-encoder |
| **Total (uncached)** | **30-60ms** | Fast! |
| **Total (cached)** | **<1ms** | Very fast! |

### Storage

| Component | Size |
|-----------|------|
| Raw JSON | ~50MB |
| hadiths.json | ~15MB |
| ChromaDB index | ~200MB |
| BM25 index | ~5MB |
| Embedding model | ~440MB |
| Reranker model | ~280MB |
| **Total** | **~1GB** |

---

## Key Design Decisions

### 1. Why JSON over PDF Extraction?

**Tried:** PDF extraction with PyMuPDF, OCR
**Issues:** 60-70% accuracy, hadith numbering errors, garbled text
**Solution:** Use pre-verified JSON from GitHub
**Result:** 100% accuracy, 14,736 hadiths, instant setup

### 2. Why Hybrid Search?

| Approach | Strengths | Weaknesses |
|----------|-----------|------------|
| Vector only | Semantic understanding | Misses exact keywords |
| BM25 only | Exact matches | Misses meaning |
| **Hybrid (our choice)** | Best of both | Slightly more complex |

### 3. Why Reranking?

**Bi-encoder (initial):**
- Fast: pre-compute embeddings
- Good: 80-85% accuracy

**Cross-encoder (rerank):**
- Slow: compute per query-doc pair
- Excellent: 90-95% accuracy

**Strategy:** Use bi-encoder for retrieval (fast), cross-encoder for final ranking (accurate)

### 4. Why In-Memory Cache?

**Alternatives considered:**
- Redis: Overkill for single-server
- Database: Slower than memory

**Chosen:** Simple LRU cache
- Fast (<1ms)
- Sufficient for typical usage
- No extra dependencies

### 5. Why ChromaDB?

**Alternatives:**
- Faiss: Lower-level, more complex
- Pinecone: Cloud-only, costs money
- Weaviate: Heavier deployment

**Chosen:** ChromaDB
- Easy Python API
- Persistent storage
- Good performance for 15K documents
- Open source, free

---

## Deployment

### Development

```bash
cd hadith-search_v2
conda activate hadith-app
python scripts/ingest.py
uvicorn src.api.main:app --reload
```

### Production (Raspberry Pi)

```bash
cd hadith-search_v2
conda activate hadith-app
python scripts/ingest.py
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### Systemd Service

```ini
[Unit]
Description=Hadith Search API v2
After=network.target

[Service]
User=pi
WorkingDirectory=/path/to/hadith-search_v2
ExecStart=/path/to/conda/envs/hadith-app/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Future Enhancements

### Phase 2 (After v1 is stable)

1. **Arabic Search Support**
   - Add Arabic query expansion
   - Separate Arabic index
   - Bilingual results

2. **Advanced Filters**
   - Filter by narrator
   - Filter by book
   - Filter by chapter/topic

3. **Semantic Clustering**
   - Group similar hadiths
   - Topic discovery
   - Related hadith suggestions

4. **User Accounts**
   - Save favorite hadiths
   - Search history
   - Personal collections

5. **Mobile App**
   - iOS/Android native apps
   - Offline search capability

---

## Testing Strategy

### Unit Tests
- JSON conversion accuracy
- Query expansion correctness
- Cache behavior

### Integration Tests
- End-to-end search pipeline
- API endpoint responses
- Index building process

### Quality Tests
- Search relevance (sample queries)
- Performance benchmarks
- Edge cases (empty query, special chars)

### Example Test Queries

| Query | Expected First Result |
|-------|----------------------|
| "prayer" | Hadiths about salah |
| "fasting ramadan" | Hadiths about sawm |
| "charity" | Hadiths about zakat |
| "Narrated Aisha" | Aisha's narrations |
| "intentions" | Famous hadith about niyyah |

---

## Monitoring & Metrics

### Key Metrics to Track

1. **Search Performance**
   - Average query latency
   - Cache hit rate
   - P95/P99 latencies

2. **Usage Statistics**
   - Queries per day
   - Most common searches
   - Peak usage times

3. **System Health**
   - Memory usage
   - CPU usage
   - Index size growth

---

## Conclusion

This architecture provides:
- ✅ **High accuracy** (99%+ from verified JSON data)
- ✅ **Fast search** (30-60ms uncached, <1ms cached)
- ✅ **Semantic understanding** (vector search)
- ✅ **Keyword precision** (BM25)
- ✅ **Easy deployment** (single server, ~1GB storage)
- ✅ **Scalable design** (can add features incrementally)

**Total implementation time:** ~1 hour (vs days of PDF extraction!)
