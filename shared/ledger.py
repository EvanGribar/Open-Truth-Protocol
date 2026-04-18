from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Protocol

from shared.observability import get_logger
from shared.schemas import LedgerReceipt, TruthConsensus

logger = get_logger("ledger")


class LedgerService(Protocol):
    """Interface for committing truth records to a ledger."""

    async def commit_consensus(self, consensus: TruthConsensus) -> LedgerReceipt | None:
        """Commit a consensus record to the ledger and IPFS.

        Args:
            consensus: The finalized truth consensus to commit.

        Returns:
            LedgerReceipt if successful, None otherwise.
        """
        ...


class NoOpLedgerService:
    """A no-op implementation of LedgerService for Phase 1.

    In Phase 1, we don't actually commit to a blockchain, but we provide
    the interface and a mock receipt for integration testing.
    """

    async def commit_consensus(self, consensus: TruthConsensus) -> LedgerReceipt | None:
        # Simulate some latency
        await asyncio.sleep(0.1)

        logger.info(
            "ledger_commitment_simulated_noop",
            task_id=consensus.task_id,
            final_truth_score=consensus.final_truth_score,
            ipfs_mock="ipfs://QmPending",
        )

        return LedgerReceipt(
            network="sepolia-mock",
            transaction_hash=f"0x{consensus.task_id.replace('-', '')}",
            block_number=1234567,
            ipfs_cid="QmPending",
            committed_at_utc=datetime.now(tz=UTC),
        )
