from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from content_ai_agent.api.routes.agent_routes import router as agent_router
from content_ai_agent.api.routes.instagram_routes import router as instagram_router
from content_ai_agent.api.routes.analytics_routes import router as analytics_router


app = FastAPI(
    title="AI Automation Agency Content Engine",
    description="API for trend analysis, script generation, competitor analysis, and content optimization",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "https://script-generator-sand.vercel.app",
        "http://localhost:3000",
        "http://localhost:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Content Generation Routes
app.include_router(agent_router, prefix="/api/v1", tags=["Content Generation"])
app.include_router(instagram_router, prefix="/api/v1/instagram", tags=["Instagram"])

# Analytics & Intelligence Routes
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics & Intelligence"])

@app.get("/")
def root():
    return {"status": "ok", "service": "Content AI Agent"}

@app.get("/health")
def health_check():
    return {"status": "ok"}


