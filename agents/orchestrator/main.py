from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from agents.orchestrator.service import OrchestratorService
from shared.env import get_settings
from shared.kafka_client import KafkaProducerClient
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


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.otp_log_level)

    producer = KafkaProducerClient(settings)
    await producer.start()

    app.state.producer = producer
    app.state.service = OrchestratorService(producer=producer)

    logger.info("orchestrator_started")
    try:
        yield
    finally:
        await producer.stop()
        logger.info("orchestrator_stopped")


app = FastAPI(title="OTP Orchestrator", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest) -> IngestResponse:
    service: OrchestratorService = app.state.service
    job = await service.create_job(
        media_type=request.media_type,
        media_size_bytes=request.media_size_bytes,
        blob_uri=request.blob_uri,
        source_url=request.source_url,
        submitted_by=request.submitted_by,
    )
    return IngestResponse(task_id=job.task_id)


@app.post("/internal/results")
async def internal_results(result: ResultEnvelope) -> dict[str, str]:
    service: OrchestratorService = app.state.service
    service.add_result(result)
    return {"status": "accepted"}


@app.get("/results/{task_id}")
async def get_result(task_id: str) -> dict[str, Any]:
    service: OrchestratorService = app.state.service
    consensus = service.get_consensus(task_id)
    if consensus is None:
        raise HTTPException(status_code=404, detail="task not found or incomplete")
    return consensus.model_dump(mode="json")
