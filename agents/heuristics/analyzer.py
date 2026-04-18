from __future__ import annotations


def analyze(media_type: str) -> dict[str, object]:
    if media_type.startswith("text/"):
        synthetic_probability = 0.70
        confidence = 0.80
        return {
            "synthetic_probability": synthetic_probability,
            "confidence": confidence,
            "signals": {
                "mean_perplexity": 26.5,
                "burstiness": 0.18,
                "classifier_votes": {
                    "roberta_detector": 0.72,
                    "binoculars": 0.68,
                },
            },
            "anomalies_detected": ["low_burstiness"],
            "heuristics_score": round(1.0 - synthetic_probability, 4),
        }

    synthetic_probability = 0.10
    confidence = 0.90
    return {
        "synthetic_probability": synthetic_probability,
        "confidence": confidence,
        "signals": {
            "frequency_artifact_score": 0.12,
            "classifier_votes": {
                "UniversalFakeDetect": 0.11,
                "secondary_classifier": 0.09,
            },
        },
        "anomalies_detected": [],
        "heuristics_score": round(1.0 - synthetic_probability, 4),
    }
