from __future__ import annotations

from typing import Final

OTP_VERSION: Final[str] = "2.2"

JOB_TOPIC_PREFIX: Final[str] = "otp.jobs"
RESULT_TOPIC_PREFIX: Final[str] = "otp.results"

SUPPORTED_MEDIA_PREFIXES: Final[tuple[str, ...]] = ("image/", "video/", "audio/", "text/")

IMAGE_VIDEO_AUDIO_WEIGHTS: Final[dict[str, float]] = {
    "heuristics": 0.50,
    "provenance": 0.30,
    "web_consensus": 0.20,
}

TEXT_WEIGHTS: Final[dict[str, float]] = {
    "heuristics": 0.60,
    "web_consensus": 0.30,
    "provenance": 0.10,
}

# Missing C2PA redistribution for image/video/audio path.
REDISTRIBUTED_WEIGHTS_NO_C2PA: Final[dict[str, float]] = {
    "heuristics": 0.64,
    "provenance": 0.10,
    "web_consensus": 0.26,
}

VERDICT_BANDS: Final[tuple[tuple[float, float, str], ...]] = (
    (0.85, 1.00, "LIKELY_AUTHENTIC"),
    (0.60, 0.84, "UNVERIFIED"),
    (0.40, 0.59, "INCONCLUSIVE"),
    (0.15, 0.39, "LIKELY_SYNTHETIC"),
    (0.00, 0.14, "SYNTHETIC"),
)

HARD_TIMEOUT_SECONDS: Final[dict[str, int]] = {
    "provenance": 8,
    "heuristics": 30,
    "web_consensus": 45,
    "ledger": 60,
}

WORKFLOW_TIMEOUTS: Final[dict[str, int]] = {
    "image/": 60,
    "audio/": 60,
    "text/": 30,
    "video/": 300,
}
