from __future__ import annotations

from redis.asyncio import Redis


class DedupeStore:
    def __init__(
        self, redis_client: Redis, *, prefix: str = "otp:dedupe", ttl_seconds: int = 86_400
    ) -> None:
        self._redis = redis_client
        self._prefix = prefix
        self._ttl_seconds = ttl_seconds

    def _key(self, task_id: str, agent: str) -> str:
        return f"{self._prefix}:{agent}:{task_id}"

    async def seen(self, task_id: str, agent: str) -> bool:
        key = self._key(task_id, agent)
        return bool(await self._redis.exists(key))

    async def mark_seen(self, task_id: str, agent: str) -> None:
        key = self._key(task_id, agent)
        await self._redis.set(key, "1", ex=self._ttl_seconds)
