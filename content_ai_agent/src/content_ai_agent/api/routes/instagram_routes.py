"""
Instagram API Routes
Endpoints for fetching Instagram trending topics and hashtags
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from content_ai_agent.services.instagram_service import InstagramService, InstagramTrendingResponse


router = APIRouter()


# ===== REQUEST MODELS =====
class InstagramTrendingRequest(BaseModel):
    niche: str
    limit: int = 10


class HashtagSearchRequest(BaseModel):
    hashtag: str


# ===== RESPONSE MODELS =====
class InstagramHashtagsResponse(BaseModel):
    success: bool
    hashtags: List[str]
    count: int


class InstagramTopicsResponse(BaseModel):
    success: bool
    data: InstagramTrendingResponse
    message: str = ""


# ===== API ENDPOINTS =====

@router.get("/trending/hashtags")
async def get_trending_hashtags(limit: int = 10):
    """
    Get current trending hashtags on Instagram

    Args:
        limit: Number of hashtags to return (default: 10)

    Returns:
        List of trending hashtags
    """
    try:
        service = InstagramService()
        hashtags = await service.get_trending_hashtags(limit=limit)

        return InstagramHashtagsResponse(
            success=True,
            hashtags=hashtags,
            count=len(hashtags)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trending/niche", response_model=InstagramTopicsResponse)
async def get_trending_by_niche(request: InstagramTrendingRequest):
    """
    Get trending topics and hashtags for a specific niche

    Args:
        request: Contains niche and limit

    Returns:
        Trending hashtags and topics for the niche
    """
    try:
        service = InstagramService()
        data = await service.get_trending_for_niche(
            niche=request.niche,
            limit=request.limit
        )

        return InstagramTopicsResponse(
            success=True,
            data=data,
            message=f"Trending data fetched for niche: {request.niche}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hashtag/search")
async def search_hashtag(request: HashtagSearchRequest):
    """
    Search for a specific hashtag and get its metrics

    Args:
        request: Contains hashtag to search

    Returns:
        Hashtag data including post count and recent posts
    """
    try:
        service = InstagramService()
        # Remove # if user included it
        hashtag = request.hashtag.lstrip('#')
        data = await service.search_hashtag(hashtag)

        return {
            "success": True,
            "data": data,
            "hashtag": f"#{hashtag}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending/categories")
async def get_available_categories():
    """
    Get list of available Instagram categories for trending topics

    Returns:
        List of supported categories
    """
    categories = [
        "general",
        "fashion",
        "beauty",
        "fitness",
        "food",
        "travel",
        "technology",
        "business",
        "lifestyle",
        "art",
        "photography",
        "music",
        "gaming",
        "sports",
        "health",
        "education"
    ]

    return {
        "success": True,
        "categories": categories,
        "count": len(categories)
    }
