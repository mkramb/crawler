import re

SKIP_EXTENSIONS_RE = re.compile(
    r"\.(?:pdf|docx?|xlsx?|pptx?|zip|rar|7z|tar|gz|jpg|jpeg|png|gif|bmp|svg|webp|mp3|mp4|avi|mov|wmv|flv|css|js|ico|xml|json)$",
    re.IGNORECASE,
)


def strip_default_port(scheme: str, netloc: str) -> str:
    """Lowercase host; strip :80 for http and :443 for https"""
    host = netloc.lower()

    if (scheme == "http" and host.endswith(":80")) or (
        scheme == "https" and host.endswith(":443")
    ):
        host = host.rsplit(":", 1)[0]

    return host


def normalize_trailing_slash(path: str) -> str:
    """Keep "/" for root, strip trailing slash otherwise"""
    if path == "/":
        return path

    return path[:-1] if path.endswith("/") else path
