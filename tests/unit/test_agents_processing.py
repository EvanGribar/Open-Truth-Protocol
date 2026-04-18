from datetime import UTC, datetime

from agents.heuristics.main import process_job as process_heuristics_job
from agents.provenance.main import process_job as process_provenance_job


def _base_job() -> dict[str, object]:
    return {
        "task_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "timestamp_utc": datetime.now(tz=UTC).isoformat(),
        "media_type": "image/jpeg",
        "media_size_bytes": 1024,
        "sha256_hash": "abc123",
        "blob_uri": "s3://otp-intake/sample.jpg",
        "active_agents": ["provenance", "heuristics"],
        "client_metadata": {"source_url": "https://example.com", "submitted_by": "test"},
    }


def test_heuristics_process_job_success() -> None:
    result = process_heuristics_job(_base_job())
    assert result.agent == "heuristics"
    assert result.status.value == "success"
    assert result.payload is not None


def test_provenance_process_job_success() -> None:
    result = process_provenance_job(_base_job())
    assert result.agent == "provenance"
    assert result.status.value == "success"
    assert result.payload is not None
