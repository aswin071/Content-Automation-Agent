from ctypes import cdll
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from content_ai_agent.api.routes.agent_routes import router


app= FastAPI(title="Content AI Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router,prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok"}
