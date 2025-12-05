# Instagram API - Quick Start

## What Was Added

✅ **Instagram Service** - Fetch trending topics and hashtags from Instagram
✅ **New API Endpoints** - 4 new endpoints for Instagram data
✅ **RapidAPI Integration** - Easy setup with free tier available

## How to Get Started (5 Minutes)

### 1. Get Your API Key
```
1. Go to: https://rapidapi.com/
2. Sign up (free)
3. Search: "Instagram Bulk Profile Scrapper"
4. Subscribe to FREE plan
5. Copy your X-RapidAPI-Key
```

### 2. Add to .env File
```bash
RAPIDAPI_KEY="paste_your_key_here"
RAPIDAPI_INSTAGRAM_HOST="instagram-bulk-profile-scrapper.p.rapidapi.com"
```

### 3. Test Locally
```bash
# Start server
uvicorn content_ai_agent.api.main:app --reload

# Get trending hashtags
curl http://localhost:8000/api/v1/instagram/trending/hashtags?limit=10

# Get trending by niche
curl -X POST http://localhost:8000/api/v1/instagram/trending/niche \
  -H "Content-Type: application/json" \
  -d '{"niche": "fitness", "limit": 10}'
```

## New API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/instagram/trending/hashtags` | GET | Get trending Instagram hashtags |
| `/api/v1/instagram/trending/niche` | POST | Get trending topics for a niche |
| `/api/v1/instagram/hashtag/search` | POST | Search specific hashtag metrics |
| `/api/v1/instagram/trending/categories` | GET | List available categories |

## Example Usage

### Get Trending Hashtags
```bash
GET /api/v1/instagram/trending/hashtags?limit=10

Response:
{
  "success": true,
  "hashtags": ["#fitness", "#motivation", "#workout", ...],
  "count": 10
}
```

### Get Trending by Niche
```bash
POST /api/v1/instagram/trending/niche
{
  "niche": "AI Automation Agency",
  "limit": 10
}

Response:
{
  "success": true,
  "data": {
    "trending_hashtags": ["#ai", "#automation", ...],
    "trending_topics": [...],
    "source": "instagram"
  }
}
```

## Deploy to AWS

See full instructions in [INSTAGRAM_API_SETUP.md](./INSTAGRAM_API_SETUP.md)

Quick version:
```bash
# Add secret to AWS
aws secretsmanager create-secret \
  --name RAPIDAPI_KEY \
  --secret-string "your_key" \
  --region us-east-1

# Update task definition and deploy
# (See full guide for details)
```

## Cost

- **Free Tier**: 100-500 requests/month (varies by API provider)
- **Paid Tier**: $0.001 - $0.01 per request
- **Recommendation**: Start with free tier, cache responses

## Need Help?

See detailed setup: [INSTAGRAM_API_SETUP.md](./INSTAGRAM_API_SETUP.md)
