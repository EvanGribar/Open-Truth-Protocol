# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [Unreleased]

### Added

- OSS governance baseline documents (license, code of conduct, security policy)
- Contributor tooling configuration for local quality gate automation
- Expanded onboarding and local development guidance
- Kafka worker loops for heuristics, provenance, and web consensus agents
- Agent-side Redis-backed deduplication enforcement on task_id
- Orchestrator background consumer for `otp.results.*` result aggregation
- Docker Compose wiring for all three analysis agents

### Changed

- Standardized quality enforcement on a single canonical CI workflow
- Added `ruff format --check .` to CI and local `make check` gates
- Enabled dependency review failure on moderate-or-higher vulnerabilities
- Tightened Bandit policy to fail on medium severity and confidence findings
- Enforced pytest coverage threshold (`--cov-fail-under=45`)

### Removed

- Removed legacy Python package workflow that targeted unsupported interpreter versions
- Removed legacy pylint workflow that duplicated and conflicted with canonical CI checks
