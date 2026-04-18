from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from shared.constants import OTP_VERSION


class Status(StrEnum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


class ErrorPayload(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    code: str
    message: str
    retryable: bool


class ClientMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    source_url: str | None = None
    submitted_by: str | None = None


class JobPayload(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    task_id: str
    timestamp_utc: datetime
    media_type: str
    media_size_bytes: int = Field(ge=0)
    sha256_hash: str
    blob_uri: str
    active_agents: list[str]
    client_metadata: ClientMetadata = Field(default_factory=ClientMetadata)

    @field_validator("timestamp_utc", mode="before")
    @classmethod
    def parse_timestamp(cls, value: datetime | str) -> datetime:
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    @field_validator("timestamp_utc")
    @classmethod
    def ensure_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


class ResultEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    task_id: str
    agent: str
    status: Status
    duration_ms: int = Field(ge=0)
    payload: dict[str, Any] | None = None
    error: ErrorPayload | None = None


class AgentReport(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True)

    status: Status
    duration_ms: int = Field(ge=0)


class LedgerReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    network: str
    transaction_hash: str
    block_number: int
    ipfs_cid: str
    committed_at_utc: datetime


class TruthConsensus(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    otp_version: str = OTP_VERSION
    task_id: str
    media_hash: str
    media_type: str
    processed_at_utc: datetime
    processing_duration_ms: int = Field(ge=0)
    final_truth_score: float = Field(ge=0.0, le=1.0)
    verdict: str
    degraded_mode: bool = False
    agent_reports: dict[str, dict[str, Any]]
    ledger_receipt: LedgerReceipt | None = None
