from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.api.stream_routes import router as stream_router
from app.auth.routes import router as auth_router
from app.sessions.routes import router as session_router
from app.database.connection import init_db
from app.api.rate_limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import logging
import os

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000, https://veri-scope-three.vercel.app"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.include_router(stream_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(session_router, prefix="/api")
logging.basicConfig(level=logging.INFO)

@app.on_event("startup")
async def startup():
    await init_db()

