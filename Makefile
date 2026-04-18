.PHONY: lint type test check precommit

lint:
	uv run ruff check .

type:
	uv run mypy .

test:
	uv run pytest

precommit:
	uv run pre-commit run --all-files

check: lint type test
