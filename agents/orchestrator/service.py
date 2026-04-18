from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from shared.constants import HARD_TIMEOUT_SECONDS, JOB_TOPIC_PREFIX
from shared.kafka_client import KafkaProducerClient
from shared.routing import get_active_agents
from shared.schemas import (
    ClientMetadata,
    ErrorPayload,
    JobPayload,
    ResultEnvelope,
    Status,
    TruthConsensus,
)
from shared.scorer import compute_truth_score, map_score_to_verdict


class OrchestratorService:
    def __init__(self, producer: KafkaProducerClient) -> None:
        self._producer = producer
        self._reports: dict[str, dict[str, dict[str, Any]]] = {}
        self._jobs: dict[str, JobPayload] = {}

    @staticmethod
    def _timeout_error_payload(agent: str) -> dict[str, Any]:
        return ErrorPayload(
            code="AGENT_TIMEOUT",
            message=f"{agent} did not publish a result before workflow timeout",
            retryable=False,
        ).model_dump(mode="json")

    @staticmethod
    def _synthetic_timeout_report(agent: str, duration_ms: int) -> dict[str, Any]:
        return {
            "task_id": "",
            "agent": agent,
            "status": Status.TIMEOUT.value,
            "duration_ms": max(duration_ms, 0),
            "payload": None,
            "error": OrchestratorService._timeout_error_payload(agent),
        }

    def _finalize_with_missing_timeouts(self, task_id: str) -> None:
        job = self._jobs[task_id]
        reports = self._reports.setdefault(task_id, {})
        now = datetime.now(tz=UTC)
        duration_ms = int((now - job.timestamp_utc).total_seconds() * 1000)

        for agent in job.active_agents:
            if agent not in reports:
                synthetic = self._synthetic_timeout_report(agent=agent, duration_ms=duration_ms)
                synthetic["task_id"] = task_id
                reports[agent] = synthetic

    def has_task(self, task_id: str) -> bool:
        return task_id in self._jobs

    def is_task_complete(self, task_id: str) -> bool:
        job = self._jobs.get(task_id)
        if job is None:
            return False

        reports = self._reports.get(task_id, {})
        if all(agent in reports for agent in job.active_agents):
            return True

        timeout_seconds = self.workflow_timeout_for_media_type(job.media_type)
        elapsed_seconds = max(
            0.0,
            (datetime.now(tz=UTC) - job.timestamp_utc).total_seconds(),
        )
        if elapsed_seconds >= timeout_seconds:
            self._finalize_with_missing_timeouts(task_id)
            return True

        return False

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
        job = self._jobs.get(result.task_id)
        if job is None:
            return
        if result.agent not in job.active_agents:
            return

        task_reports = self._reports.setdefault(result.task_id, {})
        task_reports[result.agent] = result.model_dump(mode="json")

    def get_consensus(self, task_id: str) -> TruthConsensus | None:
        job = self._jobs.get(task_id)
        if not job:
            return None

        if not self.is_task_complete(task_id):
            return None

        reports = self._reports.get(task_id, {})
        if not reports:
            return None

        final_score = compute_truth_score(job.media_type, reports)
        verdict = map_score_to_verdict(final_score, reports)
        degraded_mode = "heuristics" not in job.active_agents

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
            degraded_mode=degraded_mode,
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
