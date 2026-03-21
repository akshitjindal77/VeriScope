from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

load_dotenv()

class Settings(BaseSettings):
    app_name: str
    env: str = "development"

    WEB_SEARCH_PROVIDER: str ="brave"
    BRAVE_API_KEY: Optional[str] = None
    BRAVE_ENDPOINT: str = "https://api.search.brave.com/res/v1/web/search"
    WEB_SEARCH_MAX_RESULTS: int = 8
    WEB_SEARCH_TIMEOUT_S: float = 10.0
    WEB_SEARCH_CACHE_TTL_S: int = 300

    WEB_SEARCH_BLOCK_DOMAINS: List[str] = []
    WEB_SEARCH_ALLOW_DOMAINS: Optional[List[str]] = None

    # ── LLM Provider Settings ──
    LLM_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2048
    LLM_TIMEOUT_S: float = 120.0
    SOURCE_MIN_QUALITY: float = 0.3
    REACT_MAX_STEPS: int = 7
    REACT_STEP_TIMEOUT_S: float = 60.0

    # ── Database Settings ──
    DATABASE_URL: str = "sqlite+aiosqlite:///./veriscope.db"

    # ── Auth Settings ──
    JWT_SECRET_KEY: str = "change-this-to-a-random-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()