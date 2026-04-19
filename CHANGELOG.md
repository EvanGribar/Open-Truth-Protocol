# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [Unreleased]

### Added

- **Heuristics Agent** (AGENTS §5.3): Text signal analysis with perplexity and burstiness computation
  - Detects LLM-generated text via statistical signatures
  - Computes mean_perplexity and burstiness metrics
  - Returns synthetic_probability and confidence scores
  - Stubs for image/audio/video analysis (Phase 2)
  - 14 comprehensive unit tests, 100% test pass rate

- **Provenance Agent** (AGENTS §5.2): Document metadata extraction
  - Analyzes document formats (PLAINTEXT, DOCX, PDF, HTML)
  - Checks for C2PA cryptographic manifests (stub for Phase 2)
  - EXIF metadata framework (implementation Phase 2)
  - Timestamp anomaly detection framework
  - 12 comprehensive unit tests, 100% test pass rate

- **Web Consensus Agent** (AGENTS §5.4): Cache-backed lookups and registry checks
  - Text content hashing and cache framework
  - Perceptual hash generation stubs (Phase 2: real pHash)
  - 24-hour cache TTL per AGENTS spec
  - Reverse search framework (APIs Phase 2)
  - 13 comprehensive unit tests, 100% test pass rate

- **Implementation Plan** at `docs/IMPLEMENTATION_PLAN.md`
  - Detailed roadmap for remaining Phase 1 and Phase 2 work
  - TDD patterns and contract-first implementation guidelines
  - Test organization and mocking strategies

### Changed

- Updated `PHASE1_PROGRESS_REPORT.md` with completion status and agent implementation details
- Overall test coverage increased to 53%+ (target: 45%)
- Agent test suite: 39 new tests, all passing

### Changed

- Improved `degraded_mode` logic in orchestrator service to match AGENTS.md §8:
  - Now set to true when 2+ agents fail/timeout OR heuristics is inactive
  - Previously only set when heuristics was inactive
- Updated README with Phase 1 implementation roadmap snapshot
- GitHub issue templates for bug, feature, and security reporting flows
- Pull request template with AGENTS.md contract and benchmark checklist
- Phase 1 backlog workflow document at `.github/project/BACKLOG.md`
- Temporal workflow worker bootstrap in orchestrator service startup
- Orchestrator Temporal activities that dispatch pending jobs and collect reports until completion/timeout
- Unit test coverage for orchestrator activity behavior and pending-job dispatch flow

### Changed

- Improved orchestrator ingest endpoint with better fallback error handling
- Enhanced results endpoint with clearer status logging
- Better error messages for Temporal workflow startup failures
- Standardized quality enforcement on a single canonical CI workflow
- Added `ruff format --check .` to CI and local `make check` gates
- Enabled dependency review failure on moderate-or-higher vulnerabilities
- Tightened Bandit policy to fail on medium severity and confidence findings
- Enforced pytest coverage threshold (`--cov-fail-under=45`)
- Expanded contributor workflow documentation for issue-driven development
- Expanded backlog workflow and issue lifecycle requirements for AGENTS-referenced implementation tasks
- Added a public roadmap snapshot to `README.md` that points to the implementation plan and Phase 1 backlog
- Expanded CODEOWNERS coverage for agents, tests, docs, and CI paths
- Ingest runtime path now starts Temporal workflow execution before job dispatch to Kafka

### Removed

- Removed legacy Python package workflow that targeted unsupported interpreter versions
- Removed legacy pylint workflow that duplicated and conflicted with canonical CI checks
