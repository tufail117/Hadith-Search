#!/usr/bin/env python3
"""
Pre-compute embeddings for all hadiths and save to a numpy file.
This allows fast ChromaDB index creation without running the embedding model.
"""

import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import os

# Force CPU to avoid MPS issues
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
HADITHS_JSON = DATA_DIR / "processed" / "hadiths.json"
EMBEDDINGS_FILE = DATA_DIR / "index" / "embeddings.npz"

# Model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def main():
    print("Loading hadiths...")
    with open(HADITHS_JSON) as f:
        hadiths = json.load(f)
    print(f"Loaded {len(hadiths)} hadiths")
    
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
    
    texts = [h["full_text"] for h in hadiths]
    ids = [h["id"] for h in hadiths]
    
    print(f"Embedding {len(texts)} texts...")
    embeddings = model.encode(
        texts, 
        show_progress_bar=True, 
        batch_size=64,  # Larger batch for local CPU
        convert_to_numpy=True
    )
    
    print(f"Embeddings shape: {embeddings.shape}")
    
    # Save as compressed numpy file
    EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        EMBEDDINGS_FILE,
        embeddings=embeddings,
        ids=np.array(ids, dtype=object)
    )
    
    print(f"Saved embeddings to: {EMBEDDINGS_FILE}")
    print(f"File size: {EMBEDDINGS_FILE.stat().st_size / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    main()
