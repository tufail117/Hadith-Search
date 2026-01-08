"""Pydantic models for API request/response."""

from typing import List, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request model for hadith search."""

    query: str = Field(..., description="Search query", min_length=1)
    top_k: int = Field(default=10, description="Number of results", ge=1, le=50)


class HadithResult(BaseModel):
    """Single hadith search result."""

    id: str = Field(..., description="Unique hadith identifier")
    book: str = Field(..., description="Book name (bukhari/muslim)")
    volume: int = Field(..., description="Volume number")
    chapter: str = Field(..., description="Chapter name/number")
    hadith_number: int = Field(..., description="Hadith number")
    narrator: str = Field(..., description="Chain of narration")
    text: str = Field(..., description="Hadith text")
    score: float = Field(..., description="Relevance score")


class SearchResponse(BaseModel):
    """Response model for hadith search."""

    query: str = Field(..., description="Original query")
    expanded_query: str = Field(..., description="Query with expanded terms")
    results: List[HadithResult] = Field(..., description="Search results")
    cached: bool = Field(..., description="Whether results were from cache")
    took_ms: float = Field(..., description="Search time in milliseconds")


class CacheStats(BaseModel):
    """Cache statistics."""

    size: int = Field(..., description="Current cache size")
    max_size: int = Field(..., description="Maximum cache size")
    hits: int = Field(..., description="Cache hits")
    misses: int = Field(..., description="Cache misses")
    hit_rate: float = Field(..., description="Hit rate (0-1)")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="ok", description="Service status")
    version: str = Field(default="1.0", description="API version")


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(..., description="Response message")
