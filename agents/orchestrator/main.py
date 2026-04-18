from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from typing import Any

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field
from temporalio.client import Client
from temporalio.worker import Worker

from agents.orchestrator.activities import collect_results, dispatch_job, set_orchestrator_service
from agents.orchestrator.service import OrchestratorService
from agents.orchestrator.workflow import VerificationWorkflow
from shared.constants import RESULT_TOPIC_PREFIX
from shared.env import get_settings
from shared.kafka_client import KafkaConsumerClient, KafkaProducerClient
from shared.observability import configure_logging, get_logger
from shared.schemas import ResultEnvelope

logger = get_logger("orchestrator")


class IngestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    media_type: str
    media_size_bytes: int = Field(ge=0)
    blob_uri: str
    source_url: str | None = None
    submitted_by: str | None = None


class IngestResponse(BaseModel):
    task_id: str


async def consume_results(consumer: KafkaConsumerClient, service: OrchestratorService) -> None:
    while True:
        try:
            record = await consumer.getone()
            result = ResultEnvelope.model_validate(record.value)
            service.add_result(result)
            await consumer.commit()
        except Exception as exc:
            logger.exception("orchestrator_result_consume_error", error=str(exc))


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.otp_log_level)

    producer = KafkaProducerClient(settings)
    result_consumer = KafkaConsumerClient(
        settings,
        topic_pattern=f"{RESULT_TOPIC_PREFIX}.*",
        group_id="cg-orchestrator-results",
    )

    await producer.start()
    await result_consumer.start()

    service = OrchestratorService(producer=producer)
    set_orchestrator_service(service)

    temporal_client = await Client.connect(
        settings.temporal_host,
        namespace=settings.temporal_namespace,
    )
    worker = Worker(
        temporal_client,
        task_queue=settings.temporal_task_queue,
        workflows=[VerificationWorkflow],
        activities=[dispatch_job, collect_results],
    )

    app.state.producer = producer
    app.state.service = service
    app.state.temporal_client = temporal_client
    app.state.temporal_task_queue = settings.temporal_task_queue
    app.state.temporal_worker_task = asyncio.create_task(worker.run())
    app.state.result_consumer = result_consumer
    app.state.result_consumer_task = asyncio.create_task(consume_results(result_consumer, service))

    logger.info("orchestrator_started")
    try:
        yield
    finally:
        app.state.temporal_worker_task.cancel()
        with suppress(asyncio.CancelledError):
            await app.state.temporal_worker_task

        app.state.result_consumer_task.cancel()
        with suppress(asyncio.CancelledError):
            await app.state.result_consumer_task

        set_orchestrator_service(None)
        await result_consumer.stop()
        await producer.stop()
        logger.info("orchestrator_stopped")


app = FastAPI(title="OTP Orchestrator", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest) -> IngestResponse:
    """Ingest media for verification.

    Args:
        request: IngestRequest with media_type, blob_uri, etc.

    Returns:
        IngestResponse with task_id for polling results

    Raises:
        HTTPException: If temporal workflow fails to start
    """
    service: OrchestratorService = app.state.service
    client: Client = app.state.temporal_client

    job = service.create_pending_job(
        media_type=request.media_type,
        media_size_bytes=request.media_size_bytes,
        blob_uri=request.blob_uri,
        source_url=request.source_url,
        submitted_by=request.submitted_by,
    )

    timeout_seconds = service.workflow_timeout_for_media_type(request.media_type)

    try:
        # Temporal SDK stubs do not model this bound method overload correctly.
        await client.start_workflow(
            VerificationWorkflow.run,
            job.task_id,
            timeout_seconds,
            id=f"verify-{job.task_id}",
            task_queue=app.state.temporal_task_queue,
        )  # type: ignore[call-overload]
        logger.info(
            "workflow_started",
            task_id=job.task_id,
            media_type=request.media_type,
            timeout_seconds=timeout_seconds,
        )
    except Exception as exc:
        logger.exception(
            "temporal_start_failed_fallback_dispatch",
            error=str(exc),
            task_id=job.task_id,
            error_type=type(exc).__name__,
        )
        try:
            await service.dispatch_pending_job(job.task_id)
            logger.info("fallback_dispatch_success", task_id=job.task_id)
        except Exception as fallback_exc:
            logger.exception(
                "fallback_dispatch_failed",
                task_id=job.task_id,
                error=str(fallback_exc),
                error_type=type(fallback_exc).__name__,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start verification workflow and fallback dispatch",
            ) from fallback_exc

    return IngestResponse(task_id=job.task_id)


@app.post("/internal/results")
async def internal_results(result: ResultEnvelope) -> dict[str, str]:
    service: OrchestratorService = app.state.service
    service.add_result(result)
    return {"status": "accepted"}


@app.get("/results/{task_id}")
async def get_result(task_id: str) -> Response | dict[str, Any]:
    """Get verification results for a task.

    Returns:
        - 200 OK with TruthConsensus JSON if results are ready
        - 202 ACCEPTED if results are still being processed
        - 404 NOT FOUND if task_id doesn't exist
    """
    service: OrchestratorService = app.state.service
    if not service.has_task(task_id):
        logger.debug("result_query_not_found", task_id=task_id)
        raise HTTPException(status_code=404, detail="task not found")

    consensus = service.get_consensus(task_id)
    if consensus is None:
        logger.debug("result_query_still_processing", task_id=task_id)
        return Response(status_code=status.HTTP_202_ACCEPTED)

    logger.info("result_query_ready", task_id=task_id, verdict=consensus.verdict)
    return consensus.model_dump(mode="json")
