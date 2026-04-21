# Open Truth Protocol: AI-Generated Text Detection

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/EvanGribar/Open-Truth-Protocol/badge)](https://scorecard.dev/viewer/?uri=github.com/EvanGribar/Open-Truth-Protocol)

## Mission

**Achieve 100% accuracy in detecting AI-generated text.**

Open Truth Protocol is an open-source research and engineering effort to build the most accurate, transparent, and reproducible system for identifying AI-generated text. We treat this as a solved problem that requires rigorous, verifiable methodology—not probabilistic heuristics.

## The Problem

AI-generated text is indistinguishable from human writing at scale. Current detection systems are:

- **Unreliable.** Detection rates vary wildly (40-90%) depending on model, language, and domain.
- **Black-box.** Proprietary systems offer no transparency into their methodology.
- **Non-reproducible.** Academic detectors are often built on proprietary datasets and cannot be audited by the community.
- **Model-dependent.** Detectors trained on GPT-3 fail on Claude, Gemini, Llama, etc.

**Result:** There is no reliable, open, verifiable way to detect AI-generated text in the wild.

## Our Approach

OTP pursues 100% accuracy through:

1. **Multi-signal analysis.** Perplexity, burstiness, entropy patterns, linguistic markers, semantic consistency, and more.
2. **Comprehensive benchmarking.** Systematic evaluation across all major LLMs (OpenAI, Anthropic, Google, Meta, Open-source).
3. **Transparent methodology.** Every detection signal is explained. No black-box neural networks without interpretability.
4. **Open datasets.** All training and test data are publicly available for community auditing.
5. **Reproducible results.** All code, metrics, and results are published in peer-review format.

## What's In This Repository

- **`SPECIFICATION.md`** — The authoritative technical specification for 100% accuracy.
- **`RESEARCH_ROADMAP.md`** — Our research priorities and validation methodology.
- **`DATASETS.md`** — Data collection, annotation, and benchmark protocols.
- **`ALGORITHMS.md`** — Detailed signal descriptions and scoring logic.

## Why Open?

Text detection is a **scientific problem**, not a product problem. It requires:

- Open data for validation
- Reproducible methodology
- Peer review and scrutiny
- Community collaboration across institutions

We are publishing this as open-source to ensure the findings benefit society, not a single company or service.

## Current Status

**Phase 1:** Research and specification. We are defining the 100% accuracy target through systematic analysis of LLM outputs and human text.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for collaboration guidelines.

## License

MIT. See [LICENSE](LICENSE) for details.

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
