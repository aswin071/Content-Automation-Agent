from os import getenv
from pathlib import Path
from crewai import Agent, Crew, Process, Task
from content_ai_agent.tools.serp_api import SerpAPITool
from content_ai_agent.models import ContentResearchOutput
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)

LLM_MODEL = getenv('MODEL', 'anthropic/claude-3-5-haiku-20241022')


class ContentResearcherCrew:
    """Crew with only the Content Researcher agent"""

    def __init__(self):
        self.agent = self._create_agent()
        self.task = self._create_task()

    def _create_agent(self) -> Agent:
        return Agent(
            role="Content Research Analyst",
            goal="Gather comprehensive context and insights about {topic}",
            backstory="Skilled at synthesizing information from multiple sources into actionable insights",
            llm=LLM_MODEL,
            tools=[SerpAPITool()],
            verbose=True
        )

    def _create_task(self) -> Task:
        return Task(
            description="""
            Research the selected topic: {topic}
            Gather key facts, statistics, expert opinions, and audience pain points.
            Use Google Search & Trends tool to find real data.
            """,
            expected_output="Structured research doc with: key points, stats, quotes, hooks, audience insights",
            agent=self.agent,
            output_pydantic=ContentResearchOutput
        )

    def crew(self) -> Crew:
        return Crew(
            agents=[self.agent],
            tasks=[self.task],
            process=Process.sequential,
            verbose=True
        )

    def run(self, topic: str) -> dict:
        """Run the content researcher crew"""
        result = self.crew().kickoff(inputs={
            "topic": topic
        })
        return result
