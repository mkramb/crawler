from typing import Protocol, Set


class URLExtractor(Protocol):
    def extract_urls(self, html: str, base_url: str) -> Set[str]: ...
