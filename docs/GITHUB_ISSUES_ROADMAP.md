# GitHub Issues Roadmap — Phase 1 completion

This roadmap defines the remaining issues to be closed for the official Phase 1 release of the Open Truth Protocol.

## Completed Issues ✅

1. **#1: feat(orchestrator): Implement Temporal worker bootstrap**
   - Wire worker to FastAPI lifespan
   - Register workflows and activities

2. **#3: feat(orchestrator): Implement result collection activity**
   - Activity polls for reports in OrchestratorService
   - Handles timeout and finalization

3. **#4: feat(orchestrator): Enforce per-agent hard timeout**
   - Workflow respects hard_timeout_seconds parameter
   - Synthesizes TIMEOUT results for missing active agents

4. **#6: test(scorer): Comprehensive verdict boundary coverage**
   - Validate [0.14, 0.15], [0.39, 0.40], [0.59, 0.60], [0.84, 0.85] transitions

5. **#7: feat(ledger): Define commitment service and connect orchestrator**
   - Create `LedgerService` interface
   - Add post-consensus commitment step to Temporal workflow

6. **#8: feat(shared): Align routing matrix behavior with AGENTS.md §3.5**
   - Ensure `text/*` routing degrades Provenance weight to 0.10

7. **#10: feat(cli): Create otp-verify tool**
   - Standalone CLI for job submission and monitoring

8. **#11: feat(eval): Initial benchmark.py suite**
   - Swarm accuracy reporting framework

## Open Items ⏭️

9. **#9: docs: Update documentation for Phase 1 completion**
   - Finalize README, AGENTS.md, and CHANGELOG.md

10. **#12: chore(ci): Final security hardening and PR merge**
    - Review Scorecard findings and resolve
    - Merge current feature set to main branch

---
*Reference: AGENTS.md v2.2*
