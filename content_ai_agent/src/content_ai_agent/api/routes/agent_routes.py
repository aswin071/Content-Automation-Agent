import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from content_ai_agent.crews import (
    TopicFinderCrew,
    ContentResearcherCrew,
    ScriptWriterCrew,
    FullContentCrew,
    SmartScriptCrew
)

router = APIRouter()


# ===== REQUEST MODELS =====
class TopicRequest(BaseModel):
    niche: str
    topic: str = ""


class ResearchRequest(BaseModel):
    topic: str


class ScriptRequest(BaseModel):
    topic: str
    platform: str = "youtube"
    research_context: str = ""


class FullGenerateRequest(BaseModel):
    niche: str
    topic: str = ""
    platform: str = "youtube"


class SmartScriptRequest(BaseModel):
    topic: str
    platform: str = "youtube"


# ===== RESPONSE MODEL =====
class AgentResponse(BaseModel):
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
            return json.loads(result.raw)
        return {"raw": str(result)}
    except json.JSONDecodeError:
        return {"raw": str(result.raw) if hasattr(result, 'raw') else str(result)}


def validate_environment() -> dict:
    """Validate that required environment variables are set"""
    missing = []
    env_vars = {
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "YOUTUBE_API_KEY": os.getenv("YOUTUBE_API_KEY"),
        "SERP_API_KEY": os.getenv("SERP_API_KEY"),
    }
    
    for key, value in env_vars.items():
        if not value:
            missing.append(key)
    
    return {
        "valid": len(missing) == 0,
        "missing": missing,
        "present": [k for k, v in env_vars.items() if v]
    }


def handle_crew_error(error: Exception) -> HTTPException:
    """Handle errors from CrewAI/LLM calls with better error messages"""
    error_str = str(error)
    
    # Check for authentication errors
    if "authentication_error" in error_str or "invalid x-api-key" in error_str or "401" in error_str:
        return HTTPException(
            status_code=503,
            detail="LLM service authentication failed. Please check ANTHROPIC_API_KEY configuration."
        )
    
    # Check for missing API key
    if "ANTHROPIC_API_KEY is required" in error_str or "API key" in error_str.lower():
        return HTTPException(
            status_code=503,
            detail="LLM API key not configured. Please set ANTHROPIC_API_KEY environment variable."
        )
    
    # Generic error - don't expose internal details
    return HTTPException(
        status_code=500,
        detail="An error occurred while processing your request. Please check the service configuration."
    )


# ===== API ENDPOINTS =====

@router.get("/health/detailed")
def detailed_health_check():
    """
    Detailed health check that validates environment variables.
    Useful for debugging deployment issues.
    """
    env_status = validate_environment()
    return {
        "status": "ok" if env_status["valid"] else "degraded",
        "environment": env_status,
        "model": os.getenv("MODEL", "anthropic/claude-3-5-haiku-20241022")
    }


@router.post("/topics", response_model=AgentResponse)
def find_topics(request: TopicRequest):
    """
    Find trending topics in a niche.
    Runs ONLY the Topic Finder agent.
    """
    try:
        crew = TopicFinderCrew()
        result = crew.run(niche=request.niche, topic=request.topic)

        return AgentResponse(
            success=True,
            data=parse_result(result),
            message="Topics found successfully"
        )
    except Exception as e:
        raise handle_crew_error(e)


@router.post("/research", response_model=AgentResponse)
def research_content(request: ResearchRequest):
    """
    Research a specific topic.
    Runs ONLY the Content Researcher agent.
    """
    try:
        crew = ContentResearcherCrew()
        result = crew.run(topic=request.topic)

        return AgentResponse(
            success=True,
            data=parse_result(result),
            message="Research completed successfully"
        )
    except Exception as e:
        raise handle_crew_error(e)


@router.post("/script", response_model=AgentResponse)
def write_script(request: ScriptRequest):
    """
    Generate a script for a topic.
    Runs ONLY the Script Writer agent.
    """
    try:
        crew = ScriptWriterCrew()
        result = crew.run(
            topic=request.topic,
            platform=request.platform,
            research_context=request.research_context
        )

        return AgentResponse(
            success=True,
            data=parse_result(result),
            message="Script generated successfully"
        )
    except Exception as e:
        raise handle_crew_error(e)


@router.post("/generate", response_model=AgentResponse)
def generate_full_content(request: FullGenerateRequest):
    """
    Generate complete content: topics → research → script.
    Runs ALL 3 agents sequentially.
    """
    try:
        crew = FullContentCrew()
        result = crew.run(
            niche=request.niche,
            topic=request.topic,
            platform=request.platform
        )

        # Parse all task outputs
        data = {}
        if hasattr(result, 'tasks_output'):
            for task in result.tasks_output:
                task_name = task.name if hasattr(task, 'name') else "unknown"
                data[task_name] = parse_result(task)

        # Add final result
        data["final"] = parse_result(result)

        return AgentResponse(
            success=True,
            data=data,
            message="Full content generated successfully"
        )
    except Exception as e:
        raise handle_crew_error(e)


@router.post("/smart-script", response_model=AgentResponse)
def generate_smart_script(request: SmartScriptRequest):
    """
    Generate a script using REAL data from multiple sources.

    This is the RECOMMENDED endpoint for script generation.

    Flow:
    1. Collects REAL data from YouTube API, Google Trends, SERP API (no LLM)
    2. Analyzer agent finds gaps and opportunities from real data
    3. Writer agent creates script informed by real analysis

    Response includes:
    - collected_data: Stats on what real data was fetched
    - analysis: Gap analysis from real competitor data
    - script: Final script informed by real research
    """
    try:
        crew = SmartScriptCrew()
        result = crew.run(
            topic=request.topic,
            platform=request.platform
        )

        # Handle case where data collection failed
        if isinstance(result, dict) and not result.get("success", True):
            return AgentResponse(
                success=False,
                data=result,
                message=result.get("message", "Data collection failed")
            )

        # Parse successful result
        data = {
            "collected_data": result.get("collected_data", {}),
        }

        crew_result = result.get("result")
        if crew_result and hasattr(crew_result, 'tasks_output'):
            for i, task in enumerate(crew_result.tasks_output):
                if i == 0:
                    data["analysis"] = parse_result(task)
                else:
                    data["script"] = parse_result(task)

        # Add final result if script not parsed
        if not data.get("script") and crew_result:
            data["script"] = parse_result(crew_result)

        return AgentResponse(
            success=True,
            data=data,
            message="Smart script generated with real data"
        )
    except Exception as e:
        raise handle_crew_error(e)
