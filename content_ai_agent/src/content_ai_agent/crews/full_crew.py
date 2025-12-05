from os import getenv
from pathlib import Path
from crewai import Agent, Crew, Process, Task
from content_ai_agent.tools.youtube_api import YouTubeTool
from content_ai_agent.tools.serp_api import SerpAPITool
from content_ai_agent.models import TopicFinderOutput, ContentResearchOutput, ScriptOutput
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)

LLM_MODEL = getenv('MODEL', 'anthropic/claude-3-5-haiku-20241022')


class FullContentCrew:
    """Full crew with all 3 agents running sequentially"""

    def __init__(self):
        self.topic_finder = self._create_topic_finder()
        self.content_researcher = self._create_content_researcher()
        self.script_writer = self._create_script_writer()

        self.find_topics_task = self._create_find_topics_task()
        self.research_task = self._create_research_task()
        self.script_task = self._create_script_task()

    def _create_topic_finder(self) -> Agent:
        return Agent(
            role="Trending Topic Specialist",
            goal="Find viral/trending topics in {niche} using YouTube and search data",
            backstory="Expert at identifying trending content opportunities before they peak",
            llm=LLM_MODEL,
            tools=[YouTubeTool(), SerpAPITool()],
            verbose=True
        )

    def _create_content_researcher(self) -> Agent:
        return Agent(
            role="Content Research Analyst",
            goal="Gather comprehensive context and insights about {topic}",
            backstory="Skilled at synthesizing information from multiple sources into actionable insights",
            llm=LLM_MODEL,
            tools=[SerpAPITool()],
            verbose=True
        )

    def _create_script_writer(self) -> Agent:
        return Agent(
            role="Social Media Script Writer",
            goal="Create engaging {platform} scripts that hook viewers in 3 seconds",
            backstory="Former viral content creator who understands platform-specific algorithms",
            llm=LLM_MODEL,
            tools=[],
            verbose=True
        )

    def _create_find_topics_task(self) -> Task:
        return Task(
            description="""
            If a specific topic is provided: "{topic}" - search YouTube for the best performing content about this exact topic.
            If no topic provided: Find 5 trending topics in {niche} that have viral potential.
            Use YouTube Trending Search tool to find real data.
            """,
            expected_output="List of 5 best content ideas with: title, why it works, key angles to cover",
            agent=self.topic_finder,
            output_pydantic=TopicFinderOutput
        )

    def _create_research_task(self) -> Task:
        return Task(
            description="""
            Research the selected topic: {topic}
            Gather key facts, statistics, expert opinions, and audience pain points.
            """,
            expected_output="Structured research doc with: key points, stats, quotes, hooks, audience insights",
            agent=self.content_researcher,
            output_pydantic=ContentResearchOutput
        )

    def _create_script_task(self) -> Task:
        return Task(
            description="""
            Create a {platform} script for: {topic}
            Include strong hook (first 3 sec), engaging body, clear CTA.
            """,
            expected_output="Ready-to-record script with: hook, main content, CTA, suggested visuals/B-roll",
            agent=self.script_writer,
            output_pydantic=ScriptOutput,
            output_file='script.json'
        )

    def crew(self) -> Crew:
        return Crew(
            agents=[self.topic_finder, self.content_researcher, self.script_writer],
            tasks=[self.find_topics_task, self.research_task, self.script_task],
            process=Process.sequential,
            verbose=True
        )

    def run(self, niche: str, topic: str = "", platform: str = "youtube") -> dict:
        """Run the full content crew"""
        result = self.crew().kickoff(inputs={
            "niche": niche,
            "topic": topic,
            "platform": platform
        })
        return result
