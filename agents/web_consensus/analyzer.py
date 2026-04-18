"""Deterministic web consensus heuristics used for the first implementation slice."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from shared.schemas import JobPayload


def _derive_content_hash(job: JobPayload) -> str:
    digest = hashlib.sha256()
    digest.update(job.blob_uri.encode("utf-8"))
    digest.update(b"|")
    digest.update(job.media_type.encode("utf-8"))
    digest.update(b"|")
    if job.client_metadata.source_url:
        digest.update(job.client_metadata.source_url.encode("utf-8"))
    return f"sha256:{digest.hexdigest()}"


def analyze(job: JobPayload) -> dict[str, object]:
    """Return a stable, testable web-consensus payload for the supplied job."""

    now = datetime.now(tz=UTC).date().isoformat()

    if job.media_type.startswith("text/"):
        source_url_present = job.client_metadata.source_url is not None
        semantic_similarity_score = 0.31 if source_url_present else 0.19
        web_consensus_score = 0.82 if source_url_present else 0.68
        return {
            "content_hash": _derive_content_hash(job),
            "verbatim_match_found": False,
            "semantic_similarity_score": semantic_similarity_score,
            "known_synthetic_corpus_match": False,
            "quote_attribution_failures": [],
            "temporal_anomaly": False,
            "source_url_content_match": source_url_present,
            "web_consensus_score": web_consensus_score,
            "confidence": 0.84,
        }

    has_source_context = job.client_metadata.source_url is not None
    return {
        "phash": hashlib.sha256(job.blob_uri.encode("utf-8")).hexdigest()[:16],
        "earliest_web_index_date": now,
        "known_deepfake_registry_match": False,
        "fact_check_results": [],
        "temporal_anomaly": False,
        "context_consistency_score": 0.87 if has_source_context else 0.74,
        "web_consensus_score": 0.83 if has_source_context else 0.71,
        "confidence": 0.82,
    }
