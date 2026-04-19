from __future__ import annotations

import hashlib
from collections.abc import MutableMapping
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from cachetools import TTLCache

from shared.constants import JOB_TOPIC_PREFIX, WORKFLOW_TIMEOUTS
from shared.kafka_client import KafkaProducerClient
from shared.observability import get_logger
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

logger = get_logger("orchestrator")


class OrchestratorService:
    def __init__(self, producer: KafkaProducerClient) -> None:
        self._producer = producer
        # Prevent memory leaks with TTL caches (per review feedback)
        self._reports: MutableMapping[str, dict[str, Any]] = TTLCache(maxsize=1000, ttl=3600)
        self._jobs: MutableMapping[str, JobPayload] = TTLCache(maxsize=1000, ttl=3600)
        self._consensus_cache: MutableMapping[str, TruthConsensus] = TTLCache(
            maxsize=1000, ttl=3600
        )

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

    @staticmethod
    def _build_job_payload(
        *,
        task_id: str,
        media_type: str,
        media_size_bytes: int,
        blob_uri: str,
        source_url: str | None,
        submitted_by: str | None,
    ) -> JobPayload:
        active_agents = list(get_active_agents(media_type))
        sha256_hash = hashlib.sha256(blob_uri.encode("utf-8")).hexdigest()
        return JobPayload(
            task_id=task_id,
            timestamp_utc=datetime.now(tz=UTC),
            media_type=media_type,
            media_size_bytes=media_size_bytes,
            sha256_hash=sha256_hash,
            blob_uri=blob_uri,
            active_agents=active_agents,
            client_metadata=ClientMetadata(source_url=source_url, submitted_by=submitted_by),
        )

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
        job = self.create_pending_job(
            media_type=media_type,
            media_size_bytes=media_size_bytes,
            blob_uri=blob_uri,
            source_url=source_url,
            submitted_by=submitted_by,
        )
        await self.dispatch_pending_job(job.task_id)
        return job

    def create_pending_job(
        self,
        *,
        media_type: str,
        media_size_bytes: int,
        blob_uri: str,
        source_url: str | None,
        submitted_by: str | None,
    ) -> JobPayload:
        """Create a new job and store it for dispatch.

        Args:
            media_type: MIME type of media (e.g., 'image/jpeg')
            media_size_bytes: Size of media in bytes
            blob_uri: S3 URI to the media blob
            source_url: Optional source URL for client context
            submitted_by: Optional identifier for request source

        Returns:
            JobPayload with generated task_id and routing configuration

        Raises:
            ValidationError: If media_type is not supported
        """
        task_id = str(uuid4())
        job = self._build_job_payload(
            task_id=task_id,
            media_type=media_type,
            media_size_bytes=media_size_bytes,
            blob_uri=blob_uri,
            source_url=source_url,
            submitted_by=submitted_by,
        )
        self._jobs[task_id] = job
        self._reports[task_id] = {}

        logger.info(
            "job_created",
            task_id=task_id,
            media_type=media_type,
            media_size_bytes=media_size_bytes,
            active_agents=list(job.active_agents),
        )

        return job

    async def dispatch_pending_job(self, task_id: str) -> bool:
        job = self._jobs.get(task_id)
        if job is None:
            return False

        topic = f"{JOB_TOPIC_PREFIX}.{task_id}"
        await self._producer.send(topic=topic, payload=job.model_dump(mode="json"), key=task_id)
        return True

    def add_result(self, result: ResultEnvelope) -> None:
        """Add an agent result to the task reports.

        Validates:
        - Task exists
        - Agent is in active set for this task
        - Result status is one of SUCCESS, ERROR, TIMEOUT

        Args:
            result: ResultEnvelope from an agent
        """
        job = self._jobs.get(result.task_id)
        if job is None:
            logger.warning("result_for_unknown_task", task_id=result.task_id, agent=result.agent)
            return

        if result.agent not in job.active_agents:
            logger.warning(
                "result_from_inactive_agent",
                task_id=result.task_id,
                agent=result.agent,
                active_agents=list(job.active_agents),
            )
            return

        if result.status not in {Status.SUCCESS, Status.ERROR, Status.TIMEOUT}:
            logger.warning(
                "result_with_invalid_status",
                task_id=result.task_id,
                agent=result.agent,
                status=result.status,
            )
            return

        task_reports = self._reports.setdefault(result.task_id, {})
        task_reports[result.agent] = result.model_dump(mode="json")
        logger.info(
            "result_added",
            task_id=result.task_id,
            agent=result.agent,
            status=result.status,
            duration_ms=result.duration_ms,
        )

    def get_consensus(self, task_id: str) -> TruthConsensus | None:
        """Build TruthConsensus from collected reports if task is complete.

        Returns:
            TruthConsensus with final score, verdict, and agent reports if complete.
            None if task does not exist, is not complete, or has no reports.
        """
        if task_id in self._consensus_cache:
            return self._consensus_cache[task_id]

        job = self._jobs.get(task_id)
        if not job:
            logger.debug("get_consensus_task_not_found", task_id=task_id)
            return None

        if not self.is_task_complete(task_id):
            logger.debug("get_consensus_task_not_complete", task_id=task_id)
            return None

        reports = self._reports.get(task_id, {})
        if not reports:
            logger.warning("get_consensus_no_reports", task_id=task_id)
            return None

        final_score = compute_truth_score(job.media_type, reports)

        # Check for multiple agent failures (per AGENTS §8)
        failure_count = sum(
            1
            for report in reports.values()
            if report.get("status") in {Status.ERROR.value, Status.TIMEOUT.value}
        )

        # Degraded mode: 2+ agents failed/timed out OR heuristics agent not active (per AGENTS §8)
        degraded_mode = failure_count >= 2 or "heuristics" not in job.active_agents

        verdict = map_score_to_verdict(final_score, reports)

        now = datetime.now(tz=UTC)
        processing_duration_ms = int((now - job.timestamp_utc).total_seconds() * 1000)

        consensus = TruthConsensus(
            task_id=task_id,
            media_hash=job.sha256_hash,
            media_type=job.media_type,
            processed_at_utc=now,
            processing_duration_ms=max(processing_duration_ms, 0),
            final_truth_score=final_score,
            verdict=verdict,
            degraded_mode=degraded_mode,
            agent_reports=reports,
            ledger_receipt=None,  # Will be populated by commit_to_ledger activity
        )

        self._consensus_cache[task_id] = consensus

        logger.info(
            "consensus_built",
            task_id=task_id,
            score=final_score,
            verdict=verdict,
            report_count=len(reports),
            failure_count=failure_count,
            degraded_mode=degraded_mode,
            processing_duration_ms=processing_duration_ms,
        )

        return consensus

    def update_ledger_receipt(self, task_id: str, receipt: Any) -> None:
        """Update the ledger receipt for a consensus record.

        This is usually called by a post-processing activity.
        """
        if task_id in self._consensus_cache:
            self._consensus_cache[task_id].ledger_receipt = receipt
            logger.info("ledger_receipt_updated", task_id=task_id)
        else:
            logger.warning("ledger_receipt_update_failed_task_not_in_cache", task_id=task_id)

    def aggregate_results(self, task_id: str, timeout_seconds: int) -> dict[str, dict[str, Any]]:
        """Collect and aggregate per-agent results for a task, respecting per-agent timeouts.
        Returns a dict keyed by agent name with each agent's result or a synthetic timeout payload."""
        import time as _time
        job = self._jobs.get(task_id)
        if job is None:
            logger.warning("aggregate_for_unknown_task", task_id=task_id)
            return {}

        reports: dict[str, dict[str, Any]] = {}
        active = list(job.active_agents)
        if not active:
            return reports

        # Compute remaining time after dispatch has already consumed some
        elapsed = (datetime.now(tz=UTC) - job.timestamp_utc).total_seconds()
        remaining = max(0.0, timeout_seconds - elapsed)

        # Per-agent deadline tracking
        deadlines: dict[str, float] = {
            agent: monotonic() + max(agent_timeout, 1)
            for agent, agent_timeout in (
                (a, self.workflow_timeout_for_media_type(job.media_type))
                for a in active
            )
        }

        pending = set(active)
        while pending and monotonic() < min(deadlines.values()):
            task_reports = self._reports.get(task_id)
            if task_reports:
                for agent in list(pending):
                    if agent in task_reports and agent not in reports:
                        reports[agent] = task_reports[agent]
                        pending.remove(agent)
            if pending:
                sleep_for = min(0.05, (min(deadlines.values()) - monotonic()) if deadlines else 0.1)
                if sleep_for > 0:
                    _time.sleep(sleep_for)

        # Emit synthetic timeouts for any agent that didn't respond
        for agent in pending:
            synthetic = self._synthetic_timeout_report(agent=agent, duration_ms=int(elapsed * 1000))
            synthetic["task_id"] = task_id
            reports[agent] = synthetic
            logger.warning("aggregate_agent_timeout", task_id=task_id, agent=agent)

        activity.logger.info(
            "aggregate_results",
            task_id=task_id,
            aggregated_count=len(reports),
            pending_count=len(pending),
        )
        return reports

    def get_reports(self, task_id: str) -> dict[str, dict[str, Any]]:
        reports = self._reports.get(task_id)
        if reports is None:
            return {}
        return dict(reports)

    def finalize_missing_timeouts(self, task_id: str) -> None:
        if task_id in self._jobs:
            self._finalize_with_missing_timeouts(task_id)

    @staticmethod
    def workflow_timeout_for_media_type(media_type: str) -> int:
        """Determines the workflow timeout based on the media type (per AGENTS.md §5.1)."""
        for prefix, timeout in WORKFLOW_TIMEOUTS.items():
            if media_type.startswith(prefix):
                return timeout
        return 60  # Default fallback
