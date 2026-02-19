from fastapi import APIRouter
from app.config.settings import settings
from pydantic import BaseModel
from app.services.research_services import run_research
from app.models.research_models import ResearchResponse
from fastapi import HTTPException

router = APIRouter()
MAX_PROMPT_LENGTH = 2000

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
    # validate empty or just spaces prompt
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty or just spaces")
    
    if len(request.prompt) > MAX_PROMPT_LENGTH:
        raise HTTPException(status_code=413, detail="Prompt cannot be too long, The maximum allowed is {MAX_PROMPT_LENGTH} characters")
    
    result = await run_research(request.prompt)
    
    return {
        "status": "success",
        "prompt": request.prompt,
        "answer": result["answer"],
        "citations": result["citations"],
        "confidence": result["confidence"]
    }


