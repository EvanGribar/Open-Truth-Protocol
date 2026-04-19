# OTP Phase 1 Backlog Structure

This file defines the GitHub Issues backlog structure for Phase 1 implementation.

Detailed sequencing and track-level exit criteria live in `docs/IMPLEMENTATION_PLAN.md`.

## Backlog Model
- Create one Phase 1 epic issue.
- Create child issues for each component listed below.
- Link each child issue to the epic.
- Keep one focused PR per child issue.

## Epic
- `EPIC: Phase 1 MVP completion (AGENTS.md compliant)`

## Child Issue Buckets
1. Orchestrator
- Temporal workflow dispatch and collection
- Timeout and partial-result handling
- Ingest/result API behavior

2. Routing and Scoring Contracts
- Media routing matrix alignment
- Degraded-mode and verdict edge cases
- Shared schema consistency

3. Provenance Agent
- C2PA and metadata extraction behavior
- Text provenance degraded mode

4. Heuristics Agent
- Real signal extraction by media type
- Confidence handling and output normalization

5. Web Consensus Agent
- Web lookup orchestration and caching
- Temporal anomaly and source consistency checks

6. Test and Quality
- Unit/integration coverage expansion
- CI gate hardening

7. Documentation and Release Hygiene
- AGENTS/README/CONTRIBUTING/CHANGELOG sync
- Troubleshooting and contributor workflow notes

## Labels
Apply at minimum:
- `type: feature` or `type: bugfix`
- `area: agents`, `area: shared`, `area: tests`, `area: infra`, or `area: docs`
- optional phase labels: `phase: 1`, `phase: 2`, `phase: 3`

## Milestones
Create milestone: `Phase 1 MVP`.

## Definition of Done for Phase 1
- All child issues closed with linked PRs.
- CI, security, and quality gates passing on `main`.
- Documentation reflects merged behavior.
- `CHANGELOG.md` updated under `Unreleased` for user-visible changes.

## Kickoff Sequence (First 10 Issues)

Create these first to start implementation immediately with small, reviewable slices:

1. `feat(orchestrator): emit degraded_mode in TruthConsensus`
2. `test(orchestrator): add degraded-mode and timeout edge-case coverage`
3. `feat(orchestrator): wire Temporal workflow client and worker bootstrap`
4. `feat(orchestrator): enforce per-agent hard timeout in workflow execution`
5. `feat(shared): align routing matrix behavior with AGENTS.md section 3.5`
6. `feat(provenance): implement document metadata extraction for text/*`
7. `feat(heuristics): replace mock text heuristic path with real signal pipeline`
8. `feat(web-consensus): implement hash cache and source-url consistency checks`
9. `feat(ledger): add ledger commitment service skeleton and contract tests`
10. `docs: update README and CONTRIBUTING for implemented phase-1 behavior`

## Issue Template Addendum (for every implementation issue)

Add this checklist to every issue body before work starts:

- [ ] AGENTS.md section(s) referenced
- [ ] Security implications reviewed
- [ ] Tests identified (unit/integration/e2e)
- [ ] Docs update required paths listed
- [ ] Rollback strategy noted
- [ ] Changelog update needed (`yes/no`) and rationale
