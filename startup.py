#!/usr/bin/env python3
"""
Startup script for Hadith Search.
Indices are pre-built in the Docker image - just verify and start server.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def verify_indices():
    """Verify that pre-built indices exist."""
    from src.config import CHROMA_DIR, BM25_INDEX, HADITHS_JSON
    
    print("=" * 60)
    print("HADITH SEARCH - STARTUP")
    print("=" * 60)
    
    # Check required files
    checks = [
        (CHROMA_DIR, "ChromaDB directory"),
        (BM25_INDEX, "BM25 index"),
        (HADITHS_JSON, "Hadiths JSON"),
    ]
    
    all_ok = True
    for path, name in checks:
        if path.exists():
            print(f"✓ {name}: {path}")
        else:
            print(f"✗ {name}: NOT FOUND at {path}")
            all_ok = False
    
    if not all_ok:
        print("\nERROR: Missing pre-built indices!")
        print("Indices should be built at Docker build time.")
        sys.exit(1)
    
    # Quick ChromaDB health check
    try:
        import chromadb
        from src.config import CHROMA_COLLECTION
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        collection = client.get_collection(CHROMA_COLLECTION)
        count = collection.count()
        print(f"✓ ChromaDB collection: {count} documents")
    except Exception as e:
        print(f"✗ ChromaDB error: {e}")
        sys.exit(1)
    
    print("=" * 60)
    print("All indices verified!")
    print("=" * 60)


def main():
    """Main startup routine."""
    verify_indices()
    
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
