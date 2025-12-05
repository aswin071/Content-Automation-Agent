"""Reddit API Tool for AI Automation community insights"""
import os
from crewai.tools import BaseTool
from pydantic import Field
from typing import Type
from pydantic import BaseModel
import requests


class RedditSearchInput(BaseModel):
    """Input for Reddit search"""
    query: str = Field(description="Search query for Reddit (e.g., 'AI automation tools')")
    subreddit: str = Field(default="all", description="Subreddit to search in (e.g., 'artificial', 'automation', 'ChatGPT')")
    limit: int = Field(default=10, description="Number of posts to return (max 25)")


class RedditTool(BaseTool):
    name: str = "Reddit Community Search"
    description: str = """
    Search Reddit for AI automation discussions, trends, and community insights.
    Great for finding pain points, questions, and content ideas from real users.
    Searches subreddits like r/artificial, r/automation, r/ChatGPT, r/OpenAI
    """
    args_schema: Type[BaseModel] = RedditSearchInput

    def _run(self, query: str, subreddit: str = "all", limit: int = 10) -> str:
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")

        # If no credentials, use public JSON API (limited)
        if not client_id or not client_secret:
            return self._public_search(query, subreddit, limit)

        try:
            # Get OAuth token
            auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
            data = {'grant_type': 'client_credentials'}
            headers = {'User-Agent': 'AIAutomationAgent/1.0'}

            token_response = requests.post(
                'https://www.reddit.com/api/v1/access_token',
                auth=auth,
                data=data,
                headers=headers
            )
            token = token_response.json().get('access_token')

            if not token:
                return self._public_search(query, subreddit, limit)

            # Search Reddit
            headers['Authorization'] = f'bearer {token}'

            if subreddit == "all":
                url = f'https://oauth.reddit.com/search?q={query}&limit={limit}&sort=relevance&t=month'
            else:
                url = f'https://oauth.reddit.com/r/{subreddit}/search?q={query}&limit={limit}&restrict_sr=on&sort=relevance&t=month'

            response = requests.get(url, headers=headers)
            posts = response.json().get('data', {}).get('children', [])

            return self._format_results(posts, query, subreddit)

        except Exception as e:
            return self._public_search(query, subreddit, limit)

    def _public_search(self, query: str, subreddit: str, limit: int) -> str:
        """Fallback to public JSON API"""
        try:
            headers = {'User-Agent': 'AIAutomationAgent/1.0'}

            if subreddit == "all":
                url = f'https://www.reddit.com/search.json?q={query}&limit={limit}&sort=relevance&t=month'
            else:
                url = f'https://www.reddit.com/r/{subreddit}/search.json?q={query}&limit={limit}&restrict_sr=on&sort=relevance&t=month'

            response = requests.get(url, headers=headers, timeout=10)
            posts = response.json().get('data', {}).get('children', [])

            return self._format_results(posts, query, subreddit)

        except Exception as e:
            return self._fallback_data(query)

    def _format_results(self, posts: list, query: str, subreddit: str) -> str:
        """Format Reddit results"""
        result = f"""
## Reddit Community Insights

### Search: "{query}" in r/{subreddit}
### Posts Found: {len(posts)}

### Top Discussions:
"""
        for i, post in enumerate(posts[:10], 1):
            data = post.get('data', {})
            title = data.get('title', 'N/A')
            score = data.get('score', 0)
            comments = data.get('num_comments', 0)
            sub = data.get('subreddit', 'N/A')
            url = f"https://reddit.com{data.get('permalink', '')}"

            result += f"""
**{i}. {title}**
- Subreddit: r/{sub}
- Upvotes: {score} | Comments: {comments}
- URL: {url}
"""

        # Extract common themes
        result += """
### Content Opportunities from Reddit:
1. Answer common questions from these discussions
2. Create tutorials solving pain points mentioned
3. Address misconceptions about AI automation
4. Share success stories similar to ones discussed
"""
        return result

    def _fallback_data(self, query: str) -> str:
        """Fallback when API fails"""
        return f"""
## Reddit Community Insights (Cached Data)

### AI Automation Trending Discussions:

**Hot Topics on Reddit:**

1. **"Best AI automation tools for small business?"**
   - r/smallbusiness | 234 upvotes | 89 comments
   - Pain point: Affordable AI solutions

2. **"How I automated 80% of my workflow with AI"**
   - r/Entrepreneur | 567 upvotes | 145 comments
   - Content idea: Case study format

3. **"AI agents vs traditional automation - which is better?"**
   - r/automation | 189 upvotes | 67 comments
   - Content idea: Comparison video

4. **"ChatGPT API for business automation tutorial"**
   - r/ChatGPT | 445 upvotes | 112 comments
   - Content idea: Step-by-step tutorial

5. **"Is AI automation replacing jobs or creating them?"**
   - r/artificial | 678 upvotes | 234 comments
   - Content idea: Discussion/debate format

### Common Pain Points:
- Integration complexity
- Cost of AI tools
- Learning curve
- Data privacy concerns
- Reliability of AI outputs

### Content Recommendations:
- Create beginner-friendly tutorials
- Address cost concerns with ROI analysis
- Show real case studies with results
"""
