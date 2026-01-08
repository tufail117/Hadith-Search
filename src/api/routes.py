"""API routes for hadith search."""

from typing import Optional

from fastapi import APIRouter, HTTPException

from src.api.models import (
    SearchRequest,
    SearchResponse,
    HadithResult,
    CacheStats,
    HealthResponse,
    MessageResponse
)
from src.search.hybrid_search import hybrid_search
from src.search.cache import get_cache
from src.search.bm25_search import get_bm25_data

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_hadiths(request: SearchRequest) -> SearchResponse:
    """Search for hadiths matching the query.

    Args:
        request: Search request with query and optional top_k.

    Returns:
        SearchResponse with matching hadiths.
    """
    try:
        results, expanded_query, cached, took_ms = hybrid_search(
            query=request.query,
            top_k=request.top_k
        )

        # Convert to HadithResult objects
        hadith_results = [
            HadithResult(
                id=r["id"],
                book=r["book"],
                volume=r["volume"],
                chapter=r["chapter"],
                hadith_number=r["hadith_number"],
                narrator=r["narrator"],
                text=r["text"],
                score=r["score"]
            )
            for r in results
        ]

        return SearchResponse(
            query=request.query,
            expanded_query=expanded_query,
            results=hadith_results,
            cached=cached,
            took_ms=took_ms
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hadith/{hadith_id}", response_model=HadithResult)
async def get_hadith(hadith_id: str) -> HadithResult:
    """Get a single hadith by ID.

    Args:
        hadith_id: Unique hadith identifier.

    Returns:
        HadithResult with hadith details.
    """
    try:
        data = get_bm25_data()
        hadiths = data["hadiths"]

        if hadith_id not in hadiths:
            raise HTTPException(status_code=404, detail="Hadith not found")

        hadith = hadiths[hadith_id]

        return HadithResult(
            id=hadith["id"],
            book=hadith["book"],
            volume=hadith["volume"],
            chapter=hadith["chapter"],
            hadith_number=hadith["hadith_number"],
            narrator=hadith["narrator"],
            text=hadith["text"],
            score=1.0
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns:
        HealthResponse with status and version.
    """
    return HealthResponse(status="ok", version="1.0")


@router.get("/cache/stats", response_model=CacheStats)
async def cache_stats() -> CacheStats:
    """Get cache statistics.

    Returns:
        CacheStats with current cache info.
    """
    cache = get_cache()
    stats = cache.stats()
    return CacheStats(**stats)


@router.post("/cache/clear", response_model=MessageResponse)
async def clear_cache() -> MessageResponse:
    """Clear the search cache.

    Returns:
        MessageResponse confirming cache cleared.
    """
    cache = get_cache()
    cache.clear()
    return MessageResponse(message="Cache cleared")
