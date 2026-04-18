from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any, cast

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.structs import ConsumerRecord

from shared.env import Settings

Serializer = Callable[[dict[str, Any]], bytes]
Deserializer = Callable[[bytes], dict[str, Any]]


def _default_serializer(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _default_deserializer(raw: bytes) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(raw.decode("utf-8")))


class KafkaProducerClient:
    def __init__(self, settings: Settings, serializer: Serializer = _default_serializer) -> None:
        self._serializer = serializer
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            security_protocol=settings.kafka_security_protocol,
            acks="all",
            enable_idempotence=True,
            linger_ms=10,
            compression_type="zstd",
            value_serializer=self._serializer,
            retries=10,
            request_timeout_ms=30_000,
        )

    async def start(self) -> None:
        await self._producer.start()

    async def stop(self) -> None:
        await self._producer.stop()

    async def send(self, topic: str, payload: dict[str, Any], key: str) -> None:
        await self._producer.send_and_wait(topic, payload, key=key.encode("utf-8"))


class KafkaConsumerClient:
    def __init__(
        self,
        settings: Settings,
        *,
        topic_pattern: str,
        group_id: str,
        deserializer: Deserializer = _default_deserializer,
    ) -> None:
        self._consumer = AIOKafkaConsumer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            security_protocol=settings.kafka_security_protocol,
            group_id=group_id,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            value_deserializer=deserializer,
        )
        self._topic_pattern = topic_pattern

    async def start(self) -> None:
        await self._consumer.start()
        self._consumer.subscribe(pattern=self._topic_pattern)

    async def stop(self) -> None:
        await self._consumer.stop()

    async def getone(self) -> ConsumerRecord:
        return await self._consumer.getone()

    async def commit(self) -> None:
        await self._consumer.commit()
