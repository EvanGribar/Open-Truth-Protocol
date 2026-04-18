.PHONY: lint format type test check precommit

lint:
	uv run ruff check .

format:
	uv run ruff format --check .

type:
	uv run mypy .

test:
	uv run pytest

precommit:
	uv run pre-commit run --all-files

check: lint format type test
