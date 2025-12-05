"""Analytics API routes for AI Automation Agency"""
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from content_ai_agent.crews import (
    TrendAnalyzerCrew,
    CompetitorAnalysisCrew,
    TrendPredictionCrew,
    SEOOptimizerCrew
)

router = APIRouter()


# ===== REQUEST MODELS =====
class CompetitorRequest(BaseModel):
    competitors: str = ""  # Comma-separated competitor names/channels


class SEORequest(BaseModel):
    topic: str


# ===== RESPONSE MODEL =====
class AnalyticsResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: str = ""


# ===== HELPER FUNCTIONS =====
def parse_result(result) -> dict:
    """Parse CrewAI result to dict"""
    try:
        if hasattr(result, 'pydantic') and result.pydantic:
            return result.pydantic.model_dump()
        if hasattr(result, 'raw') and result.raw:
            try:
                return json.loads(result.raw)
            except json.JSONDecodeError:
                return {"raw": str(result.raw)}
        return {"raw": str(result)}
    except Exception:
        return {"raw": str(result)}


def handle_error(error: Exception) -> HTTPException:
    """Handle errors from CrewAI calls"""
    error_str = str(error)

    if "authentication_error" in error_str or "401" in error_str:
        return HTTPException(
            status_code=503,
            detail="LLM service authentication failed. Check API key configuration."
        )

    return HTTPException(
        status_code=500,
        detail=f"An error occurred: {str(error)[:200]}"
    )


# ===== API ENDPOINTS =====

@router.get("/trends", response_model=AnalyticsResponse)
def analyze_trends():
    """
    Analyze current AI automation trends.
    Uses Google Trends, Reddit, Twitter, and AI news sources.
    Returns trending topics, rising keywords, and content opportunities.
    """
    try:
        crew = TrendAnalyzerCrew()
        result = crew.run()

        return AnalyticsResponse(
            success=True,
            data=parse_result(result),
            message="Trend analysis completed successfully"
        )
    except Exception as e:
        raise handle_error(e)


@router.post("/competitors", response_model=AnalyticsResponse)
def analyze_competitors(request: CompetitorRequest):
    """
    Analyze competitors in the AI automation space.
    Returns competitor strategies, content gaps, and opportunities.
    """
    try:
        crew = CompetitorAnalysisCrew()
        result = crew.run(competitors=request.competitors)

        return AnalyticsResponse(
            success=True,
            data=parse_result(result),
            message="Competitor analysis completed successfully"
        )
    except Exception as e:
        raise handle_error(e)


@router.get("/predictions", response_model=AnalyticsResponse)
def predict_trends():
    """
    Predict future AI automation trends.
    Returns trend predictions for 1-12 months with confidence scores.
    """
    try:
        crew = TrendPredictionCrew()
        result = crew.run()

        return AnalyticsResponse(
            success=True,
            data=parse_result(result),
            message="Trend predictions generated successfully"
        )
    except Exception as e:
        raise handle_error(e)


@router.post("/seo", response_model=AnalyticsResponse)
def optimize_seo(request: SEORequest):
    """
    Generate SEO optimization for a topic.
    Returns keywords, titles, descriptions, and hashtags.
    """
    try:
        crew = SEOOptimizerCrew()
        result = crew.run(topic=request.topic)

        return AnalyticsResponse(
            success=True,
            data=parse_result(result),
            message="SEO optimization completed successfully"
        )
    except Exception as e:
        raise handle_error(e)


@router.get("/dashboard", response_model=AnalyticsResponse)
def get_dashboard_data():
    """
    Get quick dashboard overview.
    Returns summary of trends, top opportunities, and recommendations.
    """
    try:
        # Quick summary without running full crews
        dashboard_data = {
            "trending_topics": [
                "AI Agents",
                "ChatGPT Automation",
                "No-Code AI Tools",
                "Workflow Automation",
                "AI for Business"
            ],
            "content_opportunities": [
                "AI Agent tutorials for beginners",
                "ChatGPT API automation guides",
                "AI tool comparison videos",
                "Business automation case studies",
                "AI news weekly roundups"
            ],
            "recommended_actions": [
                "Create content about AI agents (rising trend)",
                "Cover latest OpenAI/Anthropic updates",
                "Target 'AI automation for beginners' keyword",
                "Analyze top competitor's recent videos",
                "Post during peak hours: Tue-Thu 9-11 AM EST"
            ],
            "quick_stats": {
                "ai_automation_trend": "📈 Rising (+45% YoY)",
                "competition_level": "Medium-High",
                "best_platforms": ["YouTube", "LinkedIn", "Twitter"],
                "top_hashtags": ["#AIAutomation", "#ChatGPT", "#AIAgents", "#NoCode"]
            }
        }

        return AnalyticsResponse(
            success=True,
            data=dashboard_data,
            message="Dashboard data retrieved successfully"
        )
    except Exception as e:
        raise handle_error(e)
