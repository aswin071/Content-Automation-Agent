"""
Instagram API Service
Fetches trending topics, hashtags, and content from Instagram using RapidAPI
"""
import os
import httpx
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class InstagramTrendingResponse(BaseModel):
    """Response model for trending Instagram content"""
    trending_hashtags: List[str]
    trending_topics: List[Dict[str, Any]]
    source: str = "instagram"


class InstagramService:
    """Service to interact with Instagram API via RapidAPI"""

    def __init__(self):
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
        self.rapidapi_host = os.getenv("RAPIDAPI_INSTAGRAM_HOST", "instagram-bulk-profile-scrapper.p.rapidapi.com")

        if not self.rapidapi_key:
            raise ValueError("RAPIDAPI_KEY environment variable is required")

    async def get_trending_hashtags(self, limit: int = 10) -> List[str]:
        """
        Fetch trending hashtags from Instagram

        Args:
            limit: Number of trending hashtags to fetch

        Returns:
            List of trending hashtag strings
        """
        url = f"https://{self.rapidapi_host}/trending/hashtags"

        headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": self.rapidapi_host
        }

        params = {"limit": limit}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

                # Parse response based on API structure
                if isinstance(data, dict) and "hashtags" in data:
                    return data["hashtags"][:limit]
                elif isinstance(data, list):
                    return data[:limit]

                return []

        except httpx.HTTPError as e:
            raise Exception(f"Failed to fetch trending hashtags: {str(e)}")

    async def get_trending_topics_by_category(self, category: str = "general") -> List[Dict]:
        """
        Fetch trending topics from Instagram by category

        Args:
            category: Category like 'fashion', 'tech', 'food', 'fitness', etc.

        Returns:
            List of trending topics with metadata
        """
        url = f"https://{self.rapidapi_host}/trending/topics"

        headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": self.rapidapi_host
        }

        params = {"category": category}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

                return data if isinstance(data, list) else []

        except httpx.HTTPError as e:
            raise Exception(f"Failed to fetch trending topics: {str(e)}")

    async def search_hashtag(self, hashtag: str) -> Dict:
        """
        Search for a specific hashtag and get its metrics

        Args:
            hashtag: Hashtag to search (without #)

        Returns:
            Hashtag data including post count, recent posts, etc.
        """
        url = f"https://{self.rapidapi_host}/hashtag/{hashtag}"

        headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": self.rapidapi_host
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPError as e:
            raise Exception(f"Failed to search hashtag: {str(e)}")

    async def get_trending_for_niche(self, niche: str, limit: int = 10) -> InstagramTrendingResponse:
        """
        Get comprehensive trending data for a specific niche

        Args:
            niche: The niche/category to get trends for
            limit: Number of results to return

        Returns:
            InstagramTrendingResponse with hashtags and topics
        """
        try:
            # Fetch trending hashtags
            hashtags = await self.get_trending_hashtags(limit=limit)

            # Fetch trending topics for the niche
            topics = await self.get_trending_topics_by_category(category=niche.lower())

            return InstagramTrendingResponse(
                trending_hashtags=hashtags[:limit],
                trending_topics=topics[:limit]
            )

        except Exception as e:
            raise Exception(f"Failed to get trending data for niche '{niche}': {str(e)}")


# Alternative: Simple scraping approach (no API key needed, but less reliable)
class InstagramScraperService:
    """
    Alternative service that scrapes public Instagram data
    Note: This is less reliable and may break if Instagram changes their structure
    Use RapidAPI service above for production
    """

    async def get_top_hashtags_by_keyword(self, keyword: str) -> List[str]:
        """
        Scrape top hashtags related to a keyword from Instagram web

        Args:
            keyword: Search keyword

        Returns:
            List of related hashtags
        """
        # This would require implementing web scraping with BeautifulSoup/Playwright
        # For now, return common patterns
        base_hashtags = [
            f"#{keyword}",
            f"#{keyword}gram",
            f"#{keyword}life",
            f"#{keyword}daily",
            f"#{keyword}love"
        ]
        return base_hashtags
