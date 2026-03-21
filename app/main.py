from fastapi import FastAPI
from app.api.routes import router
from app.auth.routes import router as auth_router
from app.sessions.routes import router as session_router
from app.database.connection import init_db
import logging

app = FastAPI()

app.include_router(router)
app.include_router(auth_router)
app.include_router(session_router)
logging.basicConfig(level=logging.INFO)

@app.on_event("startup")
async def startup():
    await init_db()

