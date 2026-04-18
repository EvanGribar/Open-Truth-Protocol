from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from time import monotonic
from typing import Any

from temporalio import activity

from agents.orchestrator.service import OrchestratorService
from shared.ledger import LedgerService

_service: OrchestratorService | None = None
_ledger_service: LedgerService | None = None


def set_orchestrator_service(service: OrchestratorService | None) -> None:
    global _service
    _service = service


def set_ledger_service(service: LedgerService | None) -> None:
    global _ledger_service
    _ledger_service = service


def _require_service() -> OrchestratorService:
    if _service is None:
        raise RuntimeError("orchestrator service is not configured for activities")
    return _service


def _require_ledger_service() -> LedgerService:
    if _ledger_service is None:
        raise RuntimeError("ledger service is not configured for activities")
    return _ledger_service


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


@activity.defn
async def commit_to_ledger(task_id: str) -> dict[str, Any] | None:
    service = _require_service()
    ledger = _require_ledger_service()

    consensus = service.get_consensus(task_id)
    if consensus is None:
        activity.logger.error("commit_to_ledger_failed_no_consensus", task_id=task_id)
        return None

    receipt = await ledger.commit_consensus(consensus)
    if receipt:
        service.update_ledger_receipt(task_id, receipt)
        activity.logger.info(
            "commit_to_ledger_success", task_id=task_id, tx_hash=receipt.transaction_hash
        )
        return receipt.model_dump(mode="json")

    return None
