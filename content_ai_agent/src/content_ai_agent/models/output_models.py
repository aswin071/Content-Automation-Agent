from pydantic import BaseModel, Field
from typing import List, Optional


# ===== TOPIC FINDER OUTPUT =====
class VideoAnalytics(BaseModel):
    """Analytics data for a trending video"""
    views: str = Field(description="Total view count (e.g., '1.2M views')")
    likes: str = Field(description="Total like count (e.g., '45K likes')")
    comments: str = Field(description="Total comment count (e.g., '2.3K comments')")
    shares: Optional[str] = Field(default=None, description="Share count if available")
    engagement_rate: Optional[str] = Field(default=None, description="Calculated engagement rate percentage")
    published_date: Optional[str] = Field(default=None, description="When the video was published")


class TrendingTopic(BaseModel):
    title: str = Field(description="Content title/idea")
    platform: str = Field(description="Platform where this content is trending (YouTube, TikTok, Instagram, etc.)")
    url: Optional[str] = Field(default=None, description="URL to the trending video/content")
    creator: Optional[str] = Field(default=None, description="Content creator/channel name")
    analytics: Optional[VideoAnalytics] = Field(default=None, description="Detailed analytics (views, likes, shares)")
    why_it_works: str = Field(description="Why this topic has viral potential")
    key_angles: List[str] = Field(description="Different angles to cover this topic")
    estimated_views: Optional[str] = Field(default=None, description="Estimated view potential for new content")
    competition_level: Optional[str] = Field(default=None, description="Competition level: Low/Medium/High")


class TopicFinderOutput(BaseModel):
    niche: str = Field(description="The niche searched")
    topics: List[TrendingTopic] = Field(description="List of trending topics with analytics data")
    search_date: Optional[str] = Field(default=None, description="When the search was performed")
    total_topics_analyzed: Optional[int] = Field(default=None, description="Total number of topics analyzed")


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
class PlatformGuidelines(BaseModel):
    """Platform-specific formatting and optimization guidelines"""
    optimal_length: str = Field(description="Recommended content length for the platform")
    tone: str = Field(description="Recommended tone (conversational, professional, casual, energetic)")
    pacing: str = Field(description="Content pacing (fast-paced, moderate, slow and detailed)")
    visual_style: str = Field(description="Recommended visual approach for the platform")
    key_optimization_tips: List[str] = Field(description="Platform-specific tips for maximum engagement")


class ScriptSection(BaseModel):
    hook: str = Field(description="Powerful, attention-grabbing opening hook (first 3-5 seconds) designed to stop scrolling and captivate the audience immediately")
    introduction: str = Field(description="Brief, engaging introduction that sets context and builds curiosity")
    main_content: List[str] = Field(description="Core content broken into digestible, engaging sections with natural flow and storytelling elements")
    key_insights: List[str] = Field(description="Main takeaways and valuable insights the audience will gain")
    emotional_elements: Optional[List[str]] = Field(default=None, description="Emotional triggers and relatable moments to connect with audience")
    transitions: Optional[List[str]] = Field(default=None, description="Smooth transitions between sections to maintain flow")
    cta: str = Field(description="Compelling call-to-action that feels natural and provides clear next steps")
    closing: str = Field(description="Memorable closing statement that reinforces value and leaves lasting impact")


class ScriptOutput(BaseModel):
    topic: str = Field(description="Script topic")
    platform: str = Field(description="Target platform (YouTube, Instagram, TikTok, Newsletter, Skool)")
    duration: Optional[str] = Field(default=None, description="Estimated duration/length")
    target_audience: str = Field(description="Who this content is for and their pain points")
    content_goal: str = Field(description="Primary objective (educate, inspire, entertain, convert)")

    script: ScriptSection = Field(description="Complete, human-contextual script optimized for the platform")
    platform_guidelines: PlatformGuidelines = Field(description="Platform-specific optimization guidelines")

    visual_suggestions: List[str] = Field(default=[], description="Detailed visual/B-roll suggestions that enhance storytelling")
    thumbnail_ideas: List[str] = Field(default=[], description="Eye-catching thumbnail concepts (for video platforms)")
    formatting_notes: Optional[List[str]] = Field(default=None, description="Platform-specific formatting requirements")


# ===== SOCIAL MEDIA OPTIMIZER OUTPUT =====
class SocialMediaOutput(BaseModel):
    caption: str = Field(description="Complete social media caption with hook, content summary, and CTA")
    hashtags: List[str] = Field(description="8-15 highly relevant and trending hashtags for the niche and platform")
    visual_description: str = Field(description="Detailed description of recommended visuals (images/videos)")
    post_type: str = Field(description="Specific post type (YouTube Video, YouTube Shorts, Instagram Reel, TikTok, Carousel, Story, Tweet, etc.)")
    best_posting_time: str = Field(description="Optimal time to post based on platform and audience analytics (e.g., 'Tuesday-Thursday, 9-11 AM EST')")
    estimated_engagement_rate: str = Field(description="Predicted engagement rate with reasoning (e.g., '4.5-6.2% based on niche trends and content quality')")


# ===== COMPLETE CONTENT OUTPUT (combines Script + Social Media) =====
class CompleteContentOutput(BaseModel):
    topic: str = Field(description="Content topic")
    platform: str = Field(description="Target platform")
    duration: Optional[str] = Field(default=None, description="Estimated duration")

    # Script Details
    script: ScriptSection = Field(description="The actual script with hook, content, and CTA")
    visual_suggestions: List[str] = Field(default=[], description="B-roll and visual ideas")
    thumbnail_ideas: List[str] = Field(default=[], description="Thumbnail suggestions")

    # Social Media Optimization
    caption: str = Field(description="Complete social media caption")
    hashtags: List[str] = Field(description="8-15 highly relevant hashtags")
    visual_description: str = Field(description="Detailed visual recommendations")
    post_type: str = Field(description="Specific post format")
    best_posting_time: str = Field(description="Optimal posting time with reasoning")
    estimated_engagement_rate: str = Field(description="Predicted engagement rate with analysis")
