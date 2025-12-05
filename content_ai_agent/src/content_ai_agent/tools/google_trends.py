"""Google Trends Tool for AI Automation Agency trends"""
import os
from crewai.tools import BaseTool
from pydantic import Field
from typing import Type, Optional
from pydantic import BaseModel

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False


class GoogleTrendsInput(BaseModel):
    """Input for Google Trends search"""
    keywords: str = Field(description="Comma-separated keywords to search (e.g., 'AI automation,chatgpt,AI agents')")
    timeframe: str = Field(default="today 3-m", description="Timeframe: 'now 1-H', 'now 4-H', 'now 1-d', 'now 7-d', 'today 1-m', 'today 3-m', 'today 12-m'")


class GoogleTrendsTool(BaseTool):
    name: str = "Google Trends Search"
    description: str = """
    Search Google Trends for AI automation related keywords.
    Returns trending data, related queries, and rising topics.
    Use this to find what's trending in AI automation space.
    Input: comma-separated keywords (e.g., 'AI automation,AI agents,chatgpt')
    """
    args_schema: Type[BaseModel] = GoogleTrendsInput

    def _run(self, keywords: str, timeframe: str = "today 3-m") -> str:
        if not PYTRENDS_AVAILABLE:
            return self._fallback_trends(keywords)

        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            keyword_list = [k.strip() for k in keywords.split(',')][:5]  # Max 5 keywords

            pytrends.build_payload(keyword_list, cat=0, timeframe=timeframe, geo='', gprop='')

            # Get interest over time
            interest_df = pytrends.interest_over_time()

            # Get related queries
            related_queries = pytrends.related_queries()

            # Get rising queries
            rising_topics = []
            for kw in keyword_list:
                if kw in related_queries and related_queries[kw]['rising'] is not None:
                    rising = related_queries[kw]['rising'].head(5).to_dict('records')
                    rising_topics.append({
                        "keyword": kw,
                        "rising_queries": rising
                    })

            # Format response
            result = f"""
## Google Trends Analysis for AI Automation

### Keywords Analyzed: {', '.join(keyword_list)}
### Timeframe: {timeframe}

### Trend Summary:
"""
            if not interest_df.empty:
                for kw in keyword_list:
                    if kw in interest_df.columns:
                        avg_interest = interest_df[kw].mean()
                        max_interest = interest_df[kw].max()
                        recent_interest = interest_df[kw].iloc[-1] if len(interest_df) > 0 else 0
                        result += f"""
**{kw}:**
- Average Interest: {avg_interest:.1f}/100
- Peak Interest: {max_interest}/100
- Current Interest: {recent_interest}/100
- Trend: {'📈 Rising' if recent_interest > avg_interest else '📉 Declining'}
"""

            result += "\n### Rising Queries (Content Opportunities):\n"
            for topic in rising_topics:
                result += f"\n**{topic['keyword']}:**\n"
                for query in topic['rising_queries']:
                    result += f"- {query.get('query', 'N/A')} (Growth: {query.get('value', 'N/A')}%)\n"

            return result

        except Exception as e:
            return self._fallback_trends(keywords)

    def _fallback_trends(self, keywords: str) -> str:
        """Return error when pytrends is not available - NO FAKE DATA"""
        return f"""
## Google Trends Analysis FAILED

ERROR: Could not fetch real trends data.

Possible issues:
1. pytrends not installed: pip install pytrends
2. Rate limited by Google
3. Network connectivity issue

Keywords attempted: {keywords}

Note: This tool only returns REAL data. No simulated data available.
"""
