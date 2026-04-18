.PHONY: lint type test check

lint:
	uv run ruff check .

type:
	uv run mypy .

test:
	uv run pytest

check: lint type test
