# Open Truth Protocol

[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/EvanGribar/Open-Truth-Protocol/badge)](https://scorecard.dev/viewer/?uri=github.com/EvanGribar/Open-Truth-Protocol)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/9944/badge)](https://bestpractices.coreinfrastructure.org/projects/9944)

## What is OTP?

**OTP is a decentralized, open-source swarm of AI agents that collectively verify the authenticity of digital media.**

A piece of media—image, video, audio, or text—enters the pipeline. Multiple specialized agents analyze it for authenticity signals. A cryptographically anchored `TruthConsensus` record exits, immutably pinned to IPFS and hashed to a public blockchain. Every verification is:

- **Transparent.** Each agent surfaces human-readable evidence for its score
- **Asynchronous.** Agents run in parallel; no single point of failure
- **Immutable.** Every attestation is permanently auditable
- **Extensible.** Any developer can write and submit a new agent for inclusion

## Why OTP?

Digital authenticity is broken. Deepfakes are indistinguishable from reality. AI-generated text floods social media. Communities have no way to verify what they see.

Existing solutions are siloed: X has a fact-check label, Facebook has a label, TikTok has a label—each proprietary, each a black box, each governed by a corporation. OTP inverts this model: **the protocol is owned by the community.**

- **Not a content moderator.** OTP scores authenticity, not legality. It cannot be weaponized for censorship.
- **Not a black box.** Every score is explainable. If an agent detects synthesis artifacts, it shows you what it found.
- **Not a legal oracle.** OTP scores are probabilistic attestations, not admissible evidence. Communities use them as a baseline for discussion, not as fact.

## Repository Structure

This repository is the core implementation of OTP:

- **`AGENTS.md`** — The authoritative technical contract. Every agent, every interface, every timeout lives here.
- **`shared/`** — Contract-first schemas, Kafka client, routing matrix, and scoring logic
- **`agents/`** — Orchestrator, Heuristics, Provenance, and Web Consensus agents
- **`tests/`** — Comprehensive unit and integration tests (60+ tests, 58%+ coverage)

## Contributing Guidelines

This repository is maintained for public open-source collaboration:

- **`AGENTS.md`** is the authoritative technical contract.
- **`CONTRIBUTING.md`** defines the quality gate for all pull requests.
- **`CODE_OF_CONDUCT.md`** defines collaboration behavior expectations.
- **`SECURITY.md`** defines responsible vulnerability disclosure.
- **GitHub Issues** and `.github/project/BACKLOG.md` track the Phase 1 execution model.

## Current Implementation Status

**Phase 1 Tracks**: 1-2 Complete ✅ | Tracks 3-5 Ready to Start

- ✅ **Track 1 (Orchestrator)**: Per-agent timeouts, degraded-mode logic, edge-case coverage
- ✅ **Track 2 (Shared)**: Routing matrix, scoring verdict boundaries, confidence discounting
- ⏭️ **Track 3 (Agents)**: Real signal pipelines (text heuristics, text provenance, web cache)
- ⏭️ **Track 4 (Ledger)**: Commitment service and smart contract
- ⏭️ **Track 5 (Release)**: Documentation finalization and Phase 1 completion

## How to Contribute

**Start here:**

1. Read [AGENTS.md](AGENTS.md) for your task's section and the [Implementation Guide](docs/IMPLEMENTATION_GUIDE.md) for execution patterns
2. Follow [CONTRIBUTING.md](CONTRIBUTING.md) for the development workflow
3. Pick an issue from the GitHub Issues backlog or [.github/project/BACKLOG.md](.github/project/BACKLOG.md)
4. Create a focused branch and implement with tests
5. Run quality gates (see Quick Start) to verify all requirements
6. Open a PR with clear reference to AGENTS.md section(s)


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

## Backlog & Issue Workflow

The source of truth for Phase 1 work is GitHub Issues. Structure:

1. **Create an issue** referencing the relevant AGENTS.md section(s)
2. **Add labels** before coding: one `type:*`, one `area:*`, optionally `phase: 1`
3. **Implement on a branch** with tests and documentation updates
4. **Open a PR** using `.github/pull_request_template.md`
5. **Keep AGENTS.md, README.md, and CHANGELOG.md in sync**

See `.github/project/BACKLOG.md` for the Phase 1 issue structure and child issue templates.

**Important**: Every merged PR should have a corresponding CHANGELOG entry under `Unreleased`.

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
