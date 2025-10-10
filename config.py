# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional, List, Union


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # ignore unknown keys from .env
    )

    APP_NAME: str = "Authorized Website Scraper"
    APP_VERSION: str = "0.0.2"
    API_PREFIX: str = "/api/v1"

    # Scraper settings
    MAX_CONCURRENT_PAGES: int = 5
    PAGE_TIMEOUT: int = 30000
    MAX_DEPTH: int = 5
    RESPECT_ROBOTS_TXT: bool = True

    # Security
    ALLOWED_DOMAINS: Optional[List[str]] = None  # <— made this a list

    # Storage
    OUTPUT_DIR: str = "./scraped_data"

    # CORS origins
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:5173"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @field_validator("ALLOWED_DOMAINS", mode="before")
    @classmethod
    def parse_allowed_domains(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
            return [d.strip() for d in v.split(",") if d.strip()]
        return v


settings = Settings()
