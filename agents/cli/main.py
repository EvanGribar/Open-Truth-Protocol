from __future__ import annotations

import asyncio
import mimetypes
import sys
from pathlib import Path

import httpx

from shared.constants import WORKFLOW_TIMEOUTS
from shared.env import get_settings
from shared.observability import get_logger

logger = get_logger("cli")


def _resolve_local_file(file_path: str) -> tuple[str, int, str]:
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    media_type, _ = mimetypes.guess_type(path)
    if not media_type:
        media_type = "application/octet-stream"

    return path.name, path.stat().st_size, media_type


async def verify_file(file_name: str, file_size_bytes: int, media_type: str, api_url: str) -> None:

    # In a real CLI, we would upload to S3 first.
    # For Phase 1 MVP, we simulate or assume the file is already in S3 or provided via local path
    # if the API supports it. But AGENTS.md says "Agents... pull from S3".

    # Let's assume for now the user has uploaded it or we use a mock blob_uri
    # Actually, the Orchestrator.create_job handles normalization to S3.
    # So the CLI should just send the media to the API Gateway.

    # Wait, Orchestrator main.py has an /ingest endpoint.
    # It takes media_type, media_size_bytes, blob_uri, etc.
    # It seems the API expects the blob to ALREADY be in S3.

    print(f"Verifying {file_name}...")

    # Mocking S3 upload for now as this is a Phase 1 MVP CLI
    blob_uri = f"s3://otp-intake/cli-upload/{file_name}"

    timeout_seconds = 60
    for prefix, timeout in WORKFLOW_TIMEOUTS.items():
        if media_type.startswith(prefix):
            timeout_seconds = timeout
            break

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 1. Ingest
            response = await client.post(
                f"{api_url}/ingest",
                json={
                    "media_type": media_type,
                    "media_size_bytes": file_size_bytes,
                    "blob_uri": blob_uri,
                    "source_url": "cli://local-file",
                    "submitted_by": "otp-verify-cli",
                },
            )
            response.raise_for_status()
            task_id = response.json()["task_id"]
            print(f"Job submitted. Task ID: {task_id}")

            # 2. Poll for results
            print(f"Waiting for results (timeout: {timeout_seconds}s)...", end="", flush=True)
            start_time = asyncio.get_event_loop().time()
            max_wait = timeout_seconds + 30  # Allow some buffer for network/Kafka

            while asyncio.get_event_loop().time() - start_time < max_wait:
                res = await client.get(f"{api_url}/results/{task_id}")
                if res.status_code == 200:
                    data = res.json()
                    print("\n--- Verification Result ---")
                    print(f"Verdict: {data['verdict']}")
                    print(f"Score:   {data['final_truth_score']:.4f}")
                    print(f"Mode:    {'Degraded' if data['degraded_mode'] else 'Full'}")
                    print("\nAgent Reports:")
                    for agent, report in data["agent_reports"].items():
                        status = report["status"]
                        duration = report.get("duration_ms", 0)
                        print(f"  - {agent:15}: {status} ({duration}ms)")
                    return
                elif res.status_code in {202, 404}:
                    print(".", end="", flush=True)
                    await asyncio.sleep(2.0)
                else:
                    res.raise_for_status()

            print(f"\nError: Timeout reached ({max_wait}s) without final result.")
            sys.exit(1)
        except Exception as exc:
            print(f"\nError: {exc}")
            sys.exit(1)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: otp-verify <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    file_name, file_size_bytes, media_type = _resolve_local_file(file_path)

    settings = get_settings()
    api_url = f"http://{settings.otp_api_host}:{settings.otp_api_port}"

    asyncio.run(verify_file(file_name, file_size_bytes, media_type, api_url))


if __name__ == "__main__":
    main()
