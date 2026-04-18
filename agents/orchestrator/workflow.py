from __future__ import annotations

from datetime import timedelta
from typing import Any, cast

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from agents.orchestrator.activities import collect_results, dispatch_job


@workflow.defn
class VerificationWorkflow:
    @workflow.run
    async def run(
        self,
        task_id: str,
        hard_timeout_seconds: int,
    ) -> dict[str, Any]:
        await workflow.execute_activity(
            dispatch_job,
            args=[task_id],
            start_to_close_timeout=timedelta(seconds=10),
        )

        result = await workflow.execute_activity(
            collect_results,
            args=[task_id, hard_timeout_seconds],
            start_to_close_timeout=timedelta(seconds=hard_timeout_seconds),
        )
        return cast(dict[str, Any], result)
