# Open Truth Protocol

Core implementation scaffold for the Open Truth Protocol (OTP) swarm defined in AGENTS.md.

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

## Core Contracts

All architecture and behavioral contracts are defined in AGENTS.md. If implementation diverges from AGENTS.md, AGENTS.md is authoritative.
