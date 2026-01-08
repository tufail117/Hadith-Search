"""Build search indices from processed hadiths."""

import pickle
from pathlib import Path
from typing import List, Dict, Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

from src.config import (
    EMBEDDING_MODEL,
    EMBEDDING_BATCH_SIZE_CPU,
    CHROMA_DIR,
    BM25_INDEX,
    CHROMA_COLLECTION,
    HADITHS_JSON
)


def tokenize(text: str) -> List[str]:
    """Simple tokenizer for BM25.

    Args:
        text: Text to tokenize.

    Returns:
        List of lowercase tokens.
    """
    return text.lower().split()


def build_vector_index(hadiths: List[Dict[str, Any]]) -> None:
    """Build ChromaDB vector index from hadiths.

    Args:
        hadiths: List of hadith records.
    """
    import torch
    import os
    
    # Force CPU to avoid MPS segfault issues with sentence-transformers
    # Set environment variable to disable MPS
    os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
    
    # Use CPU by default for stability (MPS can cause segfaults)
    force_cpu = os.environ.get("FORCE_CPU", "1") == "1"
    
    if not force_cpu and torch.cuda.is_available():
        device = "cuda"
        batch_size = 512
        print(f"Using CUDA GPU (batch_size={batch_size})")
    else:
        device = "cpu"
        batch_size = EMBEDDING_BATCH_SIZE_CPU
        print(f"Using CPU (batch_size={batch_size})")
    
    print("Loading embedding model...")
    model = SentenceTransformer(EMBEDDING_MODEL, device=device)

    print("Creating ChromaDB collection...")
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Delete existing collection if it exists
    try:
        client.delete_collection(CHROMA_COLLECTION)
    except Exception:
        pass  # Collection doesn't exist, continue

    collection = client.create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"}
    )

    # batch_size is already set based on detected device above
    total = len(hadiths)

    for i in range(0, total, batch_size):
        batch = hadiths[i:i + batch_size]

        ids = [h["id"] for h in batch]
        texts = [h["full_text"] for h in batch]
        metadatas = [
            {
                "book": h["book"],
                "volume": h["volume"],
                "chapter": h["chapter"],
                "hadith_number": h["hadith_number"],
                "narrator": h["narrator"],
                "text": h["text"][:1000]  # Truncate for metadata
            }
            for h in batch
        ]

        print(f"Embedding batch {i // batch_size + 1}/{(total + batch_size - 1) // batch_size}")
        embeddings = model.encode(texts, show_progress_bar=False).tolist()

        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=texts
        )

    print(f"Vector index built with {total} hadiths")


def build_chroma_index(hadiths_json: Path, chroma_dir: Path) -> None:
    """Build ChromaDB index from hadiths JSON file.

    Args:
        hadiths_json: Path to hadiths JSON file
        chroma_dir: Path to ChromaDB directory
    """
    import json

    print(f"Loading hadiths from {hadiths_json}...")
    with open(hadiths_json) as f:
        hadiths = json.load(f)
    print(f"Loaded {len(hadiths)} hadiths")

    build_vector_index(hadiths)


def build_bm25_index(hadiths_json: Path, bm25_index: Path) -> None:
    """Build BM25 index from hadiths JSON file.

    Args:
        hadiths_json: Path to hadiths JSON file
        bm25_index: Path to BM25 index file
    """
    import json

    print(f"Loading hadiths from {hadiths_json}...")
    with open(hadiths_json) as f:
        hadiths = json.load(f)
    print(f"Loaded {len(hadiths)} hadiths")

    # Build BM25 index (function below handles the actual indexing)
    print("Building BM25 index...")

    # Tokenize all documents
    corpus = [tokenize(h["full_text"]) for h in hadiths]

    # Build BM25 index
    bm25 = BM25Okapi(corpus)

    # Save index with hadith IDs
    index_data = {
        "bm25": bm25,
        "hadith_ids": [h["id"] for h in hadiths],
        "hadiths": {h["id"]: h for h in hadiths}
    }

    bm25_index.parent.mkdir(parents=True, exist_ok=True)

    with open(bm25_index, 'wb') as f:
        pickle.dump(index_data, f)

    print(f"✓ BM25 index built with {len(hadiths)} hadiths")


def build_all_indices() -> None:
    """Build all search indices from processed hadiths."""
    import json

    print("Loading hadiths...")
    with open(HADITHS_JSON) as f:
        hadiths = json.load(f)
    print(f"Loaded {len(hadiths)} hadiths")

    build_vector_index(hadiths)

    # Build BM25 separately
    print("Building BM25 index...")
    corpus = [tokenize(h["full_text"]) for h in hadiths]
    bm25 = BM25Okapi(corpus)
    index_data = {
        "bm25": bm25,
        "hadith_ids": [h["id"] for h in hadiths],
        "hadiths": {h["id"]: h for h in hadiths}
    }
    BM25_INDEX.parent.mkdir(parents=True, exist_ok=True)
    with open(BM25_INDEX, 'wb') as f:
        pickle.dump(index_data, f)

    print("All indices built successfully!")
