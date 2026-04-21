# Changelog

All notable changes to the Open Truth Protocol project are documented in this file.

## [Project Pivot] April 2026

### BREAKING CHANGES
- **Project scope completely refocused** from multi-modal media verification (images, video, audio) to **100% accuracy AI-generated text detection**
- All legacy agent code (Orchestrator, Provenance, Heuristics, Web Consensus) is archived
- Repository is now documentation-first, with code to follow

### Added
- **SPECIFICATION.md** — Complete technical specification for 100% accuracy in text detection
- **RESEARCH_ROADMAP.md** — Four-phase validation roadmap (Q2 2026 → 2027)
- **DATASETS.md** — Data collection, annotation, and benchmarking protocols
- **ALGORITHMS.md** — Detailed specifications for 8 core detection signals
- Multi-signal detection approach: Perplexity, Entropy, Semantic Coherence, Syntactic Uniformity, Burstiness, Linguistic Markers, Word Frequency, Punctuation

### Changed
- **README.md** — Completely rewritten to reflect text detection mission
- **AGENTS.md** — Now serves as project transition document; references new specification files

### Removed
- Active development of image/video/audio detection (moved to future phases)
- Docker containers for legacy agents (agents/ directory archived)
- Temporal.io and Kafka infrastructure specifications

### Status
- Phase 1 (Signal Research): In progress
- Phase 2 (Ensemble & Tuning): Pending Phase 1 completion
- Phase 3 (Adversarial Testing): Pending Phase 2 completion
- Phase 4 (Production): Pending Phase 3 completion

### Migration Guide
Users of the previous version should:
1. Archive any code depending on legacy agents
2. Refer to SPECIFICATION.md for the new architecture
3. See RESEARCH_ROADMAP.md for current development priorities

---

## [2.2] — Local-First Architecture Transition
- Transitioned from centralized (Kafka + S3) to Local-First (Redis + local storage)
- Reduced system requirements for local execution
- Introduced Python Asyncio for orchestration (replacing Temporal.io)

## [2.1] — Multi-Agent Foundation
- Implemented core 5-agent architecture
- Added comprehensive test suite (60+ tests, 58%+ coverage)
- Published initial AGENTS.md specification

## [2.0] — Project Launch
- Initial open-source release
- Multi-modal media verification framework (images, video, audio, text)
- Agent-based distributed architecture
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
