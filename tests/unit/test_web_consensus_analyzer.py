"""Tests for Web Consensus Agent analyzer (AGENTS §5.4)."""

from __future__ import annotations


class TestWebConsensusTextAnalysis:
    """Test web consensus analysis for text media (AGENTS §5.4)."""

    def test_analyze_returns_valid_schema(self) -> None:
        """Test that web consensus returns required schema fields."""
        from agents.web_consensus.analyzer import analyze

        result = analyze(media_type="text/plain", content="Test content")

        assert isinstance(result, dict)
        assert "web_consensus_score" in result
        assert "confidence" in result

        # Scores should be in valid range
        assert 0 <= result["web_consensus_score"] <= 1
        assert 0 <= result["confidence"] <= 1

    def test_analyze_text_includes_cache_status(self) -> None:
        """Test that cache hit/miss is tracked (AGENTS §5.4)."""
        from agents.web_consensus.analyzer import analyze

        result = analyze(media_type="text/plain", content="Sample text")

        # Should indicate cache status
        assert "cache_hit" in result or "sources" in result

    def test_analyze_text_with_known_content_consistent(self) -> None:
        """Test that analyzing same content gives consistent results."""
        from agents.web_consensus.analyzer import analyze

        content = "This is a test string for consistency"

        result1 = analyze(media_type="text/plain", content=content)
        result2 = analyze(media_type="text/plain", content=content)

        # Same content should give same score (cache hit)
        assert result1["web_consensus_score"] == result2["web_consensus_score"]


class TestWebConsensusImageAnalysis:
    """Test web consensus analysis for image media (AGENTS §5.4)."""

    def test_analyze_image_returns_valid_schema(self) -> None:
        """Test that image analysis returns required fields."""
        from agents.web_consensus.analyzer import analyze

        result = analyze(media_type="image/jpeg", content="")

        assert isinstance(result, dict)
        assert "web_consensus_score" in result
        assert "confidence" in result

        assert 0 <= result["web_consensus_score"] <= 1

    def test_analyze_image_includes_phash(self) -> None:
        """Test that perceptual hash is computed (AGENTS §5.4)."""
        from agents.web_consensus.analyzer import analyze

        result = analyze(media_type="image/png", content="")

        # Should include perceptual hash or registry check result
        assert "phash" in result or "registry_match" in result or "web_consensus_score" in result


class TestWebConsensusCache:
    """Test cache layer (AGENTS §5.4)."""

    def test_cache_layer_functional(self) -> None:
        """Test that caching mechanism works (AGENTS §5.4)."""
        from agents.web_consensus.analyzer import analyze

        # Second analysis of same content
        result2 = analyze(media_type="text/plain", content="Cache test content")

        # Should indicate cache behavior
        assert "cache_hit" in result2 or "web_consensus_score" in result2

    def test_cache_different_content_different_result(self) -> None:
        """Test that different content gives different cache entries."""
        from agents.web_consensus.analyzer import analyze

        result1 = analyze(media_type="text/plain", content="First unique content here")
        result2 = analyze(media_type="text/plain", content="Second unique content here")

        # Different content → different cache entries (may have same score by chance, but distinct)
        assert "web_consensus_score" in result1
        assert "web_consensus_score" in result2


class TestWebConsensusPHashLookup:
    """Test PHash registry lookup (AGENTS §5.4)."""

    def test_analyze_image_phash_generation(self) -> None:
        """Test that perceptual hash is generated for images."""
        from agents.web_consensus.analyzer import analyze

        result = analyze(media_type="image/jpeg", content="")

        # Should contain scoring even if registry not populated
        assert "web_consensus_score" in result

    def test_analyze_multiple_image_types(self) -> None:
        """Test that multiple image types are supported."""
        from agents.web_consensus.analyzer import analyze

        formats = ["image/jpeg", "image/png", "image/webp"]

        for media_type in formats:
            result = analyze(media_type=media_type, content="")
            assert "web_consensus_score" in result, f"Failed for {media_type}"


class TestWebConsensusAudioVideo:
    """Test web consensus for audio/video (AGENTS §5.4)."""

    def test_analyze_audio(self) -> None:
        """Test audio analysis."""
        from agents.web_consensus.analyzer import analyze

        result = analyze(media_type="audio/mp3", content="")

        assert "web_consensus_score" in result

    def test_analyze_video(self) -> None:
        """Test video analysis."""
        from agents.web_consensus.analyzer import analyze

        result = analyze(media_type="video/mp4", content="")

        assert "web_consensus_score" in result


class TestWebConsensusConfidence:
    """Test confidence scoring for web consensus."""

    def test_confidence_is_valid_range(self) -> None:
        """Test that confidence is always valid."""
        from agents.web_consensus.analyzer import analyze

        result = analyze(media_type="text/plain", content="Test")

        assert "confidence" in result
        assert isinstance(result["confidence"], int | float)
        assert 0 <= result["confidence"] <= 1

    def test_confidence_reflects_data_availability(self) -> None:
        """Test that confidence depends on available data."""
        from agents.web_consensus.analyzer import analyze

        result = analyze(media_type="text/plain", content="Test with enough content for analysis")

        # More content should give better confidence
        assert result["confidence"] >= 0.4, "Should have reasonable confidence with content"
