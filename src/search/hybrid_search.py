"""Hybrid search combining vector and BM25 with RRF fusion."""

import time
from typing import List, Dict, Any, Tuple

from src.config import VECTOR_TOP_K, BM25_TOP_K, RERANK_TOP_K, FINAL_TOP_K, RRF_K
from src.search.query_expansion import expand_query
from src.search.vector_search import vector_search
from src.search.bm25_search import bm25_search
from src.search.reranker import rerank_results
from src.search.cache import get_cache


def reciprocal_rank_fusion(
    vector_results: List[Dict[str, Any]],
    bm25_results: List[Dict[str, Any]],
    k: int = RRF_K
) -> List[Dict[str, Any]]:
    """Combine results using Reciprocal Rank Fusion.

    RRF formula: score(doc) = Σ 1/(k + rank)

    Args:
        vector_results: Results from vector search.
        bm25_results: Results from BM25 search.
        k: RRF parameter (default 60).

    Returns:
        Combined and scored results.
    """
    # Calculate RRF scores
    rrf_scores: Dict[str, float] = {}
    result_data: Dict[str, Dict[str, Any]] = {}

    # Process vector results
    for rank, result in enumerate(vector_results, start=1):
        hadith_id = result["id"]
        rrf_scores[hadith_id] = rrf_scores.get(hadith_id, 0) + 1 / (k + rank)
        result_data[hadith_id] = result

    # Process BM25 results
    for rank, result in enumerate(bm25_results, start=1):
        hadith_id = result["id"]
        rrf_scores[hadith_id] = rrf_scores.get(hadith_id, 0) + 1 / (k + rank)
        if hadith_id not in result_data:
            result_data[hadith_id] = result

    # Sort by RRF score
    sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

    # Build result list
    combined_results = []
    for hadith_id in sorted_ids:
        result = result_data[hadith_id].copy()
        result["rrf_score"] = rrf_scores[hadith_id]
        combined_results.append(result)

    return combined_results


def hybrid_search(
    query: str,
    top_k: int = FINAL_TOP_K,
    use_cache: bool = True
) -> Tuple[List[Dict[str, Any]], str, bool, float]:
    """Perform hybrid search with query expansion, RRF fusion, and reranking.

    Args:
        query: User search query.
        top_k: Number of results to return.
        use_cache: Whether to use caching.

    Returns:
        Tuple of (results, expanded_query, cached, took_ms).
    """
    start_time = time.time()

    # Check cache first
    if use_cache:
        cache = get_cache()
        cached_results = cache.get(query)
        if cached_results is not None:
            took_ms = (time.time() - start_time) * 1000
            # Get expanded query for display
            expanded_query = expand_query(query)
            return cached_results[:top_k], expanded_query, True, took_ms

    # Expand query with Islamic terminology
    expanded_query = expand_query(query)

    # Run vector search
    vector_results = vector_search(expanded_query, top_k=VECTOR_TOP_K)

    # Run BM25 search
    bm25_results = bm25_search(expanded_query, top_k=BM25_TOP_K)

    # Combine with RRF
    combined_results = reciprocal_rank_fusion(vector_results, bm25_results)

    # Rerank top candidates
    candidates = combined_results[:RERANK_TOP_K]
    reranked_results = rerank_results(query, candidates, top_k=top_k)

    # Update scores to use rerank score as final
    for result in reranked_results:
        result["score"] = result.get("rerank_score", result.get("rrf_score", 0))

    # Cache results
    if use_cache:
        cache = get_cache()
        cache.set(query, reranked_results)

    took_ms = (time.time() - start_time) * 1000
    return reranked_results[:top_k], expanded_query, False, took_ms
