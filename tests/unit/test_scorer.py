from shared.scorer import apply_confidence_discount, compute_truth_score, map_score_to_verdict


def test_apply_confidence_discount_low_confidence() -> None:
    adjusted = apply_confidence_discount(0.9, 0.3)
    assert 0.5 < adjusted < 0.9


def test_compute_truth_score_with_two_successful_agents() -> None:
    reports: dict[str, dict[str, object]] = {
        "heuristics": {
            "status": "success",
            "payload": {"heuristics_score": 0.8, "confidence": 0.9},
        },
        "provenance": {
            "status": "success",
            "payload": {"provenance_score": 0.6, "c2pa_manifest_present": True},
        },
        "web_consensus": {
            "status": "timeout",
            "payload": None,
        },
    }
    score = compute_truth_score("image/jpeg", reports)
    assert 0.7 < score <= 1.0


def test_map_score_to_verdict_inconclusive_on_multiple_failures() -> None:
    reports: dict[str, dict[str, object]] = {
        "heuristics": {"status": "error"},
        "provenance": {"status": "timeout"},
        "web_consensus": {"status": "success"},
    }
    verdict = map_score_to_verdict(0.92, reports)
    assert verdict == "INCONCLUSIVE"
