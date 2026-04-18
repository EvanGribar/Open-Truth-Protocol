from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from shared.dedupe import DedupeStore


@pytest.mark.asyncio
async def test_dedupe_store() -> None:
    mock_redis = AsyncMock()
    mock_redis.exists.return_value = 0
    store = DedupeStore(mock_redis)

    assert await store.seen("task1", "agent1") is False
    mock_redis.exists.assert_called_with("otp:dedupe:agent1:task1")

    await store.mark_seen("task1", "agent1")
    mock_redis.set.assert_called_with("otp:dedupe:agent1:task1", "1", ex=86400)

    mock_redis.exists.return_value = 1
    assert await store.seen("task1", "agent1") is True
