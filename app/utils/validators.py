from urllib.parse import urlparse
from typing import Optional
import re


class URLValidator:
    @staticmethod
    def is_valid_url(url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def is_same_domain(url1: str, url2: str) -> bool:
        domain1 = urlparse(url1).netloc
        domain2 = urlparse(url2).netloc
        return domain1 == domain2

    @staticmethod
    def normalize_url(url: str) -> str:
        url = url.split('#')[0]
        url = url.rstrip('/')
        return url

    @staticmethod
    def is_valid_content_type(content_type: Optional[str]) -> bool:
        if not content_type:
            return False
        valid_types = ['text/html', 'application/xhtml+xml']
        return any(ct in content_type.lower() for ct in valid_types)

    @staticmethod
    def url_to_directory_name(url: str) -> str:
        """Convert URL to a safe directory name"""
        parsed = urlparse(url)
        domain = parsed.netloc

        # Remove www. prefix
        domain = domain.replace('www.', '')

        # Replace special characters with underscores
        safe_name = re.sub(r'[^\w\-.]', '_', domain)

        return safe_name
