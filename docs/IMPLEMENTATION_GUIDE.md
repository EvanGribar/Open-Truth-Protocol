# OTP Phase 1 Implementation Guide - Getting Started

**Status**: Ready for Developers  
**Target Audience**: Contributors starting on Track 3+ implementation  
**Last Updated**: 2026-04-17

---

## Quick Navigation

- **🎯 Want to contribute?** → Start at [Contribution Workflow](#contribution-workflow)
- **🔧 Setting up locally?** → Jump to [Local Development](#local-development)
- **📋 Need a specific task?** → See [GitHub Issues](https://github.com/EvanGribar/Open-Truth-Protocol/issues)
- **📖 Understanding the architecture?** → Read [AGENTS.md](../AGENTS.md)

---

## Current Status (As of 2026-04-17)

### ✅ Completed (Track 1-2)
- Orchestrator core logic (dispatch, collect, timeout handling)
- Scoring model with all verdict boundaries
- Comprehensive test coverage (60 tests, 58% coverage)
- Routing matrix validated for all media types
- GitHub issues roadmap created

### ⚠️ In Progress (Track 3 Ready to Start)
- **Heuristics Agent**: Text signal pipeline (perplexity, burstiness)
- **Provenance Agent**: Document metadata extraction (DOCX, PDF, HTML)
- **Web Consensus Agent**: Cache-backed lookups, source consistency

### ❌ Not Yet Started (Track 4-5)
- Ledger commitment integration
- Final documentation sync

---

## Contribution Workflow

### Step 1: Pick an Issue

Go to the [GitHub Issues](https://github.com/EvanGribar/Open-Truth-Protocol/issues) tab and select one:

**Recommended Starting Issues** (ordered by priority):
1. `feat(orchestrator): enforce per-agent hard timeouts` — Already ~90% done
2. `feat(heuristics): implement real text signal pipeline` — High impact
3. `feat(provenance): text metadata extraction` — Well-defined scope
4. `feat(web-consensus): cache-backed lookup` — Clean API contract

### Step 2: Create a Feature Branch

```bash
cd /path/to/opentruthprotocol

# Create a focused branch named after the issue
git checkout -b feat/heuristics-text-signals
# or
git checkout -b feat/provenance-text-metadata
# or
git checkout -b feat/web-consensus-cache
```

### Step 3: Implement with AGENTS.md as Your Contract

**Critical Rule**: Every line of code must trace back to AGENTS.md.

Before implementing, review:
- **AGENTS.md §5** — Your agent specification
- **AGENTS.md §3.5** — Media type routing (which paths apply to you)
- **AGENTS.md §6** — Output schema your agent must produce
- **AGENTS.md §7** — Scoring integration (how your scores are weighted)

**Example**: Implementing heuristics text signals?
- Read AGENTS.md §5.3 (Synthetic Heuristics Agent)
- Find the section: "Text path:"
- See the exact output schema required (payload fields, confidence, etc.)
- Implement exactly to that schema

### Step 4: Write Tests First

**Test-Driven Development Pattern** (per Karpathy Guidelines):

```python
# tests/unit/test_heuristics_text.py - Write this FIRST
import pytest
from agents.heuristics.analyzer import analyze

def test_analyze_synthetic_text_high_probability():
    """GPT-generated text should score high synthetic probability."""
    synthetic_text = "The rapid advancement of artificial intelligence has revolutionized..."
    result = analyze("text/plain", synthetic_text)
    
    assert result["synthetic_probability"] > 0.8
    assert result["confidence"] > 0.7
    assert "perplexity" in result["signals"]
    assert "burstiness" in result["signals"]

def test_analyze_human_text_low_probability():
    """Real human writing should score low synthetic probability."""
    human_text = "I went to the store. It was raining. The milk was expired."
    result = analyze("text/plain", human_text)
    
    assert result["synthetic_probability"] < 0.3
    assert result["confidence"] > 0.6

# THEN implement to make tests pass
```

### Step 5: Run Local Quality Gates

Before pushing, verify:

```bash
# Run tests
uv run pytest tests/unit/test_<your_agent>.py -v

# Format code
uv run ruff format agents/<your_agent>/

# Check lint
uv run ruff check agents/<your_agent>/

# Type check
uv run mypy agents/<your_agent>/

# All gates at once
make check

# Check coverage
uv run pytest --cov=agents/<your_agent> --cov-report=term-missing
```

### Step 6: Update Documentation

**Files to update for every PR**:
1. `CHANGELOG.md` — Add entry under [Unreleased]
2. Agent docstring — Document your implementation approach
3. Test file docstrings — Explain what each test validates

**Example CHANGELOG entry**:
```markdown
## [Unreleased]

### Added
- Heuristics agent text perplexity scoring with segment-level analysis (AGENTS §5.3)
- Burstiness metric for detecting LLM-generated content
- 8 comprehensive tests for text signal extraction
```

### Step 7: Commit with AGENTS References

**Commit message format**:
```
feat(heuristics): implement text perplexity and burstiness signals

- Add real token-level perplexity computation via transformers
- Implement segment-level (100-token) burstiness metric
- Match output schema exactly per AGENTS §5.3
- Add 8 tests covering synthetic/human text boundaries

AGENTS References: §5.3 (Synthetic Heuristics Agent), §6.1 (TruthConsensus)
```

### Step 8: Create a Pull Request

**PR checklist** (from [.github/pull_request_template.md](../.github/pull_request_template.md)):

- [ ] AGENTS.md section(s) referenced in description
- [ ] Tests added or updated
- [ ] `make check` passes (lint, format, type, test)
- [ ] Coverage maintained or improved
- [ ] CHANGELOG.md updated under [Unreleased]
- [ ] Documentation updated (docstrings, comments)
- [ ] Security implications reviewed
- [ ] Issue link included

---

## Local Development

### Prerequisites

```bash
# Install uv (Python package manager)
# https://docs.astral.sh/uv/

# Clone the repo
git clone https://github.com/EvanGribar/Open-Truth-Protocol.git
cd Open-Truth-Protocol

# Install dependencies
uv sync --extra dev

# Install pre-commit hooks (optional but recommended)
pre-commit install
```

### Running Infrastructure

Start Kafka, Redis, S3, Temporal, and all agents:

```bash
# Terminal 1: Start infrastructure
docker compose up -d

# Verify services are running
docker compose ps

# Check Temporal UI
open http://localhost:8088

# Check Prometheus metrics
open http://localhost:9090
```

### Running Tests Locally

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_orchestrator_service.py -v

# Run with coverage
uv run pytest --cov=agents --cov=shared --cov-report=html
# Open htmlcov/index.html to see coverage

# Run with detailed output
uv run pytest -vvs

# Run only failing tests (useful for iterating)
uv run pytest --lf
```

### Common Development Tasks

#### Add a new dependency

```bash
# Add to pyproject.toml dependencies
uv add transformers torch  # for ML models

# Or add as dev dependency
uv add --dev pytest-benchmark
```

#### Debug a failing test

```bash
# Run with detailed traceback
uv run pytest tests/unit/test_orchestrator_service.py -vv --tb=long

# Drop into debugger on failure
uv run pytest tests/unit/test_orchestrator_service.py --pdb

# Show print statements
uv run pytest -s
```

#### Check what changed

```bash
# See uncommitted changes
git diff

# See staged changes
git diff --staged

# See changes in a specific file
git diff agents/heuristics/analyzer.py
```

---

## Agent Implementation Patterns

### Pattern 1: Real Signal Computation

**Example: Heuristics text perplexity**

```python
# agents/heuristics/analyzer.py
from transformers import AutoModelForCausalLM, AutoTokenizer

def analyze(media_type: str, content: str = "") -> dict[str, object]:
    """Analyze media for synthetic indicators per AGENTS §5.3."""
    
    if media_type.startswith("text/"):
        return _analyze_text(content)
    
    # ... image/video/audio paths ...

def _analyze_text(text: str) -> dict[str, object]:
    """Text path per AGENTS §5.3."""
    
    # Load model once (cache it!)
    model = _load_model()
    
    # Compute perplexity segment-by-segment
    segments = _split_text(text, window=100)
    perplexities = [_compute_perplexity(model, seg) for seg in segments]
    
    # Calculate burstiness (variance)
    burstiness = _compute_burstiness(perplexities)
    mean_perplexity = sum(perplexities) / len(perplexities)
    
    # Map to synthetic probability
    synthetic_prob = _score_synthetic(mean_perplexity, burstiness)
    
    return {
        "synthetic_probability": synthetic_prob,
        "confidence": 0.85,  # Adjust based on signal strength
        "signals": {
            "mean_perplexity": mean_perplexity,
            "burstiness": burstiness,
            "high_synthetic_segments": [
                {"start_char": 0, "end_char": 100, "probability": 0.92}
            ],
        },
        "anomalies_detected": ["low_burstiness"] if burstiness < 0.1 else [],
        "heuristics_score": 1.0 - synthetic_prob,
    }
```

### Pattern 2: Metadata Extraction

**Example: Provenance DOCX parsing**

```python
# agents/provenance/analyzer.py
from python_docx import Document
from datetime import datetime

def analyze(media_type: str, blob_uri: str = "") -> dict[str, object]:
    """Analyze media provenance per AGENTS §5.2."""
    
    if media_type.startswith("text/"):
        return _analyze_text_metadata(blob_uri)
    
    # ... image/video/audio paths ...

def _analyze_text_metadata(blob_uri: str) -> dict[str, object]:
    """Text path: extract document metadata per AGENTS §5.2."""
    
    # Download from S3
    doc_bytes = _download_from_s3(blob_uri)
    
    # Try DOCX first
    if _is_docx(doc_bytes):
        doc = Document(io.BytesIO(doc_bytes))
        props = doc.core_properties
        
        return {
            "c2pa_manifest_present": False,
            "document_metadata": {
                "creator": props.author,
                "created_date": props.created.isoformat() if props.created else None,
                "modified_date": props.modified.isoformat() if props.modified else None,
                "creator_tool": props.application,
                "revision_count": props.revision,
            },
            "ai_tool_signature_match": _check_ai_signatures(props.application),
            "timestamp_anomaly": _check_timestamp_anomaly(props.created, props.modified),
            "provenance_score": 0.45,  # Per AGENTS §7 text weights
        }
```

### Pattern 3: Cache Integration

**Example: Web Consensus cache**

```python
# agents/web_consensus/analyzer.py
import redis
import hashlib

_cache: redis.Redis | None = None

def analyze(media_type: str, blob_uri: str = "") -> dict[str, object]:
    """Analyze per AGENTS §5.4 with cache per AGENTS §5.4."""
    
    if media_type.startswith("text/"):
        return _analyze_text_with_cache(blob_uri)

def _analyze_text_with_cache(blob_uri: str) -> dict[str, object]:
    """Text: check cache first, then do lookup per AGENTS §5.4."""
    
    cache = _get_cache()
    
    # Download and hash
    content = _download_from_s3(blob_uri)
    content_hash = hashlib.sha256(content).hexdigest()
    
    # Check cache (24h TTL per AGENTS §5.4)
    cache_key = f"otp:web_consensus:text:{content_hash}"
    cached = cache.get(cache_key)
    
    if cached:
        logger.info("cache_hit", cache_key=cache_key)
        metrics.cache_hits.inc()  # Prometheus per AGENTS §4.4
        return json.loads(cached)
    
    # Cache miss - do lookup (when APIs implemented)
    result = _do_web_lookup(content)
    
    # Store in cache with 24h TTL
    cache.setex(cache_key, 86400, json.dumps(result))
    
    return result
```

---

## Testing Strategy

### Unit Tests (Fast, Local)

```python
# tests/unit/test_heuristics_text.py
# These run in < 100ms, no external calls

def test_high_synthetic_probability_for_gpt_output():
    """GPT-generated text should score high."""
    text = "The advancement of technology has..."
    result = analyze("text/plain", text)
    assert result["synthetic_probability"] > 0.8

def test_low_synthetic_for_human_text():
    """Human writing should score low."""
    text = "I went to the store yesterday. It was nice."
    result = analyze("text/plain", text)
    assert result["synthetic_probability"] < 0.3
```

### Integration Tests (Slower, Hit APIs)

```python
# tests/integration/test_heuristics_end_to_end.py
# These might hit external APIs, take longer

@pytest.mark.integration
def test_heuristics_orchestrator_integration():
    """Full flow: ingest → dispatch → heuristics analyze → score."""
    # Create job
    # Wait for result
    # Verify consensus score includes heuristics
    pass
```

### Benchmark Tests (Performance)

```python
# tests/benchmarks/test_heuristics_perf.py
import pytest

@pytest.mark.benchmark
def test_text_analysis_performance(benchmark):
    """Ensure analysis stays under P95 SLA of 5s per AGENTS §5.3."""
    text = "..." * 1000  # Long text
    
    result = benchmark(analyze, "text/plain", text)
    # Benchmark will fail if > 5s
```

---

## Code Review Checklist

When reviewing a PR, verify:

### Architecture
- [ ] Code follows AGENTS.md contract exactly
- [ ] Output schema matches specification
- [ ] No agent calls another agent directly (Kafka only)
- [ ] All external APIs have retry logic

### Testing
- [ ] Tests written before implementation (TDD)
- [ ] Edge cases covered (empty input, very long, malformed)
- [ ] Coverage maintained or improved
- [ ] No flaky tests (deterministic, no timeouts)

### Code Quality
- [ ] Linting passes (`ruff check`)
- [ ] Formatting passes (`ruff format --check`)
- [ ] Type checking passes (`mypy --strict`)
- [ ] No hardcoded secrets or credentials
- [ ] No print statements in production code (use logging)

### Documentation
- [ ] CHANGELOG.md updated
- [ ] AGENTS.md section referenced in PR description
- [ ] Docstrings added/updated
- [ ] README updated if behavior changed

### Performance
- [ ] Meets SLA target per AGENTS §5:
  - Provenance: 3s P95 (8s hard timeout)
  - Heuristics: 15s P95 (30s hard timeout)
  - Web Consensus: 20s P95 (45s hard timeout)
- [ ] No N+1 queries or loops
- [ ] Caching used where specified

---

## Troubleshooting

### Issue: Tests fail with "coverage below 45%"

**Solution**: When running a single test file, coverage can be low. Always run full suite:
```bash
uv run pytest  # Full suite
# Not: uv run pytest tests/unit/test_heuristics.py
```

### Issue: Type checker errors on Kafka/Temporal imports

**Solution**: Some libraries have incomplete type stubs. Add to `pyproject.toml`:
```toml
[[tool.mypy.overrides]]
module = ["aiokafka.*", "temporalio.*"]
ignore_missing_imports = true
```

### Issue: Docker Compose fails to start

**Solution**:
```bash
# Clean and rebuild
docker compose down -v
docker compose build --no-cache
docker compose up -d

# Check logs
docker compose logs kafka
docker compose logs temporal
```

### Issue: Redis connection refused

**Solution**:
```bash
# Verify Redis is running
docker compose ps redis

# Connect and test
docker compose exec redis redis-cli ping
# Should return: PONG
```

---

## Resources

- **[AGENTS.md](../AGENTS.md)** — Authoritative specification
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** — Contribution guidelines
- **[GitHub Issues Roadmap](./GITHUB_ISSUES_ROADMAP.md)** — 13 issues ready to implement
- **[Phase 1 Progress Report](./PHASE1_PROGRESS_REPORT.md)** — What's been done
- **[README.md](../README.md)** — Quick start

---

## Getting Help

1. **Check existing tests** — `tests/unit/` has examples for every agent
2. **Read AGENTS.md §5 for your agent** — Complete specification
3. **Look at passing tests** — Understand expected behavior
4. **Ask on GitHub Issues** — Tag maintainers with questions

---

**Ready to contribute?** Pick an issue from [GitHub Issues Roadmap](./GITHUB_ISSUES_ROADMAP.md) and start coding! 🚀
