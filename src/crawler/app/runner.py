import asyncio
from collections import deque
from typing import AsyncIterator, Callable, Optional, Set

from loguru import logger

from crawler.app.models import Config, Result
from crawler.collector.api import Collector
from crawler.collector.page import PageCollector
from crawler.extractor.api import URLExtractor


class Runner:
    def __init__(
        self,
        config: Config,
        *,
        extractor: Optional[URLExtractor] = None,
        collector_factory: Callable[[Config], Collector],
    ):
        self.config = config
        self.extractor: URLExtractor = extractor
        self.collector_factory = collector_factory

        # state management
        self.url_queue: deque = deque()
        self.visited_urls: Set[str] = set()

        # starting page has depth 0 (url, depth),
        # we start by adding provided base URL to the queue
        self.url_queue.append((str(config.base_url), 0))

    async def start(self) -> AsyncIterator[Result]:
        """Run the crawler."""
        logger.info(f"Starting crawl of {self.config.base_url}")
        logger.info(f"Configuration={self.config}")

        async with self.collector_factory(self.config) as collector:
            while self.url_queue:
                batch: list[tuple[str, int]] = []

                while len(batch) < self.config.max_concurrency and self.url_queue:
                    url, depth = self.url_queue.popleft()

                    if url not in self.visited_urls:
                        self.visited_urls.add(url)
                        batch.append((url, depth))

                if not batch:
                    break

                tasks = [
                    asyncio.create_task(self._crawl_url(collector, url, depth))
                    for url, depth in batch
                ]

                for completed in asyncio.as_completed(tasks):
                    try:
                        result = await completed
                    except Exception as e:
                        logger.error("Task failed: %s", e, exc_info=True)
                        continue

                    yield result

    async def _crawl_url(
        self, collector: PageCollector, url: str, depth: int
    ) -> Result:
        """Crawl a single URL and extract links as result."""
        result = Result(url=url, depth=depth)

        try:
            page = await collector.fetch_page(url)
            result.status_code = page.status

            if page.error:
                result.error = page.error
            elif page.content:
                found_urls = self.extractor.extract_urls(page.content, url)
                result.found_urls = found_urls

                if (
                    self.config.max_pages_depth == 0
                    or depth < self.config.max_pages_depth
                ):
                    for found_url in found_urls:
                        if found_url not in self.visited_urls:
                            self.url_queue.append((found_url, depth + 1))

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            result.error = f"Unexpected error: {str(e)}"

        return result
