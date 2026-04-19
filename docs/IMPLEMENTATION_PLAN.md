# Phase 1 Agent Implementation Plan

**Status:** In Progress  
**Last Updated:** April 19, 2026  
**Target:** Complete agent implementations + 75%+ test coverage

## Executive Summary

This document outlines the execution plan to complete Phase 1 of OTP by implementing the three analysis agents (Heuristics, Provenance, Web Consensus) and bringing test coverage to 75%+.

**Current State:**
- Orchestrator: 90% complete (dispatch, timeout, scoring)
- Heuristics: 5% (stub with hardcoded test values)
- Provenance: 5% (stub with hardcoded test values)
- Web Consensus: 15% (stub with hardcoded test values)
- Test Coverage: 58%
- Infrastructure: Kafka/Temporal hybrid (functional, per-spec refactor deferred)

**What This Plan Will Deliver:**
- ✅ Full heuristics agent (text + image signal detection)
- ✅ Full provenance agent (metadata extraction + C2PA)
- ✅ Full web consensus agent (caching + reverse lookup)
- ✅ 75%+ test coverage
- ✅ Security audit + fixes
- ✅ Updated documentation

---

## Execution Strategy

### Principle 1: Test-Driven Development
Every agent implementation follows TDD:
```
1. Write failing test(s) for the expected behavior
2. Implement minimum code to make tests pass
3. Refactor for clarity (if needed)
4. Document the implementation
```

### Principle 2: Contract-First Implementation
Every line of code must trace back to AGENTS.md:
- **AGENTS §5.3** → Heuristics agent spec
- **AGENTS §5.2** → Provenance agent spec
- **AGENTS §5.4** → Web Consensus agent spec
- **AGENTS §6** → Shared data schemas
- **AGENTS §7** → Scoring integration

### Principle 3: Surgical Changes
- No speculative features
- No "nice-to-have" abstractions
- Focus on core signal detection logic
- Keep dependencies minimal

---

## Agent Implementation Roadmap

### Phase 1A: Heuristics Agent (HIGH PRIORITY)

**Location:** `agents/heuristics/`

**Responsibilities** (per AGENTS §5.3):
1. **Text Analysis:** Compute perplexity and burstiness to detect LLM-generated text
2. **Frequency Analysis:** Detect periodic grid artifacts from diffusion models (images)
3. **PRNU Extraction:** Compare sensor noise patterns (images)

**Stack:** PyTorch 2.x, Hugging Face Transformers

**Implementation Approach:**

```python
# agents/heuristics/analyzer.py

def analyze(media_type: str, file_path: str) -> dict[str, object]:
    """Analyze media per AGENTS §5.3."""
    if media_type.startswith("text/"):
        return _analyze_text(file_path)
    elif media_type.startswith("image/"):
        return _analyze_image(file_path)
    elif media_type.startswith("audio/"):
        return _analyze_audio(file_path)
    elif media_type.startswith("video/"):
        return _analyze_video(file_path)
    return {}

def _analyze_text(file_path: str) -> dict[str, object]:
    """Text path: perplexity + burstiness (AGENTS §5.3 Text path)."""
    content = _read_file(file_path)
    
    # Compute perplexity using HF Transformers
    mean_perplexity = _compute_mean_perplexity(content)
    burstiness = _compute_burstiness(content)
    
    # Map to synthetic probability
    synthetic_prob = _score_text_synthetic(mean_perplexity, burstiness)
    
    return {
        "synthetic_probability": synthetic_prob,
        "confidence": 0.85,
        "signals": {
            "mean_perplexity": mean_perplexity,
            "burstiness": burstiness,
        },
        "heuristics_score": 1.0 - synthetic_prob,
    }
```

**Test Strategy:**
- Test with known LLM outputs (e.g., GPT-4 samples) → expect high synthetic_prob
- Test with authentic text samples → expect low synthetic_prob
- Test edge cases (very short text, code, structured data)
- Mock ML models for unit tests (avoid GPU requirements in CI)

**Success Criteria:**
- ✅ Text perplexity computation implemented
- ✅ Burstiness metric computation implemented
- ✅ Synthetic probability mapping functional
- ✅ Image/video/audio stub implementations (return reasonable defaults)
- ✅ 100% of heuristics-related tests passing
- ✅ Docstrings match AGENTS §5.3

---

### Phase 1B: Provenance Agent (HIGH PRIORITY)

**Location:** `agents/provenance/`

**Responsibilities** (per AGENTS §5.2):
1. **C2PA Extraction:** Validate cryptographic manifests
2. **EXIF Evaluation:** Flag timestamp anomalies
3. **Document Inspection:** Extract OOXML and PDF metadata

**Stack:** `c2pa-python`, `pyca/cryptography`, `Pillow`, `exiftool` (subprocess)

**Implementation Approach:**

```python
# agents/provenance/analyzer.py

def analyze(media_type: str, file_path: str) -> dict[str, object]:
    """Analyze media provenance per AGENTS §5.2."""
    if media_type.startswith("text/"):
        return _analyze_text_metadata(file_path)
    elif media_type.startswith("image/"):
        return _analyze_image_provenance(file_path)
    # ... video, audio paths ...
    return {}

def _analyze_text_metadata(file_path: str) -> dict[str, object]:
    """Text path: extract document metadata (AGENTS §5.2 Text path)."""
    
    # Read file bytes
    file_bytes = _read_file(file_path)
    
    # Try DOCX
    if _is_docx(file_bytes):
        doc = Document(io.BytesIO(file_bytes))
        props = doc.core_properties
        return _docx_to_provenance(props)
    
    # Try PDF
    if _is_pdf(file_bytes):
        pdf = PdfReader(io.BytesIO(file_bytes))
        metadata = pdf.metadata
        return _pdf_to_provenance(metadata)
    
    return {"provenance_score": 0.5}  # Unknown format

def _image_provenance(file_path: str) -> dict[str, object]:
    """Image path: C2PA + EXIF (AGENTS §5.2 Image path)."""
    
    # Read EXIF data
    img = Image.open(file_path)
    exif_data = _extract_exif(img)
    
    # Check C2PA manifest
    c2pa_manifest = _extract_c2pa(file_path)
    
    # Flag anomalies
    anomalies = _check_timestamp_anomalies(exif_data)
    
    return {
        "c2pa_manifest_present": c2pa_manifest is not None,
        "exif_data": exif_data,
        "timestamp_anomalies": anomalies,
        "provenance_score": _score_provenance(c2pa_manifest, exif_data),
    }
```

**Test Strategy:**
- Test with real DOCX/PDF files with various metadata
- Test with images containing EXIF data
- Test with C2PA-signed images (if available)
- Mock file I/O for unit tests

**Success Criteria:**
- ✅ DOCX metadata extraction functional
- ✅ PDF metadata extraction functional
- ✅ Image EXIF reading functional
- ✅ C2PA detection implemented
- ✅ Timestamp anomaly detection working
- ✅ 100% of provenance-related tests passing

---

### Phase 1C: Web Consensus Agent (MEDIUM PRIORITY)

**Location:** `agents/web_consensus/`

**Responsibilities** (per AGENTS §5.4):
1. **PHash Lookup:** Check known deepfake registries
2. **Reverse Search:** Find earliest indexed appearances
3. **Context Check:** Detect temporal anomalies

**Stack:** LangChain, Tavily Search API, FAISS/Chroma

**Implementation Approach:**

```python
# agents/web_consensus/analyzer.py

def analyze(media_type: str, file_path: str) -> dict[str, object]:
    """Analyze web consensus per AGENTS §5.4."""
    
    if media_type.startswith("text/"):
        return _analyze_text_web(file_path)
    elif media_type.startswith("image/"):
        return _analyze_image_web(file_path)
    # ... video, audio ...
    return {}

def _analyze_text_web(file_path: str) -> dict[str, object]:
    """Text path: cache-backed lookup (AGENTS §5.4 Text path)."""
    
    content = _read_file(file_path)
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    
    # Check cache
    cache = _get_cache()
    cache_key = f"otp:web_consensus:text:{content_hash}"
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Cache miss: do lookup (Tavily/Google when APIs ready)
    result = {
        "cache_hit": False,
        "web_consensus_score": 0.5,
        "sources": [],
    }
    
    # Cache result (24h TTL per AGENTS §5.4)
    cache.setex(cache_key, 86400, json.dumps(result))
    
    return result

def _analyze_image_web(file_path: str) -> dict[str, object]:
    """Image path: PHash + reverse lookup (AGENTS §5.4 Image path)."""
    
    # Compute perceptual hash
    phash = _compute_phash(file_path)
    
    # Check local registry (when built)
    registry_match = _check_phash_registry(phash)
    
    # Placeholder for reverse image search (when APIs ready)
    reverse_search_results = []
    
    return {
        "phash": phash,
        "registry_match": registry_match,
        "reverse_search_results": reverse_search_results,
        "web_consensus_score": 0.5,
    }
```

**Test Strategy:**
- Test cache hit/miss scenarios
- Test PHash computation consistency
- Mock API calls (Tavily) for unit tests
- Test with known deepfake images/text

**Success Criteria:**
- ✅ Cache layer working (Redis integration)
- ✅ PHash computation for images
- ✅ Text hash computation for lookups
- ✅ API stubs in place (real APIs deferred to Phase 2)
- ✅ 100% of web consensus tests passing

---

## Testing Strategy

### Test Organization

```
tests/
├── unit/
│   ├── test_heuristics_analyzer.py      (NEW)
│   ├── test_provenance_analyzer.py      (NEW)
│   ├── test_web_consensus_analyzer.py   (NEW)
│   ├── test_orchestrator_service.py     (UPDATED)
│   └── ... existing tests ...
└── integration/
    └── test_end_to_end.py              (NEW - verifies all agents together)
```

### Test Patterns

**Unit Test Template:**
```python
@pytest.mark.asyncio
async def test_heuristics_text_detection():
    """Test that heuristics detects LLM text (AGENTS §5.3)."""
    llm_text = "This is generated by GPT-4..."  # or load from file
    
    analyzer = HeuristicsAnalyzer()
    result = analyzer.analyze("text/plain", content=llm_text)
    
    assert result["synthetic_probability"] > 0.7
    assert result["heuristics_score"] < 0.3
    assert "mean_perplexity" in result["signals"]
```

**Mock Pattern (for external APIs):**
```python
@pytest.fixture
def mock_tavily_api(monkeypatch):
    def mock_search(query):
        return {"results": [{"url": "...", "title": "..."}]}
    
    monkeypatch.setattr("agents.web_consensus.tavily_search", mock_search)
```

---

## Success Metrics

### Code Quality
- [ ] 75%+ test coverage (current: 58% → target: 75%)
- [ ] 100% of Ruff linting passes
- [ ] 100% type checking passes (mypy)
- [ ] Zero security findings (Bandit)

### Documentation
- [ ] Each agent has complete docstrings (AGENTS §5 references)
- [ ] Each test explains what it validates
- [ ] Implementation comments trace to AGENTS.md sections

### Functionality
- [ ] All agents return correct schema (AGENTS §6.1)
- [ ] Scoring integration validated (AGENTS §7)
- [ ] All timeouts respected (AGENTS §8)
- [ ] Idempotency on task_id verified (AGENTS §4.2)

---

## Timeline & Dependencies

**Week 1 (This Session):**
1. Complete Heuristics agent (2-3h)
2. Complete Provenance agent (2-3h)
3. Complete Web Consensus agent (1-2h)
4. Add comprehensive tests (2-3h)
5. Security review + fixes (1h)
6. Update documentation (1h)

**Deliverable:** PR ready for merge with 75%+ coverage

---

## Known Limitations & Deferred Items

### Infrastructure Transition (Phase 2)
- Kafka → Redis migration (currently functional with Kafka)
- Temporal → Asyncio simplification (currently functional with Temporal)
- S3 → Local filesystem (currently uses S3 URIs)

### Feature Completeness
- Tavily Search API integration (Phase 2)
- PHash deepfake registry (Phase 2)
- GPU acceleration for models (Optional)

### Documentation
- Desktop app / UI (Phase 2)
- Ledger commitment full integration (Phase 2)
- Agent performance benchmarks (Phase 2)

---

## References

- AGENTS.md — Authoritative technical contract
- CONTRIBUTING.md — Development workflow
- IMPLEMENTATION_GUIDE.md — Code patterns and best practices
- tests/unit/*.py — Existing test patterns to follow

