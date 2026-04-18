from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, cast

import pytest

from agents.orchestrator.service import OrchestratorService
from shared.schemas import ResultEnvelope, Status


class _FakeProducer:
    def __init__(self) -> None:
        self.messages: list[tuple[str, dict[str, object], str]] = []

    async def send(self, topic: str, payload: dict[str, object], key: str) -> None:
        self.messages.append((topic, payload, key))


def _make_service() -> OrchestratorService:
    return OrchestratorService(producer=cast(Any, _FakeProducer()))


def _producer_from_service(service: OrchestratorService) -> _FakeProducer:
    return cast(_FakeProducer, service._producer)


@pytest.mark.asyncio
async def test_get_consensus_returns_none_until_job_complete() -> None:
    service = _make_service()
    job = await service.create_job(
        media_type="image/jpeg",
        media_size_bytes=1024,
        blob_uri="s3://otp-intake/item.jpg",
        source_url="https://example.com",
        submitted_by="test",
    )

    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="heuristics",
            status=Status.SUCCESS,
            duration_ms=100,
            payload={"heuristics_score": 0.8, "confidence": 0.9},
        )
    )

    assert service.get_consensus(job.task_id) is None


@pytest.mark.asyncio
async def test_pending_job_is_not_published_until_dispatched() -> None:
    service = _make_service()
    producer = _producer_from_service(service)

    job = service.create_pending_job(
        media_type="image/jpeg",
        media_size_bytes=1024,
        blob_uri="s3://otp-intake/pending.jpg",
        source_url="https://example.com",
        submitted_by="test",
    )

    assert producer.messages == []

    dispatched = await service.dispatch_pending_job(job.task_id)

    assert dispatched is True
    assert len(producer.messages) == 1
    assert producer.messages[0][2] == job.task_id


@pytest.mark.asyncio
async def test_dispatch_pending_job_returns_false_for_unknown_task() -> None:
    service = _make_service()

    dispatched = await service.dispatch_pending_job("missing-task")

    assert dispatched is False


@pytest.mark.asyncio
async def test_get_consensus_synthesizes_timeouts_after_workflow_deadline() -> None:
    service = _make_service()
    job = await service.create_job(
        media_type="text/plain",
        media_size_bytes=120,
        blob_uri="s3://otp-intake/item.txt",
        source_url="https://example.com",
        submitted_by="test",
    )

    # Simulate workflow deadline pass for text (30s).
    stale_job = job.model_copy(
        update={"timestamp_utc": datetime.now(tz=UTC) - timedelta(seconds=40)}
    )
    service._jobs[job.task_id] = stale_job

    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="heuristics",
            status=Status.SUCCESS,
            duration_ms=120,
            payload={"heuristics_score": 0.2, "confidence": 0.8},
        )
    )

    consensus = service.get_consensus(job.task_id)
    assert consensus is not None
    assert "provenance" in consensus.agent_reports
    assert "web_consensus" in consensus.agent_reports
    assert consensus.agent_reports["provenance"]["status"] == Status.TIMEOUT.value
    assert consensus.agent_reports["web_consensus"]["status"] == Status.TIMEOUT.value
    assert consensus.verdict == "INCONCLUSIVE"


@pytest.mark.asyncio
async def test_add_result_ignores_inactive_agent() -> None:
    service = _make_service()
    job = await service.create_job(
        media_type="text/plain",
        media_size_bytes=120,
        blob_uri="s3://otp-intake/item.txt",
        source_url="https://example.com",
        submitted_by="test",
    )

    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="ledger",
            status=Status.SUCCESS,
            duration_ms=1,
            payload={"ledger_score": 1.0},
        )
    )

    assert service._reports[job.task_id] == {}


@pytest.mark.asyncio
async def test_get_consensus_sets_degraded_mode_when_heuristics_inactive() -> None:
    service = _make_service()
    job = await service.create_job(
        media_type="text/plain",
        media_size_bytes=120,
        blob_uri="s3://otp-intake/item.txt",
        source_url="https://example.com",
        submitted_by="test",
    )

    # Simulate degraded mode where heuristics is not in active fan-out.
    service._jobs[job.task_id] = job.model_copy(
        update={"active_agents": ["provenance", "web_consensus"]}
    )

    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="provenance",
            status=Status.SUCCESS,
            duration_ms=10,
            payload={"provenance_score": 0.6},
        )
    )
    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="web_consensus",
            status=Status.SUCCESS,
            duration_ms=10,
            payload={"web_consensus_score": 0.7},
        )
    )

    consensus = service.get_consensus(job.task_id)

    assert consensus is not None
    assert consensus.degraded_mode is True
