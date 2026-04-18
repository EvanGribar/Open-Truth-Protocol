from __future__ import annotations

import pytest

from agents.orchestrator.activities import (
    collect_results,
    dispatch_job,
    set_orchestrator_service,
)


class _FakeActivityService:
    def __init__(self) -> None:
        self.dispatched: list[str] = []
        self.complete_checks = 0

    async def dispatch_pending_job(self, task_id: str) -> bool:
        self.dispatched.append(task_id)
        return task_id != "missing"

    def is_task_complete(self, task_id: str) -> bool:
        self.complete_checks += 1
        return self.complete_checks >= 2 and task_id == "task-1"

    def finalize_missing_timeouts(self, task_id: str) -> None:
        self.dispatched.append(f"finalized:{task_id}")

    def get_reports(self, task_id: str) -> dict[str, dict[str, object]]:
        return {
            "heuristics": {
                "task_id": task_id,
                "status": "success",
                "duration_ms": 10,
                "payload": {"heuristics_score": 0.7},
                "error": None,
            }
        }


@pytest.mark.asyncio
async def test_dispatch_job_raises_when_task_missing() -> None:
    fake_service = _FakeActivityService()
    set_orchestrator_service(fake_service)  # type: ignore[arg-type]

    with pytest.raises(RuntimeError):
        await dispatch_job("missing")

    set_orchestrator_service(None)


@pytest.mark.asyncio
async def test_collect_results_returns_reports_when_task_completes() -> None:
    fake_service = _FakeActivityService()
    set_orchestrator_service(fake_service)  # type: ignore[arg-type]

    result = await collect_results("task-1", timeout_seconds=1)

    assert result["task_id"] == "task-1"
    assert "collected_at" in result
    reports = result["reports"]
    assert isinstance(reports, dict)
    assert reports["heuristics"]["status"] == "success"

    set_orchestrator_service(None)
