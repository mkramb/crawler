import asyncio
from typing import Optional

import aiohttp
from loguru import logger

from crawler.app.models import Config
from crawler.collector.models import PageResult


class PageCollector:
    def __init__(self, config: Config):
        self.session: Optional[aiohttp.ClientSession] = None
        self.config = config

    async def __aenter__(self):
        """Async context manager entry."""
        connector = aiohttp.TCPConnector(
            limit=self.config.max_concurrency,
            limit_per_host=min(self.config.max_concurrency, 5),
        )

        timeout = aiohttp.ClientTimeout(total=self.config.timeout)

        self.session = aiohttp.ClientSession(
            headers={"User-Agent": self.config.user_agent},
            connector=connector,
            timeout=timeout,
        )

        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
        self.session = None

    async def fetch_page(self, url: str) -> PageResult:
        """Fetch page content if available."""
        try:
            async with self.session.get(url) as response:
                status = response.status

                if 200 <= status < 300:
                    try:
                        raw = await response.text()
                        content = raw if raw.strip() else None
                    except Exception as e:
                        logger.warning(f"Decoding failed: {e}")
                        content = None

                    return PageResult(
                        url=url,
                        status=status,
                        content=content,
                        error=None,
                    )

                return PageResult(
                    url=url,
                    status=status,
                    content=None,
                    error=f"HTTP {status}",
                )

        except asyncio.TimeoutError:
            return PageResult(
                url=url,
                status=None,
                content=None,
                error="Timeout",
            )
        except Exception as e:
            return PageResult(
                url=url,
                status=None,
                content=None,
                error=f"Unexpected error: {e}",
            )
