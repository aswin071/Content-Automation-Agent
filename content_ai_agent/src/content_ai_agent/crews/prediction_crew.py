"""Prediction Crew - Predicts future AI automation trends"""
from os import getenv
from pathlib import Path
from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv

from content_ai_agent.tools.google_trends import GoogleTrendsTool
from content_ai_agent.tools.ai_news_aggregator import AINewsAggregatorTool
from content_ai_agent.tools.twitter_api import TwitterTool

# Load .env
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)

LLM_MODEL = getenv('MODEL', 'anthropic/claude-3-5-haiku-20241022')


class TrendPredictionCrew:
    """Crew that predicts future AI automation trends"""

    def __init__(self):
        self.tools = [
            GoogleTrendsTool(),
            AINewsAggregatorTool(),
            TwitterTool()
        ]
        self.agent = self._create_agent()
        self.task = self._create_task()

    def _create_agent(self) -> Agent:
        return Agent(
            role="AI Automation Futurist & Trend Predictor",
            goal="Predict upcoming trends in AI automation and identify future content opportunities",
            backstory="""
            You are an AI industry futurist with a proven track record of predicting technology trends.
            You've accurately forecasted the rise of ChatGPT, AI agents, and no-code automation tools
            before they went mainstream. Your predictions are based on:
            - Pattern analysis from historical data
            - Early signals from research papers and developer communities
            - Understanding of technology adoption curves
            - Industry insider knowledge and connections

            You help content creators stay 3-6 months ahead of trends, creating content that will
            become highly relevant when the trend peaks. Your predictions focus on:
            - What AI capabilities will become mainstream
            - Which industries will adopt AI automation next
            - What pain points will emerge
            - What content will be in demand
            """,
            llm=LLM_MODEL,
            tools=self.tools,
            verbose=True
        )

    def _create_task(self) -> Task:
        return Task(
            description="""
            Create a comprehensive AI automation trend prediction report:

            1. **Current Trend Analysis:**
               - Analyze current Google Trends data for AI automation
               - Review recent AI announcements and their implications
               - Study early adopter discussions on Twitter and tech forums

            2. **Near-Term Predictions (1-3 months):**
               - What AI tools/features will go mainstream
               - Which topics will trend on social media
               - What content will be in high demand

            3. **Medium-Term Predictions (3-6 months):**
               - Industry shifts and new AI capabilities
               - Emerging use cases for AI automation
               - New audience segments entering the market

            4. **Long-Term Predictions (6-12 months):**
               - Major industry transformations
               - New AI automation categories
               - Shifts in content consumption patterns

            5. **Content Strategy Recommendations:**
               - Topics to create content about NOW (for future traffic)
               - Keywords to target before they peak
               - Content formats that will grow in demand

            Base predictions on data patterns, industry signals, and technology adoption curves.
            """,
            expected_output="""
            Trend prediction report with:
            - Top 10 predicted trends with confidence scores
            - Timeline for each prediction (when it will peak)
            - Early content opportunities (create now, benefit later)
            - Keywords to target before competition increases
            - Industries/niches that will adopt AI automation next
            - Predicted pain points and questions from future audience
            - Content calendar recommendations for next 3 months
            - Risk assessment for each prediction
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
        """Run the trend prediction crew"""
        result = self.crew().kickoff()
        return result
