# Open Truth Protocol: Documentation Index

**Status:** ✅ Repository Cleaned & Documentation Complete  
**Last Updated:** April 20, 2026  
**Phase:** 1 - Signal Research (Active)

---

## 📖 Essential Reading Order

### Getting Started (15 minutes)
1. [START.md](START.md) — Quick navigation guide
2. [README.md](README.md) — Project mission and overview
3. [STATUS.md](STATUS.md) — Current phase and FAQs

### Understanding the Approach (90 minutes)
4. [SPECIFICATION.md](SPECIFICATION.md) — Complete technical specification
5. [ALGORITHMS.md](ALGORITHMS.md) — Detection signals in depth
6. [DATASETS.md](DATASETS.md) — Benchmarking methodology

### Development & Contribution (30 minutes)
7. [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md) — Four-phase execution plan
8. [CONTRIBUTING.md](CONTRIBUTING.md) — How to contribute
9. [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — Community guidelines

### Reference
- [CHANGELOG.md](CHANGELOG.md) — Project history and pivot
- [AGENTS.md](AGENTS.md) — Archived legacy architecture
- [SECURITY.md](SECURITY.md) — Vulnerability disclosure

---

## 🎯 By Role

### Researchers
**Goal:** Understand the 100% accuracy approach

```
README.md 
  → SPECIFICATION.md 
  → ALGORITHMS.md 
  → DATASETS.md
```

**Time:** 2 hours | **Outcome:** Full technical understanding

### Contributors
**Goal:** Find ways to help

```
CONTRIBUTING.md 
  → RESEARCH_ROADMAP.md 
  → GitHub Issues
```

**Time:** 30 minutes | **Outcome:** Know where to contribute

### Users / Waiters
**Goal:** Understand when/if OTP will be ready

```
README.md 
  → STATUS.md 
  → RESEARCH_ROADMAP.md (Phase dates)
```

**Time:** 20 minutes | **Outcome:** Know v1.0 is Q4 2026

### Developers (Future)
**Goal:** Implement the specification

```
SPECIFICATION.md 
  → ALGORITHMS.md 
  → DATASETS.md 
  → RESEARCH_ROADMAP.md
```

**Time:** Full read | **Outcome:** Ready to code

---

## 📋 Complete Document Guide

| Document | Purpose | Audience | Read Time |
|----------|---------|----------|-----------|
| [START.md](START.md) | Navigation guide | Everyone | 5 min |
| [README.md](README.md) | Mission & problem statement | Everyone | 5 min |
| [STATUS.md](STATUS.md) | Current phase & FAQ | Everyone | 10 min |
| [SPECIFICATION.md](SPECIFICATION.md) | 8 signals, ensemble, validation | Researchers, Developers | 30 min |
| [ALGORITHMS.md](ALGORITHMS.md) | Signal implementations | Developers | 45 min |
| [DATASETS.md](DATASETS.md) | Data protocols | Researchers, Data Engineers | 30 min |
| [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md) | 4-phase plan with gates | Contributors, Project managers | 20 min |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to help | Contributors | 10 min |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community standards | Everyone | 5 min |
| [SECURITY.md](SECURITY.md) | Vulnerability reporting | Security researchers | 5 min |
| [CHANGELOG.md](CHANGELOG.md) | Project history | Everyone | 5 min |
| [AGENTS.md](AGENTS.md) | Legacy architecture (archived) | Historical reference | 10 min |

**Total reading time for full understanding:** ~2.5 hours

---

## 🔑 Key Concepts

### The 8 Detection Signals
1. **Perplexity Distribution** — Variance in sentence-level surprise
2. **Entropy Patterns** — Token frequency randomness
3. **Semantic Coherence** — Sentence-to-sentence similarity
4. **Syntactic Uniformity** — Parsing tree diversity
5. **Burstiness** — Word repetition clustering (Zipfian analysis)
6. **Linguistic Markers** — Intensifiers, hedges, transitions
7. **Word Frequency** — Function word anomalies
8. **Punctuation Patterns** — Punctuation distribution entropy

### Success Metrics
- **Accuracy:** ≥ 99% on benchmark
- **False Positive Rate:** < 0.1%
- **False Negative Rate:** < 0.1%
- **Inference Time:** < 2s per 1000 tokens
- **Cross-LLM Generalization:** ≥ 95% on leave-one-out

### Four Phases
| Phase | Timeline | Goal | Gate |
|-------|----------|------|------|
| 1 | Q2 2026 | Validate all signals ≥ 75% | ✅ All signals validated |
| 2 | Q3 2026 | Ensemble ≥ 95% F1 | ✅ Cross-LLM generalization works |
| 3 | Q4 2026 | Adversarial ≥ 92% accuracy | ✅ Robust against evasion |
| 4 | 2027+ | Production deployment | ✅ v1.0 released, continuous monitoring |

---

## 🚀 Next Actions

### For Immediate Understanding
→ Read [START.md](START.md) (5 min)  
→ Read [README.md](README.md) (5 min)  
→ Read [STATUS.md](STATUS.md) (10 min)  

### For Technical Depth
→ Read [SPECIFICATION.md](SPECIFICATION.md) (30 min)  
→ Read [ALGORITHMS.md](ALGORITHMS.md) (45 min)  

### For Contributing
→ Read [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md) (20 min)  
→ Read [CONTRIBUTING.md](CONTRIBUTING.md) (10 min)  
→ Open a GitHub issue with your idea  

### For Implementation (Q3 2026+)
→ Use [SPECIFICATION.md](SPECIFICATION.md) as reference  
→ Follow [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md#phase-2) for Phase 2  
→ Check [DATASETS.md](DATASETS.md) for test data  

---

## ❓ FAQ

**Q: Is there code I can use?**  
A: Not yet. We're in Phase 1 (signal research). Code releases begin Q3 2026.

**Q: How can I help?**  
A: See [CONTRIBUTING.md](CONTRIBUTING.md) and [RESEARCH_ROADMAP.md](RESEARCH_ROADMAP.md#contributing).

**Q: When is v1.0?**  
A: End of Q4 2026 (after all phase gates pass). See [STATUS.md](STATUS.md) for timeline.

**Q: What happened to the old code?**  
A: Archived. See [AGENTS.md](AGENTS.md) for historical reference. We pivoted to text-only focus.

**Q: Why only text?**  
A: To achieve 100% accuracy, we're focusing on the hardest problem first. Image/video detection is a future phase.

**Q: Is this only for English?**  
A: Phase 1 is English-only. Multilingual support planned for Phase 4 (2027).

---

## 📊 Repository Structure (After Cleanup)

```
opentruthprotocol/
├── README.md                 ← Start here
├── START.md                  ← Navigation guide
├── STATUS.md                 ← Current phase & FAQ
├── SPECIFICATION.md          ← Technical specification
├── ALGORITHMS.md             ← Signal details
├── DATASETS.md               ← Data protocols
├── RESEARCH_ROADMAP.md       ← 4-phase plan
├── CONTRIBUTING.md           ← How to contribute
├── CODE_OF_CONDUCT.md        ← Community standards
├── SECURITY.md               ← Vulnerability reporting
├── CHANGELOG.md              ← History
├── AGENTS.md                 ← Legacy (archived)
├── docker/                   ← Infrastructure reference
├── LICENSE                   ← MIT
├── Makefile                  ← Build tools
├── pyproject.toml            ← Python config
└── requirements.txt          ← Dependencies
```

**Note:** `agents/`, `shared/`, `tests/`, `config/`, `eval/`, `scratch/`, and `docs/` have been removed. The repository is now **documentation-first**.

---

## 🔗 Quick Links

- **GitHub:** https://github.com/EvanGribar/Open-Truth-Protocol
- **License:** [MIT](LICENSE)
- **Code of Conduct:** [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- **Issues:** GitHub Issues tab

---

**Last Updated:** April 20, 2026  
**Next Phase Gate:** End Q2 2026 (Signal Validation)
