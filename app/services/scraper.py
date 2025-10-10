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
import csv

from app.models.schemas import PageData, SitemapData, FailedURL
from app.services.content_cleaner import ContentCleaner
from app.utils.validators import URLValidator
from config import settings


class WebScraper:
    """Advanced web scraper using Playwright with hierarchy support"""

    # File extensions to skip
    SKIP_EXTENSIONS = {
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.zip', '.rar', '.tar', '.gz', '.7z',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico',
        '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv',
        '.mp3', '.wav', '.ogg', '.flac',
        '.exe', '.dmg', '.app', '.deb', '.rpm',
        '.xml', '.json', '.csv', '.txt'
    }

    def __init__(self, base_url: str, max_depth: int = 3, existing_output_dir: Optional[str] = None):
        self.base_url = URLValidator.normalize_url(base_url)
        self.base_domain = urlparse(base_url).netloc
        self.max_depth = max_depth

        self.visited_urls: Set[str] = set()
        self.url_hierarchy: Dict[str, List[str]] = {}  # Parent -> Children mapping
        self.scraped_pages: List[PageData] = []
        self.failed_urls: List[FailedURL] = []  # Track failed URLs with details
        self.errors: List[str] = []

        self.browser: Optional[Browser] = None
        self.content_cleaner = ContentCleaner()
        self.validator = URLValidator()

        # Create or use existing output directory
        if existing_output_dir:
            self.output_dir = Path(existing_output_dir)
        else:
            self.directory_name = self._create_url_based_directory()
            self.output_dir = Path(settings.OUTPUT_DIR) / self.directory_name

        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Output directory: {self.output_dir}")

    def _create_url_based_directory(self) -> str:
        """Create directory name based on URL and timestamp"""
        domain = self.validator.url_to_directory_name(self.base_url)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return f"{domain}_{timestamp}"

    def _is_valid_webpage_url(self, url: str) -> bool:
        """Check if URL is a valid webpage (not a file)"""
        parsed = urlparse(url)
        path = parsed.path.lower()

        # Check for file extensions
        for ext in self.SKIP_EXTENSIONS:
            if path.endswith(ext):
                return False

        # Check if it's a valid HTTP(S) URL
        if parsed.scheme not in ['http', 'https']:
            return False

        return True

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

    async def discover_urls(self, page: Page, current_url: str) -> List[str]:
        """Discover all URLs on a page"""
        discovered = []

        try:
            await page.wait_for_load_state('networkidle', timeout=settings.PAGE_TIMEOUT)

            links = await page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    return links.map(a => a.href);
                }
            """)

            for link in links:
                try:
                    normalized = self.validator.normalize_url(link)

                    if (self.validator.is_same_domain(normalized, self.base_url) and
                            normalized not in self.visited_urls and
                            self.validator.is_valid_url(normalized) and
                            self._is_valid_webpage_url(normalized)):
                        discovered.append(normalized)
                except Exception:
                    continue

        except Exception as e:
            self.errors.append(f"URL discovery error on {current_url}: {str(e)}")

        return list(set(discovered))

    async def build_sitemap_hierarchy(self) -> SitemapData:
        """Build hierarchical sitemap by crawling the website"""
        if not self.browser:
            await self.initialize_browser()

        all_urls: Set[str] = {self.base_url}
        url_queue: List[tuple[str, int, Optional[str]]] = [(self.base_url, 0, None)]

        print(f"🗺️  Building hierarchical sitemap (max depth: {self.max_depth})...")

        while url_queue and len(self.visited_urls) < 500:
            current_url, depth, parent_url = url_queue.pop(0)

            if current_url in self.visited_urls or depth > self.max_depth:
                continue

            self.visited_urls.add(current_url)
            print(f"📍 Depth {depth}: {current_url}")

            try:
                context = await self.browser.new_context()
                page = await context.new_page()
                await page.goto(current_url, wait_until='domcontentloaded', timeout=settings.PAGE_TIMEOUT)

                discovered = await self.discover_urls(page, current_url)

                # Build hierarchy
                if parent_url:
                    if parent_url not in self.url_hierarchy:
                        self.url_hierarchy[parent_url] = []
                    self.url_hierarchy[parent_url].append(current_url)

                if current_url not in self.url_hierarchy:
                    self.url_hierarchy[current_url] = []

                # Add discovered URLs to hierarchy
                for url in discovered:
                    if url not in self.visited_urls:
                        url_queue.append((url, depth + 1, current_url))
                        all_urls.add(url)

                await context.close()

            except Exception as e:
                self.errors.append(f"Sitemap building error {current_url}: {str(e)}")

        print(f"✅ Sitemap complete: {len(all_urls)} URLs discovered")

        return SitemapData(
            total_urls=len(all_urls),
            urls=list(all_urls),
            hierarchy=self.url_hierarchy
        )

    async def scrape_page(self, url: str, retry_count: int = 0) -> Optional[PageData]:
        """Scrape a single page with structured content"""
        try:
            context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()

            response = await page.goto(url, wait_until='networkidle', timeout=settings.PAGE_TIMEOUT)

            if not response or response.status not in [200, 304]:
                raise Exception(f"Failed to load page: HTTP {response.status if response else 'No response'}")

            html_content = await page.content()

            # Extract metadata
            metadata = self.content_cleaner.extract_metadata(html_content)

            # Extract structured content with images at their positions
            structured_content = self.content_cleaner.clean_html_to_structured_content(html_content, url)

            # Extract all image URLs
            all_images = self.content_cleaner.extract_all_images(html_content, url)

            await context.close()

            return PageData(
                url=url,
                title=metadata.get('title'),
                metadata=metadata,
                structured_content=structured_content,
                all_images=all_images
            )

        except Exception as e:
            error_msg = f"Page scraping error {url}: {str(e)}"
            self.errors.append(error_msg)

            # Add to failed URLs list
            self.failed_urls.append(FailedURL(
                url=url,
                error=str(e),
                attempted_at=datetime.utcnow(),
                retry_count=retry_count
            ))

            return None

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

        scraped = [r for r in results if isinstance(r, PageData)]

        print(f"✅ Scraped {len(scraped)} pages successfully")
        return scraped

    async def retry_failed_urls(self, urls_to_retry: List[str], existing_sitemap: Optional[SitemapData] = None) -> Dict:
        """Retry scraping specific failed URLs"""
        print(f"🔄 Retrying {len(urls_to_retry)} failed URLs...")

        try:
            await self.initialize_browser()

            # Update retry count for these URLs
            for failed_url in self.failed_urls:
                if failed_url.url in urls_to_retry:
                    failed_url.retry_count += 1

            # Scrape the URLs
            scraped_pages = await self.scrape_all_pages(urls_to_retry)

            # Remove successfully scraped URLs from failed list
            successfully_scraped = {page.url for page in scraped_pages}
            self.failed_urls = [f for f in self.failed_urls if f.url not in successfully_scraped]

            # Update or append results
            await self._save_results(existing_sitemap, scraped_pages, is_retry=True)

            print(f"✅ Retry complete! {len(scraped_pages)} pages scraped successfully")

            return {
                "sitemap": existing_sitemap,
                "pages": scraped_pages,
                "total_pages": len(scraped_pages),
                "failed_urls": self.failed_urls,
                "errors": self.errors,
                "output_directory": str(self.output_dir)
            }

        finally:
            await self.close_browser()

    async def run_full_scrape(self) -> Dict:
        """Execute complete scraping process"""
        try:
            print(f"🚀 Starting scrape for: {self.base_url}")
            await self.initialize_browser()

            # Step 1: Build hierarchical sitemap FIRST
            sitemap = await self.build_sitemap_hierarchy()

            # Step 2: Scrape all pages
            scraped_pages = await self.scrape_all_pages(sitemap.urls)

            # Step 3: Save results
            await self._save_results(sitemap, scraped_pages)

            print(f"🎉 Scraping complete! Files saved to: {self.output_dir}")

            return {
                "sitemap": sitemap,
                "pages": scraped_pages,
                "total_pages": len(scraped_pages),
                "failed_urls": self.failed_urls,
                "errors": self.errors,
                "output_directory": str(self.output_dir)
            }

        finally:
            await self.close_browser()

    async def _save_results(self, sitemap: Optional[SitemapData], pages: List[PageData], is_retry: bool = False):
        """Save scraping results to JSON and CSV"""

        # For retries, load existing data and merge
        if is_retry:
            # Load existing pages
            pages_json_file = self.output_dir / "pages.json"
            if pages_json_file.exists():
                async with aiofiles.open(pages_json_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    existing_pages_data = json.loads(content)

                # Remove old versions of retried pages and add new ones
                retried_urls = {page.url for page in pages}
                existing_pages_data = [p for p in existing_pages_data if p['url'] not in retried_urls]

                # Add new pages
                for page in pages:
                    existing_pages_data.append({
                        'url': page.url,
                        'title': page.title,
                        'metadata': page.metadata,
                        'structured_content': page.structured_content,
                        'all_images': page.all_images,
                        'scraped_at': page.scraped_at.isoformat() if page.scraped_at else None
                    })

                # Save merged data
                async with aiofiles.open(pages_json_file, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(existing_pages_data, indent=2, ensure_ascii=False))

                pages = [PageData(**p) for p in existing_pages_data]

        # Save hierarchical sitemap as JSON (if provided)
        if sitemap:
            sitemap_file = self.output_dir / "sitemap.json"
            async with aiofiles.open(sitemap_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps({
                    'total_urls': sitemap.total_urls,
                    'base_url': self.base_url,
                    'scraped_at': datetime.utcnow().isoformat(),
                    'hierarchy': sitemap.hierarchy,
                    'urls': sitemap.urls
                }, indent=2, default=str))

        # Save all pages as JSON (new or updated)
        if not is_retry:
            pages_json_file = self.output_dir / "pages.json"
            pages_data = []

            for page in pages:
                page_dict = {
                    'url': page.url,
                    'title': page.title,
                    'metadata': page.metadata,
                    'structured_content': page.structured_content,
                    'all_images': page.all_images,
                    'scraped_at': page.scraped_at.isoformat() if page.scraped_at else None
                }
                pages_data.append(page_dict)

            async with aiofiles.open(pages_json_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(pages_data, indent=2, ensure_ascii=False))

        # Save pages as CSV
        pages_csv_file = self.output_dir / "pages.csv"
        async with aiofiles.open(pages_csv_file, 'w', encoding='utf-8', newline='') as f:
            if pages:
                fieldnames = ['url', 'title', 'description', 'keywords', 'author',
                              'image_count', 'content_blocks', 'full_content', 'all_images']

                csv_data = []
                csv_data.append(','.join(f'"{field}"' for field in fieldnames) + '\n')

                for page in pages:
                    # Combine structured content into readable text
                    full_content = ''
                    for block in page.structured_content:
                        if block['type'] == 'text':
                            full_content += block['content'] + ' '
                        else:
                            full_content += f"[IMAGE: {block['url']}] "

                    row = [
                        page.url,
                        page.title or '',
                        page.metadata.get('description', ''),
                        page.metadata.get('keywords', ''),
                        page.metadata.get('author', ''),
                        str(len(page.all_images)),
                        str(len(page.structured_content)),
                        full_content.strip(),
                        '; '.join(page.all_images)
                    ]

                    # Escape and quote CSV values
                    escaped_row = ','.join(f'"{str(val).replace(chr(34), chr(34) + chr(34))}"' for val in row)
                    csv_data.append(escaped_row + '\n')

                await f.writelines(csv_data)

        # Save summary with failed URLs
        summary_file = self.output_dir / "summary.json"
        summary = {
            'website': self.base_url,
            'scraped_at': datetime.utcnow().isoformat(),
            'total_urls_discovered': sitemap.total_urls if sitemap else len(pages),
            'pages_scraped': len(pages),
            'total_images_found': sum(len(p.all_images) for p in pages),
            'failed_urls_count': len(self.failed_urls),
            'failed_urls': [
                {
                    'url': f.url,
                    'error': f.error,
                    'attempted_at': f.attempted_at.isoformat(),
                    'retry_count': f.retry_count
                }
                for f in self.failed_urls
            ],
            'errors_count': len(self.errors),
            'errors': self.errors[:50],  # Limit errors
            'max_depth': self.max_depth,
            'output_formats': ['JSON', 'CSV']
        }

        async with aiofiles.open(summary_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(summary, indent=2))

        print(f"💾 Saved: sitemap.json, pages.json, pages.csv, summary.json")
