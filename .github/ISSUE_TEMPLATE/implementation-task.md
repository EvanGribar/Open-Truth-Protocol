---
name: Implementation Task
about: Execute a scoped coding task tied to AGENTS.md contracts.
title: "[TASK] "
labels: ["type: feature", "phase: 1"]
---

## Summary
Describe the implementation slice in one paragraph.

## AGENTS.md References
List exact sections that define expected behavior.

## Scope
- [ ] Orchestrator
- [ ] Provenance
- [ ] Heuristics
- [ ] Web Consensus
- [ ] Ledger
- [ ] Shared/Infra
- [ ] Tests
- [ ] Docs

## Acceptance Criteria
- [ ] Behavior change is explicit and testable
- [ ] Edge cases are covered
- [ ] Existing contracts remain compatible (or are intentionally versioned)

## Security Review
Describe input validation, secret handling, and failure-mode implications.

## Test Plan
List unit/integration/e2e coverage to add or update.

## Documentation Plan
List exact files to update (README, CONTRIBUTING, AGENTS, CHANGELOG, etc.).

## Rollback Plan
Describe how to revert safely if regressions appear.

## Done Checklist
- [ ] `make check` passes locally
- [ ] PR links this issue with `Closes #<id>`
- [ ] Changelog update reviewed (`required` or `not required` with reason)
