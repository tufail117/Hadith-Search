#!/usr/bin/env python3
"""
Startup script for Railway deployment.
Starts the server immediately and rebuilds index in background if needed.
This ensures healthchecks pass while long-running index builds continue.
"""

import os
import sys
import threading
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Global flag to track indexing status
_indexing_in_progress = False
_indexing_complete = False
_indexing_error = None


def get_indexing_status():
    """Get current indexing status for API health endpoint."""
    return {
        "in_progress": _indexing_in_progress,
        "complete": _indexing_complete,
        "error": str(_indexing_error) if _indexing_error else None
    }


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
        return count > 0  # Must have documents
    except Exception as e:
        print(f"ChromaDB health check failed: {e}")
        return False


def rebuild_indices():
    """Rebuild all search indices."""
    global _indexing_in_progress, _indexing_complete, _indexing_error
    
    _indexing_in_progress = True
    _indexing_complete = False
    _indexing_error = None
    
    try:
        print("=" * 70)
        print("REBUILDING SEARCH INDICES (BACKGROUND)")
        print("=" * 70)
        
        from src.config import HADITHS_JSON, CHROMA_DIR, BM25_INDEX
        from src.ingestion.indexer import build_chroma_index, build_bm25_index
        
        # Check if hadiths.json exists
        if not HADITHS_JSON.exists():
            raise FileNotFoundError(f"{HADITHS_JSON} not found!")
        
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
        
        _indexing_complete = True
        
    except Exception as e:
        print(f"ERROR during index rebuild: {e}")
        _indexing_error = e
    finally:
        _indexing_in_progress = False


def start_background_indexing():
    """Start index rebuild in a background thread."""
    thread = threading.Thread(target=rebuild_indices, daemon=True)
    thread.start()
    print("Background indexing thread started")
    return thread


def main():
    """Main startup routine."""
    print("=" * 70)
    print("HADITH SEARCH - STARTUP CHECK")
    print("=" * 70)
    
    # Check if we should force rebuild
    force_rebuild = os.environ.get("FORCE_REBUILD_INDEX", "0") == "1"
    needs_rebuild = force_rebuild or not check_chromadb_health()
    
    if needs_rebuild:
        if force_rebuild:
            print("FORCE_REBUILD_INDEX=1 detected")
        print("Index needs rebuild - starting in background thread...")
        start_background_indexing()
    else:
        global _indexing_complete
        _indexing_complete = True
        print("All indices healthy!")
    
    # Start the server IMMEDIATELY (don't wait for indexing)
    print("\nStarting uvicorn server (indexing continues in background)...")
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
