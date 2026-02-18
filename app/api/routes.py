from fastapi import APIRouter
from app.config.settings import settings
from pydantic import BaseModel
from app.services.research_services import run_research

router = APIRouter()

@router.get("/")
def hello():
    return ("hello bitch")

@router.get("/health")
def health_check():
    return{
        "status": "ok",
        "app_name": settings.app_name,
        "env": settings.env
    }

class ResearchRequest(BaseModel):
    prompt: str

@router.post("/research")
async def research(request: ResearchRequest):
    answer = await run_research(request.prompt)
    return {
        "received": request.prompt,
        "answer": answer
    }

