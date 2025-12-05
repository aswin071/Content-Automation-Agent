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
            Create a HIGHLY ENGAGING, HUMAN-CONTEXTUAL script for {platform} about: {topic}

            Research context: {research_context}

            CRITICAL PLATFORM-SPECIFIC REQUIREMENTS:

            FOR YOUTUBE:
            - Hook: Must grab attention in first 5 seconds with a provocative question, bold statement, or surprising fact
            - Length: 8-12 minutes for long-form, 30-60 seconds for Shorts
            - Tone: Conversational yet authoritative, like talking to a friend who trusts your expertise
            - Structure: Hook → Problem → Solution → Proof/Examples → Action Steps → CTA
            - Pacing: Moderate with clear chapter breaks, maintain energy throughout

            FOR INSTAGRAM:
            - Hook: Visual + text combo that stops mid-scroll (first 2 seconds critical)
            - Length: 15-30 seconds for Reels, 60-90 seconds for in-depth
            - Tone: Casual, authentic, relatable - speak like a peer, not a lecturer
            - Structure: Pattern interrupt → Quick value → Emotional connection → Clear CTA
            - Pacing: Fast-paced, punchy, every second counts

            FOR TIKTOK:
            - Hook: Immediate value proposition or controversial take (0-3 seconds)
            - Length: 15-45 seconds (sweet spot: 21-34 seconds)
            - Tone: Energetic, raw, unfiltered - Gen Z authentic
            - Structure: Hook → Fast delivery of 3-5 key points → Loop back to hook
            - Pacing: Extremely fast, no fluff, trending sound integration

            FOR NEWSLETTER:
            - Hook: Subject line + opening paragraph that creates curiosity gap
            - Length: 300-800 words (3-5 minute read)
            - Tone: Professional yet personable, storytelling approach
            - Structure: Compelling intro → Story/Context → Insights/Data → Actionable takeaways → P.S. with personal touch
            - Pacing: Scannable with subheadings, bullet points, bold text

            FOR SKOOL COMMUNITY:
            - Hook: Question or challenge that sparks discussion
            - Length: 200-500 words + discussion prompts
            - Tone: Collaborative, community-focused, vulnerable and authentic
            - Structure: Personal experience → Insight → Community question → Resource/Value add
            - Pacing: Conversational, encourages comments and engagement

            HUMAN-CONTEXTUAL REQUIREMENTS (ALL PLATFORMS):
            1. Write like a REAL PERSON talking, not an AI or corporate robot
            2. Use contractions (don't, you're, we'll) and natural speech patterns
            3. Include relatable examples, personal anecdotes, or case studies
            4. Address audience pain points with empathy and understanding
            5. Use sensory language and vivid descriptions
            6. Vary sentence length for natural rhythm
            7. Include strategic pauses, emphasis words, and emotional beats
            8. End with a CTA that feels like a natural next step
            9. Use "you" language to make it personal and direct
            10. Include pattern interrupts to maintain attention
            """,
            expected_output="""
            COMPLETE, READY-TO-USE script with:
            - Powerful hook designed for the specific platform ({platform})
            - Human-written introduction that builds rapport
            - Main content with natural flow, storytelling, and emotional resonance
            - Key insights that provide genuine value
            - Emotional elements and relatable moments
            - Smooth transitions between ideas
            - Natural, compelling CTA
            - Memorable closing
            - Platform-specific guidelines (tone, pacing, length, visual style)
            - Detailed visual suggestions
            - Thumbnail ideas (for video platforms)
            - Formatting notes specific to {platform}
            """,
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
