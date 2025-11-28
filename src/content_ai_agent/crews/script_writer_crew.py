from os import getenv
from pathlib import Path
from crewai import Agent, Crew, Process, Task
from content_ai_agent.models import ScriptOutput
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)

LLM_MODEL = getenv('MODEL', 'anthropic/claude-3-5-haiku-20241022')


class ScriptWriterCrew:
    """Crew with only the Script Writer agent"""

    def __init__(self):
        self.agent = self._create_agent()
        self.task = self._create_task()

    def _create_agent(self) -> Agent:
        return Agent(
            role="Social Media Script Writer",
            goal="Create engaging {platform} scripts that hook viewers in 3 seconds",
            backstory="Former viral content creator who understands platform-specific algorithms",
            llm=LLM_MODEL,
            tools=[],  # No tools needed - uses LLM directly
            verbose=True
        )

    def _create_task(self) -> Task:
        return Task(
            description="""
            Create a {platform} script for: {topic}

            Use the research context provided: {research_context}

            Include:
            - Strong hook (first 3 seconds)
            - Engaging body with key points
            - Clear CTA (call to action)
            - Visual suggestions for B-roll
            - Thumbnail ideas
            """,
            expected_output="Ready-to-record script with: hook, main content, CTA, suggested visuals/B-roll, thumbnail ideas",
            agent=self.agent,
            output_pydantic=ScriptOutput
        )

    def crew(self) -> Crew:
        return Crew(
            agents=[self.agent],
            tasks=[self.task],
            process=Process.sequential,
            verbose=True
        )

    def run(self, topic: str, platform: str = "youtube", research_context: str = "") -> dict:
        """Run the script writer crew"""
        result = self.crew().kickoff(inputs={
            "topic": topic,
            "platform": platform,
            "research_context": research_context
        })
        return result
