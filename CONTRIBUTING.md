# Contributing

OTP follows AGENTS.md as the authoritative implementation contract.

## Development Workflow

Use GitHub Issues as the backlog source of truth.

1. Create or pick a scoped issue.
2. Create a branch that matches labeler conventions (`feat/...`, `fix/...`, `docs/...`, `chore/...`).
3. Open a pull request using `.github/pull_request_template.md` and link the issue.
4. Keep one focused PR per issue for clean review and rollback paths.

Use this flow for all Phase 1 implementation work:

1. Create or select an issue from `.github/project/BACKLOG.md`.
2. Add labels before coding: one `type:*`, one `area:*`, and `phase: 1`.
3. Add acceptance criteria that reference AGENTS.md section numbers.
4. Keep branch and PR title aligned to issue scope only.
5. Close issue only after merge and documentation updates land.

Backlog structure for Phase 1 is documented in `.github/project/BACKLOG.md`.

## GitHub Backlog Operations

Recommended GitHub CLI workflow:

```bash
gh issue list --label "phase: 1"
gh issue create --title "feat(orchestrator): ..." --body-file .github/ISSUE_TEMPLATE/feature-request.md
gh pr create --fill --body-file .github/pull_request_template.md
```

If you are not using GitHub CLI, follow the same sequencing manually in the web UI.

## Issue and PR Templates

Use the provided templates:

- `.github/ISSUE_TEMPLATE/bug-report.md`
- `.github/ISSUE_TEMPLATE/feature-request.md`
- `.github/ISSUE_TEMPLATE/security-vulnerability.md`
- `.github/pull_request_template.md`

## Quality Gates

All pull requests must pass:

- `ruff check .`
- `ruff format --check .`
- `mypy .`
- `pytest`

For scoring and model-logic changes, include benchmark evidence in the pull request.

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
uv run ruff format --check .
uv run mypy .
uv run pytest
```

4. Or run all quality checks with one command:

```bash
make check
```
