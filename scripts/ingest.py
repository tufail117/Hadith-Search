"""
Hadith Search v2 - Ingestion Pipeline

This script:
1. Converts GitHub JSON files to unified schema
2. Builds ChromaDB vector index
3. Builds BM25 keyword index

Usage:
    python scripts/ingest.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import (
    BUKHARI_DIR,
    MUSLIM_DIR,
    HADITHS_JSON,
    CHROMA_DIR,
    BM25_INDEX
)
from src.ingestion.json_converter import convert_all_json, save_hadiths
from src.ingestion.indexer import build_chroma_index, build_bm25_index


def main():
    """Run the complete ingestion pipeline."""
    print("="*70)
    print("HADITH SEARCH V2 - INGESTION PIPELINE")
    print("="*70)

    # Step 1: Convert JSON files
    print("\n[1/3] Converting JSON files to unified schema...")
    print("-"*70)
    hadiths = convert_all_json(BUKHARI_DIR, MUSLIM_DIR)
    save_hadiths(hadiths, HADITHS_JSON)

    # Step 2: Build ChromaDB index
    print("\n[2/3] Building ChromaDB vector index...")
    print("-"*70)
    print(f"Loading {len(hadiths)} hadiths from {HADITHS_JSON}")
    build_chroma_index(HADITHS_JSON, CHROMA_DIR)
    print(f"✓ ChromaDB index saved to {CHROMA_DIR}")

    # Step 3: Build BM25 index
    print("\n[3/3] Building BM25 keyword index...")
    print("-"*70)
    build_bm25_index(HADITHS_JSON, BM25_INDEX)
    print(f"✓ BM25 index saved to {BM25_INDEX}")

    print("\n" + "="*70)
    print("INGESTION COMPLETE!")
    print("="*70)
    print(f"\nTotal hadiths indexed: {len(hadiths)}")
    print(f"  - Bukhari: {len([h for h in hadiths if h['book'] == 'bukhari'])}")
    print(f"  - Muslim: {len([h for h in hadiths if h['book'] == 'muslim'])}")
    print(f"\nOutput files:")
    print(f"  - Hadiths JSON: {HADITHS_JSON}")
    print(f"  - ChromaDB index: {CHROMA_DIR}")
    print(f"  - BM25 index: {BM25_INDEX}")
    print(f"\nYou can now start the API server:")
    print(f"  uvicorn src.api.main:app --reload")
    print("="*70)


if __name__ == "__main__":
    main()
