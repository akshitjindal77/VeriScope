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

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()