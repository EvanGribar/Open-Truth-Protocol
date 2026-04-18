# AGENTS.md — Open Truth Protocol (OTP)

**Version:** 2.2  
**Status:** Living Document — Contributors must keep this file current with implementation.  
**Last Updated:** April 2026

This file is the engineering constitution for the OTP swarm. Every agent, every interface contract, every infra decision lives here. If you're building a new agent, modifying an existing one, or wiring up infra — read this first, top to bottom.

---

## Table of Contents

1. [What OTP Is](#1-what-otp-is)
2. [What OTP Is Not](#2-what-otp-is-not)
3. [System Architecture](#3-system-architecture)
4. [Infrastructure Contracts](#4-infrastructure-contracts)
5. [Agent Specifications](#5-agent-specifications)
   - 5.1 [Orchestrator](#51-orchestrator-agent)
   - 5.2 [Cryptographic Provenance Agent](#52-cryptographic-provenance-agent)
   - 5.3 [Synthetic Heuristics Agent](#53-synthetic-heuristics-agent)
   - 5.4 [Web Consensus Agent](#54-web-consensus-agent)
   - 5.5 [Ledger Commitment Agent](#55-ledger-commitment-agent)
6. [Shared Data Schemas](#6-shared-data-schemas)
7. [Scoring Model](#7-scoring-model)
8. [Error Handling & Timeouts](#8-error-handling--timeouts)
9. [Adding a New Agent](#9-adding-a-new-agent)
10. [Local Development](#10-local-development)
11. [Environment Variables](#11-environment-variables)
12. [Roadmap & Phase Gates](#12-roadmap--phase-gates)
13. [Contributor Rules](#13-contributor-rules)

---

## 1. What OTP Is

OTP is a decentralized, open-source swarm of specialized AI agents that collectively verify the authenticity of digital media. A piece of media — image, video, audio, or text — enters the pipeline; a cryptographically anchored `TruthConsensus` record exits. The protocol is:

- **Asynchronous.** Agents run in parallel. No agent blocks another.
- **Modular.** Agents are independent services with well-defined input/output contracts.
- **Immutable.** Every attestation is pinned to IPFS and hashed onto a public ledger. It cannot be altered retroactively.
- **Open.** Any developer can write a new agent, submit it for review, and have it included in the swarm.

---

## 2. What OTP Is Not

Understanding the non-goals prevents scope creep and bad architecture decisions.

- **Not a content moderation system.** OTP scores authenticity, not legality or decency.
- **Not a real-time streaming pipeline.** P50 latency target is 8–15 seconds for images, 3–6 seconds for text. Video will be longer. Design accordingly.
- **Not a black box classifier.** Every score must be explainable via `agent_reports`. If an agent can't surface a human-readable reason for its output, it ships with a caveat flag.
- **Not a source of truth for legal proceedings.** OTP scores are probabilistic attestations, not legal evidence. Communicate this in all public-facing copy.

---

## 3. System Architecture

### 3.1 Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                        Intake Layer                             │
│                                                                 │
│   Client / Browser Extension                                    │
│         │                                                       │
│         │  HTTP POST /ingest (multipart)                        │
│         ▼                                                       │
│   API Gateway (rate limiter, auth, media normalization)         │
│         │                                                       │
│         │  Validated Job Payload                                │
│         ▼                                                       │
│   Orchestrator Service                                          │
│         │                                                       │
│         │  Publishes otp.jobs.<task_id> to Kafka               │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │  Provenance  │ │  Heuristics  │ │ Web Consensus│
     │    Agent     │ │    Agent     │ │    Agent     │
     └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
            │                │                │
            └───────────────►│◄───────────────┘
                             │
              Each publishes to otp.results.<task_id>
                             │
                             ▼
                     Orchestrator Service
                     (result collector)
                             │
                     Weighted ensemble score
                             │
                             ▼
                     Ledger Commitment Agent
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
                  IPFS          Blockchain L2
                    │
                    └──► TruthConsensus returned to client
```

### 3.2 Message Bus

**Kafka is the canonical message bus.** Redis Pub/Sub was considered and rejected — it is fire-and-forget with no persistence. In a protocol where every job must be traceable and recoverable, message loss is unacceptable.

| Parameter | Value |
|-----------|-------|
| Broker | Apache Kafka (self-hosted via KRaft mode, or Confluent Cloud for managed) |
| Topic naming | `otp.jobs.<task_id>` (fan-out), `otp.results.<task_id>` (collection) |
| Retention | 7 days (allows job replay and audit) |
| Partitions | 12 (default) — scale per throughput |
| Replication factor | 3 (production) |
| Consumer group | One per agent type (e.g., `cg-heuristics`) |

### 3.3 Workflow Orchestration

**Temporal.io** is used for the Orchestrator's state machine, replacing the originally proposed LangGraph. LangGraph is designed for conversational agent loops and carries significant overhead unsuitable for high-throughput media verification.

Temporal provides:
- Durable workflow state across process restarts
- Automatic retries with configurable backoff
- Built-in timeout handling per activity
- Full execution history for debugging

Each media verification job is a single Temporal workflow. The three analysis agents are Temporal Activities executed in parallel via `workflow.execute_activity()`.

### 3.4 Object Storage

Raw media blobs are stored in S3-compatible object storage immediately on ingest. Agents receive a `blob_uri` — they never receive the raw bytes in a Kafka message. This keeps message payloads small and avoids duplicating large media files across the bus.

For `text/*` submissions, the content is written to S3 as a UTF-8 `.txt` blob at the same `blob_uri` path. Agents treat it identically to binary media — pull from S3, process, publish result. Text is never inlined into the Kafka payload regardless of length.

### 3.5 Media Type → Agent Routing

Not all agents are useful for all media types. The Orchestrator routes fan-out based on `media_type` using the following matrix. Agents not included in the fan-out for a given type are skipped — they do not receive the job, do not time out, and do not affect the score.

| Agent | `image/*` | `video/*` | `audio/*` | `text/*` |
|-------|-----------|-----------|-----------|----------|
| Provenance | ✅ Full | ✅ Full | ⚠️ EXIF only | ⚠️ Document metadata only |
| Heuristics | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| Web Consensus | ✅ Full | ✅ Full | ⚠️ Audio fingerprint only | ✅ Full |

**Text routing rationale:**
- Provenance runs in a degraded mode: no C2PA, no PRNU, no camera signing. It inspects document metadata (`.docx` OOXML properties, PDF XMP, HTML `<meta>`) for authorship claims and modification timestamps. Its weight drops to 0.10 (same as missing-C2PA image path — see §7).
- Heuristics is the primary signal for text: perplexity, burstiness, segment-level LLM classification.
- Web Consensus is strong for text: verbatim match detection, semantic similarity against indexed content, quote attribution verification, temporal anomaly detection ("this article claims to be from 2026 but this paragraph appeared in a 2023 post").

The routing table is defined in `orchestrator/routing.py` and must be kept in sync with this section.

---

## 4. Infrastructure Contracts

These are non-negotiable. Every agent must comply.

### 4.1 Agent Isolation

Each agent is a fully independent service:
- Runs in its own Docker container
- Has its own `requirements.txt` / `package.json`
- Owns its own database or cache namespace if needed
- Communicates **only** via Kafka topics and S3 — never direct HTTP calls between agents

### 4.2 Idempotency

Every agent **must** be idempotent on `task_id`. If the same job is delivered twice (Kafka at-least-once delivery), the agent must detect the duplicate and either skip processing or return the cached result. Use Redis with a TTL of 24h keyed on `task_id` for deduplication.

### 4.3 Result Publishing Contract

Every agent publishes a result to `otp.results.<task_id>` within its SLA window (defined per agent below). The result envelope is:

```json
{
  "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "agent": "heuristics",
  "status": "success",
  "duration_ms": 4230,
  "payload": { /* agent-specific, see §5 */ },
  "error": null
}
```

If the agent fails, `status` is `"error"`, `payload` is `null`, and `error` contains a structured error object:

```json
{
  "code": "MODEL_LOAD_FAILURE",
  "message": "Could not load PRNU model checkpoint",
  "retryable": true
}
```

The Orchestrator treats `retryable: true` errors differently from terminal failures (see §8).

### 4.4 Observability

Every agent must emit:
- **Structured logs** (JSON to stdout) — no unstructured print statements in production paths
- **Prometheus metrics** on `:9090/metrics` — at minimum: `otp_agent_jobs_total`, `otp_agent_job_duration_seconds`, `otp_agent_errors_total`
- **Distributed traces** via OpenTelemetry with `task_id` as the root span attribute

---

## 5. Agent Specifications

---

### 5.1 Orchestrator Agent

**Language:** Python 3.12  
**Framework:** Temporal.io Python SDK  
**SLA:** Workflow must complete (or time out gracefully) within **60 seconds** for images/audio, **30 seconds** for text, **300 seconds** for video.

#### Responsibilities

1. Receive validated ingest payloads from the API Gateway.
2. Generate a `task_id` (UUIDv4) and normalize the media blob to S3. For text payloads, write the UTF-8 content to S3 as a `.txt` blob.
3. Determine the agent fan-out set from the media type routing table (§3.5).
4. Start a Temporal workflow that fans out to the applicable analysis agents in parallel.
5. Collect results from `otp.results.<task_id>` as they arrive. Do **not** block on all — process each result as it lands.
6. After all results arrive (or the timeout fires), run the weighted ensemble scorer (§7) to produce a `final_truth_score`.
7. Pass the compiled report to the Ledger Commitment Agent.
8. Return the `TruthConsensus` to the client.

#### Job Payload Schema (published to Kafka)

```json
{
  "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "timestamp_utc": "2026-04-17T18:55:00Z",
  "media_type": "image/jpeg",
  "media_size_bytes": 2048576,
  "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "blob_uri": "s3://otp-intake/f47ac10b-58cc-4372-a567-0e02b2c3d479/original.jpg",
  "active_agents": ["provenance", "heuristics", "web_consensus"],
  "client_metadata": {
    "source_url": "https://example.com/article/image.jpg",
    "submitted_by": "browser-extension-v1.2"
  }
}
```

For text submissions, `media_type` is one of `text/plain`, `text/html`, or `text/markdown`. The `blob_uri` points to the S3-stored UTF-8 blob. `active_agents` is populated by the Orchestrator from the routing table (§3.5) — agents that are not in this list must ignore the job.

**Text payload example:**
```json
{
  "task_id": "a1b2c3d4-...",
  "timestamp_utc": "2026-04-17T19:00:00Z",
  "media_type": "text/plain",
  "media_size_bytes": 4200,
  "sha256_hash": "abc123...",
  "blob_uri": "s3://otp-intake/a1b2c3d4-.../content.txt",
  "active_agents": ["provenance", "heuristics", "web_consensus"],
  "client_metadata": {
    "source_url": "https://example.com/article",
    "submitted_by": "api-v1"
  }
}
```

#### Timeout Behavior

If an agent does not publish a result within its SLA window, the Orchestrator marks that agent's result as `status: "timeout"` and proceeds with available results. A score can be computed from 2/3 agents. If 2+ agents time out, the job returns `verdict: "INCONCLUSIVE"` with a partial report.

---

### 5.2 Cryptographic Provenance Agent

**Language:** Python 3.12  
**Stack:** `c2pa-python`, `pyca/cryptography`, `Pillow`, `exiftool` (subprocess), `python-docx`, `pypdf`  
**SLA:** 3 seconds (P95)  
**Topic subscription:** `otp.jobs.*`

#### Responsibilities

This agent answers one question: *Does this file carry verifiable proof of where it came from?*

**Check `active_agents` in the job payload before processing.** If `"provenance"` is not in `active_agents`, discard the message immediately.

The agent branches on `media_type`:

**Image / Video / Audio path:**
1. Pull the blob from `blob_uri`.
2. Attempt C2PA manifest extraction. C2PA is the open standard for cryptographic content provenance (used by Sony, Nikon, Leica, Adobe, and the Content Authenticity Initiative).
3. If a C2PA manifest is present, validate the certificate chain against the C2PA Trust List.
4. Extract EXIF/IPTC metadata and flag anomalies: missing mandatory fields, mismatched timestamps, evidence of stripping tools (e.g., `ExifTool` writes a signature).
5. Check GPS coordinates (if present) against claimed location context from `client_metadata`.

**Text path (`text/*`):**
1. Pull the blob from `blob_uri`.
2. For `.docx` blobs: extract OOXML core properties (`dc:creator`, `dcterms:created`, `dcterms:modified`, revision count). Flag mismatches between claimed publish date and document modification timestamp.
3. For PDF blobs: extract XMP metadata (`xmp:CreatorTool`, `xmp:CreateDate`, `pdf:Producer`). Flag documents created by known AI writing tools (e.g., Jasper, Copy.ai, Writer — maintain a list in `provenance/ai_tool_signatures.json`).
4. For plain text / HTML / Markdown: extract `<meta>` author tags, OpenGraph `og:article:author`, and any embedded digital signatures. Signal is weak — score accordingly.
5. Check claimed authorship against `client_metadata.source_url` byline if available.

#### Output Payload

For image/video/audio:
```json
{
  "c2pa_manifest_present": true,
  "c2pa_manifest_valid": true,
  "hardware_signer": "Nikon Z9",
  "certificate_chain_valid": true,
  "editing_history": ["Adobe Lightroom 7.2"],
  "exif_anomalies": [],
  "metadata_stripped": false,
  "provenance_score": 0.91
}
```

For text:
```json
{
  "c2pa_manifest_present": false,
  "document_metadata": {
    "creator": "Jane Smith",
    "created_date": "2026-04-17",
    "modified_date": "2026-04-17",
    "creator_tool": "Microsoft Word 16.0",
    "revision_count": 3
  },
  "ai_tool_signature_match": false,
  "timestamp_anomaly": false,
  "provenance_score": 0.45
}
```

`provenance_score` is a normalized `[0.0, 1.0]` float. For text, scores will generally be lower (0.3–0.6 range) due to weak signal — the ensemble weight is adjusted accordingly (§7).

#### Important Notes

- A missing C2PA manifest is **not** evidence of fakery. Most cameras don't sign yet. The agent must not penalize absence — only reward presence.
- Hardware signing (in-camera cryptography) is weighted ~3x higher than software-level C2PA claims (which can be added post-hoc by any Adobe tool).
- For text, the `ai_tool_signatures.json` list must be actively maintained. File a GitHub Issue when a new AI writing tool enters mainstream use.

---

### 5.3 Synthetic Heuristics Agent

**Language:** Python 3.12  
**Stack:** PyTorch 2.x, Hugging Face `transformers`, `torchaudio`, `opencv-python`, `scipy`, `nltk`  
**SLA:** 15 seconds (P95) for images; 60 seconds (P95) for video clips ≤60s; 5 seconds (P95) for text  
**Topic subscription:** `otp.jobs.*`  
**Hardware requirement:** NVIDIA GPU with ≥16GB VRAM (A10G or equivalent). CPU fallback supported but will exceed SLA for image/video.

#### Responsibilities

This agent answers: *Does this content exhibit statistical fingerprints of synthetic generation?*

**Check `active_agents` in the job payload before processing.** If `"heuristics"` is not in `active_agents`, discard the message.

The agent branches on `media_type`:

**Image path:**
- **Frequency domain analysis.** Apply 2D FFT and inspect the power spectrum for the periodic grid artifacts characteristic of latent diffusion upscaling. GAN outputs leave different patterns than diffusion models — check both.
- **PRNU (Photo Response Non-Uniformity).** Real camera sensors have a unique fixed-pattern noise fingerprint. Extract and compare against a reference database of known camera PRNU profiles. AI-generated images have no PRNU.
- **Classifier ensemble.** Run the image through at minimum two independent deepfake detection classifiers (e.g., UniversalFakeDetect, Grounding DINO for inconsistency detection). Do not ship with a single classifier — single-model results are too gameable.

**Text path:**
- **Perplexity scoring.** Compute token-level perplexity against a reference LM. LLM-generated text tends toward low, uniform perplexity. Compute per-segment (every ~100 tokens) rather than document-level — a human-written article with one AI-generated paragraph will have a perplexity spike in that segment.
- **Burstiness.** Compute the variance of per-segment perplexity scores. Human writing has high burstiness (complex sentences followed by simple ones); LLM output is characteristically flat. This is a more robust signal than raw perplexity alone and harder to spoof by prompt engineering.
- **Classifier ensemble.** Run through at minimum two LLM-output detectors (e.g., a RoBERTa-based detector fine-tuned on GPT-4/Claude outputs, plus a binoculars-style zero-shot detector). Report individual votes — do not average into a single number before surfacing.
- **Stylometric analysis.** Compute function word frequency distributions, sentence length variance, and punctuation density. Flag documents that fall statistically outside the distribution of the claimed author's known writing (if `source_url` resolves to a bylined publication).
- **Watermark detection.** Attempt to detect soft watermarks from known providers (OpenAI's text watermarking scheme if publicly documented; any vendor that publishes a detection API). A positive watermark detection is a strong synthetic signal, not just a probability.

**Audio path:**
- Analyze Mel-frequency cepstral coefficients (MFCCs) for the formant transition artifacts introduced by neural vocoders.
- Check for unnatural phase continuity — real speech has micro-variations; voice-cloned audio is frequently too smooth.
- Run a GAN discriminator trained on codec2 and Encodec artifacts.

#### Output Payload

For image/video/audio:
```json
{
  "synthetic_probability": 0.04,
  "confidence": 0.89,
  "signals": {
    "frequency_artifact_score": 0.02,
    "prnu_match": true,
    "prnu_camera_model": "Nikon Z9",
    "classifier_votes": {
      "UniversalFakeDetect": 0.03,
      "secondary_classifier": 0.05
    }
  },
  "anomalies_detected": [],
  "heuristics_score": 0.96
}
```

For text:
```json
{
  "synthetic_probability": 0.87,
  "confidence": 0.82,
  "signals": {
    "mean_perplexity": 23.4,
    "burstiness": 0.12,
    "high_synthetic_segments": [
      { "start_char": 1200, "end_char": 1850, "probability": 0.94 }
    ],
    "classifier_votes": {
      "roberta_detector": 0.89,
      "binoculars": 0.85
    },
    "watermark_detected": false,
    "stylometric_anomaly": true
  },
  "anomalies_detected": ["low_burstiness", "stylometric_outlier"],
  "heuristics_score": 0.13
}
```

`heuristics_score` is `1.0 - synthetic_probability`, weighted by confidence. A low-confidence result pulls the score toward 0.5 (neutral) rather than toward authentic.

#### Model Management

- All model weights are stored in a shared model registry (S3 path: `s3://otp-models/`). Agents pull weights on cold start.
- Model versions are pinned in `models/manifest.json`. Never load `latest` in production.
- New models must be benchmarked on the OTP eval suite (see `/eval/`) before being added to the manifest.

---

### 5.4 Web Consensus Agent

**Language:** Python 3.12  
**Stack:** LangChain, Tavily Search API, Weaviate (vector DB), Google Fact Check Tools API  
**SLA:** 20 seconds (P95)  
**Topic subscription:** `otp.jobs.*`

#### Responsibilities

This agent answers: *What does the open web know about this media?*

**Check `active_agents` in the job payload before processing.** If `"web_consensus"` is not in `active_agents`, discard the message.

**Image / Video path:**
1. **Perceptual hash lookup.** Compute a pHash of the media and query the Google Fact Check Tools API and known deepfake registries (e.g., Sensity, DFR Lab datasets) for matches.
2. **Reverse image search.** Use SerpAPI or Tavily to find earliest indexed appearances of this image or semantically similar images.
3. **Temporal anomaly detection.** If the media is presented in a context implying recency (e.g., "2026 event"), but the reverse search surfaces the same image indexed in 2022, that is a strong manipulation signal. Flag it explicitly.
4. **Context cross-reference.** Extract named entities from `client_metadata.source_url` and the surrounding article. Verify that claimed context (people, places, events) is consistent with what the web knows about this image.
5. **Known manipulation registry check.** Query the Weaviate vector store (populated with embeddings from known synthetic media datasets) for semantic similarity matches.

**Text path:**
1. **Verbatim match detection.** Compute a SHA-256 of normalized text (strip whitespace, lowercase) and check against a cache of previously verified content. Then search Tavily for verbatim or near-verbatim passages.
2. **Semantic similarity search.** Embed the document using a sentence-transformer model and query Weaviate for high-similarity matches in the known-synthetic text corpus. A cosine similarity > 0.92 against known AI-generated content is flagged.
3. **Quote attribution verification.** Extract quoted statements from the text (e.g., `"According to [Name]..."`). Verify each significant quote against indexed sources. Hallucinated quotes are a strong synthetic signal.
4. **Temporal anomaly detection.** If the article claims recency but core factual claims or phrasing match articles indexed months or years earlier, flag it. LLM-generated content frequently recycles prior framing.
5. **Source cross-reference.** If `client_metadata.source_url` is provided, fetch the page and verify that the submitted text actually matches the published content. Flag discrepancies (content may have been post-hoc AI-substituted).

#### Output Payload

For image/video:
```json
{
  "phash": "d4f3a2c1b0e9d8c7",
  "earliest_web_index_date": "2026-04-17",
  "known_deepfake_registry_match": false,
  "fact_check_results": [],
  "temporal_anomaly": false,
  "context_consistency_score": 0.88,
  "web_consensus_score": 0.85
}
```

For text:
```json
{
  "content_hash": "sha256:abc123...",
  "verbatim_match_found": false,
  "semantic_similarity_score": 0.31,
  "known_synthetic_corpus_match": false,
  "quote_attribution_failures": [],
  "temporal_anomaly": false,
  "source_url_content_match": true,
  "web_consensus_score": 0.79
}
```

#### Rate Limiting & Caching

Tavily and SerpAPI calls are expensive. Cache pHash lookup results in Redis with a 24-hour TTL keyed on `phash`. If a hash hits the cache, skip the external API calls and return the cached result. Log cache hits to Prometheus (`otp_webconsensus_cache_hits_total`).

For text, cache by `sha256_hash` of the normalized content. Semantic similarity queries against Weaviate are not cached (they're fast and results change as the corpus grows).

---

### 5.5 Ledger Commitment Agent

**Language:** Python 3.12  
**Stack:** `web3.py`, `ipfshttpclient`, Solidity/Rust smart contract (deployed separately)  
**SLA:** 30 seconds (P95, dominated by blockchain confirmation time)  
**Invocation:** Called directly by the Orchestrator after scoring, not via Kafka fan-out.

#### Responsibilities

1. Receive the full compiled `TruthConsensus` JSON from the Orchestrator.
2. Pin the report to IPFS. Retrieve the CID.
3. Write a minimal on-chain record to the OTP smart contract:
   ```
   commit(sha256_hash, ipfs_cid, final_truth_score_basis_points, task_id)
   ```
   `final_truth_score_basis_points` = `final_truth_score * 10000` as a uint16 (avoids float on-chain).
4. Wait for 1 block confirmation (do not wait for finality — that's too slow for UX).
5. Return the `ledger_receipt` to the Orchestrator.

#### Chain Selection

| Environment | Network |
|-------------|---------|
| Production | Arbitrum One (Ethereum L2) — low fees, EVM-compatible, ~0.3s block time |
| Staging | Arbitrum Sepolia testnet |
| Local dev | Hardhat local node |

**Do not write to Ethereum mainnet.** L1 gas costs make per-verification commits economically inviable.

#### IPFS Pinning

Use Pinata as the managed IPFS pinning service. The raw IPFS daemon is not reliable enough for production. Configure a backup pin to Web3.Storage.

#### Smart Contract Interface

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IOTPLedger {
    event AttestationCommitted(
        bytes32 indexed mediaHash,
        string ipfsCid,
        uint16 scoreBasisPoints,
        bytes32 taskId,
        uint256 timestamp
    );

    function commit(
        bytes32 mediaHash,
        string calldata ipfsCid,
        uint16 scoreBasisPoints,
        bytes32 taskId
    ) external;

    function getAttestation(bytes32 mediaHash)
        external
        view
        returns (string memory ipfsCid, uint16 scoreBasisPoints, uint256 timestamp);
}
```

---

## 6. Shared Data Schemas

### 6.1 TruthConsensus (Final Output)

This is the canonical output returned to clients and stored on IPFS. This schema is **versioned** — breaking changes require a minor version bump in `otp_version`.

```json
{
  "otp_version": "2.2",
  "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "media_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "media_type": "image/jpeg",
  "processed_at_utc": "2026-04-17T18:55:14Z",
  "processing_duration_ms": 11240,
  "final_truth_score": 0.89,
  "verdict": "LIKELY_AUTHENTIC",
  "agent_reports": {
    "provenance": {
      "status": "success",
      "duration_ms": 1200,
      "c2pa_manifest_present": true,
      "c2pa_manifest_valid": true,
      "hardware_signer": "Nikon Z9",
      "metadata_stripped": false,
      "provenance_score": 0.91
    },
    "heuristics": {
      "status": "success",
      "duration_ms": 4230,
      "synthetic_probability": 0.04,
      "confidence": 0.89,
      "heuristics_score": 0.96
    },
    "web_consensus": {
      "status": "success",
      "duration_ms": 9100,
      "earliest_web_index_date": "2026-04-17",
      "known_deepfake_registry_match": false,
      "temporal_anomaly": false,
      "web_consensus_score": 0.85
    }
  },
  "ledger_receipt": {
    "network": "Arbitrum One",
    "transaction_hash": "0xabc123...",
    "block_number": 198234221,
    "ipfs_cid": "bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi",
    "committed_at_utc": "2026-04-17T18:55:44Z"
  }
}
```

**Text submission example:**
```json
{
  "otp_version": "2.2",
  "task_id": "a1b2c3d4-...",
  "media_hash": "abc123...",
  "media_type": "text/plain",
  "processed_at_utc": "2026-04-17T19:00:08Z",
  "processing_duration_ms": 6100,
  "final_truth_score": 0.21,
  "verdict": "LIKELY_SYNTHETIC",
  "agent_reports": {
    "provenance": {
      "status": "success",
      "duration_ms": 800,
      "c2pa_manifest_present": false,
      "document_metadata": { "creator_tool": "Microsoft Word 16.0" },
      "ai_tool_signature_match": false,
      "provenance_score": 0.45
    },
    "heuristics": {
      "status": "success",
      "duration_ms": 3200,
      "synthetic_probability": 0.87,
      "confidence": 0.82,
      "signals": {
        "mean_perplexity": 23.4,
        "burstiness": 0.12,
        "watermark_detected": false
      },
      "anomalies_detected": ["low_burstiness", "stylometric_outlier"],
      "heuristics_score": 0.13
    },
    "web_consensus": {
      "status": "success",
      "duration_ms": 5100,
      "verbatim_match_found": false,
      "semantic_similarity_score": 0.31,
      "quote_attribution_failures": [],
      "temporal_anomaly": false,
      "web_consensus_score": 0.79
    }
  },
  "ledger_receipt": { "..." : "..." }
}
```

### 6.2 Verdict Mapping

| Score Range | Verdict |
|-------------|---------|
| 0.85 – 1.00 | `LIKELY_AUTHENTIC` |
| 0.60 – 0.84 | `UNVERIFIED` |
| 0.40 – 0.59 | `INCONCLUSIVE` |
| 0.15 – 0.39 | `LIKELY_SYNTHETIC` |
| 0.00 – 0.14 | `SYNTHETIC` |

If 2 or more agents returned `status: "timeout"` or `status: "error"`, the verdict is forced to `INCONCLUSIVE` regardless of score.

---

## 7. Scoring Model

The `final_truth_score` is a weighted ensemble of the active agent scores. Weights differ by media type — text has weak provenance signal and strong heuristics signal, which the weights reflect.

### Default Weights by Media Type

**Image / Video / Audio:**

| Agent | Weight | Rationale |
|-------|--------|-----------|
| Heuristics | 0.50 | Hardest to spoof; directly detects synthesis artifacts |
| Provenance | 0.30 | High signal when present; zero signal when absent (weight redistributed) |
| Web Consensus | 0.20 | Valuable corroboration; gameable with SEO/seeding attacks |

**Text:**

| Agent | Weight | Rationale |
|-------|--------|-----------|
| Heuristics | 0.60 | Primary signal for text — perplexity, burstiness, classifiers |
| Web Consensus | 0.30 | Strong for text — verbatim match, quote attribution, temporal anomaly |
| Provenance | 0.10 | Weak signal — document metadata is easily spoofed or absent |

### Weight Redistribution on Missing Provenance

If C2PA is not present (`c2pa_manifest_present: false`), the Provenance agent produces a partial score based only on EXIF analysis. Its weight drops to 0.10 and the remaining 0.20 redistributes proportionally to Heuristics (0.14 added) and Web Consensus (0.06 added).

### Confidence Discounting

Each agent exposes a `confidence` field. If `confidence < 0.60`, the agent's contribution is pulled toward 0.5 (neutral) before weighting:

```python
def apply_confidence_discount(score: float, confidence: float) -> float:
    if confidence >= 0.60:
        return score
    blend_factor = confidence / 0.60
    return score * blend_factor + 0.5 * (1 - blend_factor)
```

### Final Computation

```python
def compute_truth_score(reports: dict, weights: dict) -> float:
    total_weight = 0.0
    weighted_sum = 0.0

    for agent, report in reports.items():
        if report["status"] != "success":
            continue
        score = apply_confidence_discount(
            report["agent_score"],
            report.get("confidence", 1.0)
        )
        w = weights[agent]
        weighted_sum += score * w
        total_weight += w

    if total_weight == 0:
        return 0.5  # No data — inconclusive

    # Renormalize in case agents timed out
    return weighted_sum / total_weight
```

---

## 8. Error Handling & Timeouts

### Per-Agent SLA and Timeout Policy

| Agent | Soft SLA (P95) | Hard Timeout | On Timeout |
|-------|---------------|-------------|------------|
| Provenance | 3s | 8s | Mark timeout, continue |
| Heuristics | 15s | 30s | Mark timeout, continue |
| Web Consensus | 20s | 45s | Mark timeout, continue |
| Ledger | 30s | 60s | Return report without ledger receipt; queue retry |

### Retry Policy

- Agent failures with `retryable: true` are retried by Temporal with exponential backoff: `[1s, 2s, 4s]`, max 3 attempts.
- Ledger commitment failures are queued in a dedicated Kafka topic (`otp.ledger.retry`) and retried by a background worker independently of the client response. Clients receive the `TruthConsensus` without a `ledger_receipt` and are notified via webhook when commitment completes.
- Never retry Web Consensus calls within the same job — they're expensive and the result is time-sensitive. Log the failure and mark the agent as `status: "error"`.

### Degraded Mode

If the Heuristics agent is down entirely (circuit breaker open), the system operates in degraded mode: Provenance + Web Consensus only, with an explicit `degraded_mode: true` flag in the `TruthConsensus`. Do not silently return scores in degraded mode without flagging it.

---

## 9. Adding a New Agent

OTP is designed to be extended. Community agents go through a defined review process before inclusion in the production swarm.

### Step 1: Proposal

Open a GitHub Discussion in the `agent-proposals` category. Include:
- What signal the agent detects that existing agents don't cover
- Estimated SLA and hardware requirements
- Benchmark results on the OTP eval dataset (`/eval/benchmark/`)
- False positive rate on the known-authentic test set

### Step 2: Implementation Requirements

Your agent must:
- [ ] Subscribe to `otp.jobs.*` and consume `JobPayload` (§6 schema)
- [ ] Publish to `otp.results.<task_id>` with the standard result envelope (§4.3)
- [ ] Be idempotent on `task_id` (§4.2)
- [ ] Expose Prometheus metrics on `:9090/metrics` (§4.4)
- [ ] Include a `Dockerfile` and `docker-compose` entry
- [ ] Pass all tests in `/eval/` on the standard benchmark set
- [ ] Document its scoring logic and output fields in this file (§5)

### Step 3: Review

Maintainers review the proposal and implementation. A new agent requires:
- 2 maintainer approvals
- False positive rate < 5% on the known-authentic test set
- No regression on the existing benchmark suite

### Step 4: Weight Assignment

New agents initially run in **shadow mode** — they process jobs and publish results, but their scores are not included in the ensemble. After 30 days of production shadow data, maintainers review performance metrics and assign a weight. The existing weights are renormalized to sum to 1.0.

---

## 10. Local Development

### Prerequisites

- Docker Desktop (or Colima on macOS)
- Python 3.12
- Node.js 20+ (for smart contract tooling)
- Hardhat (for local blockchain)

### Quickstart

```bash
# Clone and enter
git clone https://github.com/open-truth-protocol/otp
cd otp

# Spin up infrastructure (Kafka, Zookeeper, Redis, Weaviate, local S3)
docker compose up -d infra

# Start Temporal dev server
temporal server start-dev

# Run a specific agent in isolation
cd agents/heuristics
pip install -r requirements.txt
python agent.py --dev

# Verify a local file end-to-end (CLI tool)
otp-verify ./samples/test-image.jpg
```

### Running the Full Stack

```bash
docker compose up
# All agents, orchestrator, and API gateway start
# Temporal UI at http://localhost:8088
# API at http://localhost:8000
# Prometheus at http://localhost:9090
```

### Test Data

The `/eval/` directory contains:
- `known_authentic/` — 500 verified real images with C2PA manifests
- `known_synthetic/` — 500 AI-generated images across 10 model families
- `adversarial/` — 100 synthetic images with anti-detection post-processing applied
- `benchmark.py` — Runs all agents against the full test set and outputs a score report

Always run `benchmark.py` before opening a PR that touches any agent's scoring logic.

---

## 11. Environment Variables

All secrets are loaded from environment. Never commit secrets or hardcode values. Use `.env.local` for development (gitignored).

```bash
# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_SECURITY_PROTOCOL=PLAINTEXT  # SASL_SSL in production

# Object Storage
S3_ENDPOINT=http://localhost:4566  # LocalStack for dev
S3_BUCKET_INTAKE=otp-intake
S3_BUCKET_MODELS=otp-models
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# Temporal
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=otp-production

# Agent: Web Consensus
TAVILY_API_KEY=...
SERPAPI_KEY=...
WEAVIATE_URL=http://localhost:8080
GOOGLE_FACT_CHECK_API_KEY=...

# Agent: Ledger
ARBITRUM_RPC_URL=https://arb1.arbitrum.io/rpc
OTP_CONTRACT_ADDRESS=0x...
LEDGER_WALLET_PRIVATE_KEY=...  # Use a dedicated deployment wallet
PINATA_JWT=...
WEB3_STORAGE_TOKEN=...

# Observability
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

---

## 12. Roadmap & Phase Gates

### Phase 1 — Core Swarm MVP (Weeks 1–2)

**Gate:** The following must be passing before Phase 2 begins.

- [ ] Orchestrator + Temporal workflow operational
- [ ] Heuristics Agent processing images end-to-end
- [ ] Provenance Agent extracting C2PA and EXIF
- [ ] `otp-verify <file>` CLI tool installable via `pip install otp-verify`
- [ ] Benchmark suite passing: >90% accuracy on known-synthetic, <5% false positives on known-authentic
- [ ] Docker Compose full-stack working on a clean machine

**Launch action:** Publish a thread demonstrating the CLI tearing down viral deepfakes in real-time. Pin the GitHub repo link. Target HN, r/MachineLearning, and relevant Twitter communities.

### Phase 2 — API & Browser Extension (Weeks 3–4)

**Gate:** Phase 1 complete and stable for 5 days.

- [ ] REST API deployed (serverless GPU on Modal or RunPod)
- [ ] Free tier: 100 verifications/day per API key, no auth required for first call
- [ ] Chrome extension: overlays OTP score badge on images in Twitter/X and Reddit feeds
- [ ] Extension pulls score from API; caches by pHash for 24h
- [ ] Web Consensus Agent operational
- [ ] Public dashboard at `opentruthprotocol.org` showing live verification feed (anonymized)

**Viral mechanic:** Extension users who flag a high-profile deepfake share a screenshot of the OTP report. Embed a `otp.gg/<task_id>` shareable link in every report.

### Phase 3 — Protocol Consortium (May 2026+)

- [ ] Ledger Commitment Agent in production on Arbitrum One
- [ ] Smart contract audited by a recognized auditing firm before mainnet deployment
- [ ] Developer SDK (`otp-js`, `otp-py`) published to npm and PyPI
- [ ] B2B integration layer: trust-layer webhook for newsrooms and platforms
- [ ] Community agent submissions open (shadow mode pipeline operational)
- [ ] Governance model documented for long-term protocol stewardship

---

## 13. Contributor Rules

1. **This file is authoritative.** If code contradicts AGENTS.md, the code is wrong. Update one or the other — never leave them diverged.
2. **No agent may call another agent directly.** All communication is through Kafka or the Orchestrator. This is not a suggestion.
3. **Schema changes require a version bump.** If you modify the `TruthConsensus` schema, bump `otp_version` and update the compatibility table in this file.
4. **Benchmark before you merge.** Any PR touching scoring logic must include benchmark output from `/eval/benchmark.py` in the PR description.
5. **Secrets never in code.** Use the environment variable pattern in §11. Any commit containing a credential will be rejected and the key must be rotated.
6. **One language per agent.** Currently: Python 3.12. Introducing a new language requires a maintainer vote.
7. **Document your agent.** A new agent without a §5 entry will not be merged.