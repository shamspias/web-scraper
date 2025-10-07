from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import subprocess
import sys

from app.api.routes import router
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup: Install Playwright browsers if needed
    print("🚀 Starting Web Scraper API...")
    try:
        result = subprocess.run(
            ["playwright", "install", "chromium"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ Playwright browsers ready")
        else:
            print("⚠️  Playwright browser installation issue")
    except Exception as e:
        print(f"⚠️  Could not auto-install Playwright: {e}")
        print("   Run manually: playwright install chromium")

    yield

    # Shutdown
    print("👋 Shutting down Web Scraper API...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Professional web scraping API for authorized use only. Files saved under scraped_data/{domain}_{"
                "timestamp}/",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix=settings.API_PREFIX, tags=["scraper"])


@app.get("/")
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "legal_notice": "This service must only be used on websites you own or have explicit permission to scrape.",
        "output_structure": "Files saved to: scraped_data/{domain}_{timestamp}/"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
