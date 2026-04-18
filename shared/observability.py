from __future__ import annotations

import logging
import sys
from typing import Any, Final

import structlog
from prometheus_client import Counter, Histogram

LOGGER_NAME: Final[str] = "otp"

jobs_total = Counter("otp_agent_jobs_total", "Total jobs handled by agent", ["agent", "status"])
job_duration_seconds = Histogram(
    "otp_agent_job_duration_seconds",
    "Agent processing duration",
    ["agent"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 3, 5, 8, 15, 30, 60),
)
errors_total = Counter("otp_agent_errors_total", "Total agent errors", ["agent", "code"])


def configure_logging(level: str) -> None:
    logging.basicConfig(
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(message)s",
    )
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        cache_logger_on_first_use=True,
    )


def get_logger(component: str) -> Any:
    return structlog.get_logger(LOGGER_NAME).bind(component=component)
