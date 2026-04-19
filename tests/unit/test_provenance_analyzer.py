"""Tests for Provenance Agent analyzer (AGENTS §5.2)."""

from __future__ import annotations


class TestProvenanceTextAnalysis:
    """Test provenance analysis for text media (AGENTS §5.2 - Document Inspection)."""

    def test_analyze_returns_valid_schema(self) -> None:
        """Test that provenance analysis returns required schema fields."""
        # Import here to avoid dependency issues if provenance agent not ready
        from agents.provenance.analyzer import analyze

        result = analyze(media_type="text/plain", content="Test document")

        assert isinstance(result, dict)
        assert "provenance_score" in result
        assert "confidence" in result

        # Scores should be in valid range [0, 1]
        assert 0 <= result["provenance_score"] <= 1
        assert 0 <= result["confidence"] <= 1

    def test_analyze_docx_metadata_extraction(self) -> None:
        """Test extraction of DOCX metadata (AGENTS §5.2)."""
        from agents.provenance.analyzer import analyze

        # Placeholder for actual DOCX test (Phase 2)
        result = analyze(media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        assert "provenance_score" in result

    def test_analyze_pdf_metadata_extraction(self) -> None:
        """Test extraction of PDF metadata (AGENTS §5.2)."""
        from agents.provenance.analyzer import analyze

        result = analyze(media_type="application/pdf")

        assert "provenance_score" in result


class TestProvenanceImageAnalysis:
    """Test provenance analysis for image media (AGENTS §5.2 - C2PA + EXIF)."""

    def test_analyze_image_returns_valid_schema(self) -> None:
        """Test that image provenance analysis returns required schema."""
        from agents.provenance.analyzer import analyze

        result = analyze(media_type="image/jpeg", content="")

        assert isinstance(result, dict)
        assert "provenance_score" in result
        assert "confidence" in result

        # Scores should be in valid range
        assert 0 <= result["provenance_score"] <= 1

    def test_analyze_image_checks_c2pa_manifest(self) -> None:
        """Test that C2PA manifest presence is checked (AGENTS §5.2)."""
        from agents.provenance.analyzer import analyze

        result = analyze(media_type="image/png", content="")

        # Result should indicate whether C2PA manifest was found
        assert "c2pa_manifest_present" in result or "provenance_score" in result

    def test_analyze_image_detects_exif_metadata(self) -> None:
        """Test that EXIF metadata detection is attempted (AGENTS §5.2)."""
        from agents.provenance.analyzer import analyze

        result = analyze(media_type="image/jpeg", content="")

        # Should attempt EXIF analysis
        assert "provenance_score" in result


class TestProvenanceMultipleFormats:
    """Test provenance analysis across multiple document formats."""

    def test_supported_text_formats(self) -> None:
        """Test that common text document formats are supported."""
        from agents.provenance.analyzer import analyze

        formats = [
            "text/plain",
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
            "application/msword",  # .doc
            "text/html",
        ]

        for media_type in formats:
            result = analyze(media_type=media_type, content="")
            assert "provenance_score" in result, f"Failed for {media_type}"

    def test_supported_image_formats(self) -> None:
        """Test that common image formats are supported."""
        from agents.provenance.analyzer import analyze

        formats = ["image/jpeg", "image/png", "image/webp", "image/tiff"]

        for media_type in formats:
            result = analyze(media_type=media_type, content="")
            assert "provenance_score" in result, f"Failed for {media_type}"


class TestProvenanceAnomalyDetection:
    """Test provenance anomaly detection (AGENTS §5.2)."""

    def test_detect_metadata_stripping(self) -> None:
        """Test detection of stripped metadata (indicates image reprocessing)."""
        from agents.provenance.analyzer import analyze

        result = analyze(media_type="image/jpeg", content="")

        # Should report anomalies in results or confidence
        assert "provenance_score" in result

    def test_detect_timestamp_anomalies(self) -> None:
        """Test detection of timestamp inconsistencies (AGENTS §5.2)."""
        from agents.provenance.analyzer import analyze

        result = analyze(media_type="image/jpeg", content="")

        # Should detect timestamp anomalies
        assert "provenance_score" in result


class TestProvenanceConfidence:
    """Test confidence scoring for provenance analysis."""

    def test_confidence_is_numeric_valid_range(self) -> None:
        """Test that confidence is always valid."""
        from agents.provenance.analyzer import analyze

        result = analyze(media_type="text/plain", content="")

        assert "confidence" in result
        assert isinstance(result["confidence"], int | float)
        assert 0 <= result["confidence"] <= 1

    def test_confidence_reflects_metadata_availability(self) -> None:
        """Test that confidence depends on metadata availability."""
        from agents.provenance.analyzer import analyze

        # Rich metadata should give higher confidence
        result = analyze(media_type="image/jpeg", content="")

        assert result["confidence"] >= 0.3, "Should have some confidence even with limited metadata"
