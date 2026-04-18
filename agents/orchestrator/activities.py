from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from time import monotonic
from typing import Any

from temporalio import activity

from agents.orchestrator.service import OrchestratorService

_service: OrchestratorService | None = None


def set_orchestrator_service(service: OrchestratorService | None) -> None:
    global _service
    _service = service


def _require_service() -> OrchestratorService:
    if _service is None:
        raise RuntimeError("orchestrator service is not configured for activities")
    return _service


@activity.defn
async def dispatch_job(task_id: str) -> str:
    service = _require_service()
    dispatched = await service.dispatch_pending_job(task_id)
    if not dispatched:
        raise RuntimeError(f"task not found for dispatch: {task_id}")
    activity.logger.info("dispatch_job", task_id=task_id)
    return task_id


@activity.defn
async def collect_results(task_id: str, timeout_seconds: int) -> dict[str, Any]:
    service = _require_service()
    deadline = monotonic() + max(timeout_seconds, 1)

    while monotonic() < deadline:
        if service.is_task_complete(task_id):
            break
        await asyncio.sleep(0.1)

    if not service.is_task_complete(task_id):
        service.finalize_missing_timeouts(task_id)

    reports = service.get_reports(task_id)
    activity.logger.info(
        "collect_results",
        task_id=task_id,
        timeout_seconds=timeout_seconds,
        report_count=len(reports),
    )
    return {
        "task_id": task_id,
        "collected_at": datetime.now(tz=UTC).isoformat(),
        "reports": reports,
    }
