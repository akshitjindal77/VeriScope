from fastapi import APIRouter
from app.config.settings import settings
from pydantic import BaseModel
from app.services.research_services import run_research
from app.models.research_models import ResearchResponse

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


@router.post("/research", response_model = ResearchResponse)
async def research(request: ResearchRequest):
    result = await run_research(request.prompt)
    return {
        "status": "success",
        "prompt": request.prompt,
        "answer": result["answer"],
        "citations": result["citations"],
        "confidence": result["confidence"]
    }


