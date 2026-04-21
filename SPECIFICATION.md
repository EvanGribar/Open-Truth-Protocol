# OTP Technical Specification: 100% AI-Generated Text Detection

**Version:** 1.0  
**Status:** Research Phase  
**Last Updated:** April 2026

---

## Executive Summary

This document defines the technical specification for Open Truth Protocol's core mission: achieving **100% accuracy** in detecting AI-generated text across all major language models, domains, and languages.

The protocol is structured around **multi-signal analysis**—combining linguistic, statistical, semantic, and behavioral indicators to achieve deterministic classification with zero false positives and false negatives on standard benchmarks.

---

## 1. Definitions

### 1.1 Accuracy Target

**100% accuracy** means:
- **0% false positive rate:** No human-written text classified as AI-generated
- **0% false negative rate:** No AI-generated text classified as human-written
- **Scope:** English text, 100-10,000 word samples, on benchmark datasets

### 1.2 Supported LLMs (Phase 1)

- OpenAI: GPT-3.5, GPT-4, GPT-4o
- Anthropic: Claude 3 (Opus, Sonnet, Haiku)
- Google: Gemini 1.0, 1.5
- Meta: Llama 2, 3, 3.1
- Open-source: Mistral, Mixtral, Qwen
- Specialized: Code LLMs (Copilot, CodeLlama)

### 1.3 Text Categories

1. **General prose** (news, blogs, essays)
2. **Technical documentation** (code comments, API docs)
3. **Social media** (tweets, posts, comments)
4. **Academic** (papers, abstracts)
5. **Creative** (fiction, storytelling)
6. **Email and correspondence**

---

## 2. Detection Signals

### 2.1 Statistical Signals

#### Perplexity Distribution
- LLM-generated text has **lower variance in perplexity** across sentences
- Human text shows natural peaks and valleys
- **Metric:** Coefficient of variation (CV) of per-sentence perplexity
- **Threshold:** CV < 0.15 → AI signal

#### Entropy Patterns
- AI text exhibits **lower Shannon entropy** in token distributions
- Specific tokens appear with **higher probability** than natural language
- **Metric:** Jensen-Shannon divergence from human baseline
- **Threshold:** JSD > 0.08 → AI signal

#### Burstiness
- Human text has **bursty** word frequency patterns (Zipfian)
- AI text is more **uniform** in repetition
- **Metric:** Hurst exponent
- **Threshold:** H < 0.50 → AI signal

### 2.2 Linguistic Signals

#### Lexical Diversity
- AI text often exhibits **forced diversity** or **repetitive patterns**
- Type-token ratio (TTR) in AI is either too high or too low
- **Metric:** Adjusted TTR with sample size correction
- **Threshold:** Deviation > 2 SD → AI signal

#### Syntactic Uniformity
- LLMs produce **stereotypical sentence structures**
- Dependency parse trees show **less variation** than human writing
- **Metric:** Parse tree similarity clustering coefficient
- **Threshold:** Clustering > 0.72 → AI signal

#### Linguistic Markers
- Overuse of intensifiers: "truly", "remarkably", "incredibly"
- Hedging language: "arguably", "might suggest"
- Transition phrases at unnatural frequencies
- **Metric:** Ratio of markers to sentence count
- **Threshold:** Ratio > 1.8x baseline → AI signal

### 2.3 Semantic Signals

#### Semantic Coherence
- LLMs maintain **excessive semantic consistency** across long passages
- Human text naturally shifts focus, contradicts, or explores tangents
- **Metric:** Cosine similarity of consecutive sentence embeddings (using SBERT)
- **Threshold:** Mean similarity > 0.68 → AI signal

#### Conceptual Repetition
- AI tends to **repeat ideas** in different phrasings within the same text
- **Metric:** Semantic similarity of non-adjacent paragraph pairs
- **Threshold:** High repetition clusters → AI signal

### 2.4 Behavioral Signals

#### Word Frequency Anomalies
- AI text favors certain function words at different rates than human text
- Example: overuse of "the", "to", "and" at specific intervals
- **Metric:** Chi-squared test vs. human baseline corpus
- **Threshold:** χ² > critical value (p < 0.01) → AI signal

#### Punctuation Patterns
- Certain punctuation usage is **predictable** in AI text
- Semicolon usage, em-dash patterns, parenthetical density
- **Metric:** Punctuation entropy
- **Threshold:** PE < 2.1 bits → AI signal

---

## 3. Ensemble Scoring

The final classification is computed as a **weighted ensemble** of signal strengths:

```
AI_SCORE = Σ(w_i × signal_i) / Σ(w_i)

where:
  w_i = weight of signal i
  signal_i ∈ [0, 1] (normalized evidence)
```

### 3.1 Signal Weights (Phase 1)

| Signal | Weight | Justification |
|--------|--------|---------------|
| Perplexity Distribution | 0.25 | Strong LLM fingerprint |
| Entropy Patterns | 0.20 | Fundamental property |
| Semantic Coherence | 0.20 | Distinctive characteristic |
| Syntactic Uniformity | 0.15 | Easily observable |
| Burstiness | 0.10 | Supplementary validation |
| Linguistic Markers | 0.07 | Context-dependent |
| Word Frequency | 0.02 | Noisy at short ranges |
| Punctuation | 0.01 | Edge case indicator |

### 3.2 Classification Rules

```
IF AI_SCORE >= 0.92:     VERDICT = "AI_GENERATED" (confidence: very high)
IF AI_SCORE >= 0.75:     VERDICT = "AI_GENERATED" (confidence: high)
IF AI_SCORE <= 0.25:     VERDICT = "HUMAN_WRITTEN" (confidence: high)
IF AI_SCORE <= 0.08:     VERDICT = "HUMAN_WRITTEN" (confidence: very high)
ELSE:                    VERDICT = "UNCERTAIN" (requires manual review)
```

---

## 4. Benchmark Protocol

### 4.1 Dataset Construction

#### Human Text
- **Corpus sources:**
  - Common Crawl (web)
  - Project Gutenberg (books)
  - arXiv (academic)
  - Twitter API (social)
  - Reddit (forums)
- **Curation:** Remove AI-generated content (flagged by community)
- **Size:** 50,000+ unique samples per category
- **Annotation:** Multiple human judges, inter-rater reliability > 0.95

#### AI-Generated Text
- **Generation protocol:** Identical prompts, multiple LLMs, multiple runs
- **Sampling:** Full range of temperature (0.0 - 2.0)
- **Prompt diversity:** 500+ different prompts covering all categories
- **Size:** 100,000+ samples (2+ per prompt × models)

### 4.2 Evaluation Metrics

```
Precision = TP / (TP + FP)     [Should be 1.0]
Recall    = TP / (TP + FN)     [Should be 1.0]
F1-Score  = 2 × (Precision × Recall) / (Precision + Recall)
Accuracy  = (TP + TN) / (TP + TN + FP + FN)
```

**Success Criterion:** All metrics ≥ 0.99 on held-out test set.

### 4.3 Cross-Model Validation

Must achieve ≥ 99% accuracy when:
- Model A trained on, Model B tested (leave-one-out)
- Temperature variations (cold: 0.1 → hot: 2.0)
- Prompt injection attempts (adversarial examples)
- Language mixing (codeswitching, multilingual)

---

## 5. Validation Strategy

### 5.1 Phase 1: Signal Validation
1. Implement each signal individually
2. Measure signal correlation with ground truth
3. Validate on small benchmark (10k samples)
4. **Gate:** All signals > 75% accuracy in isolation

### 5.2 Phase 2: Ensemble Tuning
1. Train ensemble weights on validation set (20k samples)
2. Cross-validate with stratified K-fold (k=5)
3. Hyperparameter sweep (learning rate, regularization)
4. **Gate:** Ensemble achieves > 95% F1 on validation

### 5.3 Phase 3: Adversarial Testing
1. Generate adversarial examples (paraphrasing, style transfer)
2. Test against edge cases (multilingual, code, tables)
3. Evaluate on out-of-distribution LLMs
4. **Gate:** Maintains > 92% accuracy on adversarial set

### 5.4 Phase 4: Production Validation
1. Real-world data collection (opt-in community submission)
2. Manual annotation by multiple reviewers
3. Continuous monitoring and retraining
4. **Gate:** Maintains > 98% accuracy on production data

---

## 6. Implementation Architecture

### 6.1 Core Components

```
Text Input
    ↓
[Preprocessing: Normalization, Tokenization]
    ↓
┌─────────────────────────────────────────┐
│ Signal Extraction Pipeline              │
│ ├─ Perplexity Analyzer                  │
│ ├─ Entropy Analyzer                     │
│ ├─ Semantic Coherence Analyzer          │
│ ├─ Syntactic Uniformity Analyzer        │
│ ├─ Linguistic Marker Detector           │
│ ├─ Burstiness Analyzer                  │
│ ├─ Word Frequency Analyzer              │
│ └─ Punctuation Analyzer                 │
└─────────────────────────────────────────┘
    ↓
[Ensemble Scorer: Weighted Combination]
    ↓
[Classification: AI vs. Human]
    ↓
Output: {
  "verdict": "AI_GENERATED" | "HUMAN_WRITTEN" | "UNCERTAIN",
  "confidence": 0.0 - 1.0,
  "score_breakdown": {...},
  "reasoning": "..."
}
```

### 6.2 Technology Stack

- **Language:** Python 3.12+
- **NLP:** NLTK, spaCy, Hugging Face Transformers
- **Embeddings:** Sentence-BERT (all-MiniLM or all-mpnet)
- **Perplexity:** Hugging Face pipeline with GPT-2 / OPT
- **Data:** Pandas, NumPy, SciPy
- **Benchmarking:** scikit-learn, pytest
- **Observability:** Structured logging, metrics export

---

## 7. Success Criteria

| Metric | Target | Rationale |
|--------|--------|-----------|
| Accuracy (Phase 1 benchmark) | ≥ 99% | True benchmark |
| F1-Score (macro) | ≥ 0.99 | Balance precision/recall |
| Cross-model generalization | ≥ 95% | Works on unseen LLMs |
| Inference time | < 2s per 1000 tokens | Real-time usability |
| False positive rate | < 0.1% | Minimize wrongful accusations |
| False negative rate | < 0.1% | Catch real AI |

---

## 8. Roadmap

### Q2 2026: Foundation
- [x] Define signals and architecture
- [ ] Implement 5/8 core signals
- [ ] Build benchmark dataset
- [ ] Phase 1 validation gate

### Q3 2026: Ensemble & Tuning
- [ ] Complete all 8 signals
- [ ] Ensemble training and optimization
- [ ] Phase 2 validation gate
- [ ] Open-source MVP release

### Q4 2026: Adversarial & Scale
- [ ] Adversarial testing suite
- [ ] Multi-language support
- [ ] Phase 3 validation gate
- [ ] v1.0 stable release

### 2027: Production
- [ ] Community dataset collection
- [ ] Continuous benchmarking infrastructure
- [ ] API and CLI tools
- [ ] Integration partnerships

---

## 9. Contributing

All contributions must:
1. Include benchmark results on standard test set
2. Maintain or improve accuracy metrics
3. Be fully reproducible and documented
4. Undergo peer review before merge

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

---

## 10. References

- Jawahar et al. (2020): "Automatic Detection of Generated Text is Easiest when Humans are Fooled"
- Opitz et al. (2023): "Detecting Machine Generated Text"
- Wang et al. (2023): "ChatGPT as a Tool for Data Augmentation for Named Entity Recognition"
- Kumarage et al. (2023): "Detecting AI Synthesized Fake-Face Videos"
