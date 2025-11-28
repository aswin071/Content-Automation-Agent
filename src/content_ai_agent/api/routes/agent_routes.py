import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from content_ai_agent.crews import (
    TopicFinderCrew,
    ContentResearcherCrew,
    ScriptWriterCrew,
    FullContentCrew
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


# ===== RESPONSE MODEL =====
class AgentResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: str = ""


# ===== HELPER FUNCTION =====
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


# ===== API ENDPOINTS =====

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
        raise HTTPException(status_code=500, detail=str(e))


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
        raise HTTPException(status_code=500, detail=str(e))


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
        raise HTTPException(status_code=500, detail=str(e))


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
        raise HTTPException(status_code=500, detail=str(e))
