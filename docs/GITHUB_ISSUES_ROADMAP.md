# GitHub Issues Roadmap - Phase 1 Implementation (OTP v0.1.0)

**Status**: Ready to create on GitHub  
**Created**: 2026-04-17  
**Target Completion**: 2026-05-01

## Overview

This document defines the issue sequence for Phase 1 MVP completion. Each issue maps to AGENTS.md sections and includes Definition of Done criteria.

---

## 🔒 Security & Quality Gates (Create First)

### [CRITICAL] Issue #1: Security Audit - Code and Infrastructure
**Type**: `type:security` `area:infra`  
**Priority**: CRITICAL  
**Depends on**: None  

**Description**:
```
Conduct comprehensive security audit of all code paths per OWASP Top 10 and code-scanning output.

Checklist:
- [ ] Review code for SQL injection risks (AGENTS §5 agent paths)
- [ ] Audit all external API calls for SSRF protection (AGENTS §5.4)
- [ ] Validate secret handling (no hardcoded keys, all env var-based)
- [ ] Check S3 operations for path traversal vulnerabilities
- [ ] Verify Kafka client configs (SSL/TLS, SASL in prod)
- [ ] Review Docker configs for non-root execution, image pinning
- [ ] Run `uv run bandit -r agents/ shared/` and resolve findings
- [ ] Run GitHub CodeQL and secret scanning, triage all findings
- [ ] Document any findings in SECURITY.md with mitigation plan

AGENTS Sections: §4 (Infrastructure Contracts), §11 (Environment Variables)
```

**Exit Criteria**:
- All Bandit/CodeQL/secret-scan findings triaged with resolution
- No P1 vulnerabilities remain
- SECURITY.md updated with response procedures
- PR includes security audit checklist

---

### [CRITICAL] Issue #2: GitHub Dependabot and Supply Chain Setup
**Type**: `type:chore` `area:infra`  
**Priority**: CRITICAL  
**Depends on**: None  

**Description**:
```
Enable Dependabot for dependency updates and verify GitHub Code Scanning.

Checklist:
- [ ] Enable Dependabot version updates (weekly, auto-merge minor/patch)
- [ ] Enable Dependabot security alerts
- [ ] Verify CodeQL workflow is enabled and running
- [ ] Configure dependency review to fail on medium+ severity
- [ ] Create SECURITY.md vulnerability disclosure process
- [ ] Pin all Docker image versions (no latest tags)
- [ ] Document supply chain review process in CONTRIBUTING.md

AGENTS Sections: §13 (Contributor Rules), §11 (Environment Variables)
```

**Exit Criteria**:
- Dependabot enabled with auto-merge for safe updates
- All CI workflows green
- SECURITY.md has vulnerability reporting instructions

---

## ✅ Orchestrator Hardening (Track A)

### Issue #3: Enforce Per-Agent Hard Timeouts in Temporal Workflow
**Type**: `type:feature` `area:orchestrator`  
**Priority**: HIGH  
**Depends on**: None  
**Estimate**: 4h  

**Description**:
```
Implement hard timeout enforcement per AGENTS §8 for each agent in the Temporal workflow.

**Current State**:
- Temporal activities dispatch jobs but don't enforce per-agent timeouts

**Requirements** (AGENTS §8):
| Agent | Soft SLA (P95) | Hard Timeout | On Timeout |
|-------|---|---|---|
| Provenance | 3s | 8s | Mark timeout, continue |
| Heuristics | 15s | 30s | Mark timeout, continue |
| Web Consensus | 20s | 45s | Mark timeout, continue |

**Implementation**:
1. Create Temporal activity `await_agent_result_with_timeout(agent: str, task_id: str)` that uses asyncio.wait_for()
2. Modify VerificationWorkflow to execute activities in parallel with timeout per agent
3. On timeout, return synthetic ResultEnvelope with status=TIMEOUT
4. Pass all results to scorer even if some timed out

**Code Changes**:
- agents/orchestrator/workflow.py: Add timeout parameters to workflow execution
- agents/orchestrator/activities.py: Add await_agent_result_with_timeout activity
- shared/constants.py: Add AGENT_TIMEOUTS dict

AGENTS Sections: §3.3 (Temporal), §5.1 (Orchestrator), §8 (Error Handling)
```

**Exit Criteria**:
- Workflow enforces per-agent hard timeouts
- Tests verify timeout behavior via mocked delays
- Timeout results properly formatted per ResultEnvelope schema
- `make check` passes

---

### Issue #4: Emit `degraded_mode` Flag in TruthConsensus
**Type**: `type:feature` `area:orchestrator`  
**Priority**: HIGH  
**Depends on**: Issue #3  
**Estimate**: 2h  

**Description**:
```
Add degraded_mode flag to TruthConsensus output when 2+ agents fail/timeout.

**Current State**:
- TruthConsensus schema includes degraded_mode but it's never set

**Requirements** (AGENTS §6.1, §8):
- If 2+ agents have status != SUCCESS → degraded_mode = true
- Include caveat in documentation that score is partial
- Emit explicit warning to logs when degraded mode triggered

**Implementation**:
1. Update shared/scorer.py compute_truth_score() to detect 2+ failures
2. Set degraded_mode = true in returned TruthConsensus
3. Add test case forcing 2+ timeouts and verifying flag

AGENTS Sections: §2 (What OTP Is Not), §6.1 (TruthConsensus), §8 (Error Handling)
```

**Exit Criteria**:
- degraded_mode set correctly in all edge cases
- Tests verify 1 failure (degraded=false), 2+ failures (degraded=true)
- Documentation in README explains degraded mode semantics

---

### Issue #5: Comprehensive Orchestrator Edge-Case Test Coverage
**Type**: `type:test` `area:tests`  
**Priority**: HIGH  
**Depends on**: Issue #4  
**Estimate**: 6h  

**Description**:
```
Expand test coverage for orchestrator timeout, partial results, and degraded-mode scenarios.

**Test Cases to Add**:
1. Complete results (all agents respond on time)
2. Partial results (1 agent times out, score computed from 2)
3. Multiple timeouts (2+ agents timeout → forced INCONCLUSIVE)
4. Unknown task error handling
5. Timeout and error mixed (1 timeout + 1 error → degraded_mode true)
6. Verdict mapping for boundary scores per AGENTS §6.2
7. Confidence discounting applied correctly per AGENTS §7

**Coverage Goal**: 85%+ for orchestrator service and workflow paths

AGENTS Sections: §6.2 (Verdict Mapping), §7 (Scoring Model), §8 (Error Handling)
```

**Exit Criteria**:
- Test coverage for orchestrator/ reaches 85%
- All edge cases covered with explicit test names
- `pytest --cov=agents/orchestrator` shows 85%+

---

## 🛣️ Routing and Scoring (Track B)

### Issue #6: Validate Media Routing Matrix Against AGENTS.md §3.5
**Type**: `type:feature` `area:shared`  
**Priority**: HIGH  
**Depends on**: None  
**Estimate**: 3h  

**Description**:
```
Ensure routing logic exactly matches AGENTS.md §3.5 media type matrix.

**Current State**:
- routing.py exists but needs comprehensive test coverage

**Matrix to Test** (AGENTS §3.5):
| Agent | image/* | video/* | audio/* | text/* |
|-------|---------|---------|---------|--------|
| Provenance | ✅ Full | ✅ Full | ⚠️ EXIF only | ⚠️ Document metadata only |
| Heuristics | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| Web Consensus | ✅ Full | ✅ Full | ⚠️ Audio fingerprint only | ✅ Full |

**Implementation**:
1. Create comprehensive test_routing.py with parametrized tests for all media types
2. Add tests for edge cases: unknown media types, empty types, malformed strings
3. Update docstring in routing.py to reference §3.5

AGENTS Sections: §3.5 (Media Type Routing)
```

**Exit Criteria**:
- All media type + agent combinations tested
- Routing table matches AGENTS.md exactly
- Tests include edge case validation

---

### Issue #7: Scorer Confidence Discount and Verdict Boundary Coverage
**Type**: `type:test` `area:shared`  
**Priority**: HIGH  
**Depends on**: None  
**Estimate**: 4h  

**Description**:
```
Add comprehensive tests for scorer behavior per AGENTS.md §7 (Scoring Model).

**Test Cases to Add**:
1. Confidence discounting: score pulled toward 0.5 when confidence < 0.60
2. Weight redistribution: when provenance C2PA missing, weight redistributes
3. All verdict boundaries (AGENTS §6.2):
   - 0.85-1.00 → LIKELY_AUTHENTIC
   - 0.60-0.84 → UNVERIFIED
   - 0.40-0.59 → INCONCLUSIVE
   - 0.15-0.39 → LIKELY_SYNTHETIC
   - 0.00-0.14 → SYNTHETIC
4. Text weights vs image weights (different weight models)
5. Missing agent (agent didn't respond) → weight redistributes
6. Final score normalization when total_weight < 1.0

AGENTS Sections: §6.2 (Verdict Mapping), §7 (Scoring Model)
```

**Exit Criteria**:
- Test coverage for scorer.py reaches 90%+
- All scoring edge cases covered with explicit assertions
- Verdict boundaries verified exhaustively

---

## 🔍 Agent Signal Pipelines (Track C)

### Issue #8: Heuristics Agent - Implement Real Text Signal Pipeline
**Type**: `type:feature` `area:heuristics`  
**Priority**: HIGH  
**Depends on**: None  
**Estimate**: 8h  

**Description**:
```
Replace mock text heuristics with real perplexity, burstiness, and signal pipeline.

**Current State**:
- agents/heuristics/analyzer.py returns mock data

**Requirements** (AGENTS §5.3):
For text/*:
- Compute token-level perplexity against reference LM
- Compute per-segment (100 tokens) perplexity
- Calculate burstiness (variance of per-segment perplexity)
- Flag synthetic_probability based on signals
- Include confidence score
- Surface anomalies_detected list

**Implementation**:
1. Load pre-trained reference LM (e.g., GPT2 or RoBERTa) at agent startup
2. Tokenize and compute perplexity per segment
3. Calculate burstiness metric
4. Set synthetic_probability based on signal thresholds (tunable)
5. Return full signals dict per AGENTS §5.3 output payload

**Dependencies**:
- transformers, torch (add to pyproject.toml dev extras)

AGENTS Sections: §5.3 (Synthetic Heuristics Agent)
```

**Exit Criteria**:
- Real perplexity computed for text input
- Output payload matches AGENTS §5.3 schema
- Tests verify signal extraction on known synthetic text
- Agent still passes routing checks (non-text routes skip analysis)

---

### Issue #9: Provenance Agent - Text Metadata Extraction
**Type**: `type:feature` `area:provenance`  
**Priority**: HIGH  
**Depends on**: None  
**Estimate**: 6h  

**Description**:
```
Implement document metadata extraction for text/* payloads (DOCX, PDF, HTML).

**Current State**:
- agents/provenance/analyzer.py returns mock data for text

**Requirements** (AGENTS §5.2, §3.5):
For text/* (degraded mode):
- Extract OOXML core properties from .docx (creator, created_date, modified_date, revision_count)
- Extract XMP metadata from PDF (CreatorTool, CreateDate, Producer)
- Detect AI tool signatures (Jasper, Copy.ai, Writer, etc.) via creator_tool field
- Extract <meta> author tags from HTML/Markdown
- Flag timestamp anomalies (created vs submitted)
- Return provenance_score: 0.45 (weaker signal per §7)

**Implementation**:
1. Use python-docx for .docx parsing
2. Use pypdf for PDF XMP extraction
3. Maintain ai_tool_signatures.json list
4. Return degraded payload matching AGENTS §5.2

**Dependencies**:
- python-docx, pypdf (add to pyproject.toml)

AGENTS Sections: §5.2 (Cryptographic Provenance Agent, text path), §3.5 (Media Routing)
```

**Exit Criteria**:
- DOCX/PDF/HTML metadata extracted when present
- AI tool detection working
- Output schema matches AGENTS §5.2
- Tests cover both text and non-text paths

---

### Issue #10: Web Consensus Agent - Cache and Source Consistency
**Type**: `type:feature` `area:web_consensus`  
**Priority**: HIGH  
**Depends on**: None  
**Estimate**: 6h  

**Description**:
```
Implement Redis-backed cache and source URL consistency checks for web consensus.

**Current State**:
- agents/web_consensus/analyzer.py returns mock data

**Requirements** (AGENTS §5.4):
- Cache pHash lookup results with 24h TTL
- Cache normalized text SHA256 with 24h TTL
- Log cache hits to Prometheus (otp_webconsensus_cache_hits_total)
- Check source_url from client_metadata against fetched content
- Flag temporal anomalies (article claims 2026 but references from 2023)
- Return source_url_content_match boolean

**Implementation**:
1. Connect to Redis on startup
2. Hash by media (pHash for images, SHA256 for text)
3. On cache hit, return cached result
4. On cache miss, log cache miss and return synthetic result (for now, until external APIs added)
5. Add web_consensus_score calculation

**Dependencies**:
- redis (already in dependencies)

AGENTS Sections: §5.4 (Web Consensus Agent), §4.4 (Observability)
```

**Exit Criteria**:
- Cache hits working with 24h TTL
- Prometheus metrics exported
- Source URL consistency checks implemented
- Tests verify cache hit/miss behavior

---

## 🔗 Ledger Commitment (Track D)

### Issue #11: Ledger Commitment Service Skeleton and Contract Tests
**Type**: `type:feature` `area:ledger`  
**Priority**: MEDIUM  
**Depends on**: None  
**Estimate**: 4h  

**Description**:
```
Add Ledger Commitment Agent service skeleton and contract-first tests.

**Current State**:
- Ledger commitment not integrated into runtime

**Requirements** (AGENTS §5.5):
- Create LedgerCommitmentService class
- Define contract: receives TruthConsensus, returns ledger_receipt
- Add stub for IPFS pinning and blockchain write
- Integrate into orchestrator post-score flow
- Add timeout/failure-safe return (return TruthConsensus without receipt on failure)
- Add retry queue for failed commits

**Implementation**:
1. Create agents/ledger/service.py with LedgerCommitmentService
2. Add activities/workflow hooks in orchestrator
3. Create contract tests (no actual blockchain calls)
4. Mock IPFS and blockchain for now

AGENTS Sections: §5.5 (Ledger Commitment Agent), §4.3 (Result Publishing Contract)
```

**Exit Criteria**:
- LedgerCommitmentService class created with contract tests
- Integrated into orchestrator flow (as stub)
- Tests verify success and failure paths

---

## 📖 Documentation and Release (Track E)

### Issue #12: Synchronize AGENTS.md, README, and CHANGELOG
**Type**: `type:docs` `area:docs`  
**Priority**: CRITICAL  
**Depends on**: Issues #3-11 (after implementation)  
**Estimate**: 4h  

**Description**:
```
Ensure all documentation reflects implemented behavior and roadmap.

**Checklist**:
- [ ] Update README.md with Phase 1 completion status
- [ ] Update AGENTS.md §5 with actual implementation notes (e.g., "Text metadata extraction done via python-docx")
- [ ] Update CHANGELOG.md under [Unreleased] with all merged PRs
- [ ] Add roadmap snapshot showing Phase 1 complete, Phase 2 upcoming
- [ ] Add troubleshooting section in CONTRIBUTING.md for common dev issues
- [ ] Verify all code examples in docs are runnable
- [ ] Add implementation notes section to AGENTS.md if gaps discovered

AGENTS Sections: §13 (Contributor Rules), §12 (Roadmap)
```

**Exit Criteria**:
- All docs updated and internally consistent
- Roadmap reflects actual completion status
- No dangling references to unimplemented features

---

### Issue #13: Final Quality Gate and Release Preparation
**Type**: `type:chore` `area:infra`  
**Priority**: CRITICAL  
**Depends on**: Issue #12  
**Estimate**: 3h  

**Description**:
```
Final quality checks, tags, and release readiness.

**Checklist**:
- [ ] All tests passing: `uv run pytest -v`
- [ ] All lint/format/type checks passing: `make check`
- [ ] Coverage ≥ 50% (current: 57.42%)
- [ ] No active GitHub Issues in Phase 1 scope
- [ ] No active security findings
- [ ] Docs build and render correctly
- [ ] Create git tag `v0.1.0-alpha` (or appropriate version)
- [ ] Create GitHub Release with CHANGELOG excerpt
- [ ] Update version in pyproject.toml to 0.2.0-dev

AGENTS Sections: §13 (Contributor Rules)
```

**Exit Criteria**:
- All CI workflows green
- Tag created on main
- GitHub Release published with migration notes

---

## 📊 Recommended Sequencing

**Week 1** (Issues 1-2, 3-5):
- Days 1-2: Security audit, Dependabot setup
- Days 3-5: Orchestrator hardening (timeouts, degraded mode, tests)

**Week 2** (Issues 6-10):
- Days 1-2: Routing and scoring validation
- Days 3-5: Agent signal pipelines (heuristics text, provenance text, web consensus cache)

**Week 3** (Issues 11-13):
- Days 1-2: Ledger commitment skeleton
- Days 3: Documentation sync
- Day 4: Final release prep

**Parallel (Always Open)**:
- Dependabot PRs (auto-merge safe updates)
- Code scanning findings (triage and resolve)

---

## Labels to Apply (All Issues)

```
Area: [ area:orchestrator | area:agents | area:shared | area:tests | area:infra | area:docs | area:ledger ]
Type: [ type:feature | type:bugfix | type:test | type:security | type:chore ]
Phase: [ phase:1 | phase:2 | phase:3 ]
Priority: [ priority:critical | priority:high | priority:medium | priority:low ]
```

---

## Definition of Done (Every PR)

- [ ] AGENTS.md section(s) referenced in description
- [ ] Tests added or updated
- [ ] `make check` passes (lint, format, type, test)
- [ ] Coverage maintained or improved
- [ ] CHANGELOG.md updated under [Unreleased]
- [ ] Documentation updated if behavior changed
- [ ] Security implications reviewed (if applicable)
- [ ] PR linked to GitHub issue(s)

---

## Related Files

- Main spec: [AGENTS.md](../AGENTS.md)
- Implementation plan: [docs/IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)
- Quick start: [README.md](../README.md)
- Contributing guide: [CONTRIBUTING.md](../CONTRIBUTING.md)
