#!/usr/bin/env python3
"""
Startup script for Railway deployment.
Checks if ChromaDB index is valid, rebuilds if needed, then starts the server.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def check_chromadb_health():
    """Check if ChromaDB collection is accessible."""
    try:
        import chromadb
        from src.config import CHROMA_DIR, CHROMA_COLLECTION
        
        if not CHROMA_DIR.exists():
            print("ChromaDB directory does not exist")
            return False
            
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        collection = client.get_collection(CHROMA_COLLECTION)
        count = collection.count()
        print(f"ChromaDB health check passed: {count} documents in collection")
        return True
    except Exception as e:
        print(f"ChromaDB health check failed: {e}")
        return False


def rebuild_indices():
    """Rebuild all search indices."""
    print("=" * 70)
    print("REBUILDING SEARCH INDICES")
    print("=" * 70)
    
    from src.config import HADITHS_JSON, CHROMA_DIR, BM25_INDEX
    from src.ingestion.indexer import build_chroma_index, build_bm25_index
    
    # Check if hadiths.json exists
    if not HADITHS_JSON.exists():
        print(f"ERROR: {HADITHS_JSON} not found!")
        print("Cannot rebuild indices without source data.")
        sys.exit(1)
    
    # Rebuild ChromaDB
    print("\n[1/2] Rebuilding ChromaDB vector index...")
    import shutil
    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
    build_chroma_index(HADITHS_JSON, CHROMA_DIR)
    
    # Rebuild BM25
    print("\n[2/2] Rebuilding BM25 keyword index...")
    if BM25_INDEX.exists():
        BM25_INDEX.unlink()
    build_bm25_index(HADITHS_JSON, BM25_INDEX)
    
    print("\n" + "=" * 70)
    print("INDICES REBUILT SUCCESSFULLY")
    print("=" * 70)


def main():
    """Main startup routine."""
    print("=" * 70)
    print("HADITH SEARCH - STARTUP CHECK")
    print("=" * 70)
    
    # Check if we should force rebuild
    force_rebuild = os.environ.get("FORCE_REBUILD_INDEX", "0") == "1"
    
    if force_rebuild:
        print("FORCE_REBUILD_INDEX=1 detected, rebuilding indices...")
        rebuild_indices()
    elif not check_chromadb_health():
        print("ChromaDB not healthy, rebuilding indices...")
        rebuild_indices()
    else:
        print("All indices healthy, starting server...")
    
    # Start the server
    print("\nStarting uvicorn server...")
    import uvicorn
    from src.config import SERVER_HOST, SERVER_PORT
    
    uvicorn.run(
        "src.api.main:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info"
    )


if __name__ == "__main__":
    main()
