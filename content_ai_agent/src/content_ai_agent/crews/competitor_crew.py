"""Competitor Analysis Crew - Analyzes AI automation competitors"""
from os import getenv
from pathlib import Path
from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv

from content_ai_agent.tools.competitor_analyzer import CompetitorAnalyzerTool
from content_ai_agent.tools.youtube_api import YouTubeTool

# Load .env
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)

LLM_MODEL = getenv('MODEL', 'anthropic/claude-3-5-haiku-20241022')


class CompetitorAnalysisCrew:
    """Crew that analyzes competitors in the AI automation space"""

    def __init__(self):
        self.tools = [
            CompetitorAnalyzerTool(),
            YouTubeTool()
        ]
        self.agent = self._create_agent()
        self.task = self._create_task()

    def _create_agent(self) -> Agent:
        return Agent(
            role="AI Automation Competitor Intelligence Analyst",
            goal="Analyze competitor content strategies, identify gaps, and find opportunities to differentiate",
            backstory="""
            You are a competitive intelligence expert specializing in the AI automation content space.
            You've analyzed hundreds of YouTube channels, social media accounts, and content strategies
            in the AI/tech niche. You understand what makes content go viral, why certain creators
            succeed, and how to identify opportunities others miss. Your analysis helps creators
            develop unique positioning and content strategies that stand out in a crowded market.
            You're particularly skilled at finding content gaps and underserved audience segments.
            """,
            llm=LLM_MODEL,
            tools=self.tools,
            verbose=True
        )

    def _create_task(self) -> Task:
        return Task(
            description="""
            Perform comprehensive competitor analysis for AI automation content:

            1. **Top Competitor Analysis:**
               - Analyze top AI automation YouTubers (Liam Ottley, Nick Saraev, etc.)
               - Study their content strategy, posting frequency, and topics
               - Identify their highest performing content

            2. **Content Gap Analysis:**
               - Find topics competitors haven't covered
               - Identify underserved audience segments
               - Discover unique angles on popular topics

            3. **Strategy Insights:**
               - Analyze title and thumbnail patterns
               - Study content formats that work
               - Note engagement strategies

            4. **Opportunity Identification:**
               - List specific content opportunities
               - Recommend differentiation strategies
               - Suggest unique positioning angles

            Focus on actionable insights for an AI automation agency looking to grow their content presence.
            """,
            expected_output="""
            Competitor analysis report with:
            - Top 5 competitors with detailed strategy analysis
            - Their best performing content with metrics
            - Content gaps and opportunities (minimum 10)
            - Recommended differentiation strategies
            - Specific content ideas that competitors haven't covered
            - Audience segments to target
            - Title and thumbnail recommendations based on competitor success
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

    def run(self, competitors: str = "") -> dict:
        """Run the competitor analysis crew"""
        result = self.crew().kickoff(inputs={"competitors": competitors})
        return result
