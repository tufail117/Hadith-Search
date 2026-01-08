"""Configuration settings for Hadith Search v2."""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
RAW_DATA_DIR = BASE_DIR / "raw_data"
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
INDEX_DIR = DATA_DIR / "index"

# Data files
HADITHS_JSON = PROCESSED_DIR / "hadiths.json"
CHROMA_DIR = INDEX_DIR / "chroma_db"
BM25_INDEX = INDEX_DIR / "bm25_index.pkl"

# Source directories
BUKHARI_DIR = RAW_DATA_DIR / "bukhari"
MUSLIM_DIR = RAW_DATA_DIR / "muslim"

# AI Models
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"    # ~440MB, 768 dimensions
RERANKER_MODEL = "BAAI/bge-reranker-base"     # ~280MB

# Search parameters
VECTOR_TOP_K = 30      # Initial vector search candidates
BM25_TOP_K = 30        # Initial BM25 candidates
RERANK_TOP_K = 20      # Candidates to rerank
FINAL_TOP_K = 10       # Results returned to user

# RRF Fusion parameter
RRF_K = 60             # Constant for Reciprocal Rank Fusion

# Cache settings
CACHE_MAX_SIZE = 10000
CACHE_TTL_SECONDS = 86400  # 24 hours

# Server settings
SERVER_HOST = "0.0.0.0"
SERVER_PORT = int(os.environ.get("PORT", 8000))

# Embedding batch sizes (for ingestion)
EMBEDDING_BATCH_SIZE_GPU = 512
EMBEDDING_BATCH_SIZE_CPU = 32

# ChromaDB collection name
CHROMA_COLLECTION = "hadiths"
