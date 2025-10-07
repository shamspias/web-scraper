from pydantic import BaseModel, HttpUrl, Field, validator
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class ScrapeStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ScrapeRequest(BaseModel):
    url: HttpUrl
    max_depth: Optional[int] = Field(default=3, ge=1, le=10)
    include_images: Optional[bool] = True
    authorization_token: str = Field(..., min_length=10, description="Your website authorization token")

    @validator('url')
    def validate_url(cls, v):
        url_str = str(v)
        if not url_str.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class ImageData(BaseModel):
    url: str
    alt_text: Optional[str] = None
    downloaded_path: Optional[str] = None


class PageData(BaseModel):
    url: str
    title: Optional[str] = None
    clean_text: str
    images: List[ImageData] = []
    metadata: Dict[str, str] = {}
    scraped_at: datetime = Field(default_factory=datetime.utcnow)


class SitemapData(BaseModel):
    total_urls: int
    urls: List[str]
    structure: Dict[str, List[str]]


class ScrapeResponse(BaseModel):
    job_id: str
    status: ScrapeStatus
    message: str
    output_directory: Optional[str] = None
    sitemap: Optional[SitemapData] = None
    pages: Optional[List[PageData]] = None
    total_pages_scraped: int = 0
    errors: List[str] = []
