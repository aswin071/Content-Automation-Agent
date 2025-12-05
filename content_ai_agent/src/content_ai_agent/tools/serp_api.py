import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import httpx

class SerpSearchInput(BaseModel):
    query: str = Field(..., description="Search query for Google Trends/Search")
    search_type: str = Field(default="search", description="Type: 'search', 'trends', or 'youtube'")

class SerpAPITool(BaseTool):
    name: str = "Google Search & Trends"
    description: str = "Search Google for trending topics, news, and related queries using SerpAPI"
    args_schema: type[BaseModel] = SerpSearchInput

    def _run(self, query: str, search_type: str = "search") -> str:
        api_key = os.getenv("SERP_API_KEY")

        if not api_key:
            return "Error: SERP_API_KEY not found in environment variables"

        base_url = "https://serpapi.com/search"

        # Configure params based on search type
        if search_type == "trends":
            params = {
                "engine": "google_trends",
                "q": query,
                "api_key": api_key
            }
        elif search_type == "youtube":
            params = {
                "engine": "youtube",
                "search_query": query,
                "api_key": api_key
            }
        else:  # default google search
            params = {
                "engine": "google",
                "q": query,
                "api_key": api_key,
                "num": 10
            }

        try:
            response = httpx.get(base_url, params=params, timeout=30)
            data = response.json()

            if "error" in data:
                return f"API Error: {data['error']}"

            return self._parse_results(data, search_type)

        except Exception as e:
            return f"Request failed: {str(e)}"

    def _parse_results(self, data: dict, search_type: str) -> str:
        results = []

        if search_type == "trends":
            # Parse Google Trends data
            interest = data.get("interest_over_time", {})
            if interest:
                results.append(f"Interest over time: {interest}")

            related = data.get("related_queries", {})
            if related:
                rising = related.get("rising", [])[:5]
                results.append(f"Rising queries: {[q.get('query') for q in rising]}")

        elif search_type == "youtube":
            # Parse YouTube results from SerpAPI
            for item in data.get("video_results", [])[:10]:
                results.append({
                    "title": item.get("title"),
                    "views": item.get("views"),
                    "channel": item.get("channel", {}).get("name"),
                    "published": item.get("published_date"),
                    "link": item.get("link")
                })

        else:  # Google search
            # Organic results
            for item in data.get("organic_results", [])[:10]:
                results.append({
                    "title": item.get("title"),
                    "snippet": item.get("snippet"),
                    "link": item.get("link")
                })

            # Related searches (great for content ideas)
            related = data.get("related_searches", [])
            if related:
                results.append({
                    "related_searches": [r.get("query") for r in related[:5]]
                })

        return str(results) if results else "No results found"
