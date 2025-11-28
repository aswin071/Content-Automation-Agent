from pydantic import BaseModel, Field
from typing import List, Optional


# ===== TOPIC FINDER OUTPUT =====
class TrendingTopic(BaseModel):
    title: str = Field(description="Content title/idea")
    why_it_works: str = Field(description="Why this topic has viral potential")
    key_angles: List[str] = Field(description="Different angles to cover this topic")
    estimated_views: Optional[str] = Field(default=None, description="Estimated view potential")
    competition_level: Optional[str] = Field(default=None, description="Low/Medium/High")


class TopicFinderOutput(BaseModel):
    niche: str = Field(description="The niche searched")
    topics: List[TrendingTopic] = Field(description="List of trending topics found")
    search_date: Optional[str] = Field(default=None, description="When the search was performed")


# ===== CONTENT RESEARCHER OUTPUT =====
class ResearchInsight(BaseModel):
    key_points: List[str] = Field(description="Main points to cover")
    statistics: List[str] = Field(description="Relevant stats and data")
    quotes: List[str] = Field(default=[], description="Expert quotes or references")
    hooks: List[str] = Field(description="Potential hook ideas")
    audience_pain_points: List[str] = Field(description="What the audience struggles with")


class ContentResearchOutput(BaseModel):
    topic: str = Field(description="The topic researched")
    insights: ResearchInsight = Field(description="Research findings")
    sources: List[str] = Field(default=[], description="Sources used")


# ===== SCRIPT WRITER OUTPUT =====
class ScriptSection(BaseModel):
    hook: str = Field(description="Opening hook (first 3 seconds)")
    main_content: List[str] = Field(description="Main content points/sections")
    cta: str = Field(description="Call to action")


class ScriptOutput(BaseModel):
    topic: str = Field(description="Script topic")
    platform: str = Field(description="Target platform (YouTube, TikTok, etc.)")
    duration: Optional[str] = Field(default=None, description="Estimated duration")
    script: ScriptSection = Field(description="The actual script")
    visual_suggestions: List[str] = Field(default=[], description="B-roll and visual ideas")
    thumbnail_ideas: List[str] = Field(default=[], description="Thumbnail suggestions")
