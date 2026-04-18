from shared.scorer import apply_confidence_discount, compute_truth_score, map_score_to_verdict


def test_apply_confidence_discount_low_confidence() -> None:
    adjusted = apply_confidence_discount(0.9, 0.3)
    assert 0.5 < adjusted < 0.9


def test_apply_confidence_discount_high_confidence() -> None:
    """Test that high confidence (>0.60) doesn't discount the score."""
    adjusted = apply_confidence_discount(0.9, 0.95)
    assert adjusted == 0.9


def test_apply_confidence_discount_at_threshold() -> None:
    """Test confidence at 0.60 threshold doesn't discount."""
    adjusted = apply_confidence_discount(0.8, 0.60)
    assert adjusted == 0.8


def test_apply_confidence_discount_below_threshold() -> None:
    """Test confidence below 0.60 pulls toward neutral (0.5)."""
    adjusted = apply_confidence_discount(0.8, 0.30)
    assert 0.5 < adjusted < 0.8  # Pulled toward 0.5


def test_apply_confidence_discount_very_low_confidence() -> None:
    """Test very low confidence (0.1) pulls heavily toward 0.5."""
    adjusted = apply_confidence_discount(0.9, 0.1)
    # Should be much closer to 0.5 than to 0.9
    assert adjusted < 0.65


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
        "web_consensus": {"status": "timeout", "payload": None},
    }
    score = compute_truth_score("image/jpeg", reports)
    assert 0.7 < score <= 1.0


def test_compute_truth_score_all_agents_success_image() -> None:
    """Test scoring with all 3 agents succeeding on image (AGENTS §7 image weights)."""
    reports: dict[str, dict[str, object]] = {
        "heuristics": {
            "status": "success",
            "payload": {"heuristics_score": 1.0, "confidence": 1.0},
        },
        "provenance": {
            "status": "success",
            "payload": {"provenance_score": 1.0, "confidence": 1.0},
        },
        "web_consensus": {
            "status": "success",
            "payload": {"web_consensus_score": 1.0, "confidence": 1.0},
        },
    }
    score = compute_truth_score("image/jpeg", reports)
    assert score == 1.0  # All 1.0 scores


def test_compute_truth_score_all_agents_success_text() -> None:
    """Test scoring with all agents succeeding on text (different weights per AGENTS §7)."""
    reports: dict[str, dict[str, object]] = {
        "heuristics": {
            "status": "success",
            "payload": {"heuristics_score": 1.0, "confidence": 1.0},
        },
        "provenance": {
            "status": "success",
            "payload": {"provenance_score": 1.0, "confidence": 1.0},
        },
        "web_consensus": {
            "status": "success",
            "payload": {"web_consensus_score": 1.0, "confidence": 1.0},
        },
    }
    score = compute_truth_score("text/plain", reports)
    assert score == 1.0  # All 1.0 scores


def test_compute_truth_score_no_reports() -> None:
    """Test scoring when no agents have reported (should default to neutral)."""
    reports: dict[str, dict[str, object]] = {}
    score = compute_truth_score("image/jpeg", reports)
    assert score == 0.5  # Neutral on no data


def test_compute_truth_score_only_failed_agents() -> None:
    """Test scoring when all agents failed."""
    reports: dict[str, dict[str, object]] = {
        "heuristics": {"status": "error", "payload": None},
        "provenance": {"status": "timeout", "payload": None},
        "web_consensus": {"status": "error", "payload": None},
    }
    score = compute_truth_score("image/jpeg", reports)
    assert score == 0.5  # Neutral on all failures


def test_compute_truth_score_with_confidence_discounting() -> None:
    """Test that low-confidence scores are pulled toward neutral."""
    reports: dict[str, dict[str, object]] = {
        "heuristics": {
            "status": "success",
            "payload": {"heuristics_score": 0.95, "confidence": 0.2},  # Low confidence!
        },
        "provenance": {
            "status": "success",
            "payload": {"provenance_score": 0.5, "confidence": 1.0},
        },
        "web_consensus": {
            "status": "success",
            "payload": {"web_consensus_score": 0.5, "confidence": 1.0},
        },
    }
    score = compute_truth_score("image/jpeg", reports)
    # Heuristics' 0.95 is heavily discounted by low confidence; should pull overall down
    assert score < 0.8


def test_map_score_to_verdict_inconclusive_on_multiple_failures() -> None:
    reports: dict[str, dict[str, object]] = {
        "heuristics": {"status": "error"},
        "provenance": {"status": "timeout"},
        "web_consensus": {"status": "success"},
    }
    verdict = map_score_to_verdict(0.92, reports)
    assert verdict == "INCONCLUSIVE"


def test_map_score_to_verdict_likely_authentic() -> None:
    """Test verdict LIKELY_AUTHENTIC (0.85-1.00) per AGENTS §6.2."""
    reports: dict[str, dict[str, object]] = {
        "heuristics": {"status": "success"},
        "provenance": {"status": "success"},
        "web_consensus": {"status": "success"},
    }
    assert map_score_to_verdict(0.85, reports) == "LIKELY_AUTHENTIC"
    assert map_score_to_verdict(0.95, reports) == "LIKELY_AUTHENTIC"
    assert map_score_to_verdict(1.0, reports) == "LIKELY_AUTHENTIC"


def test_map_score_to_verdict_unverified() -> None:
    """Test verdict UNVERIFIED (0.60-0.84) per AGENTS §6.2."""
    reports: dict[str, dict[str, object]] = {
        "heuristics": {"status": "success"},
        "provenance": {"status": "success"},
        "web_consensus": {"status": "success"},
    }
    assert map_score_to_verdict(0.60, reports) == "UNVERIFIED"
    assert map_score_to_verdict(0.70, reports) == "UNVERIFIED"
    assert map_score_to_verdict(0.84, reports) == "UNVERIFIED"


def test_map_score_to_verdict_inconclusive_score() -> None:
    """Test verdict INCONCLUSIVE (0.40-0.59) per AGENTS §6.2."""
    reports: dict[str, dict[str, object]] = {
        "heuristics": {"status": "success"},
    }
    assert map_score_to_verdict(0.40, reports) == "INCONCLUSIVE"
    assert map_score_to_verdict(0.50, reports) == "INCONCLUSIVE"
    assert map_score_to_verdict(0.59, reports) == "INCONCLUSIVE"


def test_map_score_to_verdict_likely_synthetic() -> None:
    """Test verdict LIKELY_SYNTHETIC (0.15-0.39) per AGENTS §6.2."""
    reports: dict[str, dict[str, object]] = {
        "heuristics": {"status": "success"},
    }
    assert map_score_to_verdict(0.15, reports) == "LIKELY_SYNTHETIC"
    assert map_score_to_verdict(0.25, reports) == "LIKELY_SYNTHETIC"
    assert map_score_to_verdict(0.39, reports) == "LIKELY_SYNTHETIC"


def test_map_score_to_verdict_synthetic() -> None:
    """Test verdict SYNTHETIC (0.00-0.14) per AGENTS §6.2."""
    reports: dict[str, dict[str, object]] = {
        "heuristics": {"status": "success"},
    }
    assert map_score_to_verdict(0.0, reports) == "SYNTHETIC"
    assert map_score_to_verdict(0.05, reports) == "SYNTHETIC"
    assert map_score_to_verdict(0.14, reports) == "SYNTHETIC"


def test_map_score_to_verdict_boundary_between_authentic_and_unverified() -> None:
    """Test score exactly at boundary (0.85 should be LIKELY_AUTHENTIC)."""
    reports: dict[str, dict[str, object]] = {"heuristics": {"status": "success"}}
    # 0.85 is inclusive lower bound for LIKELY_AUTHENTIC
    assert map_score_to_verdict(0.85, reports) == "LIKELY_AUTHENTIC"
    # 0.8499 should be UNVERIFIED (upper bound of UNVERIFIED is 0.84)
    assert map_score_to_verdict(0.84, reports) == "UNVERIFIED"


def test_map_score_to_verdict_boundary_between_unverified_and_inconclusive() -> None:
    """Test score at boundary between UNVERIFIED (0.60-0.84) and INCONCLUSIVE (0.40-0.59)."""
    reports: dict[str, dict[str, object]] = {"heuristics": {"status": "success"}}
    # 0.60 is inclusive lower bound for UNVERIFIED
    assert map_score_to_verdict(0.60, reports) == "UNVERIFIED"
    # 0.5999 should be INCONCLUSIVE
    assert map_score_to_verdict(0.5999, reports) == "INCONCLUSIVE"


def test_compute_truth_score_text_vs_image_weights() -> None:
    """Test that text and image use different weight distributions (AGENTS §7)."""
    # Create identical reports for both text and image
    identical_reports: dict[str, dict[str, object]] = {
        "heuristics": {
            "status": "success",
            "payload": {"heuristics_score": 0.7, "confidence": 1.0},
        },
        "provenance": {
            "status": "success",
            "payload": {"provenance_score": 0.5, "confidence": 1.0},
        },
        "web_consensus": {
            "status": "success",
            "payload": {"web_consensus_score": 0.6, "confidence": 1.0},
        },
    }
    
    image_score = compute_truth_score("image/jpeg", identical_reports)
    text_score = compute_truth_score("text/plain", identical_reports)
    
    # Image: heur 0.50, prov 0.30, web 0.20 → (0.7*0.5 + 0.5*0.3 + 0.6*0.2) = 0.61
    # Text: heur 0.60, prov 0.10, web 0.30 → (0.7*0.6 + 0.5*0.1 + 0.6*0.3) = 0.65
    # Text should be higher because heuristics has higher weight and heuristics scored high
    assert text_score > image_score
