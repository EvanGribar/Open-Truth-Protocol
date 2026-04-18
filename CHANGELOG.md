# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [Unreleased]

### Added

- Initial `LedgerService` interface and `NoOpLedgerService` implementation for Phase 1
- `VerificationWorkflow` integration with ledger commitment post-processing
- `otp-verify` CLI tool for submitting and monitoring media verification jobs
- `otp-benchmark` evaluation suite for swarm accuracy tracking
- Orchestrator `consensus_cache` to support asynchronous receipt updates
- Comprehensive orchestrator timeout and degraded-mode test coverage
- Scorer verdict boundary tests covering all 5 verdict bands
- Scorer confidence discount tests validating pull-toward-neutral behavior
- Scorer weight distribution tests validating text vs image weight differences
- Tests for mixed agent status scenarios (SUCCESS/ERROR/TIMEOUT combinations)

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
