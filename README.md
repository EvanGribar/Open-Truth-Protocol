# Open Truth Protocol

Core implementation scaffold for the Open Truth Protocol (OTP) swarm defined in AGENTS.md.

## Repository Standards

This repository is maintained for public open-source collaboration.

- `AGENTS.md` is the authoritative technical contract.
- `CONTRIBUTING.md` defines the quality gate for all pull requests.
- `CODE_OF_CONDUCT.md` defines collaboration behavior expectations.
- `SECURITY.md` defines responsible vulnerability disclosure.
- `.github/project/BACKLOG.md` defines the issue-driven Phase 1 execution model.

## Current Scope

This repository currently includes:

- Contract-first shared schemas and scoring logic
- Kafka worker runtime for Heuristics, Provenance, and Web Consensus agents
- Orchestrator ingest API with background Kafka result collection
- Strict linting, format checking, type checking, and test coverage gates
- CI workflow for quality enforcement

## Roadmap

**Phase 1 Implementation Status**: Tracks 1-2 Complete ✅ | Tracks 3-5 Ready to Start

The public execution order is tracked in four documents:
- **[docs/GITHUB_ISSUES_ROADMAP.md](docs/GITHUB_ISSUES_ROADMAP.md)** — 13 detailed GitHub issues with estimation, dependencies, and DoD criteria
- **[docs/IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md)** — Developer quick-start with patterns and examples
- **[docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)** — Track-level sequencing and cross-functional dependencies
- **[docs/PHASE1_PROGRESS_REPORT.md](docs/PHASE1_PROGRESS_REPORT.md)** — Detailed status on completed work

**Phase 1 Tracks**:
1. ✅ **Track 1 (Orchestrator)**: Enforce per-agent timeouts, emit degraded_mode, timeout edge-case coverage
2. ✅ **Track 2 (Shared)**: Validate routing matrix, scorer confidence/verdict boundaries (60/60 tests, 58% coverage)
3. ⏭️ **Track 3 (Agents)**: Real signal pipelines (text heuristics, text provenance, web cache) — Ready to start
4. ⏭️ **Track 4 (Ledger)**: Commitment service skeleton and contract tests
5. ⏭️ **Track 5 (Release)**: Documentation sync and Phase 1 completion

## Contributing

**Want to contribute?** Start here:

1. Read [AGENTS.md](AGENTS.md) § for your task
2. Follow [docs/IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md) for the dev workflow
3. Pick an issue from [docs/GITHUB_ISSUES_ROADMAP.md](docs/GITHUB_ISSUES_ROADMAP.md)
4. Create a focused branch and implement per TDD pattern
5. Run `make check` to verify all quality gates
6. Open a PR referencing the AGENTS.md section

## Quick Start

1. Install dependencies:

```bash
uv sync --extra dev
```

2. Run tests:

```bash
uv run pytest
```

3. Run lint and type checks:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy .
```

4. Run all local quality gates:

```bash
make check
```

## Backlog and Review Flow

1. Create or pick a GitHub issue from [docs/GITHUB_ISSUES_ROADMAP.md](docs/GITHUB_ISSUES_ROADMAP.md).
2. Follow the dev workflow in [docs/IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md).
3. Implement on a focused branch with TDD pattern.
4. Open a PR with `.github/pull_request_template.md`, referencing AGENTS.md section(s).
5. Ensure all checks pass (`make check`, tests, coverage) before merge.

**Important**: Keep AGENTS.md, roadmap, GitHub issues, and CHANGELOG synchronized with each merged PR.

## Local Infrastructure

Start Kafka, Redis, S3 emulation, Weaviate, Temporal, Orchestrator API, and all analysis agents:

```bash
docker compose up --build
```

Or start only infra dependencies:

```bash
docker compose -f docker/docker-compose.infra.yml up -d
```

After startup:

- API health: `http://localhost:8000/health`
- Temporal UI: `http://localhost:8088`

## Runtime Flow

1. Submit a job with `POST /ingest`.
2. Orchestrator starts a Temporal verification workflow for the task.
3. Workflow dispatch activity publishes the job to `otp.jobs.<task_id>`.
4. Agent workers consume jobs, run analysis, and publish to `otp.results.<task_id>`.
5. Orchestrator background consumer aggregates reports, and workflow collect activity finalizes on completion or timeout.
6. Consensus is served at `GET /results/{task_id}`.

`POST /internal/results` remains available for local testing and fixture injection.

## Core Contracts

All architecture and behavioral contracts are defined in AGENTS.md. If implementation diverges from AGENTS.md, AGENTS.md is authoritative.
