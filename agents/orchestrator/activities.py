from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime

from temporalio import activity


@activity.defn
def dispatch_job(task_id: str, active_agents: Sequence[str]) -> str:
    activity.logger.info("dispatch_job", task_id=task_id, active_agents=list(active_agents))
    return task_id


@activity.defn
def collect_results(task_id: str, timeout_seconds: int) -> dict[str, object]:
    activity.logger.info("collect_results", task_id=task_id, timeout_seconds=timeout_seconds)
    return {
        "task_id": task_id,
        "collected_at": datetime.now(tz=UTC).isoformat(),
        "reports": {},
    }
