"""Competitor Analysis Tool for AI Automation Agency"""
import os
from crewai.tools import BaseTool
from pydantic import Field
from typing import Type
from pydantic import BaseModel
import requests


class CompetitorInput(BaseModel):
    """Input for competitor analysis"""
    competitor_channel: str = Field(description="YouTube channel name or ID to analyze")
    platform: str = Field(default="youtube", description="Platform: youtube, instagram, tiktok")


class CompetitorAnalyzerTool(BaseTool):
    name: str = "Competitor Analyzer"
    description: str = """
    Analyze competitor content in the AI automation space.
    Tracks competitor YouTube channels, content strategy, and performance.
    Use this to understand what's working for competitors.
    """
    args_schema: Type[BaseModel] = CompetitorInput

    def _run(self, competitor_channel: str, platform: str = "youtube") -> str:
        youtube_api_key = os.getenv("YOUTUBE_API_KEY")

        if platform == "youtube" and youtube_api_key:
            return self._analyze_youtube(competitor_channel, youtube_api_key)
        else:
            return self._fallback_analysis(competitor_channel, platform)

    def _analyze_youtube(self, channel_name: str, api_key: str) -> str:
        """Analyze YouTube competitor"""
        try:
            # Search for channel
            search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={channel_name}&type=channel&key={api_key}"
            response = requests.get(search_url)
            channels = response.json().get('items', [])

            if not channels:
                return self._fallback_analysis(channel_name, "youtube")

            channel_id = channels[0]['snippet']['channelId']
            channel_title = channels[0]['snippet']['title']

            # Get channel statistics
            stats_url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={channel_id}&key={api_key}"
            stats_response = requests.get(stats_url)
            stats_data = stats_response.json().get('items', [{}])[0]

            statistics = stats_data.get('statistics', {})
            subscribers = int(statistics.get('subscriberCount', 0))
            total_views = int(statistics.get('viewCount', 0))
            video_count = int(statistics.get('videoCount', 0))

            # Get recent videos
            videos_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&order=date&maxResults=10&type=video&key={api_key}"
            videos_response = requests.get(videos_url)
            videos = videos_response.json().get('items', [])

            # Get video statistics
            video_ids = [v['id']['videoId'] for v in videos if 'videoId' in v.get('id', {})]
            if video_ids:
                video_stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={','.join(video_ids)}&key={api_key}"
                video_stats_response = requests.get(video_stats_url)
                video_stats = {v['id']: v['statistics'] for v in video_stats_response.json().get('items', [])}
            else:
                video_stats = {}

            result = f"""
## Competitor Analysis: {channel_title}

### Channel Overview:
- **Subscribers:** {subscribers:,}
- **Total Views:** {total_views:,}
- **Total Videos:** {video_count}
- **Avg Views/Video:** {total_views // max(video_count, 1):,}

### Recent Content Performance:
"""
            for video in videos[:10]:
                title = video['snippet']['title']
                video_id = video.get('id', {}).get('videoId', '')
                stats = video_stats.get(video_id, {})
                views = int(stats.get('viewCount', 0))
                likes = int(stats.get('likeCount', 0))

                result += f"""
**{title}**
- Views: {views:,} | Likes: {likes:,}
- URL: https://youtube.com/watch?v={video_id}
"""

            result += """
### Content Strategy Insights:
1. **Posting Frequency:** Analyze upload schedule
2. **Top Topics:** Identify recurring themes
3. **Title Patterns:** Note successful title formats
4. **Thumbnail Style:** Analyze visual patterns

### Opportunities:
- Topics they haven't covered
- Gaps in their content strategy
- Audience questions unanswered
"""
            return result

        except Exception as e:
            return self._fallback_analysis(channel_name, "youtube")

    def _fallback_analysis(self, competitor: str, platform: str) -> str:
        """Return error when API fails - NO FAKE DATA"""
        return f"""
## Competitor Analysis FAILED

ERROR: Could not fetch real competitor data for "{competitor}" on {platform}.

Possible issues:
1. YOUTUBE_API_KEY not set or invalid
2. API quota exceeded
3. Channel not found
4. Network connectivity issue

Note: This tool only returns REAL data. No simulated data available.
To fix: Ensure YOUTUBE_API_KEY is set correctly in .env file.
"""
