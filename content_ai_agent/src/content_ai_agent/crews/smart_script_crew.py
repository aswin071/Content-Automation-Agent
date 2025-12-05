"""
Smart Script Crew - Generates scripts using REAL data

Flow:
1. DataCollector fetches real data (no LLM)
2. Analyzer agent analyzes the real data (LLM + data)
3. Writer agent creates script using analysis (LLM + analysis)
"""
from os import getenv
from pathlib import Path
from crewai import Agent, Crew, Process, Task
from content_ai_agent.models import ScriptOutput
from content_ai_agent.services.data_collector import DataCollector, CollectedData
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)

LLM_MODEL = getenv('MODEL', 'anthropic/claude-3-5-haiku-20241022')


class SmartScriptCrew:
    """
    Smart Script Generator with REAL data.

    This is what makes it better than raw LLM:
    1. First, we collect REAL data (YouTube videos, trends, SERP)
    2. Then, analyzer finds gaps and opportunities from real data
    3. Finally, writer creates script informed by real analysis
    """

    def __init__(self):
        self.data_collector = DataCollector()
        self.analyzer = self._create_analyzer()
        self.writer = self._create_writer()

    def _create_analyzer(self) -> Agent:
        return Agent(
            role="Content Gap Analyzer",
            goal="Analyze real competitor data to find content gaps and opportunities",
            backstory="""
            You are a data analyst who looks at REAL YouTube videos, REAL trends,
            and REAL search data to find opportunities. You don't make things up.
            You analyze what's actually there and find what's missing.

            Your job:
            - Look at the actual top videos (titles, view counts)
            - Identify what angles they cover
            - Find gaps they DON'T cover
            - Spot opportunities based on real trends
            """,
            llm=LLM_MODEL,
            tools=[],  # No tools - receives pre-collected data
            verbose=True
        )

    def _create_writer(self) -> Agent:
        return Agent(
            role="Script Writer",
            goal="Write scripts that use REAL research insights",
            backstory="""
            You write scripts that are INFORMED by real data. You don't write
            generic content. Every script you write:

            - References specific competitor videos by name
            - Addresses gaps found in the analysis
            - Uses real trending keywords
            - Answers real questions people are asking

            Your scripts are impossible to write without the research.
            """,
            llm=LLM_MODEL,
            tools=[],
            verbose=True
        )

    def _create_analysis_task(self, collected_data: CollectedData) -> Task:
        """Create analysis task with real data injected"""
        return Task(
            description=f"""
Analyze this REAL data and find content opportunities:

{collected_data.to_prompt_context()}

YOUR TASK:
1. Look at the top YouTube videos listed above
   - What topics do they cover?
   - What view counts do they have?
   - What patterns do you see in titles?

2. Identify GAPS (things NOT covered)
   - What questions from "People Also Ask" aren't answered?
   - What angles are missing from top videos?
   - What could differentiate new content?

3. Check the trends
   - Is the topic rising or declining?
   - What related queries are growing?

OUTPUT a structured analysis with:
- Top 3 competitor videos and what they cover
- Top 3 content gaps (specific, not generic)
- Recommended angle for the script
- Key points to include (based on real data)
            """,
            expected_output="""
Structured analysis with:
- Competitor breakdown (from real data)
- Specific content gaps identified
- Recommended unique angle
- Key talking points based on trends and questions
            """,
            agent=self.analyzer
        )

    def _create_writing_task(self, platform: str, collected_data: CollectedData) -> Task:
        """Create writing task that uses analysis with platform-specific requirements"""

        # Extract real metrics for hooks
        top_video = collected_data.youtube_videos[0] if collected_data.youtube_videos else None
        trend_info = collected_data.trends[0] if collected_data.trends else None

        real_metrics_context = ""
        if top_video:
            real_metrics_context += f"""
REAL METRICS TO USE IN HOOK:
- Top video "{top_video.title}" has {top_video.view_count:,} views
- Channel: {top_video.channel_name}
"""
        if trend_info:
            real_metrics_context += f"""
- Google Trends interest: {trend_info.current_interest}/100 ({trend_info.trend_direction})
- Rising queries: {', '.join(trend_info.rising_queries[:3]) if trend_info.rising_queries else 'None'}
"""

        platform_specs = {
            "youtube": f"""
FOR YOUTUBE (Long-form):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DURATION: 12-20 minutes (This is MANDATORY - structure content accordingly)

HOOK (First 5-10 seconds) - MUST USE REAL METRICS:
Your hook MUST include ONE of these REAL numbers from research:
{real_metrics_context}

Example hooks using real data:
- "A video about [topic] just hit {top_video.view_count:,} views... but they missed something crucial"
- "Google Trends shows [topic] at {trend_info.current_interest if trend_info else 'X'}/100 interest right now - here's why that matters"
- "I analyzed the top 10 videos on [topic] - here's what NONE of them told you"

STRUCTURE (12-20 min):
0:00-0:30 - Hook with REAL metric + Promise
0:30-2:00 - Introduction + Why this matters NOW (use trend data)
2:00-6:00 - Problem deep-dive (reference what competitors miss)
6:00-12:00 - Solution with step-by-step breakdown
12:00-16:00 - Real examples/case studies
16:00-18:00 - Common mistakes to avoid
18:00-20:00 - Action steps + CTA

STYLE: Conversational authority, like explaining to a smart friend
PACING: Change energy every 2-3 minutes, use pattern interrupts
            """,

            "instagram": f"""
FOR INSTAGRAM REELS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DURATION: 30-60 seconds (This is MANDATORY - be concise)

HOOK (First 2 seconds) - MUST USE REAL METRIC:
Your hook MUST include ONE real number from research:
{real_metrics_context}

Example hooks:
- "{top_video.view_count:,} people watched this but missed the key point..."
- "Google says interest in [topic] is at {trend_info.current_interest if trend_info else 'X'}/100..."
- "I found something in the top videos that nobody's talking about..."

STRUCTURE (30-60 sec):
0-2 sec: Pattern interrupt with REAL stat
2-10 sec: The problem/opportunity
10-40 sec: 3 rapid-fire insights
40-60 sec: CTA with urgency

STYLE: Fast, punchy, raw energy
TONE: Like texting your friend something exciting
TEXT OVERLAYS: Use bold text for key stats
            """,

            "tiktok": f"""
FOR TIKTOK:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DURATION: 21-45 seconds (This is MANDATORY)

HOOK (First 2 seconds) - MUST USE REAL METRIC:
{real_metrics_context}

Example hooks:
- "POV: You just found out [topic] videos get {top_video.view_count:,} views"
- "Wait... why is nobody talking about this?"
- "I analyzed every viral [topic] video and found THIS"

STRUCTURE (21-45 sec):
0-2 sec: Shocking stat or question
2-5 sec: "Here's what I found..."
5-35 sec: 3-5 rapid points (3-5 sec each)
35-45 sec: Loop back to hook or CTA

STYLE: Unfiltered, authentic, slightly chaotic energy
TREND: Consider trending sounds/formats
            """,

            "newsletter": f"""
FOR NEWSLETTER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LENGTH: 500-800 words (3-5 minute read)

SUBJECT LINE - MUST USE REAL METRIC:
{real_metrics_context}

Example subject lines:
- "I analyzed {len(collected_data.youtube_videos)} videos on [topic] - here's what I found"
- "[Topic] is at {trend_info.current_interest if trend_info else 'X'}/100 on Google Trends"
- "The gap nobody's filling in [topic] content"

STRUCTURE:
- Subject: Curiosity + real number
- Opening: Personal hook with data point
- Section 1: The insight from research
- Section 2: Why it matters (trend context)
- Section 3: Actionable takeaways
- Close: Personal sign-off + CTA

STYLE: Professional but personal, data-informed storytelling
            """
        }

        spec = platform_specs.get(platform.lower(), platform_specs["youtube"])

        return Task(
            description=f"""
Using the analysis provided, write a {platform} script.

{spec}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL REQUIREMENTS (Non-negotiable):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. HOOK MUST HAVE REAL NUMBER
   - Use actual view count, trend score, or specific stat from research
   - NO generic hooks like "Did you know..." without real data

2. REFERENCE COMPETITORS
   - Mention what top videos cover and what YOU cover differently
   - Be specific: "Videos like [title] focus on X, but miss Y"

3. ADDRESS REAL QUESTIONS
   - Use at least one "People Also Ask" question from research
   - Answer it directly in your content

4. USE TREND DATA
   - Mention if topic is rising/declining
   - Reference rising queries if relevant

5. WRITE LIKE A HUMAN
   - Contractions (don't, you're, we'll)
   - Conversational tone
   - Personality and opinions
   - NOT robotic or corporate

The script should be IMPOSSIBLE to write without the research data.
            """,
            expected_output=f"""
Complete {platform} script with:
- Hook containing REAL metric from research (view count, trend score, etc.)
- {"12-20 minute" if platform == "youtube" else "30-60 second" if platform == "instagram" else "appropriate"} duration structure
- Main content addressing gaps found in competitor analysis
- Specific differentiation from competitor content
- Real stats/trends woven throughout
- Natural, human writing style
- Platform-appropriate formatting and pacing
            """,
            agent=self.writer,
            output_pydantic=ScriptOutput
        )

    def run(self, topic: str, platform: str = "youtube") -> dict:
        """
        Run the smart script pipeline:
        1. Collect real data (no LLM)
        2. Analyze with LLM
        3. Write with LLM using real metrics
        """
        # STEP 1: Collect real data (NO LLM)
        collected_data = self.data_collector.collect_all(topic, platform)

        # Check if we have any real data
        if not collected_data.has_data():
            return {
                "success": False,
                "error": "Could not collect real data",
                "errors": collected_data.errors,
                "message": "API data collection failed. Check your API keys."
            }

        # STEP 2 & 3: Run crew with real data
        analysis_task = self._create_analysis_task(collected_data)
        writing_task = self._create_writing_task(platform, collected_data)  # Pass real metrics

        # Writing task depends on analysis
        writing_task.context = [analysis_task]

        crew = Crew(
            agents=[self.analyzer, self.writer],
            tasks=[analysis_task, writing_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff(inputs={
            "topic": topic,
            "platform": platform
        })

        return {
            "success": True,
            "collected_data": {
                "youtube_videos": len(collected_data.youtube_videos),
                "trends": len(collected_data.trends),
                "serp_questions": len(collected_data.serp_questions),
                "errors": collected_data.errors,
                "raw_data": collected_data.to_prompt_context()[:500] + "..."  # Preview of data
            },
            "result": result
        }
