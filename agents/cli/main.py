from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import httpx

from shared.env import get_settings
from shared.observability import get_logger

logger = get_logger("cli")


async def verify_file(file_path: str, api_url: str) -> None:
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    # In a real CLI, we would upload to S3 first.
    # For Phase 1 MVP, we simulate or assume the file is already in S3 or provided via local path
    # if the API supports it. But AGENTS.md says "Agents... pull from S3".
    
    # Let's assume for now the user has uploaded it or we use a mock blob_uri
    # Actually, the Orchestrator.create_job handles normalization to S3.
    # So the CLI should just send the media to the API Gateway.
    
    # Wait, Orchestrator main.py has an /ingest endpoint.
    # It takes media_type, media_size_bytes, blob_uri, etc.
    # It seems the API expects the blob to ALREADY be in S3.
    
    print(f"Verifying {path.name}...")
    
    # Mocking S3 upload for now as this is a Phase 1 MVP CLI
    blob_uri = f"s3://otp-intake/cli-upload/{path.name}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 1. Ingest
            response = await client.post(
                f"{api_url}/ingest",
                json={
                    "media_type": "image/jpeg",  # Simplified for MVP
                    "media_size_bytes": path.stat().st_size,
                    "blob_uri": blob_uri,
                    "source_url": "cli://local-file",
                    "submitted_by": "otp-verify-cli",
                },
            )
            response.raise_for_status()
            task_id = response.json()["task_id"]
            print(f"Job submitted. Task ID: {task_id}")
            
            # 2. Poll for results
            print("Processing...", end="", flush=True)
            while True:
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
                    break
                elif res.status_code == 404:
                    print(".", end="", flush=True)
                    await asyncio.sleep(2.0)
                else:
                    res.raise_for_status()
        except Exception as exc:
            print(f"\nError: {exc}")
            sys.exit(1)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: otp-verify <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    settings = get_settings()
    api_url = f"http://{settings.otp_api_host}:{settings.otp_api_port}"
    
    asyncio.run(verify_file(file_path, api_url))


if __name__ == "__main__":
    main()
