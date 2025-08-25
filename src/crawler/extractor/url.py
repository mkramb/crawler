from typing import Set
from urllib.parse import urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup
from loguru import logger

from crawler.app.models import Config
from crawler.extractor.utils import (
    SKIP_EXTENSIONS_RE,
    normalize_trailing_slash,
    strip_default_port,
)


class URLForSameDomain:
    """Extract and normalize same-domain page URLs from HTML."""

    def __init__(self, config: Config):
        self.config = config

        base = urlsplit(str(config.base_url))

        self.base_host = strip_default_port(base.scheme, base.netloc)
        self.base_origin = f"{base.scheme}://{self.base_host}"

    def extract_urls(self, html_content: str, base_url: str) -> Set[str]:
        """
        Extract normalized, same-domain, likely-page URLs from HTML.

        Args:
            html_content: Raw HTML content
            base_url: The URL of the page we’re parsing (for resolving relatives)

        Returns:
            Set[str] of normalized absolute URLs
        """
        try:
            soup = BeautifulSoup(html_content, "lxml")
        except Exception as e:
            logger.error(f"Error parsing HTML from {base_url}: {e}")
            return set()

        found: Set[str] = set()

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()

            if (
                not href
                or href.startswith("#")
                or href.lower().startswith("javascript:")
            ):
                continue

            try:
                normalized = self._normalize_url(href, base_url)

                if not normalized:
                    continue

                if not self._is_same_domain(normalized):
                    continue

                if not self._is_valid_page_url(normalized):
                    continue

                found.add(normalized)
            except Exception as e:
                logger.debug(f"Error processing URL '{href}' on {base_url}: {e}")
                continue

        logger.debug(f"Extracted {len(found)} URLs from {base_url}")

        return found

    def _normalize_url(self, raw_url: str, base_url: str) -> str:
        """Resolve relative URLs and produce a normalized absolute URL."""
        absolute = urljoin(base_url, raw_url)
        sp = urlsplit(absolute)

        # Scheme must be http/https
        if sp.scheme not in ("http", "https"):
            return ""

        host = strip_default_port(sp.scheme, sp.netloc)
        path = normalize_trailing_slash(sp.path or "/")

        # Rebuild without fragment
        normalized = urlunsplit((sp.scheme, host, path, sp.query, ""))

        return str(normalized)

    def _is_same_domain(self, abs_url: str) -> bool:
        """Strict same-origin check (no subdomains)."""
        sp = urlsplit(abs_url)

        return strip_default_port(sp.scheme, sp.netloc) == self.base_host

    def _is_valid_page_url(self, abs_url: str) -> bool:
        """Filter schemes, assets, and obvious non-page URLs."""
        sp = urlsplit(abs_url)

        if sp.scheme not in ("http", "https"):
            return False

        # Skip empty/anchor-only or javascript-like links
        if abs_url == "" or (not sp.path and not sp.query):
            return False

        # Skip common asset/document extensions
        if SKIP_EXTENSIONS_RE.search(sp.path):
            return False

        return True
