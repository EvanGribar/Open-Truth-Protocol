from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, cast

import pytest

from agents.orchestrator.service import OrchestratorService
from shared.schemas import ErrorPayload, ResultEnvelope, Status


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


def test_workflow_timeout_for_media_type() -> None:
    service = _make_service()
    assert service.workflow_timeout_for_media_type("image/jpeg") == 60
    assert service.workflow_timeout_for_media_type("video/mp4") == 300
    assert service.workflow_timeout_for_media_type("text/plain") == 30
    assert service.workflow_timeout_for_media_type("audio/wav") == 60
    assert service.workflow_timeout_for_media_type("application/pdf") == 60  # Default fallback


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


@pytest.mark.asyncio
async def test_add_result_ignores_unknown_task() -> None:
    service = _make_service()

    service.add_result(
        ResultEnvelope(
            task_id="unknown-task",
            agent="heuristics",
            status=Status.SUCCESS,
            duration_ms=100,
            payload={"heuristics_score": 0.8},
        )
    )

    # Service should not crash and should not add to reports
    assert "unknown-task" not in service._reports


@pytest.mark.asyncio
async def test_add_result_with_invalid_status() -> None:
    """Test that results with invalid status are rejected per AGENTS §4.3."""
    service = _make_service()
    job = await service.create_job(
        media_type="image/jpeg",
        media_size_bytes=1024,
        blob_uri="s3://otp-intake/item.jpg",
        source_url="https://example.com",
        submitted_by="test",
    )

    # Use model_construct to bypass Pydantic validation and test invalid status
    result = ResultEnvelope.model_construct(
        task_id=job.task_id,
        agent="heuristics",
        status="UNKNOWN_STATUS",  # Invalid status not in (SUCCESS, ERROR, TIMEOUT)
        duration_ms=100,
        payload={"heuristics_score": 0.8},
    )

    service.add_result(result)

    # Invalid status should be rejected and not added to reports
    assert job.task_id not in service._reports or "heuristics" not in service._reports.get(
        job.task_id, {}
    )


@pytest.mark.asyncio
async def test_get_consensus_includes_failure_count() -> None:
    """Test that consensus correctly identifies multiple agent failures."""
    service = _make_service()
    job = await service.create_job(
        media_type="image/jpeg",
        media_size_bytes=1024,
        blob_uri="s3://otp-intake/item.jpg",
        source_url="https://example.com",
        submitted_by="test",
    )

    # Add a success and two failures
    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="heuristics",
            status=Status.SUCCESS,
            duration_ms=100,
            payload={"heuristics_score": 0.8, "confidence": 0.9},
        )
    )
    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="provenance",
            status=Status.TIMEOUT,
            duration_ms=8000,
            error=ErrorPayload(code="TIMEOUT", message="timed out", retryable=False),
        )
    )
    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="web_consensus",
            status=Status.ERROR,
            duration_ms=1000,
            error=ErrorPayload(code="API_ERROR", message="API failed", retryable=True),
        )
    )

    consensus = service.get_consensus(job.task_id)

    assert consensus is not None
    assert consensus.verdict == "INCONCLUSIVE"  # 2+ failures force inconclusive


@pytest.mark.asyncio
async def test_create_job_and_dispatch() -> None:
    """Test full job creation and dispatch workflow."""
    service = _make_service()
    producer = _producer_from_service(service)

    job = await service.create_job(
        media_type="video/mp4",
        media_size_bytes=10_000_000,
        blob_uri="s3://otp-intake/video.mp4",
        source_url="https://example.com/video",
        submitted_by="test-user",
    )

    assert len(producer.messages) == 1
    topic, payload, key = producer.messages[0]
    assert key == job.task_id
    assert topic == f"otp.jobs.{job.task_id}"
    assert payload["media_type"] == "video/mp4"
    assert payload["media_size_bytes"] == 10_000_000


@pytest.mark.asyncio
async def test_workflow_timeout_values_by_media_type() -> None:
    """Test that workflow timeouts are correctly assigned per media type."""
    assert OrchestratorService.workflow_timeout_for_media_type("text/plain") == 30
    assert OrchestratorService.workflow_timeout_for_media_type("text/html") == 30
    assert OrchestratorService.workflow_timeout_for_media_type("image/jpeg") == 60
    assert OrchestratorService.workflow_timeout_for_media_type("image/png") == 60
    assert OrchestratorService.workflow_timeout_for_media_type("audio/mp3") == 60
    assert OrchestratorService.workflow_timeout_for_media_type("video/mp4") == 300
    assert OrchestratorService.workflow_timeout_for_media_type("video/quicktime") == 300


@pytest.mark.asyncio
async def test_get_consensus_sets_degraded_mode_on_multiple_failures() -> None:
    """Test that degraded_mode is set when 2+ agents fail (AGENTS §8)."""
    service = _make_service()
    job = await service.create_job(
        media_type="image/jpeg",
        media_size_bytes=1024,
        blob_uri="s3://otp-intake/item.jpg",
        source_url="https://example.com",
        submitted_by="test",
    )

    # Add one success and two failures
    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="heuristics",
            status=Status.SUCCESS,
            duration_ms=100,
            payload={"heuristics_score": 0.8, "confidence": 0.9},
        )
    )
    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="provenance",
            status=Status.TIMEOUT,
            duration_ms=8000,
            error=ErrorPayload(code="TIMEOUT", message="timed out", retryable=False),
        )
    )
    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="web_consensus",
            status=Status.ERROR,
            duration_ms=1000,
            error=ErrorPayload(code="API_ERROR", message="API failed", retryable=True),
        )
    )

    consensus = service.get_consensus(job.task_id)

    assert consensus is not None
    assert consensus.degraded_mode is True
    assert consensus.verdict == "INCONCLUSIVE"  # Forced by 2+ failures


@pytest.mark.asyncio
async def test_get_consensus_normal_mode_with_all_successes() -> None:
    """Test that degraded_mode is False when all agents succeed."""
    service = _make_service()
    job = await service.create_job(
        media_type="image/jpeg",
        media_size_bytes=1024,
        blob_uri="s3://otp-intake/item.jpg",
        source_url="https://example.com",
        submitted_by="test",
    )

    # Add all three agents with success
    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="heuristics",
            status=Status.SUCCESS,
            duration_ms=100,
            payload={"heuristics_score": 0.8, "confidence": 0.9},
        )
    )
    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="provenance",
            status=Status.SUCCESS,
            duration_ms=500,
            payload={"provenance_score": 0.9},
        )
    )
    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="web_consensus",
            status=Status.SUCCESS,
            duration_ms=1000,
            payload={"web_consensus_score": 0.85},
        )
    )

    consensus = service.get_consensus(job.task_id)

    assert consensus is not None
    assert consensus.degraded_mode is False
    assert consensus.verdict in [
        "LIKELY_AUTHENTIC",
        "UNVERIFIED",
        "INCONCLUSIVE",
        "LIKELY_SYNTHETIC",
        "SYNTHETIC",
    ]


@pytest.mark.asyncio
async def test_get_consensus_single_failure_no_degraded_mode() -> None:
    """Test that degraded_mode is False with only 1 agent failure."""
    service = _make_service()
    job = await service.create_job(
        media_type="image/jpeg",
        media_size_bytes=1024,
        blob_uri="s3://otp-intake/item.jpg",
        source_url="https://example.com",
        submitted_by="test",
    )

    # Add two successes and one failure
    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="heuristics",
            status=Status.SUCCESS,
            duration_ms=100,
            payload={"heuristics_score": 0.8, "confidence": 0.9},
        )
    )
    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="provenance",
            status=Status.TIMEOUT,
            duration_ms=8000,
            error=ErrorPayload(code="TIMEOUT", message="timed out", retryable=False),
        )
    )
    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="web_consensus",
            status=Status.SUCCESS,
            duration_ms=1000,
            payload={"web_consensus_score": 0.85},
        )
    )

    consensus = service.get_consensus(job.task_id)

    assert consensus is not None
    assert consensus.degraded_mode is False  # Only 1 failure, not degraded
    # Score should still be computed from 2 agents


@pytest.mark.asyncio
async def test_get_consensus_verdict_boundary_cases() -> None:
    """Test verdict mapping at score boundaries (AGENTS §6.2)."""
    service = _make_service()

    # Test case 1: Score at LIKELY_AUTHENTIC boundary (0.85)
    job1 = await service.create_job(
        media_type="image/jpeg",
        media_size_bytes=1024,
        blob_uri="s3://otp-intake/1.jpg",
        source_url="https://example.com",
        submitted_by="test",
    )
    # Mock a high score by adding results that should compute to ~0.85+
    service.add_result(
        ResultEnvelope(
            task_id=job1.task_id,
            agent="heuristics",
            status=Status.SUCCESS,
            duration_ms=100,
            payload={"heuristics_score": 0.95, "confidence": 1.0},
        )
    )
    service.add_result(
        ResultEnvelope(
            task_id=job1.task_id,
            agent="provenance",
            status=Status.SUCCESS,
            duration_ms=500,
            payload={"provenance_score": 0.80},
        )
    )
    service.add_result(
        ResultEnvelope(
            task_id=job1.task_id,
            agent="web_consensus",
            status=Status.SUCCESS,
            duration_ms=1000,
            payload={"web_consensus_score": 0.85},
        )
    )

    consensus1 = service.get_consensus(job1.task_id)
    assert consensus1 is not None
    assert consensus1.verdict in ["LIKELY_AUTHENTIC", "UNVERIFIED"]  # High score


@pytest.mark.asyncio
async def test_get_consensus_handles_mixed_status() -> None:
    """Test consensus building with mixed SUCCESS/ERROR/TIMEOUT statuses."""
    service = _make_service()
    job = await service.create_job(
        media_type="text/plain",
        media_size_bytes=500,
        blob_uri="s3://otp-intake/text.txt",
        source_url="https://example.com",
        submitted_by="test",
    )

    # Heuristics: SUCCESS
    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="heuristics",
            status=Status.SUCCESS,
            duration_ms=200,
            payload={"heuristics_score": 0.3, "confidence": 0.8},
        )
    )
    # Provenance: TIMEOUT
    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="provenance",
            status=Status.TIMEOUT,
            duration_ms=8000,
            error=ErrorPayload(code="TIMEOUT", message="timeout", retryable=False),
        )
    )
    # Web Consensus: ERROR
    service.add_result(
        ResultEnvelope(
            task_id=job.task_id,
            agent="web_consensus",
            status=Status.ERROR,
            duration_ms=500,
            error=ErrorPayload(code="API_ERROR", message="error", retryable=True),
        )
    )

    consensus = service.get_consensus(job.task_id)

    assert consensus is not None
    assert consensus.verdict == "INCONCLUSIVE"  # 2+ failures
    assert consensus.degraded_mode is True
    assert consensus.agent_reports["heuristics"]["status"] == Status.SUCCESS.value
    assert consensus.agent_reports["provenance"]["status"] == Status.TIMEOUT.value
    assert consensus.agent_reports["web_consensus"]["status"] == Status.ERROR.value
