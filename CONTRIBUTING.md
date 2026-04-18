# Contributing

OTP follows AGENTS.md as the authoritative implementation contract.

## Quality Gates

All pull requests must pass:

- `ruff check .`
- `mypy .`
- `pytest`

Use pre-commit hooks to run checks locally before push:

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

## Contract Change Policy

If you modify schema fields, score logic, or verdict behavior:

1. Update AGENTS.md in the same pull request.
2. Keep backward compatibility where possible.
3. Add tests proving expected behavior.

## Local Setup

1. Install dependencies:

```bash
uv sync --extra dev
```

2. Start local dependencies:

```bash
docker compose up -d
```

3. Run checks:

```bash
uv run ruff check .
uv run mypy .
uv run pytest
```

4. Or run all quality checks with one command:

```bash
make check
```
