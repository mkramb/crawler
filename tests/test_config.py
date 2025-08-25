import pytest
from pydantic import HttpUrl, ValidationError

from crawler.app.models import Config


def test_config_accepts_http_and_https():
    ok1 = Config(base_url=HttpUrl("http://example.com"))
    ok2 = Config(base_url=HttpUrl("https://example.com"))

    assert ok1.domain == "http://example.com"
    assert ok2.domain == "https://example.com"


def test_config_rejects_unsupported_scheme():
    with pytest.raises(ValidationError):
        Config(base_url=HttpUrl("ftp://example.com"))


def test_domain_property_normalizes_netloc():
    cfg1 = Config(base_url=HttpUrl("https://example.com/foo/bar"))
    cfg2 = Config(base_url=HttpUrl("https://test.example.com/foo/bar"))

    assert cfg1.domain == "https://example.com"
    assert cfg2.domain == "https://test.example.com"
