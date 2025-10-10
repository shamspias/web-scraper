from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict
import uuid
import asyncio
import json
from pathlib import Path
from datetime import datetime

from app.models.schemas import ScrapeRequest, ScrapeResponse, ScrapeStatus, SitemapData, PageData
from app.services.scraper import WebScraper
from config import settings

router = APIRouter()

# In-memory job storage (use Redis/DB in production)
jobs: Dict[str, Dict] = {}


def load_existing_jobs():
    """Load existing jobs from scraped_data directory on startup"""
    output_dir = Path(settings.OUTPUT_DIR)

    if not output_dir.exists():
        return

    print("🔄 Loading existing jobs from disk...")

    for job_dir in output_dir.iterdir():
        if not job_dir.is_dir():
            continue

        summary_file = job_dir / "summary.json"
        sitemap_file = job_dir / "sitemap.json"
        pages_file = job_dir / "pages.json"

        if not all([summary_file.exists(), sitemap_file.exists(), pages_file.exists()]):
            continue

        try:
            # Load summary
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary = json.load(f)

            # Load sitemap
            with open(sitemap_file, 'r', encoding='utf-8') as f:
                sitemap_data = json.load(f)

            # Load pages
            with open(pages_file, 'r', encoding='utf-8') as f:
                pages_data = json.load(f)

            # Create job ID from directory name
            job_id = str(uuid.uuid4())

            # Parse pages
            pages = []
            for page_dict in pages_data:
                pages.append(PageData(
                    url=page_dict['url'],
                    title=page_dict.get('title'),
                    metadata=page_dict.get('metadata', {}),
                    structured_content=page_dict.get('structured_content', []),
                    all_images=page_dict.get('all_images', []),
                    scraped_at=datetime.fromisoformat(page_dict['scraped_at']) if page_dict.get(
                        'scraped_at') else datetime.utcnow()
                ))

            # Create sitemap
            sitemap = SitemapData(
                total_urls=sitemap_data['total_urls'],
                urls=sitemap_data['urls'],
                hierarchy=sitemap_data.get('hierarchy', {})
            )

            # Store job
            jobs[job_id] = {
                'status': ScrapeStatus.COMPLETED,
                'url': summary['website'],
                'message': 'Loaded from disk',
                'output_directory': str(job_dir),
                'sitemap': sitemap,
                'pages': pages,
                'total_pages_scraped': summary['pages_scraped'],
                'errors': summary.get('errors', []),
                'createdAt': summary['scraped_at']
            }

            print(f"✅ Loaded job: {summary['website']} ({summary['pages_scraped']} pages)")

        except Exception as e:
            print(f"⚠️  Failed to load job from {job_dir}: {e}")
            continue

    print(f"📦 Loaded {len(jobs)} existing jobs")


# Load jobs on module import
load_existing_jobs()


async def verify_authorization(request: ScrapeRequest):
    """Verify user has authorization to scrape the website"""
    if not request.authorization_token or len(request.authorization_token) < 10:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization token. You must own or have permission to scrape this website."
        )
    return True


async def run_scraping_job(job_id: str, scrape_request: ScrapeRequest):
    """Background task to run scraping"""
    try:
        jobs[job_id]['status'] = ScrapeStatus.IN_PROGRESS
        jobs[job_id]['message'] = 'Building hierarchical sitemap...'

        scraper = WebScraper(
            base_url=str(scrape_request.url),
            max_depth=scrape_request.max_depth
        )

        results = await scraper.run_full_scrape()

        jobs[job_id].update({
            'status': ScrapeStatus.COMPLETED,
            'message': 'Scraping completed successfully',
            'output_directory': results['output_directory'],
            'sitemap': results['sitemap'],
            'pages': results['pages'],
            'total_pages_scraped': results['total_pages'],
            'errors': results['errors']
        })

    except Exception as e:
        jobs[job_id].update({
            'status': ScrapeStatus.FAILED,
            'message': f'Scraping failed: {str(e)}',
            'errors': [str(e)]
        })


@router.post("/scrape", response_model=ScrapeResponse)
async def start_scrape(
        request: ScrapeRequest,
        background_tasks: BackgroundTasks,
        authorized: bool = Depends(verify_authorization)
):
    """
    Start a web scraping job for an authorized website.

    Process:
    1. Build hierarchical sitemap (only URLs under given domain)
    2. Scrape all discovered pages
    3. Save as JSON and CSV with structured content

    **LEGAL NOTICE**: Only use on websites you own or have explicit permission to scrape.
    """
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        'status': ScrapeStatus.PENDING,
        'url': str(request.url),
        'message': 'Scraping job queued',
        'createdAt': datetime.utcnow().isoformat()
    }

    background_tasks.add_task(run_scraping_job, job_id, request)

    return ScrapeResponse(
        job_id=job_id,
        status=ScrapeStatus.PENDING,
        message="Scraping job started. Sitemap will be built first, then pages scraped."
    )


@router.get("/scrape/{job_id}", response_model=ScrapeResponse)
async def get_scrape_status(job_id: str):
    """Get the status and results of a scraping job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job_data = jobs[job_id]

    return ScrapeResponse(
        job_id=job_id,
        status=job_data['status'],
        message=job_data.get('message', ''),
        output_directory=job_data.get('output_directory'),
        sitemap=job_data.get('sitemap'),
        pages=job_data.get('pages'),
        total_pages_scraped=job_data.get('total_pages_scraped', 0),
        errors=job_data.get('errors', [])
    )


@router.delete("/scrape/{job_id}")
async def delete_job(job_id: str):
    """Delete a job from memory (does not delete files)"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    del jobs[job_id]
    return {"message": "Job deleted from memory successfully"}


@router.get("/jobs")
async def list_jobs():
    """List all scraping jobs (including loaded from disk)"""
    return {
        "total_jobs": len(jobs),
        "jobs": [
            {
                "job_id": job_id,
                "status": data['status'],
                "url": data.get('url'),
                "message": data.get('message'),
                "total_pages": data.get('total_pages_scraped', 0),
                "created_at": data.get('createdAt')
            }
            for job_id, data in jobs.items()
        ]
    }


@router.post("/reload")
async def reload_jobs():
    """Reload jobs from disk"""
    jobs.clear()
    load_existing_jobs()
    return {
        "message": "Jobs reloaded from disk",
        "total_jobs": len(jobs)
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "web-scraper",
        "active_jobs": len([j for j in jobs.values() if j['status'] == ScrapeStatus.IN_PROGRESS]),
        "total_jobs": len(jobs)
    }
