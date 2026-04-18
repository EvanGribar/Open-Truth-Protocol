# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [Unreleased]

### Added

- Comprehensive routing matrix tests for all media types (image, video, audio, text)
- Edge-case routing tests for missing/empty agent sets
- Extended scorer tests for confidence discount behavior and verdict boundaries
- Media-type weight validation tests showing text vs. image weight differences
- C2PA absence weight redistribution tests
- Tests for single vs. multiple agent failure verdict handling
- Enhanced error handling and logging in orchestrator service and main API
- Comprehensive validation and error messages for agent result ingestion
- Failure count tracking in consensus building for improved degraded-mode detection
- Structured logging with task context throughout orchestrator lifecycle
- Enhanced test coverage for error handling paths and edge cases (57.42% project coverage)
- Tests for timeout synthesis, inactive agent rejection, and degraded mode validation
- OSS governance baseline documents (license, code of conduct, security policy)
- Contributor tooling configuration for local quality gate automation
- Expanded onboarding and local development guidance
- AGENTS-aligned implementation execution plan at `docs/IMPLEMENTATION_PLAN.md`
- Kafka worker loops for heuristics, provenance, and web consensus agents
- Agent-side Redis-backed deduplication enforcement on task_id
- Orchestrator background consumer for `otp.results.*` result aggregation
- Docker Compose wiring for all three analysis agents
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
- Expanded CODEOWNERS coverage for agents, tests, docs, and CI paths
- Ingest runtime path now starts Temporal workflow execution before job dispatch to Kafka

### Removed

- Removed legacy Python package workflow that targeted unsupported interpreter versions
- Removed legacy pylint workflow that duplicated and conflicted with canonical CI checks
