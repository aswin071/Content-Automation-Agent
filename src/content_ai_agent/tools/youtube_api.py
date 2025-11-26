import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import httpx
api_key = os.getenv("YOUTUBE_API_KEY")

class YouTubeSearchInput(BaseModel):
    query: str = Field(..., description="Search query for trending topics")
    max_results: int = Field(default=5, description="Number of results")

class YouTubeTool(BaseTool):
    name: str = "YouTube Trending Search"
    description: str = "Search YouTube for trending videos in a niche"
    args_schema: type[BaseModel] = YouTubeSearchInput

    def _run(self, query: str, max_results: int = 5) -> str:
        api_key = os.getenv("YOUTUBE_API_KEY")
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "order": "viewCount",
            "maxResults": max_results,
            "key": api_key
        }
        response = httpx.get(url, params=params)
        data = response.json()
        
        results = []
        for item in data.get("items", []):
            results.append({
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "channel": item["snippet"]["channelTitle"]
            })
        return str(results)