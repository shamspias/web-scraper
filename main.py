from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import subprocess
import os
from pathlib import Path

from app.api.routes import router
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("🚀 Starting Web Scraper API...")
    try:
        result = subprocess.run(
            ["playwright", "install", "chromium"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ Playwright browsers ready")
    except Exception as e:
        print(f"⚠️  Could not auto-install Playwright: {e}")

    yield

    print("👋 Shutting down Web Scraper API...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Professional web scraping API with beautiful Vue.js frontend",
    lifespan=lifespan
)

# CORS - Only needed if frontend is on different origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix=settings.API_PREFIX, tags=["scraper"])

# Check if frontend build exists
frontend_dist = Path("frontend/dist")
if frontend_dist.exists():
    # Serve frontend static files
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")


    @app.get("/", include_in_schema=False)
    async def serve_root():
        """Serve Vue.js frontend"""
        return FileResponse("frontend/dist/index.html")


    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """Catch-all route for Vue Router"""
        # Check if it's an API route (will be handled by router above)
        if full_path.startswith("api/"):
            return {"detail": "Not found"}

        # Check if file exists in dist
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)

        # Serve index.html for all other routes (Vue Router handles these)
        return FileResponse("frontend/dist/index.html")
else:
    @app.get("/")
    async def root():
        return {
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "legal_notice": "This service must only be used on websites you own or have explicit permission to scrape.",
            "frontend": "Not built yet. Run: cd frontend && npm run build",
            "output_structure": "Files saved to: scraped_data/{domain}_{timestamp}/"
        }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
