import pytest


@pytest.fixture
def fake_site():
    """
    In-memory site map shared by tests.
    If a test needs to mutate it, make a copy first (e.g., dict(fake_site)).
    """
    return {
        "https://example.com": {
            "status": 200,
            "html": "<a href='/a'>A</a><a href='https://example.com/b'>B</a>",
            "error": None,
        },
        "https://example.com/a": {
            "status": 200,
            "html": "<a href='/b'>B</a><a href='/c'>C</a>",
            "error": None,
        },
        "https://example.com/b": {"status": 200, "html": "", "error": None},
        "https://example.com/c": {"status": 200, "html": "", "error": None},
    }


@pytest.fixture
def fake_content():
    return """
        <html>
        <body>
            <a href="/a">Relative A</a>
            <a href="b?q=1">Relative B with query</a>
            <a href="https://example.com/c">Absolute same domain</a>

            <!-- Should be skipped -->
            <a href="#section">Anchor</a>
            <a href="javascript:void(0)">JS link</a>
            <a href="https://sub.example.com/d">Subdomain</a>
            <a href="https://other.com/e">Other domain</a>
            <a href="/image.png">Image asset</a>
        </body>
        </html>
    """
