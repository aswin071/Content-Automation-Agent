import platform
from re import S
from unittest import result
from xxlimited import Str
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from content_ai_agent.crew import ContentAiAgent
from dotenv import load_dotenv

router = APIRouter()

class TopicRequest(BaseModel):
    niche : str
    topic : str = ""
    platform : str = "youtube"
@router.post("/topics")
def find_topics(request : TopicRequest):
    crew_ai = ContentAiAgent().crew()
    result = crew_ai.kickoff(inputs={
        "niche" : request.niche,
        "topic" : request.topic,
        "platform" : request.platform
    })
    return ({"result" : result})

