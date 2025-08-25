# crawler

## The Objective

Create a Python app that can be run from the command line that will accept a base URL to crawl the site. For each page it finds, the script will print the URL of the page and all the URLs it finds on that page. The crawler will only process that single domain and not crawl URLs pointing to other domains or subdomains. Please employ patterns that will allow your crawler to run as quickly as possible, making full use any patterns that might boost the speed of the task, whilst not sacrificing accuracy and compute resources. Do not use tools like Scrapy or Playwright. You may use libraries for other purposes such as making HTTP requests, parsing HTML and other similar tasks.

## Development Setup

```
# brew install just
# brew install uv
```

Install dependencies & bootstrap:

```
# uv sync
```

To run format, lint and test check just execute:

```
# just validate
```

## Example Usage

```
# uv run crawler --help
Usage: crawler [OPTIONS] BASE_URL

  Python program that accepts a base URL to crawl the site. For each page it
  finds, the script will print the URL of the page and all the URLs it finds
  on that page.

Options:
  --max-concurrency INTEGER  Maximum concurrent requests  [default: 10]
  --max-pages-depth INTEGER  Maximum crawl depth (unlimited by default)
  --timeout INTEGER          Request timeout in seconds  [default: 30]
  --help                     Show this message and exit.
```

Examples:

```
# uv run crawler https://fleethub.zego.com
# uv run crawler https://www.zego.com/blog/category/food-delivery --max-concurrency 2
```

## Local Setup

For this test assignment I used:

- VSCode, also included initial .vscode settings
- With no direct AI integration just with few direct prompts to ChatGPT

Otherwise for work I usually use:

- Cursor + prompting, not used in agent mode
- Including direct prompts for various (usually local) LLMs

## Main Components

- `Runner` (app/runner.py): orchestration loop that:
  - keeps a queue of (url, depth)
  - tracks a visited set to dedupe
  - schedules up to N async tasks per batch (max_concurrency)
  - streams results as each task completes (using asyncio.as_completed)
- `Collector`, is an async HTTP client (via aiohttp):
  - managed with an async context manager so a single ClientSession
  - connector pool are reused across all requests
- `Extractor`, to parse HTML content:
  - extract & normalize links
  - applies domain filtering

## How to Extend?

What I would do if I had more time:

- Respect robots.txt (including delays)
- Add more tests to achieve full coverage
- Add a JSON formatter for simpler post-processing
- Add retries and fallbacks to avoid nondeterministic behavior
- Add a service to render page with javascript (e.g. to support client side apps)
- Use an actual queue (e.g. redis) to distribute the work across different "workers"
- Support running in parallel per domain to support multiple domains
