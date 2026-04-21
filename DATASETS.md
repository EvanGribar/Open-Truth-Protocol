# DATASETS.md: Data Collection & Benchmarking

**Version:** 1.0  
**Status:** In Development  
**Last Updated:** April 2026

---

## Overview

This document defines the data collection, annotation, and benchmarking protocols for OTP's 100% accuracy target. All datasets are publicly available and auditable to ensure reproducibility.

---

## 1. Dataset Construction

### 1.1 Human-Written Text

#### Sources
| Source | Category | Size | Quality |
|--------|----------|------|---------|
| Common Crawl | General web | 100M documents | Filtered (no AI) |
| Project Gutenberg | Classic literature | 70k books | High |
| arXiv | Academic papers | 2.3M papers | High |
| Wikipedia | Encyclopedic | 6.6M articles | Medium-High |
| Reddit | Social discussion | 100M posts | Medium |
| News archives | Journalism | 50M articles | High |
| Twitter API v2 | Microblog | 100M tweets | Low-Medium |
| HackerNews | Tech commentary | 100M comments | Medium-High |
| Stack Overflow | Technical Q&A | 20M posts | High |

#### Curation Rules
- **Remove suspected AI:** Use previous detectors + manual review to filter out likely LLM outputs
- **Deduplication:** Remove exact duplicates and near-duplicates (edit distance > 0.95)
- **Language:** English-only (Phase 1)
- **Length:** 100-10,000 tokens (5 documents per person, 1000s per source)
- **Anonymization:** Strip personally identifiable information (emails, phone numbers, names)

#### Annotation
- **Labeling:** Multiple annotators per document
- **Inter-rater agreement (IRA):** Must be ≥ 0.95 (Cohen's kappa)
- **Ground truth:** 3+ independent labels, majority vote
- **Metadata:** Collection date, source, author role (journalist, academic, blogger, etc.)

**Phase 1 Target:** 50,000 human-written documents

---

### 1.2 AI-Generated Text

#### Generation Protocol

**Prompt Design:**
1. Select 500+ diverse prompts covering:
   - News writing
   - Technical documentation
   - Creative fiction
   - Academic papers
   - Social media posts
   - Email correspondence
   - Code comments
   - Product descriptions

2. Prompt format:
   ```
   Write a [GENRE] about [TOPIC]. Aim for [STYLE]. 
   Length: [LENGTH] words.
   ```

**LLM Matrix (Phase 1):**
```
Models:         OpenAI, Anthropic, Google, Meta, Mistral
Versions:       Latest stable at dataset creation time
Temperatures:   [0.1, 0.3, 0.7, 1.0, 1.5, 2.0]
Samples/Config: 2 (different runs)
Total samples:  500 prompts × 5 models × 6 temps × 2 runs = 30,000 samples
```

**Sampling Strategy:**
- Random seed for reproducibility: `seed = 42 + prompt_id`
- Max tokens: 2,000 (allow model to generate naturally)
- Top-p: 0.95 (default, except where testing sampling)
- Stop sequences: None (full completion)

#### Validation
- **Human review:** 10% of samples reviewed by human judges
- **Authenticity check:** Confirm output is from claimed model (API logs)
- **Deduplication:** Remove exact duplicates within model cohort
- **Format standardization:** Normalize line breaks, whitespace

**Phase 1 Target:** 100,000 AI-generated documents (across all models/temperatures)

---

## 2. Dataset Splits

### 2.1 Train/Validation/Test Split

```
Total Documents: 150,000 (50k human + 100k AI)

Training Set:    60,000 (40k human + 20k AI)  [40%]
Validation Set:  30,000 (5k human + 25k AI)   [20%]
Test Set:        60,000 (5k human + 55k AI)   [40%]
  ├─ In-distribution: 40,000 (LLMs in training)
  └─ Out-of-distribution: 20,000 (novel LLMs)
```

### 2.2 Stratification

Splits must be balanced by:
- **Source:** Each source represented proportionally
- **Domain:** {prose, technical, social, academic, creative, email}
- **Model:** Each LLM represented in training and validation
- **Temperature:** Uniform distribution across temps

### 2.3 Reproducibility

All splits use deterministic random seed:
```python
np.random.seed(42)
```

Split logic is published in `datasets/split.py` with documented random state.

---

## 3. Annotation Protocol

### 3.1 Inter-Rater Agreement

**Kappa Calculation (Cohen's Kappa):**
```
κ = (P_o - P_e) / (1 - P_e)

where:
  P_o = observed agreement
  P_e = expected agreement by chance
```

**Acceptance Criteria:**
- κ ≥ 0.95: Excellent agreement → accept document
- 0.81 ≤ κ < 0.95: Good agreement → minor review
- κ < 0.81: Poor agreement → reject or re-annotate

### 3.2 Ground Truth Consensus

**Majority Voting:**
1. Collect 3+ independent binary labels (AI vs. Human)
2. Compute majority vote
3. If tied (for even n): Escalate to senior reviewer
4. Document decision and confidence level

### 3.3 Annotation Metadata

Track:
- Annotator ID (anonymized)
- Annotation timestamp
- Time taken (for quality signals)
- Confidence level (1-5 scale)
- Comments (reasons for classification)

---

## 4. Benchmark Evaluation

### 4.1 Metrics

**Binary Classification Metrics:**
```
Accuracy     = (TP + TN) / (TP + TN + FP + FN)
Precision    = TP / (TP + FP)  [How many predicted AI are actually AI]
Recall       = TP / (TP + FN)  [How many AI are detected]
F1-Score     = 2 × (Precision × Recall) / (Precision + Recall)
Specificity  = TN / (TN + FP)  [How many human correctly identified]
FPR          = FP / (FP + TN)  [False positive rate]
FNR          = FN / (FN + TP)  [False negative rate]
```

### 4.2 Success Thresholds

| Metric | Target | Rationale |
|--------|--------|-----------|
| Accuracy | ≥ 0.99 | 100% goal |
| F1-Score | ≥ 0.99 | Balance precision/recall |
| Precision | ≥ 0.99 | Minimize false accusations |
| Recall | ≥ 0.99 | Catch all AI |
| FPR | ≤ 0.001 | < 0.1% innocent flagged |
| FNR | ≤ 0.001 | < 0.1% AI missed |

### 4.3 Confidence Intervals

For each metric, compute:
```
CI_95% = point_estimate ± 1.96 × SE

where SE = sqrt(p(1-p) / n)
```

Report all metrics with 95% CI.

---

## 5. Generalization Testing

### 5.1 Cross-Model Generalization

**Leave-one-LLM-out evaluation:**
```
For each LLM_i in {GPT-3.5, GPT-4, Claude, Gemini, Llama}:
  1. Train ensemble on all models EXCEPT LLM_i
  2. Evaluate on test set from LLM_i only
  3. Record F1-score for LLM_i
  4. Compute mean cross-LLM F1
```

**Target:** Mean F1 ≥ 0.95 across leave-one-out folds

### 5.2 Domain Generalization

**Per-domain evaluation:**
```
For each domain_j in {prose, technical, social, academic, creative, email}:
  1. Evaluate on test samples from domain_j only
  2. Record F1-score and accuracy
  3. Analyze failure cases
```

**Target:** F1 ≥ 0.90 in each domain

### 5.3 Temperature Generalization

**Bin by generation temperature:**
```
Temp_low   = [0.1, 0.3]
Temp_mid   = [0.5, 1.0]
Temp_high  = [1.5, 2.0]

For each temperature bin:
  - Evaluate F1-score
  - Analyze accuracy trend
```

**Target:** Maintain F1 ≥ 0.92 across all temperature ranges

---

## 6. Benchmark Releases

### 6.1 Schedule

| Release | Date | Status | Details |
|---------|------|--------|---------|
| v1.0 | Q2 2026 | Research | 50k human, 100k AI (in-distribution) |
| v1.1 | Q3 2026 | Extended | +20k adversarial examples |
| v1.2 | Q4 2026 | Production | +10k community submissions |
| v2.0 | 2027 | Multilingual | Spanish, French, German, Mandarin |

### 6.2 Public Availability

All datasets released under:
- **License:** CC-BY 4.0 or CC0 (public domain for models)
- **Format:** Parquet files with metadata
- **Documentation:** Dataset cards (Hugging Face format)
- **Hosting:** Hugging Face Datasets + GitHub releases
- **Version control:** Git tags for reproducibility

### 6.3 Data Protection

- **PII removal:** All personally identifiable information stripped
- **Copyright:** Source material respect (respect fair use, Creative Commons)
- **Anonymization:** Author names and identifiers removed
- **Terms of service:** Compliance with source platforms (Reddit, Twitter, arXiv)

---

## 7. Quality Assurance

### 7.1 Data Validation

Checks performed on all datasets:

```python
# Check 1: No duplicates within class
assert len(human_docs) == len(set(human_docs))
assert len(ai_docs) == len(set(ai_docs))

# Check 2: Length bounds
assert all(100 <= len(doc.split()) <= 10000 for doc in all_docs)

# Check 3: Balanced split
assert 0.45 < ai_ratio < 0.55  # ~50/50 split

# Check 4: No data leakage
assert len(train & test) == 0
assert len(train & val) == 0
assert len(val & test) == 0
```

### 7.2 Annotation Quality

- **Cohen's Kappa:** κ ≥ 0.95 on 10% sample
- **Inter-annotator agreement:** ≥ 95%
- **Ground truth consensus:** Majority vote with 3+ raters

---

## 8. Contributing New Data

Community members can contribute:

1. **Curated document collections** (with manual labels)
2. **New LLM outputs** (as AI text becomes available)
3. **Adversarial examples** (paraphrases, style transfers)
4. **Real-world submissions** (opt-in, anonymized)

Process:
1. Create GitHub issue with dataset proposal
2. Pass sanity checks (format, PII, deduplication)
3. Undergo peer review (2+ maintainers)
4. Integrate into benchmark with version bump

---

## 9. References

- Hugging Face Datasets: https://huggingface.co/datasets
- Dataset Cards: https://github.com/huggingface/datasets/blob/main/DATASET_CARD_TEMPLATE.md
- CC Licenses: https://creativecommons.org/licenses/
