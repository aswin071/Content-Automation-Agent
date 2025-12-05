# Instagram API Integration Setup Guide

## Overview
This guide will help you set up Instagram API integration to fetch trending topics and hashtags for your Content Automation Agent.

## Option 1: RapidAPI (Recommended - Easiest)

### Step 1: Sign Up for RapidAPI
1. Go to https://rapidapi.com/
2. Click "Sign Up" (free account)
3. Verify your email

### Step 2: Subscribe to Instagram API
1. Search for "Instagram" in the RapidAPI marketplace
2. **Recommended APIs:**
   - **Instagram Bulk Profile Scrapper** by DataTech Labs
     - https://rapidapi.com/DataTechLabs/api/instagram-bulk-profile-scrapper
     - Free tier: 100 requests/month
     - Features: Trending hashtags, profile data, post metrics

   - **Instagram Data** by Prasadbro
     - https://rapidapi.com/Prasadbro/api/instagram-data
     - Free tier: 500 requests/month
     - Features: Hashtag search, trending content

   - **Instagram API** by Social Media API
     - https://rapidapi.com/social-media-api/api/instagram-api
     - Free tier: 50 requests/month
     - Features: Profile data, trending topics

3. Click **"Subscribe to Test"** on your chosen API
4. Select the **Free plan** (or paid plan if you need more requests)
5. Click **"Subscribe"**

### Step 3: Get Your API Key
1. After subscribing, go to the API's "Endpoints" tab
2. Look for the **"X-RapidAPI-Key"** in the code snippet section
3. Copy your API key (starts with something like: `abc123def456...`)

### Step 4: Configure Your Application
1. Open your `.env` file
2. Replace `YOUR_RAPIDAPI_KEY_HERE` with your actual API key:
   ```
   RAPIDAPI_KEY="your_actual_key_here"
   ```
3. Update the host if you chose a different API:
   ```
   RAPIDAPI_INSTAGRAM_HOST="instagram-bulk-profile-scrapper.p.rapidapi.com"
   ```

### Step 5: Test the Integration Locally
```bash
# Start your FastAPI server
uvicorn content_ai_agent.api.main:app --reload

# Test the trending hashtags endpoint
curl http://localhost:8000/api/v1/instagram/trending/hashtags?limit=10

# Test trending topics by niche
curl -X POST http://localhost:8000/api/v1/instagram/trending/niche \
  -H "Content-Type: application/json" \
  -d '{"niche": "fitness", "limit": 10}'
```

---

## Option 2: Meta Graph API (Official - More Complex)

### Requirements:
- Facebook Developer Account
- Instagram Business or Creator Account (cannot be personal account)
- Your app must be reviewed and approved by Meta

### Step 1: Create Facebook App
1. Go to https://developers.facebook.com/
2. Click "My Apps" → "Create App"
3. Select "Business" type
4. Fill in app details

### Step 2: Add Instagram Products
1. In your app dashboard, click "Add Product"
2. Find "Instagram" and click "Set Up"
3. Choose either:
   - **Instagram Basic Display** - For basic profile data
   - **Instagram Graph API** - For business accounts with insights

### Step 3: Generate Access Token
1. Go to Tools → Graph API Explorer
2. Select your app
3. Add these permissions:
   - `instagram_basic`
   - `instagram_manage_insights`
   - `pages_read_engagement`
4. Click "Generate Access Token"

### Step 4: Configure Environment
```bash
INSTAGRAM_ACCESS_TOKEN="your_access_token"
INSTAGRAM_BUSINESS_ACCOUNT_ID="your_account_id"
```

### Limitations:
- Can only access your own business account data
- Cannot fetch general public trending topics
- Requires app review for production use
- More complex to set up

---

## Available Endpoints

Once configured, your API will have these Instagram endpoints:

### 1. Get Trending Hashtags
```bash
GET /api/v1/instagram/trending/hashtags?limit=10
```

### 2. Get Trending by Niche
```bash
POST /api/v1/instagram/trending/niche
{
  "niche": "technology",
  "limit": 10
}
```

### 3. Search Specific Hashtag
```bash
POST /api/v1/instagram/hashtag/search
{
  "hashtag": "fitness"
}
```

### 4. Get Available Categories
```bash
GET /api/v1/instagram/trending/categories
```

---

## Deploy to AWS ECS

After testing locally, you'll need to add the RapidAPI key to AWS Secrets Manager:

### 1. Create Secret in AWS
```bash
aws secretsmanager create-secret \
  --name RAPIDAPI_KEY \
  --secret-string "your_rapidapi_key_here" \
  --region us-east-1
```

### 2. Update ECS Task Definition
Add to the `secrets` section in `ecs-task-definition.json`:
```json
{
  "name": "RAPIDAPI_KEY",
  "valueFrom": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT_ID:secret:RAPIDAPI_KEY-XXXXX"
},
{
  "name": "RAPIDAPI_INSTAGRAM_HOST",
  "valueFrom": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT_ID:secret:RAPIDAPI_INSTAGRAM_HOST-XXXXX"
}
```

Or add as environment variables:
```json
"environment": [
  {
    "name": "RAPIDAPI_INSTAGRAM_HOST",
    "value": "instagram-bulk-profile-scrapper.p.rapidapi.com"
  }
]
```

### 3. Register and Deploy
```bash
# Register new task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Force new deployment
aws ecs update-service \
  --cluster content-ai-agent \
  --service content-automation-service \
  --force-new-deployment
```

---

## Troubleshooting

### Error: "RAPIDAPI_KEY is required"
- Make sure `.env` file has `RAPIDAPI_KEY` set
- For ECS, verify the secret exists in AWS Secrets Manager
- Check task definition includes the secret mapping

### Error: 401 Unauthorized
- Your RapidAPI key is invalid or expired
- You may have exceeded your free tier limit
- Check your RapidAPI dashboard for subscription status

### Error: 429 Too Many Requests
- You've hit the rate limit for your plan
- Upgrade to a higher tier on RapidAPI
- Implement caching to reduce API calls

---

## Cost Optimization Tips

1. **Cache responses** - Store trending data for 1-6 hours
2. **Use free tier wisely** - Most APIs offer 50-500 free requests/month
3. **Batch requests** - Fetch multiple niches at once when possible
4. **Monitor usage** - Check RapidAPI dashboard regularly

---

## Next Steps

1. ✅ Sign up for RapidAPI
2. ✅ Subscribe to an Instagram API
3. ✅ Add API key to `.env` file
4. ✅ Test endpoints locally
5. ✅ Deploy to AWS ECS
6. ✅ Integrate with your Content AI Agent workflows
