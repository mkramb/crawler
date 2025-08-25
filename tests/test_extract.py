from pydantic import HttpUrl

from crawler.app.models import Config
from crawler.extractor.url import URLForSameDomain


def test_extract_urls(fake_content):
    cfg = Config(base_url=HttpUrl("https://example.com"))
    extractor = URLForSameDomain(cfg)

    base_page = "https://example.com"
    urls = extractor.extract_urls(fake_content, base_page)

    assert urls == {
        "https://example.com/a",
        "https://example.com/b?q=1",
        "https://example.com/c",
    }
