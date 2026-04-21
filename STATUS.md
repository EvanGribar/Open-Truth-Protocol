# Project Status: April 2026

## Current State

**Open Truth Protocol has pivoted to focus exclusively on 100% accuracy in AI-generated text detection.**

This is a **research and engineering initiative**, not a product release. The repository currently contains **documentation only**—specifications, roadmaps, and protocols that guide implementation.

---

## What Changed?

### Previous Focus (Archived)
OTP originally targeted multi-modal media verification:
- Image deepfake detection (PRNU, frequency analysis)
- Video authentication (C2PA manifests)
- Audio forensics
- Text analysis (secondary)

**Status:** All multi-modal work is archived. See [AGENTS.md](AGENTS.md) for historical reference.

### New Focus (Active)
OTP now pursues **100% accuracy** in detecting AI-generated text:
- Multi-signal statistical analysis (8 core signals)
- Ensemble classification with transparent scoring
- Community-validated benchmarking
- Open-source, reproducible methodology

**Status:** Phase 1 (Signal Research) in progress.

---

## Where to Start

### For Researchers
1. Read [SPECIFICATION.md](SPECIFICATION.md) — Technical specification for 100% accuracy
2. Review [ALGORITHMS.md](ALGORITHMS.md) — Detailed signal descriptions
3. Explore [DATASETS.md](DATASETS.md) — Data collection and benchmarking protocols
4. Follow [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md) — Four-phase validation plan

### For Contributors
1. See [CONTRIBUTING.md](CONTRIBUTING.md) — Contribution guidelines
2. Check [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md#contributing) — How to propose signals or improvements
3. Open GitHub issues to discuss new ideas

### For Users
- **OTP v1.0 is not yet available.** The project is in active research.
- Phase 1 validation gates must be passed before code release.
- Expected v1.0 release: **Q4 2026**

---

## Current Phase: Phase 1 (Signal Research)

**Timeline:** Q2 2026  
**Goal:** Validate all 8 detection signals independently achieve > 75% accuracy

### In Progress
- [ ] Perplexity Distribution Analysis
- [ ] Entropy Pattern Detection
- [ ] Semantic Coherence Analysis
- [ ] Syntactic Uniformity Detection
- [ ] Burstiness & Zipfian Analysis
- [ ] Linguistic Marker Detection
- [ ] Word Frequency Anomalies
- [ ] Punctuation Pattern Analysis

### Validation Gate (End of Phase 1)
✅ All signals ≥ 75% accuracy in isolation  
✅ Benchmark dataset (50k human + 100k AI) finalized  
✅ Correlation matrix computed (signal independence)  
✅ Reproducibility documentation complete  

---

## Archived Code

The `agents/`, `shared/`, and `tests/` directories contain legacy code from the previous architecture. These are **not actively maintained** and will be refactored or removed as the text-focused implementation progresses.

### Legacy Components (No Longer Active)
- `agents/orchestrator/` — Temporal.io-based orchestration
- `agents/provenance/` — C2PA and EXIF analysis (images/video focus)
- `agents/heuristics/` — Multi-modal heuristics (PRNU, frequency analysis)
- `agents/web_consensus/` — Reverse image search integration
- `shared/ledger.py` — IPFS and blockchain integration

### What to Ignore
- Docker containers in `docker/`
- Kafka configuration in `docker-compose.yml`
- Image/video/audio-focused tests
- Entemporal workflow files

---

## Documentation

### Core Reference Documents
- **[SPECIFICATION.md](SPECIFICATION.md)** — Complete technical spec (8 signals, ensemble, benchmarks)
- **[RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md)** — Four-phase execution plan with gates
- **[DATASETS.md](DATASETS.md)** — Data collection and annotation protocols
- **[ALGORITHMS.md](ALGORITHMS.md)** — Detailed signal specifications

### Governance
- **[README.md](README.md)** — Project overview and mission
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — How to contribute
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** — Community expectations
- **[SECURITY.md](SECURITY.md)** — Vulnerability disclosure
- **[LICENSE](LICENSE)** — MIT license

### Historical
- **[AGENTS.md](AGENTS.md)** — Legacy multi-modal architecture (archived)
- **[CHANGELOG.md](CHANGELOG.md)** — Project history and transitions

---

## Upcoming Milestones

| Phase | Target Date | Key Metric | Status |
|-------|-------------|-----------|--------|
| **Phase 1** | End Q2 2026 | All signals ≥ 75% accuracy | 🟡 In Progress |
| **Phase 2** | End Q3 2026 | Ensemble ≥ 95% F1 | ⏳ Pending |
| **Phase 3** | End Q4 2026 | Adversarial ≥ 92% accuracy | ⏳ Pending |
| **Phase 4** | Q1 2027+ | v1.0 release + continuous monitoring | ⏳ Pending |

---

## Frequently Asked Questions

**Q: When will there be code to download?**  
A: Phase 1 validation gates must be passed first (target: end Q2 2026). Expect implementation code in Q3 2026.

**Q: Can I help with the research?**  
A: Yes! See [CONTRIBUTING.md](CONTRIBUTING.md) and [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md#contributing) for how to propose new signals or improvements.

**Q: Why is all the old code still here?**  
A: For reference and historical context. It will be archived or removed as the new implementation progresses. Contributors should focus on the new specification.

**Q: Is this related to ChatGPT detection?**  
A: OTP is a **general-purpose, model-agnostic** text detection system. It must work equally well on GPT-3.5, GPT-4, Claude, Gemini, Llama, and other LLMs.

**Q: Will this detect jailbroken or adversarial AI text?**  
A: That's Phase 3 (Adversarial Testing). Phase 1 focuses on standard outputs. Phase 3 will test against paraphrases, style transfer, and prompt injections.

---

## Contact & Support

- **GitHub Issues:** For bugs, questions, or feature requests
- **Discussions:** For research ideas and methodological questions
- **Email:** See [CONTRIBUTING.md](CONTRIBUTING.md) for maintainer contact

---

**Last Updated:** April 20, 2026
