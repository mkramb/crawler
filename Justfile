# https://github.com/casey/just

# Don’t echo the recipe commands, before running them
set quiet

default:
  just --list --unsorted

dev-sync:
    uv sync --all-extras

format:
	uv run ruff format

lint:
  uv run ty check --error-on-warning
  uv run ruff check --fix

test:
	uv run pytest --verbose --color=yes tests

validate: format lint test