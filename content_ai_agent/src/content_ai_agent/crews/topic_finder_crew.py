from os import getenv
from pathlib import Path
from crewai import Agent, Crew, Process, Task
from content_ai_agent.tools.youtube_api import YouTubeTool
from content_ai_agent.tools.serp_api import SerpAPITool
from content_ai_agent.models import TopicFinderOutput
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)

LLM_MODEL = getenv('MODEL', 'anthropic/claude-3-5-haiku-20241022')


class TopicFinderCrew:
    """Crew with only the Topic Finder agent"""

    def __init__(self):
        self.agent = self._create_agent()
        self.task = self._create_task()

    def _create_agent(self) -> Agent:
        return Agent(
            role="Trending Topic Specialist",
            goal="Find viral/trending topics in {niche} using YouTube and search data",
            backstory="Expert at identifying trending content opportunities before they peak",
            llm=LLM_MODEL,
            tools=[YouTubeTool(), SerpAPITool()],
            verbose=True
        )

    def _create_task(self) -> Task:
        return Task(
            description="""
            If a specific topic is provided: "{topic}" - search YouTube for the best performing content about this exact topic.
            If no topic provided: Find 5 trending topics in {niche} that have viral potential.
            Use YouTube Trending Search tool to find real data.
            """,
            expected_output="List of 5 best content ideas with: title, why it works, key angles to cover",
            agent=self.agent,
            output_pydantic=TopicFinderOutput
        )

    def crew(self) -> Crew:
        return Crew(
            agents=[self.agent],
            tasks=[self.task],
            process=Process.sequential,
            verbose=True
        )

    def run(self, niche: str, topic: str = "") -> dict:
        """Run the topic finder crew"""
        result = self.crew().kickoff(inputs={
            "niche": niche,
            "topic": topic
        })
        return result
