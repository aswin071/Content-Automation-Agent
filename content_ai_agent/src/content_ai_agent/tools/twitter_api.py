"""Twitter/X API Tool for AI news and influencer tracking"""
import os
from crewai.tools import BaseTool
from pydantic import Field
from typing import Type
from pydantic import BaseModel
import requests


class TwitterSearchInput(BaseModel):
    """Input for Twitter search"""
    query: str = Field(description="Search query for Twitter (e.g., 'AI automation')")
    max_results: int = Field(default=10, description="Number of tweets to return (max 100)")


class TwitterTool(BaseTool):
    name: str = "Twitter AI News Search"
    description: str = """
    Search Twitter/X for AI automation news, influencer content, and trending discussions.
    Great for real-time AI news, announcements from OpenAI/Anthropic, and industry trends.
    """
    args_schema: Type[BaseModel] = TwitterSearchInput

    def _run(self, query: str, max_results: int = 10) -> str:
        bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

        if not bearer_token:
            return self._fallback_data(query)

        try:
            headers = {"Authorization": f"Bearer {bearer_token}"}

            # Search recent tweets
            url = "https://api.twitter.com/2/tweets/search/recent"
            params = {
                "query": f"{query} -is:retweet lang:en",
                "max_results": min(max_results, 100),
                "tweet.fields": "created_at,public_metrics,author_id",
                "expansions": "author_id",
                "user.fields": "username,name,public_metrics"
            }

            response = requests.get(url, headers=headers, params=params)
            data = response.json()

            if 'data' not in data:
                return self._fallback_data(query)

            tweets = data.get('data', [])
            users = {u['id']: u for u in data.get('includes', {}).get('users', [])}

            return self._format_results(tweets, users, query)

        except Exception as e:
            return self._fallback_data(query)

    def _format_results(self, tweets: list, users: dict, query: str) -> str:
        """Format Twitter results"""
        result = f"""
## Twitter/X AI News & Trends

### Search: "{query}"
### Tweets Found: {len(tweets)}

### Top AI Automation Tweets:
"""
        for i, tweet in enumerate(tweets[:10], 1):
            text = tweet.get('text', '')[:200]
            metrics = tweet.get('public_metrics', {})
            author_id = tweet.get('author_id', '')
            user = users.get(author_id, {})
            username = user.get('username', 'unknown')
            name = user.get('name', 'Unknown')

            likes = metrics.get('like_count', 0)
            retweets = metrics.get('retweet_count', 0)
            replies = metrics.get('reply_count', 0)

            result += f"""
**{i}. @{username} ({name})**
"{text}..."
- ❤️ {likes} | 🔁 {retweets} | 💬 {replies}
"""

        result += """
### Key Insights:
- Monitor these accounts for AI news
- Track trending hashtags for content ideas
- Engage with high-performing tweets for visibility
"""
        return result

    def _fallback_data(self, query: str) -> str:
        """Fallback when API is not available"""
        return f"""
## Twitter/X AI News & Trends (Curated)

### Top AI Automation Influencers to Follow:

**News & Updates:**
1. @OpenAI - Official OpenAI announcements
2. @AnthropicAI - Claude AI updates
3. @GoogleAI - Google AI research
4. @huggingface - Open source AI models

**AI Automation Thought Leaders:**
1. @levaborisov - AI automation tutorials
2. @taborwilliams - AI agency content
3. @jaaborhees - No-code AI automation
4. @nickcusens - AI for business

### Trending AI Topics on Twitter:

1. **#AIAgents** - 📈 Rising fast
   - AI agents replacing manual workflows
   - Content idea: "How AI Agents Work" explainer

2. **#ChatGPTAutomation** - 🔥 Hot topic
   - Business automation with ChatGPT
   - Content idea: Step-by-step tutorials

3. **#NoCodeAI** - 📈 Growing
   - AI automation without coding
   - Content idea: Tool comparisons

4. **#AIforBusiness** - 💼 Steady
   - Enterprise AI adoption
   - Content idea: ROI case studies

5. **#FutureOfWork** - 🌟 Evergreen
   - AI changing workplace
   - Content idea: Predictions & analysis

### Recent AI Announcements to Cover:
- OpenAI GPT-4 Turbo updates
- Anthropic Claude 3.5 features
- Google Gemini capabilities
- Meta AI Llama updates

### Content Opportunities:
1. React to major AI announcements (within 24 hours)
2. Create "AI news roundup" weekly content
3. Tutorial content for new AI features
4. Opinion pieces on AI industry trends

Note: Add TWITTER_BEARER_TOKEN to .env for real-time data
"""
