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

OTP is a decentralized, open-source protocol for specialized AI agents that collectively verify the authenticity of digital media **locally on user hardware**. A piece of media — image, video, audio, or text — is processed by a local orchestrator; a cryptographically anchored `TruthConsensus` record is generated. The protocol is:

- **Local-First.** Users run the analysis on their own devices. No media ever leaves the user's control.
- **Asynchronous.** Agents run in parallel. No agent blocks another.
- **Modular.** Agents are independent modules or containers with well-defined input/output contracts.
- **Immutable.** Every attestation is pinned to IPFS and hashed onto a public ledger. It cannot be altered retroactively.

---

## 2. What OTP Is Not

Understanding the non-goals prevents scope creep and bad architecture decisions.

- **Not a hosted SaaS.** OTP is software you run, not a service you call.
- **Not a content moderation system.** OTP scores authenticity, not legality or decency.
- **Not a source of truth for legal proceedings.** OTP scores are probabilistic attestations, not legal evidence.
- **Not a real-time streaming pipeline.** Latency depends on local hardware (CPU/GPU).

---

## 3. System Architecture

### 3.1 Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                        Local Runtime                            │
│                                                                 │
│   CLI / Desktop App / Browser Extension                         │
│         │                                                       │
│         │  Local Ingest (File path / Blob)                      │
│         ▼                                                       │
│   Local Orchestrator (Orchestrator Agent)                       │
│         │                                                       │
│         │  Local Task Dispatch (Redis / multiprocessing)        │
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
```

### 3.2 Task Dispatch

**Redis Pub/Sub or local IPC is the canonical dispatch mechanism.** Unlike the centralized version which required Kafka for high availability, the local version prioritizes low overhead.

| Parameter | Value |
|-----------|-------|
| Broker | Local Redis (primary) or Python `multiprocessing` (fallback) |
| Channel naming | `otp:jobs:<task_id>` (fan-out), `otp:results:<task_id>` (collection) |
| Retention | Job-scoped (cleaned up after completion) |
| Storage | Local RAM / Volatile |

### 3.3 Task Orchestration

**Python Asyncio** or **Celery (Local)** is used for the Orchestrator's state machine. Temporal.io is removed to reduce local system requirements.

The Orchestrator provides:
- Parallel execution of agent modules
- Timeout handling per agent
- Local execution logging for transparent verification

### 3.4 Local Storage

Raw media blobs are stored in a local data directory (default: `~/.otp/data/`). Agents receive a `file_path` — they never receive the raw bytes in a message. This keeps IPC payloads small and uses the local filesystem for efficient random access.

For `text/*` submissions, the content is written to a local `.txt` file.

---

## 4. Infrastructure Contracts

These are non-negotiable. Every agent must comply.

### 4.1 Agent Isolation

Each agent is a fully independent service:
- Runs in its own Docker container or as a standalone Python module
- Communicates **only** via Redis topics or Standard IO
- Reads media from the local storage path provided by the Orchestrator

### 4.2 Idempotency

Every agent **must** be idempotent on `task_id`. If the same job is delivered twice, the agent must detect the duplicate and return the cached result. Use a local SQLite database or Redis with a TTL of 24h for deduplication.

### 4.3 Result Publishing Contract

Every agent publishes a result to `otp:results:<task_id>` within its SLA window. The result envelope is:

```json
{
  "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "agent": "heuristics",
  "status": "success",
  "duration_ms": 4230,
  "payload": { /* agent-specific */ },
  "error": null
}
```

### 4.4 Observability

Every agent must emit:
- **Human-readable logs** to stdout
- **Progress updates** via the dispatch channel
- **Trace files** (optional JSON) in the task directory for debugging

---

## 5. Agent Specifications

### 5.1 Orchestrator Agent

**Language:** Python 3.12  
**Responsibilities:**

1. Receive local ingest requests via CLI/UI.
2. Generate a `task_id` and normalize the media to the local data directory.
3. Determine the agent fan-out set based on `media_type`.
4. Dispatch tasks to the applicable analysis agents in parallel.
5. Collect results and run the weighted ensemble scorer.
6. Store and return the `TruthConsensus` report.

---

### 5.2 Cryptographic Provenance Agent

**Language:** Python 3.12  
**Stack:** `c2pa-python`, `pyca/cryptography`, `Pillow`, `exiftool` (subprocess)  
**Responsibilities:**

1. **C2PA extraction.** Validate cryptographic manifests (Sony, Nikon, Leica, Adobe).
2. **EXIF evaluation.** Flag timestamp anomalies or evidence of metadata stripping.
3. **Document inspection.** Extract OOXML and PDF metadata for text-based files.

---

### 5.3 Synthetic Heuristics Agent

**Language:** Python 3.12  
**Stack:** PyTorch 2.x, Hugging Face `transformers`  
**Responsibilities:**

1. **Frequency Analysis.** Detect periodic grid artifacts from diffusion models.
2. **PRNU extraction.** Compare sensor noise patterns (AI images have no PRNU).
3. **Text Analysis.** Compute perplexity and burstiness to detect LLM-generated text.

---

### 5.4 Web Consensus Agent

**Language:** Python 3.12  
**Stack:** LangChain, Tavily Search API, Local Vector Store (FAISS/Chroma)  
**Responsibilities:**

1. **PHash Lookup.** Check known deepfake registries via perceptual hashes.
2. **Reverse search.** Use Tavily to find earliest indexed appearances.
3. **Context Check.** Detect temporal anomalies (e.g., "new" image indexed in 2022).

---

### 5.5 Ledger Commitment Agent (Optional)

**Language:** Python 3.12  
**Responsibilities:**

1. Pin the report to IPFS (local or via user's Pinata key).
2. Write certificate to a public ledger (Arbitrum/Polygon).

---

## 6. Shared Data Schemas

### 6.1 TruthConsensus (Final Output)

```json
{
  "otp_version": "2.2",
  "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "media_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "media_type": "image/jpeg",
  "final_truth_score": 0.89,
  "verdict": "LIKELY_AUTHENTIC",
  "agent_reports": { ... }
}
```

---

## 7. Scoring Model

The `final_truth_score` is a weighted ensemble of the active agent scores.

### Default Weights

| Media Type | Heuristics | Provenance | Web Consensus |
|------------|------------|------------|---------------|
| Image/Video| 0.50       | 0.30       | 0.20          |
| Text       | 0.60       | 0.10       | 0.30          |

---

## 8. Error Handling & Retry

- Local failures are retried with exponential backoff.
- Ledger failures (if enabled) are logged for manual retry.

---

## 9. Local Installation & Usage

### Setup

```bash
git clone https://github.com/EvanGribar/Open-Truth-Protocol.git
cd opentruthprotocol
uv sync
otp setup  # Downloads required model weights
```

### Usage (CLI)

```bash
otp verify path/to/media.jpg
```

---

## 10. Contributor Rules

1. **Local First.** All core logic must run without a centralized backend.
2. **Schema Integrity.** Changes to `TruthConsensus` require a version bump.
3. **Benchmark Before Merge.** PRs touching scoring must include a benchmark report.
4. **Secrets.** Use `.env` for API keys (Tavily, Pinata). Never commit secrets.
5. **No agent may call another agent directly.** All communication is through the Orchestrator. 
6. **Documentation.** Any new feature or agent MUST be documented in this file.