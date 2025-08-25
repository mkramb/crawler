import asyncio
import sys
from typing import Optional

import click
from pydantic import HttpUrl, ValidationError

from crawler.app.models import Config
from crawler.app.runner import Runner
from crawler.collector.page import PageCollector
from crawler.extractor.url import URLForSameDomain


async def format_results_as_text(runner: Runner) -> None:
    async for result in runner.start():
        if getattr(result, "error", None):
            click.secho(f"Error crawling {result.url}: {result.error}", fg="yellow")

        depth = getattr(result, "depth", None)

        if depth == 0:
            click.echo(f"\nStarted at {result.url}:")
        else:
            click.echo(f"\nURLs for {result.url}:")

        found = getattr(result, "found_urls", [])

        if found:
            for url in sorted(found):
                click.echo(f"  - {url}")
        else:
            click.echo("  (no links found)")


@click.command()
@click.argument("base_url")
@click.option(
    "--max-concurrency",
    default=10,
    show_default=True,
    help="Maximum concurrent requests",
)
@click.option(
    "--max-pages-depth",
    default=0,
    help="Maximum crawl depth (unlimited by default)",
)
@click.option(
    "--timeout",
    default=30,
    show_default=True,
    help="Request timeout in seconds",
)
def start_as_cli(
    base_url: str,
    max_concurrency: int,
    max_pages_depth: Optional[int],
    timeout: int,
):
    """
    Python program that accepts a base URL to crawl the site.
    For each page it finds, the script will print the URL of the page and all the URLs it finds on that page.
    """
    try:
        config = Config(
            base_url=HttpUrl(base_url),
            max_concurrency=max_concurrency,
            max_pages_depth=max_pages_depth,
            timeout=timeout,
        )

        runner = Runner(
            config,
            extractor=URLForSameDomain(config),
            collector_factory=lambda cfg: PageCollector(cfg),
        )

        asyncio.run(format_results_as_text(runner))

    except ValidationError as e:
        click.echo(f"\nConfiguration error: {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nCrawling interrupted by user.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"\nUnexpected error: {e}", err=True)
        sys.exit(1)
