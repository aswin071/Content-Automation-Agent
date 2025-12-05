"""SEO Optimizer Crew - Optimizes content for search and discoverability"""
from os import getenv
from pathlib import Path
from crewai import Agent, Crew, Process, Task
from dotenv import load_dotenv

from content_ai_agent.tools.serp_api import SerpAPITool
from content_ai_agent.tools.google_trends import GoogleTrendsTool
from content_ai_agent.tools.hashtag_generator import HashtagGeneratorTool

# Load .env
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)

LLM_MODEL = getenv('MODEL', 'anthropic/claude-3-5-haiku-20241022')


class SEOOptimizerCrew:
    """Crew that optimizes content for SEO and discoverability"""

    def __init__(self):
        self.tools = [
            SerpAPITool(),
            GoogleTrendsTool(),
            HashtagGeneratorTool()
        ]
        self.agent = self._create_agent()
        self.task = self._create_task()

    def _create_agent(self) -> Agent:
        return Agent(
            role="AI Content SEO Specialist",
            goal="Optimize AI automation content for maximum search visibility and discoverability",
            backstory="""
            You are an SEO expert specializing in AI and technology content. With 8+ years of
            experience in search optimization, you've helped tech channels grow from 0 to millions
            of views through strategic SEO. You understand:
            - YouTube algorithm and search ranking factors
            - Google search optimization for video content
            - Keyword research and competition analysis
            - Hashtag strategy for social platforms
            - Title and description optimization
            - Thumbnail click-through rate optimization

            Your strategies are data-driven and focused on:
            - Finding low-competition, high-volume keywords
            - Optimizing for both search and suggested videos
            - Creating titles that rank AND get clicks
            - Building topical authority in the AI automation niche
            """,
            llm=LLM_MODEL,
            tools=self.tools,
            verbose=True
        )

    def _create_task(self) -> Task:
        return Task(
            description="""
            Create comprehensive SEO optimization for AI automation content about: {topic}

            1. **Keyword Research:**
               - Primary keyword with search volume
               - Secondary keywords (5-10)
               - Long-tail keywords (10-15)
               - Related search queries
               - Questions people ask

            2. **Title Optimization:**
               - 5 SEO-optimized title options
               - Include primary keyword naturally
               - Optimize for CTR (curiosity, numbers, emotion)
               - Keep under 60 characters

            3. **Description Optimization:**
               - SEO-optimized description template
               - Keyword placement strategy
               - Call-to-action placement
               - Link structure

            4. **Hashtag Strategy:**
               - Platform-specific hashtags (YouTube, Instagram, TikTok)
               - Mix of high-volume and niche hashtags
               - Trending hashtags in AI space

            5. **Competition Analysis:**
               - Top ranking content for target keywords
               - Gaps in existing content
               - Opportunities to outrank

            6. **Content Recommendations:**
               - Topics to build topical authority
               - Internal linking opportunities
               - Content clusters to create
            """,
            expected_output="""
            Complete SEO optimization package:
            - Primary keyword with search volume estimate
            - 10+ secondary and long-tail keywords
            - 5 optimized title options (ranked by potential)
            - SEO-optimized description template
            - 15-20 platform-specific hashtags
            - Competitor analysis with gaps identified
            - Content cluster recommendations
            - Technical SEO checklist
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

    def run(self, topic: str) -> dict:
        """Run the SEO optimizer crew"""
        result = self.crew().kickoff(inputs={"topic": topic})
        return result
