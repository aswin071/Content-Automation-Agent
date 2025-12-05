"""
Data Collector Service - Fetches REAL data from APIs
NO FAKE DATA. If API fails, return error, not made-up data.
"""
import os
import httpx
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False


@dataclass
class YouTubeVideo:
    title: str
    video_id: str
    channel_name: str
    view_count: int
    like_count: int
    publish_date: str
    url: str


@dataclass
class TrendData:
    keyword: str
    current_interest: int
    average_interest: float
    trend_direction: str
    rising_queries: List[str]


@dataclass
class CollectedData:
    topic: str
    platform: str
    collected_at: str
    youtube_videos: List[YouTubeVideo] = field(default_factory=list)
    trends: List[TrendData] = field(default_factory=list)
    serp_questions: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def has_data(self) -> bool:
        return bool(self.youtube_videos or self.trends or self.serp_questions)

    def to_prompt_context(self) -> str:
        """Convert to string for LLM context - ONLY real data"""
        ctx = f"""
=== REAL DATA COLLECTED ===
Topic: {self.topic}
Platform: {self.platform}
Collected: {self.collected_at}

"""
        # YouTube Videos
        if self.youtube_videos:
            ctx += "### TOP YOUTUBE VIDEOS (REAL):\n"
            for i, v in enumerate(self.youtube_videos[:10], 1):
                ctx += f"""
{i}. "{v.title}"
   Channel: {v.channel_name}
   Views: {v.view_count:,} | Likes: {v.like_count:,}
   Published: {v.publish_date}
   URL: {v.url}
"""
        else:
            ctx += "### YOUTUBE: No data (API issue)\n"

        # Trends
        if self.trends:
            ctx += "\n### GOOGLE TRENDS (REAL):\n"
            for t in self.trends:
                ctx += f"""
Keyword: "{t.keyword}"
- Interest: {t.current_interest}/100 (avg: {t.average_interest:.0f})
- Direction: {t.trend_direction}
- Rising queries: {', '.join(t.rising_queries[:5]) if t.rising_queries else 'None'}
"""
        else:
            ctx += "\n### GOOGLE TRENDS: No data\n"

        # SERP Questions
        if self.serp_questions:
            ctx += "\n### PEOPLE ALSO ASK (REAL):\n"
            for q in self.serp_questions[:10]:
                ctx += f"- {q}\n"
        else:
            ctx += "\n### SERP QUESTIONS: No data\n"

        # Errors
        if self.errors:
            ctx += "\n### DATA COLLECTION ISSUES:\n"
            for e in self.errors:
                ctx += f"- {e}\n"

        return ctx


class DataCollector:
    """Collects REAL data from APIs. No fake data."""

    def __init__(self):
        self.youtube_key = os.getenv("YOUTUBE_API_KEY")
        self.serp_key = os.getenv("SERP_API_KEY")

    def collect_all(self, topic: str, platform: str = "youtube") -> CollectedData:
        """Synchronous collection of all data"""
        data = CollectedData(
            topic=topic,
            platform=platform,
            collected_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        # Collect YouTube videos
        data.youtube_videos = self._fetch_youtube(topic, data.errors)

        # Collect Google Trends
        data.trends = self._fetch_trends(topic, data.errors)

        # Collect SERP questions
        data.serp_questions = self._fetch_serp(topic, data.errors)

        return data

    def _fetch_youtube(self, query: str, errors: List[str]) -> List[YouTubeVideo]:
        """Fetch real YouTube videos"""
        if not self.youtube_key:
            errors.append("YOUTUBE_API_KEY not set")
            return []

        try:
            # Search videos
            search_url = "https://www.googleapis.com/youtube/v3/search"
            search_params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "order": "viewCount",
                "maxResults": 10,
                "key": self.youtube_key
            }

            with httpx.Client(timeout=30.0) as client:
                resp = client.get(search_url, params=search_params)
                search_data = resp.json()

            if "error" in search_data:
                errors.append(f"YouTube API: {search_data['error'].get('message', 'Unknown error')}")
                return []

            items = search_data.get("items", [])
            if not items:
                errors.append(f"No YouTube videos found for: {query}")
                return []

            # Get video stats
            video_ids = [item["id"]["videoId"] for item in items if "videoId" in item.get("id", {})]
            if not video_ids:
                return []

            stats_url = "https://www.googleapis.com/youtube/v3/videos"
            stats_params = {
                "part": "statistics",
                "id": ",".join(video_ids),
                "key": self.youtube_key
            }

            with httpx.Client(timeout=30.0) as client:
                stats_resp = client.get(stats_url, params=stats_params)
                stats_data = stats_resp.json()

            stats_map = {v["id"]: v["statistics"] for v in stats_data.get("items", [])}

            videos = []
            for item in items:
                vid = item.get("id", {}).get("videoId")
                if not vid:
                    continue

                snippet = item["snippet"]
                stats = stats_map.get(vid, {})

                videos.append(YouTubeVideo(
                    title=snippet.get("title", ""),
                    video_id=vid,
                    channel_name=snippet.get("channelTitle", ""),
                    view_count=int(stats.get("viewCount", 0)),
                    like_count=int(stats.get("likeCount", 0)),
                    publish_date=snippet.get("publishedAt", "")[:10],
                    url=f"https://youtube.com/watch?v={vid}"
                ))

            return videos

        except Exception as e:
            errors.append(f"YouTube fetch failed: {str(e)}")
            return []

    def _fetch_trends(self, topic: str, errors: List[str]) -> List[TrendData]:
        """Fetch real Google Trends data"""
        if not PYTRENDS_AVAILABLE:
            errors.append("pytrends not installed (pip install pytrends)")
            return []

        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            pytrends.build_payload([topic], cat=0, timeframe='today 3-m', geo='', gprop='')

            interest_df = pytrends.interest_over_time()
            related = pytrends.related_queries()

            if interest_df.empty:
                errors.append(f"No Google Trends data for: {topic}")
                return []

            rising_queries = []
            if topic in related and related[topic]['rising'] is not None:
                rising_queries = related[topic]['rising']['query'].tolist()[:10]

            current = int(interest_df[topic].iloc[-1])
            avg = float(interest_df[topic].mean())

            if current > avg * 1.1:
                direction = "📈 RISING"
            elif current < avg * 0.9:
                direction = "📉 DECLINING"
            else:
                direction = "➡️ STABLE"

            return [TrendData(
                keyword=topic,
                current_interest=current,
                average_interest=avg,
                trend_direction=direction,
                rising_queries=rising_queries
            )]

        except Exception as e:
            errors.append(f"Google Trends failed: {str(e)}")
            return []

    def _fetch_serp(self, query: str, errors: List[str]) -> List[str]:
        """Fetch People Also Ask from SERP API"""
        if not self.serp_key:
            errors.append("SERP_API_KEY not set")
            return []

        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": self.serp_key,
                "engine": "google"
            }

            with httpx.Client(timeout=30.0) as client:
                resp = client.get(url, params=params)
                data = resp.json()

            if "error" in data:
                errors.append(f"SERP API: {data['error']}")
                return []

            questions = []
            for item in data.get("related_questions", []):
                if "question" in item:
                    questions.append(item["question"])

            return questions

        except Exception as e:
            errors.append(f"SERP fetch failed: {str(e)}")
            return []
