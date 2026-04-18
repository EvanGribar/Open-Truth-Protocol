from __future__ import annotations

from typing import Any

from shared.constants import (
    IMAGE_VIDEO_AUDIO_WEIGHTS,
    REDISTRIBUTED_WEIGHTS_NO_C2PA,
    TEXT_WEIGHTS,
    VERDICT_BANDS,
)
from shared.schemas import Status


def apply_confidence_discount(score: float, confidence: float) -> float:
    if confidence >= 0.60:
        return score
    blend_factor = max(0.0, confidence) / 0.60
    return score * blend_factor + 0.5 * (1 - blend_factor)


def _base_weights(media_type: str) -> dict[str, float]:
    if media_type.startswith("text/"):
        return dict(TEXT_WEIGHTS)
    return dict(IMAGE_VIDEO_AUDIO_WEIGHTS)


def resolve_weights(media_type: str, reports: dict[str, dict[str, Any]]) -> dict[str, float]:
    weights = _base_weights(media_type)
    provenance_report = reports.get("provenance")
    if not media_type.startswith("text/") and provenance_report:
        payload = provenance_report.get("payload") or {}
        if payload.get("c2pa_manifest_present") is False:
            return dict(REDISTRIBUTED_WEIGHTS_NO_C2PA)
    return weights


def compute_truth_score(media_type: str, reports: dict[str, dict[str, Any]]) -> float:
    weights = resolve_weights(media_type, reports)
    weighted_sum = 0.0
    total_weight = 0.0

    for agent_name, report in reports.items():
        if report.get("status") != Status.SUCCESS.value:
            continue
        payload = report.get("payload") or {}
        score = payload.get(f"{agent_name}_score")
        if score is None:
            if agent_name == "heuristics":
                score = payload.get("heuristics_score")
            elif agent_name == "provenance":
                score = payload.get("provenance_score")
            elif agent_name == "web_consensus":
                score = payload.get("web_consensus_score")
        if score is None:
            continue
        confidence = float(payload.get("confidence", 1.0))
        adjusted = apply_confidence_discount(float(score), confidence)
        weight = weights.get(agent_name, 0.0)
        weighted_sum += adjusted * weight
        total_weight += weight

    if total_weight == 0.0:
        return 0.5
    return max(0.0, min(1.0, weighted_sum / total_weight))


def map_score_to_verdict(score: float, reports: dict[str, dict[str, Any]]) -> str:
    failure_like = sum(
        1
        for report in reports.values()
        if report.get("status") in {Status.ERROR.value, Status.TIMEOUT.value}
    )
    if failure_like >= 2:
        return "INCONCLUSIVE"

    bounded = max(0.0, min(1.0, score))
    for low, high, verdict in VERDICT_BANDS:
        if low <= bounded <= high:
            return verdict
    return "INCONCLUSIVE"
