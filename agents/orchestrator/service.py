from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from shared.constants import HARD_TIMEOUT_SECONDS, JOB_TOPIC_PREFIX
from shared.kafka_client import KafkaProducerClient
from shared.routing import get_active_agents
from shared.schemas import ClientMetadata, JobPayload, ResultEnvelope, TruthConsensus
from shared.scorer import compute_truth_score, map_score_to_verdict


class OrchestratorService:
    def __init__(self, producer: KafkaProducerClient) -> None:
        self._producer = producer
        self._reports: dict[str, dict[str, dict[str, Any]]] = {}
        self._jobs: dict[str, JobPayload] = {}

    async def create_job(
        self,
        *,
        media_type: str,
        media_size_bytes: int,
        blob_uri: str,
        source_url: str | None,
        submitted_by: str | None,
    ) -> JobPayload:
        task_id = str(uuid4())
        active_agents = list(get_active_agents(media_type))
        sha256_hash = hashlib.sha256(blob_uri.encode("utf-8")).hexdigest()
        job = JobPayload(
            task_id=task_id,
            timestamp_utc=datetime.now(tz=UTC),
            media_type=media_type,
            media_size_bytes=media_size_bytes,
            sha256_hash=sha256_hash,
            blob_uri=blob_uri,
            active_agents=active_agents,
            client_metadata=ClientMetadata(source_url=source_url, submitted_by=submitted_by),
        )
        topic = f"{JOB_TOPIC_PREFIX}.{task_id}"
        await self._producer.send(topic=topic, payload=job.model_dump(mode="json"), key=task_id)
        self._jobs[task_id] = job
        self._reports[task_id] = {}
        return job

    def add_result(self, result: ResultEnvelope) -> None:
        task_reports = self._reports.setdefault(result.task_id, {})
        task_reports[result.agent] = result.model_dump(mode="json")

    def get_consensus(self, task_id: str) -> TruthConsensus | None:
        job = self._jobs.get(task_id)
        if not job:
            return None
        reports = self._reports.get(task_id, {})
        if not reports:
            return None

        final_score = compute_truth_score(job.media_type, reports)
        verdict = map_score_to_verdict(final_score, reports)

        now = datetime.now(tz=UTC)
        processing_duration_ms = int((now - job.timestamp_utc).total_seconds() * 1000)

        return TruthConsensus(
            task_id=task_id,
            media_hash=job.sha256_hash,
            media_type=job.media_type,
            processed_at_utc=now,
            processing_duration_ms=max(processing_duration_ms, 0),
            final_truth_score=final_score,
            verdict=verdict,
            agent_reports=reports,
            ledger_receipt=None,
        )

    @staticmethod
    def workflow_timeout_for_media_type(media_type: str) -> int:
        if media_type.startswith("text/"):
            return 30
        if media_type.startswith("video/"):
            return 300
        if media_type.startswith("image/") or media_type.startswith("audio/"):
            return 60
        return HARD_TIMEOUT_SECONDS["heuristics"]
