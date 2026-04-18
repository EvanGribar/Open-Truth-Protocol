# Open Truth Protocol

[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/EvanGribar/Open-Truth-Protocol/badge)](https://scorecard.dev/viewer/?uri=github.com/EvanGribar/Open-Truth-Protocol)
[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/9944/badge)](https://bestpractices.coreinfrastructure.org/projects/9944)

## What is OTP?

**OTP is a decentralized, open-source protocol for specialized AI agents that collectively verify the authenticity of digital media locally on your hardware.**

A piece of media—image, video, audio, or text—is processed by a local orchestrator. Multiple specialized agents analyze it for authenticity signals. A cryptographically anchored `TruthConsensus` record is generated, which can be immutably pinned to IPFS and hashed to a public blockchain. Every verification is:

- **Local-First.** Users run the analysis on their own devices. No media ever leaves the user's control.
- **Transparent.** Each agent surfaces human-readable evidence for its score.
- **Asynchronous.** Agents run in parallel; no single point of failure.
- **Immutable.** Every attestation is permanently auditable via public ledgers.

## Why OTP?

Digital authenticity is broken. Deepfakes are indistinguishable from reality. AI-generated text floods social media. Communities have no way to verify what they see.

Existing solutions are siloed: X, Facebook, and TikTok each have proprietary, black-box labels governed by corporations. OTP inverts this model: **the protocol and execution are owned by the user.**

- **Not a hosted SaaS.** OTP is software you run, not a service you call. No media is ever uploaded to a central server.
- **Not a content moderator.** OTP scores authenticity, not legality. It cannot be weaponized for censorship.
- **Not a black box.** Every score is explainable. If an agent detects synthesis artifacts, it shows you what it found.
- **Not a legal oracle.** OTP scores are probabilistic attestations, not admissible evidence. Communities use them as a baseline for discussion, not as fact.

## Repository Structure

This repository is the core implementation of OTP:

- **`AGENTS.md`** — The authoritative technical contract and Local-First specification.
- **`shared/`** — Contract-first schemas, Redis/IPC logic, and scoring ensemble.
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

**Phase 1 Tracks**: 1-4 Complete ✅ | Track 5 Ready to Finalize

- ✅ **Track 1 (Orchestrator)**: Per-agent timeouts, degraded-mode logic, edge-case coverage
- ✅ **Track 2 (Shared)**: Routing matrix, scoring verdict boundaries, confidence discounting
- ✅ **Track 3 (CLI/Benchmark)**: `otp-verify` CLI tool and `otp-benchmark` evaluation suite
- ✅ **Track 4 (Ledger)**: `LedgerService` interface and no-op commitment integration
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

Run the OTP verification stack locally using Docker (optional for full isolation) or direct Python execution:

```bash
# Start local support services (Redis)
docker compose -f docker/docker-compose.infra.yml up -d
```

After startup, you can verify media via the CLI:

```bash
otp verify path/to/media.jpg
```

## Runtime Flow

1. **Ingest**: File path provided via CLI or local UI.
2. **Normalize**: Orchestrator moves media to local data directory (`~/.otp/data/`).
3. **Dispatch**: Task dispatched to agents via local Redis Pub/Sub.
4. **Analyze**: Agents compute scores in parallel modules.
5. **Consensus**: Orchestrator aggregates results into a `TruthConsensus` report.
6. **Commit (Optional)**: Consensus is pinned to IPFS and hashed to a public ledger.

`POST /internal/results` remains available for local testing and fixture injection.

## Core Contracts

All architecture and behavioral contracts are defined in AGENTS.md. If implementation diverges from AGENTS.md, AGENTS.md is authoritative.
