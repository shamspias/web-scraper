from pydantic import BaseModel, HttpUrl, Field, validator
from typing import List, Optional, Dict, Any
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
    authorization_token: str = Field(..., min_length=10, description="Your website authorization token")

    @validator('url')
    def validate_url(cls, v):
        url_str = str(v)
        if not url_str.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class RetryRequest(BaseModel):
    """Request to retry failed URLs"""
    urls: List[str] = Field(..., min_items=1, description="List of URLs to retry")


class FailedURL(BaseModel):
    """Represents a URL that failed to scrape"""
    url: str
    error: str
    attempted_at: datetime = Field(default_factory=datetime.utcnow)
    retry_count: int = 0


class ContentBlock(BaseModel):
    """Represents a block of content (text or image)"""
    type: str  # 'text' or 'image'
    content: Optional[str] = None  # For text blocks
    url: Optional[str] = None  # For image blocks
    alt: Optional[str] = None  # For image blocks
    title: Optional[str] = None  # For image blocks


class PageData(BaseModel):
    url: str
    title: Optional[str] = None
    metadata: Dict[str, str] = {}
    structured_content: List[Dict[str, Any]] = []  # List of content blocks with images at positions
    all_images: List[str] = []  # All image URLs found on page
    scraped_at: datetime = Field(default_factory=datetime.utcnow)


class SitemapData(BaseModel):
    total_urls: int
    urls: List[str]
    hierarchy: Dict[str, List[str]] = {}  # Hierarchical structure: parent -> children


class ScrapeResponse(BaseModel):
    job_id: str
    status: ScrapeStatus
    message: str
    output_directory: Optional[str] = None
    sitemap: Optional[SitemapData] = None
    pages: Optional[List[PageData]] = None
    total_pages_scraped: int = 0
    failed_urls: List[FailedURL] = []  # Structured failed URLs
    errors: List[str] = []  # General errors


class JobSummary(BaseModel):
    """Summary of a completed job loaded from disk"""
    job_id: str
    url: str
    status: ScrapeStatus
    output_directory: str
    total_pages_scraped: int
    total_urls: int
    total_images: int
    scraped_at: str
    errors_count: int
