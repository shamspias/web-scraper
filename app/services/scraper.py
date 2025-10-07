import re
from playwright.async_api import async_playwright, Page, Browser
from urllib.parse import urljoin, urlparse
import asyncio
from typing import Set, List, Dict, Optional
import aiofiles
import os
from pathlib import Path
import hashlib
from datetime import datetime
import json

from app.models.schemas import PageData, ImageData, SitemapData
from app.services.content_cleaner import ContentCleaner
from app.utils.validators import URLValidator
from config import settings


class WebScraper:
    """Advanced web scraper using Playwright"""

    def __init__(self, base_url: str, max_depth: int = 3, include_images: bool = True):
        self.base_url = URLValidator.normalize_url(base_url)
        self.base_domain = urlparse(base_url).netloc
        self.max_depth = max_depth
        self.include_images = include_images

        self.visited_urls: Set[str] = set()
        self.url_queue: List[tuple[str, int]] = [(self.base_url, 0)]
        self.scraped_pages: List[PageData] = []
        self.errors: List[str] = []

        self.browser: Optional[Browser] = None
        self.content_cleaner = ContentCleaner()
        self.validator = URLValidator()

        # Create output directory based on website URL
        self.directory_name = self._create_url_based_directory()
        self.output_dir = Path(settings.OUTPUT_DIR) / self.directory_name
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"📁 Output directory: {self.output_dir}")

    def _create_url_based_directory(self) -> str:
        """Create directory name based on URL and timestamp"""
        # Get clean domain name
        domain = self.validator.url_to_directory_name(self.base_url)

        # Add timestamp for uniqueness
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')

        return f"{domain}_{timestamp}"

    async def initialize_browser(self):
        """Initialize Playwright browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )

    async def close_browser(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()

    async def discover_urls(self, page: Page, current_url: str, depth: int) -> List[str]:
        """Discover all URLs on a page"""
        discovered = []

        try:
            # Wait for page to load
            await page.wait_for_load_state('networkidle', timeout=settings.PAGE_TIMEOUT)

            # Extract all links
            links = await page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    return links.map(a => a.href);
                }
            """)

            for link in links:
                try:
                    normalized = self.validator.normalize_url(link)

                    # Only include same-domain links
                    if (self.validator.is_same_domain(normalized, self.base_url) and
                            normalized not in self.visited_urls and
                            self.validator.is_valid_url(normalized)):
                        discovered.append(normalized)
                except Exception:
                    continue

        except Exception as e:
            self.errors.append(f"URL discovery error on {current_url}: {str(e)}")

        return list(set(discovered))  # Remove duplicates

    async def download_image(self, image_url: str, page_url: str) -> Optional[str]:
        """Download image and save locally"""
        try:
            import httpx

            # Create images directory
            images_dir = self.output_dir / "images"
            images_dir.mkdir(exist_ok=True)

            # Generate filename
            url_hash = hashlib.md5(image_url.encode()).hexdigest()[:12]
            ext = Path(urlparse(image_url).path).suffix or '.jpg'
            if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
                ext = '.jpg'
            filename = f"{url_hash}{ext}"
            filepath = images_dir / filename

            # Skip if already downloaded
            if filepath.exists():
                return str(filepath.relative_to(self.output_dir))

            # Download image
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(image_url, follow_redirects=True)
                if response.status_code == 200 and len(response.content) > 0:
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(response.content)
                    return str(filepath.relative_to(self.output_dir))

        except Exception as e:
            self.errors.append(f"Image download error {image_url}: {str(e)}")

        return None

    async def scrape_page(self, url: str) -> Optional[PageData]:
        """Scrape a single page"""
        try:
            context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = await context.new_page()

            # Navigate to page
            response = await page.goto(url, wait_until='networkidle', timeout=settings.PAGE_TIMEOUT)

            if not response or response.status not in [200, 304]:
                raise Exception(f"Failed to load page: HTTP {response.status if response else 'No response'}")

            # Get HTML content
            html_content = await page.content()

            # Extract clean text
            clean_text = self.content_cleaner.clean_html_to_text(html_content)

            # Extract metadata
            metadata = self.content_cleaner.extract_metadata(html_content)

            # Extract images
            images_data = []
            if self.include_images:
                images = self.content_cleaner.extract_images(html_content, url)

                for img in images[:30]:  # Limit to 30 images per page
                    downloaded_path = None
                    if settings.SAVE_IMAGES:
                        downloaded_path = await self.download_image(img['url'], url)

                    images_data.append(ImageData(
                        url=img['url'],
                        alt_text=img['alt_text'],
                        downloaded_path=downloaded_path
                    ))

            await context.close()

            return PageData(
                url=url,
                title=metadata.get('title'),
                clean_text=clean_text,
                images=images_data,
                metadata=metadata
            )

        except Exception as e:
            self.errors.append(f"Page scraping error {url}: {str(e)}")
            return None

    async def build_sitemap(self) -> SitemapData:
        """Build complete sitemap by crawling the website"""
        if not self.browser:
            await self.initialize_browser()

        structure: Dict[str, List[str]] = {}
        all_urls: Set[str] = {self.base_url}

        print(f"🗺️  Building sitemap (max depth: {self.max_depth})...")

        while self.url_queue and len(self.visited_urls) < 500:  # Safety limit
            current_url, depth = self.url_queue.pop(0)

            if current_url in self.visited_urls or depth > self.max_depth:
                continue

            self.visited_urls.add(current_url)
            print(f"📍 Discovering: {current_url} (depth: {depth})")

            try:
                context = await self.browser.new_context()
                page = await context.new_page()
                await page.goto(current_url, wait_until='domcontentloaded', timeout=settings.PAGE_TIMEOUT)

                # Discover new URLs
                discovered = await self.discover_urls(page, current_url, depth)

                # Add to structure
                structure[current_url] = discovered

                # Add to queue
                for url in discovered:
                    if url not in self.visited_urls:
                        self.url_queue.append((url, depth + 1))
                        all_urls.add(url)

                await context.close()

            except Exception as e:
                self.errors.append(f"Sitemap building error {current_url}: {str(e)}")

        print(f"✅ Sitemap complete: {len(all_urls)} URLs discovered")
        return SitemapData(
            total_urls=len(all_urls),
            urls=list(all_urls),
            structure=structure
        )

    async def scrape_all_pages(self, urls: List[str]) -> List[PageData]:
        """Scrape all discovered pages"""
        if not self.browser:
            await self.initialize_browser()

        semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_PAGES)

        async def scrape_with_limit(url: str):
            async with semaphore:
                print(f"🔍 Scraping: {url}")
                return await self.scrape_page(url)

        tasks = [scrape_with_limit(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out None and exceptions
        scraped = [r for r in results if isinstance(r, PageData)]

        print(f"✅ Scraped {len(scraped)} pages successfully")
        return scraped

    async def run_full_scrape(self) -> Dict:
        """Execute complete scraping process"""
        try:
            print(f"🚀 Starting scrape for: {self.base_url}")
            await self.initialize_browser()

            # Step 1: Build sitemap
            sitemap = await self.build_sitemap()

            # Step 2: Scrape all pages
            scraped_pages = await self.scrape_all_pages(sitemap.urls)

            # Step 3: Save results
            await self._save_results(sitemap, scraped_pages)

            print(f"🎉 Scraping complete! Files saved to: {self.output_dir}")

            return {
                "sitemap": sitemap,
                "pages": scraped_pages,
                "total_pages": len(scraped_pages),
                "errors": self.errors,
                "output_directory": str(self.output_dir)
            }

        finally:
            await self.close_browser()

    async def _save_results(self, sitemap: SitemapData, pages: List[PageData]):
        """Save scraping results to files"""
        # Save sitemap
        sitemap_file = self.output_dir / "sitemap.json"
        async with aiofiles.open(sitemap_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(sitemap.dict(), indent=2, default=str))

        # Save all pages data
        pages_file = self.output_dir / "all_pages.json"
        async with aiofiles.open(pages_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps([p.dict() for p in pages], indent=2, default=str))

        # Save individual page texts
        texts_dir = self.output_dir / "pages"
        texts_dir.mkdir(exist_ok=True)

        for i, page in enumerate(pages, 1):
            # Create safe filename from URL
            url_slug = re.sub(r'[^\w\-]', '_', page.url.split('/')[-1] or 'index')[:50]
            text_file = texts_dir / f"{i:04d}_{url_slug}.txt"

            async with aiofiles.open(text_file, 'w', encoding='utf-8') as f:
                await f.write(f"URL: {page.url}\n")
                await f.write(f"Title: {page.title or 'N/A'}\n")
                await f.write(f"Scraped: {page.scraped_at}\n")
                await f.write("=" * 80 + "\n\n")
                await f.write(page.clean_text)

                if page.images:
                    await f.write(f"\n\n{'=' * 80}\n")
                    await f.write(f"IMAGES ({len(page.images)}):\n")
                    await f.write("=" * 80 + "\n\n")
                    for img in page.images:
                        await f.write(f"URL: {img.url}\n")
                        if img.alt_text:
                            await f.write(f"Alt: {img.alt_text}\n")
                        if img.downloaded_path:
                            await f.write(f"File: {img.downloaded_path}\n")
                        await f.write("\n")

        # Save summary
        summary_file = self.output_dir / "summary.txt"
        async with aiofiles.open(summary_file, 'w', encoding='utf-8') as f:
            await f.write(f"SCRAPING SUMMARY\n")
            await f.write("=" * 80 + "\n\n")
            await f.write(f"Website: {self.base_url}\n")
            await f.write(f"Scraped: {datetime.utcnow().isoformat()}\n")
            await f.write(f"Total URLs discovered: {len(sitemap.urls)}\n")
            await f.write(f"Pages scraped: {len(pages)}\n")
            await f.write(f"Images downloaded: {sum(len(p.images) for p in pages)}\n")
            await f.write(f"Errors: {len(self.errors)}\n")
            await f.write("\n")

            if self.errors:
                await f.write("ERRORS:\n")
                await f.write("-" * 80 + "\n")
                for error in self.errors:
                    await f.write(f"- {error}\n")
