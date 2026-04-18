from __future__ import annotations

import time
from datetime import UTC, datetime

from agents.heuristics.analyzer import analyze
from shared.observability import errors_total, get_logger, job_duration_seconds, jobs_total
from shared.routing import should_process
from shared.schemas import ErrorPayload, JobPayload, ResultEnvelope, Status

logger = get_logger("heuristics")


def process_job(job_dict: dict[str, object]) -> ResultEnvelope:
    started_at = time.perf_counter()
    task_id = str(job_dict["task_id"])

    try:
        job = JobPayload.model_validate(job_dict)
        if not should_process("heuristics", job.active_agents):
            duration_ms = int((time.perf_counter() - started_at) * 1000)
            jobs_total.labels(agent="heuristics", status="skipped").inc()
            job_duration_seconds.labels(agent="heuristics").observe(duration_ms / 1000)
            return ResultEnvelope(
                task_id=task_id,
                agent="heuristics",
                status=Status.SUCCESS,
                duration_ms=duration_ms,
                payload={
                    "heuristics_score": 0.5,
                    "confidence": 1.0,
                    "skipped": True,
                    "processed_at_utc": datetime.now(tz=UTC).isoformat(),
                },
                error=None,
            )

        payload = analyze(job.media_type)
        duration_ms = int((time.perf_counter() - started_at) * 1000)
        jobs_total.labels(agent="heuristics", status="success").inc()
        job_duration_seconds.labels(agent="heuristics").observe(duration_ms / 1000)

        return ResultEnvelope(
            task_id=job.task_id,
            agent="heuristics",
            status=Status.SUCCESS,
            duration_ms=duration_ms,
            payload=payload,
            error=None,
        )
    except Exception as exc:
        duration_ms = int((time.perf_counter() - started_at) * 1000)
        errors_total.labels(agent="heuristics", code="HEURISTICS_PROCESSING_ERROR").inc()
        jobs_total.labels(agent="heuristics", status="error").inc()
        logger.error("heuristics_processing_failed", task_id=task_id, error=str(exc))
        return ResultEnvelope(
            task_id=task_id,
            agent="heuristics",
            status=Status.ERROR,
            duration_ms=duration_ms,
            payload=None,
            error=ErrorPayload(
                code="HEURISTICS_PROCESSING_ERROR",
                message=str(exc),
                retryable=True,
            ),
        )
