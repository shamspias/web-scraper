from bs4 import BeautifulSoup, NavigableString, Tag
import re
from typing import List, Dict, Optional


class ContentCleaner:
    """Clean and extract readable text from HTML content with image positions preserved"""

    SKIP_TAGS = {'script', 'style', 'meta', 'link', 'noscript', 'iframe', 'svg', 'head'}

    @staticmethod
    def clean_html_to_structured_content(html_content: str, base_url: str) -> List[Dict]:
        """
        Convert HTML to structured content preserving image positions
        Returns a list of content blocks (text or image)
        """
        from urllib.parse import urljoin

        soup = BeautifulSoup(html_content, 'lxml')

        # Remove unwanted tags
        for tag in soup(ContentCleaner.SKIP_TAGS):
            tag.decompose()

        # Remove comments
        for comment in soup.findAll(text=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
            comment.extract()

        # Find main content area (body)
        body = soup.find('body') or soup

        content_blocks = []

        def process_element(element, depth=0):
            """Recursively process elements maintaining structure"""
            if isinstance(element, NavigableString):
                text = str(element).strip()
                if text:
                    content_blocks.append({
                        'type': 'text',
                        'content': text
                    })
            elif isinstance(element, Tag):
                if element.name == 'img':
                    src = element.get('src') or element.get('data-src')
                    if src:
                        full_url = urljoin(base_url, src)
                        content_blocks.append({
                            'type': 'image',
                            'url': full_url,
                            'alt': element.get('alt', ''),
                            'title': element.get('title', '')
                        })
                elif element.name in ['p', 'div', 'article', 'section', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td',
                                      'th']:
                    # Process children recursively
                    for child in element.children:
                        process_element(child, depth + 1)
                    # Add spacing after block elements
                    if element.name in ['p', 'div', 'article', 'section', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        if content_blocks and content_blocks[-1]['type'] == 'text':
                            content_blocks.append({'type': 'text', 'content': '\n'})
                else:
                    for child in element.children:
                        process_element(child, depth + 1)

        process_element(body)

        # Clean up consecutive whitespace and empty blocks
        cleaned_blocks = []
        for block in content_blocks:
            if block['type'] == 'text':
                text = re.sub(r'\s+', ' ', block['content']).strip()
                if text and text != '\n':
                    cleaned_blocks.append({'type': 'text', 'content': text})
            else:
                cleaned_blocks.append(block)

        return cleaned_blocks

    @staticmethod
    def extract_all_images(html_content: str, base_url: str) -> List[str]:
        """Extract all image URLs from HTML"""
        from urllib.parse import urljoin

        soup = BeautifulSoup(html_content, 'lxml')
        images = []

        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                full_url = urljoin(base_url, src)
                images.append(full_url)

        return list(set(images))  # Remove duplicates

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

        og_image = soup.find('meta', attrs={'property': 'og:image'})
        if og_image:
            metadata['og_image'] = og_image.get('content', '')

        # Author
        author = soup.find('meta', attrs={'name': 'author'})
        if author:
            metadata['author'] = author.get('content', '')

        return metadata
