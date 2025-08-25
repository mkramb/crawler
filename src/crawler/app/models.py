from typing import Optional, Set
from urllib.parse import urlparse

from pydantic import BaseModel, Field, HttpUrl, computed_field

DEFAULT_USER_AGENT = "Crawler/1.0"


class Config(BaseModel):
    base_url: HttpUrl
    user_agent: str = DEFAULT_USER_AGENT
    max_concurrency: int = Field(default=10, ge=1, le=100)
    max_pages_depth: Optional[int] = Field(default=0, ge=0, le=100)
    timeout: int = Field(default=30, ge=1, le=120)

    @computed_field(return_type=str)
    @property
    def domain(self) -> str:
        """Extract domain from base URL."""
        parsed = urlparse(str(self.base_url))
        return f"{parsed.scheme}://{parsed.netloc}"

    @computed_field(return_type=str)
    @property
    def base_no_trailing_slash(self) -> str:
        return str(self.base_url).rstrip("/")


class Result(BaseModel):
    url: str
    depth: int = 0
    found_urls: Set[str] = Field(default_factory=set)
    status_code: Optional[int] = None
    error: Optional[str] = None
