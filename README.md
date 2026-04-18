# Open Truth Protocol

Core implementation scaffold for the Open Truth Protocol (OTP) swarm defined in AGENTS.md.

## Repository Standards

This repository is maintained for public open-source collaboration.

- `AGENTS.md` is the authoritative technical contract.
- `CONTRIBUTING.md` defines the quality gate for all pull requests.
- `CODE_OF_CONDUCT.md` defines collaboration behavior expectations.
- `SECURITY.md` defines responsible vulnerability disclosure.

## Current Scope

This repository currently includes:

- Contract-first shared schemas and scoring logic
- Core service skeletons for Orchestrator, Heuristics, and Provenance
- Strict linting, type checking, and test gates
- CI workflow for quality enforcement

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
uv run mypy .
```

4. Run all local quality gates:

```bash
make check
```

## Local Infrastructure

Start Kafka, Redis, S3 emulation, Weaviate, Temporal, and the Orchestrator API:

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

## Core Contracts

All architecture and behavioral contracts are defined in AGENTS.md. If implementation diverges from AGENTS.md, AGENTS.md is authoritative.
