"""AI News Aggregator Tool - Tracks AI updates from major sources"""
import os
from crewai.tools import BaseTool
from pydantic import Field
from typing import Type
from pydantic import BaseModel
import requests
from datetime import datetime


class AINewsInput(BaseModel):
    """Input for AI news search"""
    topic: str = Field(default="AI automation", description="Specific AI topic to search for")
    days: int = Field(default=7, description="Number of days to look back")


class AINewsAggregatorTool(BaseTool):
    name: str = "AI News Aggregator"
    description: str = """
    Aggregates latest AI news from OpenAI, Anthropic, Google AI, and tech news sources.
    Use this to stay updated on AI industry developments for content creation.
    Returns recent announcements, updates, and trending AI news.
    """
    args_schema: Type[BaseModel] = AINewsInput

    def _run(self, topic: str = "AI automation", days: int = 7) -> str:
        serp_api_key = os.getenv("SERP_API_KEY")

        if serp_api_key:
            return self._search_news(topic, days, serp_api_key)
        else:
            return self._curated_news()

    def _search_news(self, topic: str, days: int, api_key: str) -> str:
        """Search for AI news using SerpAPI"""
        try:
            url = "https://serpapi.com/search"
            params = {
                "engine": "google_news",
                "q": f"{topic} AI",
                "api_key": api_key,
                "gl": "us",
                "hl": "en"
            }

            response = requests.get(url, params=params)
            data = response.json()
            news_results = data.get('news_results', [])

            result = f"""
## AI Industry News

### Topic: {topic}
### Date: {datetime.now().strftime('%Y-%m-%d')}

### Latest News:
"""
            for i, news in enumerate(news_results[:15], 1):
                title = news.get('title', 'N/A')
                source = news.get('source', {}).get('name', 'Unknown')
                date = news.get('date', 'N/A')
                snippet = news.get('snippet', '')[:150]
                link = news.get('link', '')

                result += f"""
**{i}. {title}**
- Source: {source} | {date}
- Summary: {snippet}...
- Link: {link}
"""

            result += """
### Content Opportunities:
1. Create reaction/analysis content for major announcements
2. Explain technical updates in simple terms
3. Predict implications for AI automation industry
4. Compare new features across AI platforms
"""
            return result

        except Exception as e:
            return self._curated_news()

    def _curated_news(self) -> str:
        """Curated AI news sources and recent updates"""
        return f"""
## AI Industry News & Updates

### Date: {datetime.now().strftime('%Y-%m-%d')}

### 🔥 Recent Major AI Announcements:

**OpenAI Updates:**
1. GPT-4 Turbo - Faster, cheaper, 128K context
2. Custom GPTs - Build specialized AI assistants
3. GPT Store - Marketplace for GPTs
4. Voice and Vision capabilities expanded

**Anthropic Updates:**
1. Claude 3.5 Sonnet - Best balance of speed/quality
2. Claude 3.5 Haiku - Fast and affordable
3. Computer Use (beta) - AI can control computers
4. Improved coding capabilities

**Google AI Updates:**
1. Gemini 1.5 Pro - Million token context
2. Gemini in Google Workspace - AI across apps
3. NotebookLM - AI research assistant
4. Imagen 3 - Advanced image generation

**Meta AI Updates:**
1. Llama 3.2 - Open source multimodal
2. AI Studio - Build AI apps
3. Meta AI across platforms

### 📰 Key Sources to Monitor:

**Official Blogs:**
- blog.openai.com - OpenAI announcements
- anthropic.com/news - Anthropic updates
- blog.google/technology/ai - Google AI
- ai.meta.com/blog - Meta AI

**Tech News:**
- techcrunch.com/tag/artificial-intelligence
- theverge.com/ai-artificial-intelligence
- arstechnica.com/ai

**AI Community:**
- news.ycombinator.com (Hacker News)
- reddit.com/r/MachineLearning
- reddit.com/r/artificial

### 🎯 Content Recommendations:

**Time-Sensitive (Create within 24-48 hours):**
1. React to major AI announcements
2. First looks at new AI tools
3. Breaking down technical updates

**Evergreen (Create anytime):**
1. AI tool comparisons
2. Tutorial content for AI features
3. Industry analysis and predictions

### 📅 Upcoming AI Events to Cover:
- OpenAI DevDay announcements
- Google I/O AI sessions
- AWS re:Invent AI updates
- Microsoft Ignite AI news

### 💡 Trending AI Automation Topics:

1. **AI Agents** - Autonomous AI workflows
2. **RAG Systems** - Retrieval augmented generation
3. **Fine-tuning** - Custom AI models
4. **Multi-modal AI** - Text + Image + Audio
5. **AI Coding** - GitHub Copilot, Cursor, etc.

Note: Add SERP_API_KEY to .env for real-time news search
"""
