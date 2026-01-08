"""Cross-encoder reranking for search results."""

from typing import List, Dict, Any, Optional

from sentence_transformers import CrossEncoder

from src.config import RERANKER_MODEL

# Lazy-loaded global
_reranker: Optional[CrossEncoder] = None


def get_reranker() -> CrossEncoder:
    """Get or load reranker model (lazy loading).

    Returns:
        Loaded CrossEncoder model.
    """
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(RERANKER_MODEL)
    return _reranker


def rerank_results(
    query: str,
    results: List[Dict[str, Any]],
    top_k: int = 10
) -> List[Dict[str, Any]]:
    """Rerank search results using cross-encoder.

    Args:
        query: Original search query.
        results: List of search results to rerank.
        top_k: Number of results to return after reranking.

    Returns:
        Reranked results sorted by score.
    """
    if not results:
        return []

    reranker = get_reranker()

    # Create query-document pairs
    pairs = [
        [query, f"{r.get('narrator', '')} {r.get('text', '')}"]
        for r in results
    ]

    # Score pairs
    scores = reranker.predict(pairs)

    # Add rerank scores to results
    for i, result in enumerate(results):
        result["rerank_score"] = float(scores[i])

    # Sort by rerank score (descending) and return top k
    reranked = sorted(results, key=lambda x: x["rerank_score"], reverse=True)

    return reranked[:top_k]
