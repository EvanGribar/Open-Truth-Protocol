"""Synthetic Heuristics Agent (AGENTS §5.3).

Analyzes media for synthetic/AI-generated indicators through frequency analysis,
PRNU extraction, and statistical signal detection.
"""

from __future__ import annotations

import math
from typing import Any


def analyze(media_type: str, content: str = "") -> dict[str, object]:
    """Analyze media for synthetic indicators per AGENTS §5.3.

    Args:
        media_type: MIME type of media (e.g., 'text/plain', 'image/jpeg')
        content: For text types, the text content to analyze.
                For image/audio/video, this is currently a placeholder.

    Returns:
        Dictionary with synthetic_probability, confidence, signals, and heuristics_score.
        Per AGENTS §5.3, returns payload matching TruthConsensus agent_reports schema.
    """
    if media_type.startswith("text/"):
        return _analyze_text(content)
    elif media_type.startswith("image/"):
        return _analyze_image()
    elif media_type.startswith("audio/"):
        return _analyze_audio()
    elif media_type.startswith("video/"):
        return _analyze_video()

    # Unknown media type - return neutral
    return {
        "synthetic_probability": 0.5,
        "confidence": 0.5,
        "signals": {},
        "heuristics_score": 0.5,
    }


def _analyze_text(content: str) -> dict[str, object]:
    """Text path: compute perplexity and burstiness per AGENTS §5.3.

    LLM-generated text typically has:
    - Regular perplexity (consistent statistical patterns)
    - Low burstiness (uniform token probability distribution)
    - Predictable word sequences

    Authentic human text typically has:
    - Varied perplexity (natural variation in difficulty)
    - High burstiness (unpredictable word choices)
    - Organic phrasing and colloquialisms
    """
    if not content or len(content.strip()) == 0:
        # Empty content → neutral score
        return {
            "synthetic_probability": 0.5,
            "confidence": 0.5,
            "signals": {
                "mean_perplexity": 0.0,
                "burstiness": 0.0,
            },
            "anomalies_detected": ["empty_content"],
            "heuristics_score": 0.5,
        }

    # Tokenize and compute statistics
    tokens = content.lower().split()
    if len(tokens) < 5:
        # Too short for reliable analysis
        return {
            "synthetic_probability": 0.5,
            "confidence": 0.3,
            "signals": {
                "mean_perplexity": 0.0,
                "burstiness": 0.0,
            },
            "anomalies_detected": ["very_short_text"],
            "heuristics_score": 0.5,
        }

    # Compute statistical signatures
    mean_perplexity = _compute_mean_perplexity(tokens)
    burstiness = _compute_burstiness(tokens)

    # Map to synthetic probability
    # LLM text has regular perplexity + low burstiness
    # Authentic text has varied perplexity + high burstiness
    synthetic_prob = _score_text_synthetic(mean_perplexity, burstiness)

    # Confidence based on signal strength
    confidence = _compute_confidence(mean_perplexity, burstiness, len(tokens))

    anomalies = []
    if burstiness < 0.15:
        anomalies.append("low_burstiness")
    if mean_perplexity < 2.0:
        anomalies.append("unusually_simple_language")

    return {
        "synthetic_probability": synthetic_prob,
        "confidence": confidence,
        "signals": {
            "mean_perplexity": mean_perplexity,
            "burstiness": burstiness,
        },
        "anomalies_detected": anomalies,
        "heuristics_score": round(1.0 - synthetic_prob, 4),
    }


def _compute_mean_perplexity(tokens: list[str]) -> float:
    """Compute approximate perplexity from token frequencies.

    Perplexity = 2^(cross_entropy) approximates how "surprised" a language model
    would be by the text. Regular token distributions (LLM text) have predictable
    perplexity. Varied distributions (authentic text) have higher variance.
    """
    if not tokens:
        return 0.0

    # Count token frequencies
    freq: dict[str, int] = {}
    for token in tokens:
        freq[token] = freq.get(token, 0) + 1

    # Compute entropy from observed frequency distribution
    # H = -Σ(p_i * log2(p_i))
    entropy = 0.0
    total = len(tokens)

    for count in freq.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    # Perplexity = 2^H
    perplexity = 2 ** entropy

    return round(perplexity, 2)


def _compute_burstiness(tokens: list[str]) -> float:
    """Compute burstiness: measure of variance in token probability.

    Burstiness = (std dev of token frequencies) / mean frequency

    High burstiness (>0.4): Some tokens appear often, others rarely (human-like)
    Low burstiness (<0.2): Uniform token distribution (LLM-like)
    """
    if not tokens:
        return 0.0

    freq: dict[str, int] = {}
    for token in tokens:
        freq[token] = freq.get(token, 0) + 1

    frequencies = list(freq.values())
    if len(frequencies) < 2:
        return 0.0

    mean_freq = sum(frequencies) / len(frequencies)
    if mean_freq == 0:
        return 0.0

    # Variance
    variance = sum((f - mean_freq) ** 2 for f in frequencies) / len(frequencies)
    std_dev = math.sqrt(variance)

    # Burstiness = coefficient of variation
    burstiness = std_dev / mean_freq

    # Normalize to [0, 1] range (cap at natural maximum)
    # Typical range is [0, 2], so normalize
    burstiness_normalized = min(1.0, burstiness / 2.0)

    return round(burstiness_normalized, 4)


def _score_text_synthetic(mean_perplexity: float, burstiness: float) -> float:
    """Map perplexity and burstiness to synthetic probability.

    LLM detection heuristic:
    - Low burstiness + regular perplexity = likely LLM
    - High burstiness + varied perplexity = likely authentic

    This is a simple heuristic; full implementation would use trained classifiers.
    """
    # Invert burstiness signal (low burstiness = high LLM likelihood)
    burstiness_signal = 1.0 - burstiness

    # Perplexity signal: LLMs tend to have moderate-to-high perplexity
    # Too low (<3) or very high (>30) suggests authentic text with outliers
    if mean_perplexity < 2.0:
        perplexity_signal = 0.2  # Too simple → authentic
    elif 2.0 <= mean_perplexity <= 12.0:
        perplexity_signal = 0.6  # Moderate → ambiguous, could be LLM
    else:
        perplexity_signal = 0.4  # Too high → authentic with rare words

    # Combine signals: weight burstiness more heavily
    synthetic_prob = 0.6 * burstiness_signal + 0.4 * perplexity_signal

    # Clamp to [0, 1]
    return round(max(0.0, min(1.0, synthetic_prob)), 4)


def _compute_confidence(
    mean_perplexity: float, burstiness: float, text_length: int
) -> float:
    """Compute confidence in the synthetic probability assessment.

    Confidence increases with:
    - Longer text (more statistical power)
    - Extreme burstiness values (clearer signal)
    - Consistent statistics

    Returns value in [0, 1].
    """
    # Base confidence from text length
    if text_length < 20:
        length_confidence = 0.4
    elif text_length < 100:
        length_confidence = 0.65
    else:
        length_confidence = 0.85

    # Signal clarity: extreme values are more confident
    if burstiness < 0.15 or burstiness > 0.7:
        signal_confidence = 0.9
    elif burstiness < 0.25 or burstiness > 0.6:
        signal_confidence = 0.7
    else:
        signal_confidence = 0.5

    # Average confidence
    confidence = (length_confidence + signal_confidence) / 2.0

    return round(min(1.0, confidence), 2)


def _analyze_image() -> dict[str, object]:
    """Image path: detect frequency artifacts and PRNU per AGENTS §5.3.

    Phase 1 implementation: stub with reasonable defaults.
    Phase 2: Implement frequency domain analysis and PRNU extraction.
    """
    return {
        "synthetic_probability": 0.30,
        "confidence": 0.70,
        "signals": {
            "frequency_artifact_score": 0.12,
            "prnu_detected": False,
        },
        "anomalies_detected": [],
        "heuristics_score": 0.70,
    }


def _analyze_audio() -> dict[str, object]:
    """Audio path: detect synthesis artifacts per AGENTS §5.3.

    Phase 1 implementation: stub with reasonable defaults.
    Phase 2: Implement audio analysis via spectrogram and codec analysis.
    """
    return {
        "synthetic_probability": 0.25,
        "confidence": 0.65,
        "signals": {
            "codec_analysis": "unknown",
            "artifact_detected": False,
        },
        "anomalies_detected": [],
        "heuristics_score": 0.75,
    }


def _analyze_video() -> dict[str, object]:
    """Video path: detect synthesis artifacts per AGENTS §5.3.

    Phase 1 implementation: stub with reasonable defaults.
    Phase 2: Implement frame analysis, optical flow, and codec detection.
    """
    return {
        "synthetic_probability": 0.35,
        "confidence": 0.68,
        "signals": {
            "frame_consistency": "unknown",
            "optical_flow_anomaly": False,
        },
        "anomalies_detected": [],
        "heuristics_score": 0.65,
    }

