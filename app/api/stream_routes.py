import asyncio
import json
import logging
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.database.models import User, ResearchSession, ResearchQuery
from app.services.research_services import run_research, _make_serializable

router = APIRouter()
logger = logging.getLogger(__name__)


class StreamResearchRequest(BaseModel):
    prompt: str
    mode: str = "linear"
    session_id: Optional[str] = None


@router.post("/research/stream")
async def stream_research(
    request: StreamResearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    if len(request.prompt) > 2000:
        raise HTTPException(status_code=413, detail="Prompt too long")

    valid_modes = {"linear", "react"}
    if request.mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid mode '{request.mode}'")

    async def event_generator():
        status_queue: asyncio.Queue = asyncio.Queue()

        async def status_callback(stage: str, message: str):
            await status_queue.put({"event": "status", "stage": stage, "message": message})

        result_holder = {"result": None, "error": None}

        async def run_pipeline():
            try:
                start_time = time.time()
                result = await run_research(
                    prompt=request.prompt,
                    mode=request.mode,
                    db=db,
                    status_callback=status_callback,
                )
                result["duration_seconds"] = round(time.time() - start_time, 2)
                result_holder["result"] = result
            except Exception as e:
                logger.exception("Pipeline error during streaming: %s", e)
                result_holder["error"] = str(e)
            finally:
                await status_queue.put(None)

        pipeline_task = asyncio.create_task(run_pipeline())

        while True:
            event = await status_queue.get()

            if event is None:
                if result_holder["error"]:
                    yield f"data: {json.dumps({'event': 'error', 'message': result_holder['error']})}\n\n"
                elif result_holder["result"]:
                    result = result_holder["result"]
                    try:
                        session_id = request.session_id
                        if not session_id:
                            new_session = ResearchSession(
                                user_id=current_user.id,
                                title=request.prompt[:50],
                            )
                            db.add(new_session)
                            await db.commit()
                            await db.refresh(new_session)
                            session_id = new_session.id

                        query_record = ResearchQuery(
                            session_id=session_id,
                            prompt=request.prompt,
                            mode=request.mode,
                            answer=result.get("answer", ""),
                            citations_json=json.dumps(_make_serializable(result.get("citations", [])), default=str),
                            confidence=result.get("confidence", 0.0),
                            query_type=result.get("query_type"),
                            resolved_meaning=result.get("resolved_meaning"),
                            react_steps=result.get("react_steps"),
                            duration_seconds=result.get("duration_seconds", 0.0),
                        )
                        db.add(query_record)
                        await db.commit()

                        result["session_id"] = session_id
                    except Exception as e:
                        logger.exception("Error saving streamed result: %s", e)

                    yield f"data: {json.dumps({'event': 'result', 'data': _make_serializable(result)}, default=str)}\n\n"
                break
            else:
                yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
