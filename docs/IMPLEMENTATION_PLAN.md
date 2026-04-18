# OTP Implementation Plan (AGENTS.md v2.2)

This plan translates AGENTS.md into a clean, issue-driven execution sequence for open-source delivery.

## Objective
Ship a Phase 1-complete OTP core that is contract-aligned, testable, and easy for external contributors to extend.

## Operating Principles
- AGENTS-first: implementation follows AGENTS.md; any contract change updates AGENTS.md in the same PR.
- Small PRs: one issue, one focused branch, one focused PR.
- Test before merge: behavior changes require unit tests; scoring/agent logic changes require benchmark evidence where applicable.
- No hidden behavior: degraded mode, timeouts, and retries are explicit in outputs and docs.

## Current Gap Snapshot (as of 2026-04-17)
1. Temporal workflow path is wired for dispatch/collection, but deeper integration test coverage is still expanding.
2. Ledger commitment agent path is not implemented in runtime flow.
3. Agent analyzers are deterministic placeholders rather than production signal pipelines.
4. Routing/scoring contracts mostly exist, but edge-case behavior needs stronger test coverage.

## Execution Order

### Track A: Orchestrator Contract Completion
- Deliverables:
  - Wire Temporal client + worker bootstrap for verification workflow.
  - Replace placeholder Temporal activities with real dispatch/collect integrations.
  - Enforce per-agent hard timeout behavior from AGENTS §8.
  - Return partial reports and force `INCONCLUSIVE` on 2+ timeout/error agents.
- AGENTS references: §3.3, §5.1, §6.1, §8
- Exit criteria:
  - Tests cover complete, partial, timeout, and unknown-task flows.
  - API behavior documented in README.

### Track B: Shared Contracts and Scoring Hardening
- Deliverables:
  - Verify media routing matrix alignment to AGENTS §3.5.
  - Verify weight model and confidence discount behavior against AGENTS §7.
  - Add edge-case tests for missing confidence, timed-out agents, and forced `INCONCLUSIVE` rules.
- AGENTS references: §3.5, §6.2, §7, §8
- Exit criteria:
  - Routing/scorer tests cover all media families and verdict boundaries.

### Track C: Provenance Agent (Pragmatic v1)
- Deliverables:
  - Keep API contract stable while incrementally implementing text metadata extraction path.
  - Add signature-list scaffolding for known AI writing tools.
  - Preserve "missing C2PA is not fake" semantics.
- AGENTS references: §5.2
- Exit criteria:
  - Text payload fields populated deterministically from parsed metadata when available.
  - Unit tests for `text/*` and non-text behavior.

### Track D: Heuristics Agent (Pragmatic v1)
- Deliverables:
  - Replace placeholder text scoring with segmented signal calculations.
  - Preserve explicit signal reporting structure (`signals`, `anomalies_detected`, `confidence`).
  - Keep confidence-based neutral pull behavior in final score path.
- AGENTS references: §5.3, §7
- Exit criteria:
  - Outputs remain schema-compatible and include stable confidence + signal details.
  - Unit tests cover both text and non-text branches.

### Track E: Web Consensus Agent (Pragmatic v1)
- Deliverables:
  - Implement cache-first behavior for image/text hash lookups.
  - Add source URL consistency checks and temporal anomaly scaffolding.
  - Emit cache hit metric.
- AGENTS references: §5.4, §4.4
- Exit criteria:
  - Deterministic tests for cache hit/miss and source-url matching semantics.

### Track F: Ledger Commitment Integration
- Deliverables:
  - Add ledger commitment service interface and stub integration path.
  - Integrate post-score invocation in orchestrator path.
  - Add fallback behavior for ledger timeout/failure with retry queue placeholder.
- AGENTS references: §5.5, §8
- Exit criteria:
  - Consensus returns without ledger on failure; behavior documented and tested.

### Track G: Release Hygiene and OSS Maintainability
- Deliverables:
  - Keep README, CONTRIBUTING, BACKLOG, and CHANGELOG synchronized each PR.
  - Require issue references and AGENTS section references in every implementation PR.
  - Keep CI gates strict and green.
- AGENTS references: §13
- Exit criteria:
  - No contract/documentation drift at merge time.

## Recommended Issue Sequencing (Next 12)
1. feat(orchestrator): wire temporal workflow worker bootstrap
2. feat(orchestrator): replace placeholder collect_results activity
3. feat(orchestrator): enforce per-agent hard timeouts
4. test(orchestrator): partial results and forced inconclusive coverage
5. feat(shared): routing matrix contract tests for all media prefixes
6. test(shared): scorer confidence discount and verdict boundary coverage
7. feat(provenance): text metadata extraction for docx/pdf/html
8. test(provenance): text degraded-mode payload contract
9. feat(heuristics): segmented text signal pipeline
10. feat(web-consensus): cache-backed lookup and source-url consistency checks
11. feat(ledger): add commitment service and orchestrator integration stub
12. docs: synchronize AGENTS, README, CONTRIBUTING, CHANGELOG after runtime milestones

## Definition of Done (Per Issue)
- AGENTS section references included in issue and PR.
- Tests added or updated for behavioral changes.
- `make check` passes locally.
- Documentation updated if behavior, config, or workflow changed.
- CHANGELOG updated under Unreleased.

## Branch and PR Naming
- Branches: `feat/...`, `fix/...`, `test/...`, `docs/...`, `chore/...`
- PR titles: `<type>(<area>): <summary>`
- Example: `feat(orchestrator): enforce per-agent hard timeouts`

## Risk Controls
- Do not merge scoring logic changes without benchmark evidence.
- Do not add new runtime dependencies without security and maintenance justification.
- Do not broaden scope mid-PR; open a follow-up issue instead.
