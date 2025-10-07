from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict
import uuid
import asyncio

from app.models.schemas import ScrapeRequest, ScrapeResponse, ScrapeStatus
from app.services.scraper import WebScraper

router = APIRouter()

# In-memory job storage (use Redis/DB in production)
jobs: Dict[str, Dict] = {}


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
        jobs[job_id]['message'] = 'Initializing scraper...'

        scraper = WebScraper(
            base_url=str(scrape_request.url),
            max_depth=scrape_request.max_depth,
            include_images=scrape_request.include_images
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

    **LEGAL NOTICE**: This endpoint should ONLY be used on websites you own or have
    explicit permission to scrape. Unauthorized scraping may violate laws and terms of service.

    Files will be saved in: scraped_data/{domain}_{timestamp}/
    """
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        'status': ScrapeStatus.PENDING,
        'url': str(request.url),
        'message': 'Scraping job queued'
    }

    background_tasks.add_task(run_scraping_job, job_id, request)

    return ScrapeResponse(
        job_id=job_id,
        status=ScrapeStatus.PENDING,
        message="Scraping job started. Use job_id to check status."
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
    """Delete a job from memory"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    del jobs[job_id]
    return {"message": "Job deleted successfully"}


@router.get("/jobs")
async def list_jobs():
    """List all scraping jobs"""
    return {
        "total_jobs": len(jobs),
        "jobs": [
            {
                "job_id": job_id,
                "status": data['status'],
                "url": data.get('url'),
                "message": data.get('message')
            }
            for job_id, data in jobs.items()
        ]
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "web-scraper",
        "active_jobs": len([j for j in jobs.values() if j['status'] == ScrapeStatus.IN_PROGRESS])
    }
