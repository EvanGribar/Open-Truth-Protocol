"""Entry point for the web consensus agent."""

from __future__ import annotations

import time

from agents.web_consensus.analyzer import analyze
from shared.observability import errors_total, get_logger, job_duration_seconds, jobs_total
from shared.routing import should_process
from shared.schemas import ErrorPayload, JobPayload, ResultEnvelope, Status

logger = get_logger("web_consensus")


def process_job(job_dict: dict[str, object]) -> ResultEnvelope:
    """Validate a job payload and return a web-consensus result envelope."""

    started_at = time.perf_counter()
    task_id = str(job_dict["task_id"])

    try:
        job = JobPayload.model_validate(job_dict)
        if not should_process("web_consensus", job.active_agents):
            duration_ms = int((time.perf_counter() - started_at) * 1000)
            jobs_total.labels(agent="web_consensus", status="skipped").inc()
            job_duration_seconds.labels(agent="web_consensus").observe(duration_ms / 1000)
            return ResultEnvelope(
                task_id=task_id,
                agent="web_consensus",
                status=Status.SUCCESS,
                duration_ms=duration_ms,
                payload={
                    "web_consensus_score": 0.5,
                    "confidence": 1.0,
                    "skipped": True,
                },
                error=None,
            )

        payload = analyze(job)
        duration_ms = int((time.perf_counter() - started_at) * 1000)
        jobs_total.labels(agent="web_consensus", status="success").inc()
        job_duration_seconds.labels(agent="web_consensus").observe(duration_ms / 1000)

        return ResultEnvelope(
            task_id=job.task_id,
            agent="web_consensus",
            status=Status.SUCCESS,
            duration_ms=duration_ms,
            payload=payload,
            error=None,
        )
    except Exception as exc:
        duration_ms = int((time.perf_counter() - started_at) * 1000)
        errors_total.labels(agent="web_consensus", code="WEB_CONSENSUS_PROCESSING_ERROR").inc()
        jobs_total.labels(agent="web_consensus", status="error").inc()
        logger.exception("web_consensus_processing_failed", task_id=task_id, error=str(exc))
        return ResultEnvelope(
            task_id=task_id,
            agent="web_consensus",
            status=Status.ERROR,
            duration_ms=duration_ms,
            payload=None,
            error=ErrorPayload(
                code="WEB_CONSENSUS_PROCESSING_ERROR",
                message=str(exc),
                retryable=True,
            ),
        )
