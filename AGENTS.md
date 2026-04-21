# AGENTS.md — Open Truth Protocol (OTP) — ARCHIVED

**Status:** SUPERSEDED — See [SPECIFICATION.md](SPECIFICATION.md) and [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md)  
**Last Updated:** April 2026

> [!WARNING]
> **Project Pivot:** OTP has shifted focus from multi-modal media verification (images, video, audio) to **100% accuracy AI-generated text detection**. This document describes the legacy architecture and is retained for historical reference only. All active development follows the specifications in SPECIFICATION.md.

# AGENTS.md — Open Truth Protocol (OTP) — ARCHIVED

**Status:** SUPERSEDED — See [SPECIFICATION.md](SPECIFICATION.md) and [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md)  
**Last Updated:** April 2026

> [!WARNING]
> **Project Pivot:** OTP has shifted focus from multi-modal media verification (images, video, audio) to **100% accuracy AI-generated text detection**. This document describes the legacy architecture and is retained for historical reference only. All active development follows the specifications in SPECIFICATION.md.

---

## New Project Direction

**Mission:** Achieve 100% accuracy in detecting AI-generated text.

**Focus Areas:**
- Text-only detection (Phase 1)
- Multi-signal analysis (8 core signals)
- Ensemble scoring for classification
- Community-validated benchmarking
- Open-source, reproducible methodology

**Read Next:**
1. [SPECIFICATION.md](SPECIFICATION.md) — Technical specification for 100% accuracy
2. [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md) — Implementation roadmap and validation phases
3. [README.md](README.md) — Project overview

---

## Legacy Architecture (Archived)

The following sections describe the previous multi-modal agent architecture. This is retained for historical reference and may inform future work on image/video verification.

### Previous Scope (No Longer Active)

The original OTP design included:
- **Orchestrator Agent** — Centralized task dispatch via Kafka
- **Cryptographic Provenance Agent** — C2PA and EXIF analysis for media
- **Synthetic Heuristics Agent** — PRNU, frequency analysis, perplexity for images/video
- **Web Consensus Agent** — Reverse image search, context validation
- **Ledger Commitment Agent** — IPFS pinning and blockchain recording

All of the above is **out of scope** for the current initiative. Code in `agents/` directory reflects this legacy architecture and will be refactored or removed as the text-focused implementation progresses.

---

## Contributing

For the new text detection initiative, see [CONTRIBUTING.md](CONTRIBUTING.md) and [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md#contributing).
