from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional


class ContentCleaner:
    """Clean and extract readable text from HTML content"""

    SKIP_TAGS = {'script', 'style', 'meta', 'link', 'noscript', 'iframe', 'svg', 'head'}

    @staticmethod
    def clean_html_to_text(html_content: str) -> str:
        """Convert HTML to clean, readable text"""
        soup = BeautifulSoup(html_content, 'lxml')

        # Remove unwanted tags
        for tag in soup(ContentCleaner.SKIP_TAGS):
            tag.decompose()

        # Remove comments
        for comment in soup.findAll(text=lambda text: isinstance(text, str) and text.startswith('<!--')):
            comment.extract()

        # Get text
        text = soup.get_text(separator='\n', strip=True)

        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]

        # Remove excessive newlines
        text = '\n'.join(lines)
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    @staticmethod
    def extract_images(html_content: str, base_url: str) -> List[Dict[str, str]]:
        """Extract all images from HTML"""
        from urllib.parse import urljoin

        soup = BeautifulSoup(html_content, 'lxml')
        images = []

        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                full_url = urljoin(base_url, src)
                images.append({
                    'url': full_url,
                    'alt_text': img.get('alt', ''),
                })

        return images

    @staticmethod
    def extract_metadata(html_content: str) -> Dict[str, str]:
        """Extract metadata from HTML"""
        soup = BeautifulSoup(html_content, 'lxml')
        metadata = {}

        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()

        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content', '')

        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            metadata['keywords'] = meta_keywords.get('content', '')

        # Open Graph tags
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title:
            metadata['og_title'] = og_title.get('content', '')

        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc:
            metadata['og_description'] = og_desc.get('content', '')

        return metadata
