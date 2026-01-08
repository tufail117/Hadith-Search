"""BM25 keyword search."""

import pickle
from typing import List, Dict, Any, Optional

from src.config import BM25_INDEX, BM25_TOP_K

# Lazy-loaded globals
_bm25_data: Optional[Dict] = None


def get_bm25_data() -> Dict:
    """Get or load BM25 index data (lazy loading).

    Returns:
        Dict with bm25 index, hadith_ids, and hadiths.
    """
    global _bm25_data
    if _bm25_data is None:
        with open(BM25_INDEX, 'rb') as f:
            _bm25_data = pickle.load(f)
    return _bm25_data


def tokenize(text: str) -> List[str]:
    """Simple tokenizer for BM25.

    Args:
        text: Text to tokenize.

    Returns:
        List of lowercase tokens.
    """
    return text.lower().split()


def bm25_search(query: str, top_k: int = BM25_TOP_K) -> List[Dict[str, Any]]:
    """Search hadiths using BM25 keyword matching.

    Args:
        query: Search query.
        top_k: Number of results to return.

    Returns:
        List of search results with scores.
    """
    data = get_bm25_data()
    bm25 = data["bm25"]
    hadith_ids = data["hadith_ids"]
    hadiths = data["hadiths"]

    # Tokenize query
    query_tokens = tokenize(query)

    # Get BM25 scores for all documents
    scores = bm25.get_scores(query_tokens)

    # Get top k results
    scored_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )[:top_k]

    # Format results
    search_results = []
    for idx in scored_indices:
        if scores[idx] > 0:  # Only include positive scores
            hadith_id = hadith_ids[idx]
            hadith = hadiths[hadith_id]

            search_results.append({
                "id": hadith_id,
                "score": float(scores[idx]),
                "book": hadith.get("book", ""),
                "volume": hadith.get("volume", 0),
                "chapter": hadith.get("chapter", ""),
                "hadith_number": hadith.get("hadith_number", 0),
                "narrator": hadith.get("narrator", ""),
                "text": hadith.get("text", "")
            })

    return search_results
