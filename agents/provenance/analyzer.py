from __future__ import annotations


def analyze(media_type: str) -> dict[str, object]:
    if media_type.startswith("text/"):
        return {
            "c2pa_manifest_present": False,
            "document_metadata": {
                "creator": None,
                "created_date": None,
                "modified_date": None,
                "creator_tool": None,
                "revision_count": None,
            },
            "ai_tool_signature_match": False,
            "timestamp_anomaly": False,
            "provenance_score": 0.45,
        }

    return {
        "c2pa_manifest_present": False,
        "c2pa_manifest_valid": False,
        "hardware_signer": None,
        "certificate_chain_valid": False,
        "editing_history": [],
        "exif_anomalies": [],
        "metadata_stripped": False,
        "provenance_score": 0.50,
    }
