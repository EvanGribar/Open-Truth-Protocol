from __future__ import annotations

from datetime import UTC, datetime

import pytest

from shared.ledger import NoOpLedgerService
from shared.schemas import TruthConsensus


@pytest.mark.asyncio
async def test_noop_ledger_service() -> None:
    service = NoOpLedgerService()
    consensus = TruthConsensus(
        task_id="test-task",
        media_hash="hash",
        media_type="image/jpeg",
        processed_at_utc=datetime.now(tz=UTC),
        processing_duration_ms=100,
        final_truth_score=0.9,
        verdict="LIKELY_AUTHENTIC",
        agent_reports={},
    )
    receipt = await service.commit_consensus(consensus)
    assert receipt is not None
    assert receipt.network == "sepolia-mock"
    assert receipt.ipfs_cid == "QmPending"
