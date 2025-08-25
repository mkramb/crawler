from pydantic import HttpUrl

from crawler.app.models import Config
from crawler.app.runner import Runner
from crawler.collector.models import PageResult
from crawler.extractor.url import URLForSameDomain
from crawler.extractor.utils import normalize_trailing_slash


class FakeCollector:
    def __init__(self, _cfg: Config, fake_site: dict[str, dict]):
        self.fake_site = fake_site

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def fetch_page(self, url: str) -> PageResult:
        entry = self.fake_site.get(normalize_trailing_slash(url))

        if entry is None:
            return PageResult(url=url, status=404, content="", error=None)
        return PageResult(
            url=url,
            status=entry["status"],
            content=entry["html"],
            error=entry["error"],
        )


async def test_runner_traversal(fake_site):
    config = Config(
        base_url=HttpUrl("https://example.com"),
        max_concurrency=5,
        max_pages_depth=0,
    )

    runner = Runner(
        config,
        extractor=URLForSameDomain(config),
        collector_factory=lambda cfg: FakeCollector(cfg, fake_site),
    )

    seen_urls: list[str] = []
    by_url: dict[str, PageResult] = {}

    async for res in runner.start():
        seen_urls.append(res.url)
        by_url[res.url] = res

    root_variants = {"https://example.com", "https://example.com/"}

    assert any(r in set(seen_urls) for r in root_variants)

    assert "https://example.com/a" in seen_urls
    assert "https://example.com/b" in seen_urls
    assert "https://example.com/c" in seen_urls
