"""Entry point for the web consensus agent."""

from __future__ import annotations

import asyncio
import time
from typing import cast

from redis.asyncio import Redis

from agents.web_consensus.analyzer import analyze
from shared.constants import JOB_TOPIC_PREFIX, RESULT_TOPIC_PREFIX
from shared.dedupe import DedupeStore
from shared.env import get_settings
from shared.kafka_client import KafkaConsumerClient, KafkaProducerClient
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

        payload = analyze(job.media_type)
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


async def run_worker() -> None:
    settings = get_settings()
    producer = KafkaProducerClient(settings)
    consumer = KafkaConsumerClient(
        settings,
        topic_pattern=f"{JOB_TOPIC_PREFIX}.*",
        group_id="cg-web-consensus",
    )
    redis_client = Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    dedupe_store = DedupeStore(redis_client)

    await producer.start()
    await consumer.start()
    logger.info("web_consensus_worker_started")

    try:
        while True:
            try:
                record = await consumer.getone()
                job_dict = cast(dict[str, object], record.value)
                task_id = str(job_dict.get("task_id", ""))

                if not task_id:
                    logger.warning("web_consensus_invalid_job_missing_task_id")
                    errors_total.labels(agent="web_consensus", code="INVALID_JOB_PAYLOAD").inc()
                    await consumer.commit()
                    continue

                if await dedupe_store.seen(task_id, "web_consensus"):
                    jobs_total.labels(agent="web_consensus", status="duplicate").inc()
                    logger.info("web_consensus_duplicate_job_skipped", task_id=task_id)
                    await consumer.commit()
                    continue

                result = process_job(job_dict)
                await producer.send(
                    topic=f"{RESULT_TOPIC_PREFIX}.{result.task_id}",
                    payload=result.model_dump(mode="json"),
                    key=result.task_id,
                )
                await dedupe_store.mark_seen(result.task_id, "web_consensus")
                await consumer.commit()
            except Exception as exc:
                errors_total.labels(agent="web_consensus", code="WORKER_LOOP_ERROR").inc()
                logger.exception("web_consensus_worker_loop_error", error=str(exc))
    finally:
        await consumer.stop()
        await producer.stop()
        await redis_client.aclose()
        logger.info("web_consensus_worker_stopped")


if __name__ == "__main__":
    asyncio.run(run_worker())
