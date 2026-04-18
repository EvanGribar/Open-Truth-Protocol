# Contributing

OTP follows AGENTS.md as the authoritative implementation contract.

## Quality Gates

All pull requests must pass:

- `ruff check .`
- `mypy .`
- `pytest`

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

2. Run checks:

```bash
uv run ruff check .
uv run mypy .
uv run pytest
```
