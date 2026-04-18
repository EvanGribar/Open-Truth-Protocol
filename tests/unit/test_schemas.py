from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from shared.schemas import JobPayload


def test_job_payload_validates() -> None:
    payload = JobPayload.model_validate(
        {
            "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "timestamp_utc": datetime.now(tz=UTC).isoformat(),
            "media_type": "image/jpeg",
            "media_size_bytes": 123,
            "sha256_hash": "abc",
            "blob_uri": "s3://bucket/key",
            "active_agents": ["provenance", "heuristics"],
            "client_metadata": {"source_url": "https://example.com", "submitted_by": "test"},
        }
    )
    assert payload.media_type == "image/jpeg"


def test_job_payload_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        JobPayload.model_validate(
            {
                "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "timestamp_utc": datetime.now(tz=UTC).isoformat(),
                "media_type": "image/jpeg",
                "media_size_bytes": 123,
                "sha256_hash": "abc",
                "blob_uri": "s3://bucket/key",
                "active_agents": ["provenance", "heuristics"],
                "client_metadata": {"source_url": "https://example.com", "submitted_by": "test"},
                "unexpected": "field",
            }
        )
