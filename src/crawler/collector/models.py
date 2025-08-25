from typing import Optional

from pydantic import BaseModel


class PageResult(BaseModel):
    url: str
    status: Optional[int] = None
    content: Optional[str] = None
    error: Optional[str] = None
