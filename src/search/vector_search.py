"""ChromaDB vector semantic search."""

from typing import List, Dict, Any, Optional

import chromadb
from sentence_transformers import SentenceTransformer

from src.config import EMBEDDING_MODEL, CHROMA_DIR, CHROMA_COLLECTION, VECTOR_TOP_K

# Lazy-loaded globals
_embedding_model: Optional[SentenceTransformer] = None
_chroma_collection = None


def get_embedding_model() -> SentenceTransformer:
    """Get or load embedding model (lazy loading).

    Returns:
        Loaded SentenceTransformer model.
    """
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model


def get_chroma_collection():
    """Get or load ChromaDB collection (lazy loading).

    Returns:
        ChromaDB collection.
    """
    global _chroma_collection
    if _chroma_collection is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _chroma_collection = client.get_collection(CHROMA_COLLECTION)
    return _chroma_collection


def vector_search(query: str, top_k: int = VECTOR_TOP_K) -> List[Dict[str, Any]]:
    """Search hadiths by semantic similarity.

    Args:
        query: Search query.
        top_k: Number of results to return.

    Returns:
        List of search results with scores and metadata.
    """
    model = get_embedding_model()
    collection = get_chroma_collection()

    # Embed query
    query_embedding = model.encode(query).tolist()

    # Search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    # Format results
    search_results = []
    if results["ids"] and results["ids"][0]:
        for i, hadith_id in enumerate(results["ids"][0]):
            # Convert distance to similarity score (cosine distance to similarity)
            distance = results["distances"][0][i] if results["distances"] else 0
            score = 1 - distance  # For cosine, similarity = 1 - distance

            metadata = results["metadatas"][0][i] if results["metadatas"] else {}

            search_results.append({
                "id": hadith_id,
                "score": score,
                "book": metadata.get("book", ""),
                "volume": metadata.get("volume", 0),
                "chapter": metadata.get("chapter", ""),
                "hadith_number": metadata.get("hadith_number", 0),
                "narrator": metadata.get("narrator", ""),
                "text": metadata.get("text", "")
            })

    return search_results
