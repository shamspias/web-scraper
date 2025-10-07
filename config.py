from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    APP_NAME: str = "Authorized Website Scraper"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    # Scraper settings
    MAX_CONCURRENT_PAGES: int = 5
    PAGE_TIMEOUT: int = 30000
    MAX_DEPTH: int = 5
    RESPECT_ROBOTS_TXT: bool = True

    # Security
    ALLOWED_DOMAINS: Optional[List[str]] = None

    # Storage - files saved under website domain
    OUTPUT_DIR: str = "./scraped_data"
    SAVE_IMAGES: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
