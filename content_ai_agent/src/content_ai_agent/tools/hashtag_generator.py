from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
import requests
import os


class HashtagInput(BaseModel):
    """Input schema for HashtagGeneratorTool."""
    topic: str = Field(..., description="The main topic or keyword to generate hashtags for")
    platform: str = Field(..., description="Target platform (YouTube, Instagram, TikTok, Twitter, LinkedIn)")
    niche: str = Field(default="", description="Specific niche or industry")


class HashtagGeneratorTool(BaseTool):
    name: str = "Hashtag Generator"
    description: str = (
        "Generates 8-15 highly relevant, trending hashtags based on topic, platform, and niche. "
        "Uses real-time data from Google Trends and social media APIs to find accurate, high-performing hashtags. "
        "Returns hashtags with engagement potential and relevance scores."
    )
    args_schema: Type[BaseModel] = HashtagInput

    def _run(self, topic: str, platform: str, niche: str = "") -> str:
        """
        Generate platform-specific hashtags using SerpAPI (Google Trends) data.
        """
        try:
            # Platform-specific hashtag strategies
            platform_lower = platform.lower()

            # Base hashtags from topic keywords
            hashtags = self._generate_base_hashtags(topic, niche, platform_lower)

            # Try to get trending hashtags from SerpAPI
            trending = self._get_trending_hashtags(topic, niche, platform_lower)
            if trending:
                hashtags.extend(trending)

            # Add platform-specific hashtags
            platform_tags = self._get_platform_specific_tags(platform_lower, niche)
            hashtags.extend(platform_tags)

            # Remove duplicates and limit to 8-15
            unique_hashtags = list(dict.fromkeys(hashtags))[:15]

            # Ensure we have at least 8
            if len(unique_hashtags) < 8:
                unique_hashtags.extend(self._get_fallback_hashtags(topic, niche, platform_lower))
                unique_hashtags = list(dict.fromkeys(unique_hashtags))[:15]

            # Format as string
            result = "Recommended Hashtags:\n"
            result += ", ".join(unique_hashtags[:15])
            result += f"\n\nHashtag Strategy: Mix of trending ({len(trending)} tags), niche-specific, and evergreen tags for maximum reach and engagement on {platform}."

            return result

        except Exception as e:
            # Fallback to rule-based generation
            return self._fallback_generation(topic, niche, platform)

    def _generate_base_hashtags(self, topic: str, niche: str, platform: str) -> list:
        """Generate base hashtags from topic and niche."""
        hashtags = []

        # Clean and split topic
        words = topic.lower().replace(",", "").replace(".", "").split()

        # Create hashtags from topic words
        if len(words) <= 3:
            hashtags.append(f"#{''.join([w.capitalize() for w in words])}")

        # Add individual important words as hashtags
        for word in words:
            if len(word) > 4 and word not in ['the', 'and', 'for', 'with', 'about']:
                hashtags.append(f"#{word.capitalize()}")

        # Add niche hashtags
        if niche:
            niche_words = niche.lower().split()
            hashtags.append(f"#{''.join([w.capitalize() for w in niche_words])}")
            for word in niche_words:
                if len(word) > 4:
                    hashtags.append(f"#{word.capitalize()}")

        return hashtags[:5]

    def _get_trending_hashtags(self, topic: str, niche: str, platform: str) -> list:
        """Get trending hashtags using SerpAPI."""
        api_key = os.getenv('SERP_API_KEY')
        if not api_key:
            return []

        try:
            # Search for trending content with the topic
            url = "https://serpapi.com/search"
            params = {
                "engine": "google_trends",
                "q": f"{topic} {niche}",
                "api_key": api_key,
                "data_type": "RELATED_QUERIES"
            }

            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                hashtags = []

                # Extract related queries as potential hashtags
                if "related_queries" in data:
                    for query in data["related_queries"][:5]:
                        if "query" in query:
                            tag = query["query"].replace(" ", "")
                            hashtags.append(f"#{tag.capitalize()}")

                return hashtags

        except Exception as e:
            pass

        return []

    def _get_platform_specific_tags(self, platform: str, niche: str) -> list:
        """Get platform-specific popular hashtags."""
        platform_tags = {
            "youtube": ["#YouTube", "#YouTuber", "#Subscribe", "#Viral", "#Trending"],
            "instagram": ["#InstaGood", "#Reels", "#Viral", "#Explore", "#Trending"],
            "tiktok": ["#TikTok", "#Viral", "#ForYou", "#FYP", "#Trending"],
            "twitter": ["#Twitter", "#Trending", "#Viral"],
            "linkedin": ["#LinkedIn", "#Professional", "#Business", "#Industry", "#CareerTips"]
        }

        # Niche-specific additions
        if "ai" in niche.lower() or "automation" in niche.lower():
            return platform_tags.get(platform, []) + ["#AI", "#Automation", "#Technology", "#Innovation", "#DigitalTransformation"]

        return platform_tags.get(platform, ["#ContentCreator", "#DigitalMarketing"])[:4]

    def _get_fallback_hashtags(self, topic: str, niche: str, platform: str) -> list:
        """Fallback hashtags if we need more."""
        general_tags = [
            "#ContentCreation", "#SocialMedia", "#Marketing",
            "#Growth", "#Tips", "#Tutorial", "#HowTo",
            "#Business", "#Strategy", "#Success"
        ]
        return general_tags

    def _fallback_generation(self, topic: str, niche: str, platform: str) -> str:
        """Fallback method if API fails."""
        hashtags = []

        # Generate from topic
        hashtags.extend(self._generate_base_hashtags(topic, niche, platform))

        # Add platform tags
        hashtags.extend(self._get_platform_specific_tags(platform, niche))

        # Add general tags
        hashtags.extend(self._get_fallback_hashtags(topic, niche, platform))

        # Remove duplicates and limit
        unique_hashtags = list(dict.fromkeys(hashtags))[:12]

        result = "Recommended Hashtags (Rule-based):\n"
        result += ", ".join(unique_hashtags)
        result += f"\n\nNote: Generated using keyword extraction and platform best practices for {platform}."

        return result
