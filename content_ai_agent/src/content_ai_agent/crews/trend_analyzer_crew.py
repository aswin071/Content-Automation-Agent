"""Trend Analyzer Crew - Analyzes AI automation trends from multiple sources"""
from os import getenv
from pathlib import Path
from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv

from content_ai_agent.tools.google_trends import GoogleTrendsTool
from content_ai_agent.tools.reddit_api import RedditTool
from content_ai_agent.tools.twitter_api import TwitterTool
from content_ai_agent.tools.ai_news_aggregator import AINewsAggregatorTool

# Load .env
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)

LLM_MODEL = getenv('MODEL', 'anthropic/claude-3-5-haiku-20241022')


class TrendAnalyzerCrew:
    """Crew that analyzes AI automation trends from multiple sources"""

    def __init__(self):
        self.tools = [
            GoogleTrendsTool(),
            RedditTool(),
            TwitterTool(),
            AINewsAggregatorTool()
        ]
        self.agent = self._create_agent()
        self.task = self._create_task()

    def _create_agent(self) -> Agent:
        return Agent(
            role="AI Automation Trend Analyst",
            goal="Identify trending topics, emerging patterns, and content opportunities in the AI automation space",
            backstory="""
            You are an expert trend analyst specializing in the AI automation industry.
            With 10+ years of experience in market research and data analysis, you have a keen eye
            for identifying emerging trends before they go mainstream. You track multiple data sources
            including Google Trends, Reddit communities, Twitter discussions, and AI industry news.
            Your analysis helps content creators stay ahead of the curve and create timely, relevant content.
            You understand the AI automation agency business model and know what topics resonate with
            entrepreneurs, business owners, and tech enthusiasts looking to leverage AI.
            """,
            llm=LLM_MODEL,
            tools=self.tools,
            verbose=True
        )

    def _create_task(self) -> Task:
        return Task(
            description="""
            Perform a comprehensive trend analysis for AI automation content:

            1. **Google Trends Analysis:**
               - Search for: "AI automation, AI agents, ChatGPT automation, workflow automation, AI tools"
               - Identify rising keywords and search patterns
               - Note seasonal trends and growth trajectories

            2. **Reddit Community Insights:**
               - Search r/artificial, r/automation, r/ChatGPT, r/OpenAI
               - Find common pain points and questions
               - Identify popular discussion topics

            3. **Twitter/X AI News:**
               - Track AI influencer discussions
               - Find trending hashtags and topics
               - Note recent AI announcements

            4. **AI Industry News:**
               - Check latest updates from OpenAI, Anthropic, Google AI
               - Identify newsworthy developments
               - Find content opportunities from recent announcements

            Synthesize all data into actionable content recommendations for an AI automation agency.
            """,
            expected_output="""
            Comprehensive trend report with:
            - Top 5 trending topics with data to support each
            - Rising keywords and search terms
            - Community pain points and questions to address
            - Recent AI news worth covering
            - Content recommendations with priority ranking
            - Predicted trends for next 30 days
            - Specific content ideas with titles and angles
            """,
            agent=self.agent
        )

    def crew(self) -> Crew:
        return Crew(
            agents=[self.agent],
            tasks=[self.task],
            process=Process.sequential,
            verbose=True
        )

    def run(self) -> dict:
        """Run the trend analyzer crew"""
        result = self.crew().kickoff()
        return result
