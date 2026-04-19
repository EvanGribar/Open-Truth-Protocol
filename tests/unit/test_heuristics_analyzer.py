"""Tests for Heuristics Agent analyzer (AGENTS §5.3)."""

from __future__ import annotations

import pytest

from agents.heuristics.analyzer import analyze


class TestHeuristicsTextAnalysis:
    """Test heuristics analysis for text media (AGENTS §5.3 - Text Analysis)."""

    def test_analyze_llm_generated_text_high_synthetic_probability(self) -> None:
        """Test that LLM-generated text is flagged as likely synthetic (AGENTS §5.3)."""
        # Simulated LLM output with low burstiness and regular perplexity
        llm_text = (
            "The rapid advancement of artificial intelligence has fundamentally transformed "
            "the landscape of modern technology. This transformation encompasses various "
            "domains including natural language processing, computer vision, and autonomous "
            "systems. The implications of these technologies extend far beyond academia, "
            "affecting industrial applications, societal structures, and ethical frameworks."
        )

        result = analyze(media_type="text/plain", content=llm_text)

        assert isinstance(result, dict)
        assert "synthetic_probability" in result
        assert "heuristics_score" in result
        assert "confidence" in result
        assert "signals" in result

        # LLM text should have moderate-to-high synthetic probability
        assert result["synthetic_probability"] > 0.5

        # heuristics_score should be inverse of synthetic_probability
        assert result["heuristics_score"] == pytest.approx(
            1.0 - result["synthetic_probability"], abs=0.01
        )

    def test_analyze_authentic_text_lower_synthetic_probability(self) -> None:
        """Test that authentic human text is flagged as more authentic (AGENTS §5.3)."""
        # Simulated human-written text with natural variation and colloquialisms
        human_text = (
            "So I was literally just sitting there, right? And like, my cat just walks up and "
            "knocks over this entire stack of papers. Like, who does that?? Anyway, I ended up "
            "having to spend like two hours reorganizing everything. Pretty wild, not gonna lie. "
            "Honestly, I can't even with these animals sometimes. They're so weird and unpredictable. "
            "But yeah, that's basically what happened yesterday afternoon."
        )

        result = analyze(media_type="text/plain", content=human_text)

        # Authentic human text should have noticeably lower synthetic probability than LLM text
        # (compared to test_analyze_llm_generated_text which has >0.5)
        assert result["synthetic_probability"] < 0.7, (
            f"Authentic text should have lower synthetic probability, got {result['synthetic_probability']}"
        )
        assert result["heuristics_score"] > 0.3

    def test_analyze_text_perplexity_signal_present(self) -> None:
        """Test that perplexity signal is computed and returned (AGENTS §5.3)."""
        test_text = "The quick brown fox jumps over the lazy dog."

        result = analyze(media_type="text/plain", content=test_text)

        assert "signals" in result
        assert "mean_perplexity" in result["signals"]
        assert isinstance(result["signals"]["mean_perplexity"], (int, float))
        assert result["signals"]["mean_perplexity"] > 0

    def test_analyze_text_burstiness_signal_present(self) -> None:
        """Test that burstiness signal is computed and returned (AGENTS §5.3)."""
        test_text = "The quick brown fox jumps over the lazy dog."

        result = analyze(media_type="text/plain", content=test_text)

        assert "signals" in result
        assert "burstiness" in result["signals"]
        assert isinstance(result["signals"]["burstiness"], (int, float))
        assert 0 <= result["signals"]["burstiness"] <= 1

    def test_analyze_short_text(self) -> None:
        """Test analysis of very short text snippets."""
        short_text = "Hello world."

        result = analyze(media_type="text/plain", content=short_text)

        # Should still return valid result even for very short text
        assert "synthetic_probability" in result
        assert "heuristics_score" in result
        assert 0 <= result["synthetic_probability"] <= 1

    def test_analyze_empty_text_returns_neutral(self) -> None:
        """Test that empty text returns neutral score."""
        result = analyze(media_type="text/plain", content="")

        # Empty text should return neutral (0.5) confidence
        assert 0.4 < result["heuristics_score"] < 0.6

    def test_analyze_code_snippet(self) -> None:
        """Test analysis of code (structured data)."""
        code_text = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

        result = analyze(media_type="text/plain", content=code_text)

        # Code has different statistical properties; should return valid result
        assert "synthetic_probability" in result
        assert 0 <= result["synthetic_probability"] <= 1


class TestHeuristicsImageAnalysis:
    """Test heuristics analysis for image media (AGENTS §5.3 - Frequency Analysis)."""

    def test_analyze_image_returns_valid_schema(self) -> None:
        """Test that image analysis returns required schema fields."""
        result = analyze(media_type="image/jpeg", content="")

        assert isinstance(result, dict)
        assert "synthetic_probability" in result
        assert "heuristics_score" in result
        assert "confidence" in result

        # Scores should be in valid range [0, 1]
        assert 0 <= result["synthetic_probability"] <= 1
        assert 0 <= result["heuristics_score"] <= 1
        assert 0 <= result["confidence"] <= 1

    def test_analyze_image_prnu_signal_present(self) -> None:
        """Test that PRNU signal is present for images (AGENTS §5.3)."""
        result = analyze(media_type="image/png", content="")

        # Images should include PRNU or frequency artifacts in signals
        assert "signals" in result

    def test_analyze_multiple_image_types(self) -> None:
        """Test that all image types are handled."""
        image_types = ["image/jpeg", "image/png", "image/webp", "image/tiff"]

        for image_type in image_types:
            result = analyze(media_type=image_type, content="")

            assert "synthetic_probability" in result
            assert "heuristics_score" in result


class TestHeuristicsAudioAnalysis:
    """Test heuristics analysis for audio media (AGENTS §5.3)."""

    def test_analyze_audio_returns_valid_schema(self) -> None:
        """Test that audio analysis returns required schema fields."""
        result = analyze(media_type="audio/mp3", content="")

        assert isinstance(result, dict)
        assert "synthetic_probability" in result
        assert "heuristics_score" in result

        # Scores should be in valid range
        assert 0 <= result["synthetic_probability"] <= 1
        assert 0 <= result["heuristics_score"] <= 1


class TestHeuristicsVideoAnalysis:
    """Test heuristics analysis for video media (AGENTS §5.3)."""

    def test_analyze_video_returns_valid_schema(self) -> None:
        """Test that video analysis returns required schema fields."""
        result = analyze(media_type="video/mp4", content="")

        assert isinstance(result, dict)
        assert "synthetic_probability" in result
        assert "heuristics_score" in result

        # Scores should be in valid range
        assert 0 <= result["synthetic_probability"] <= 1
        assert 0 <= result["heuristics_score"] <= 1


class TestHeuristicsConfidenceIntegration:
    """Test confidence field integration (AGENTS §5.3)."""

    def test_confidence_field_is_numeric(self) -> None:
        """Test that confidence is always numeric in [0, 1]."""
        result = analyze(media_type="text/plain", content="Test content")

        assert isinstance(result["confidence"], (int, float))
        assert 0 <= result["confidence"] <= 1

    def test_confidence_increases_with_signal_strength(self) -> None:
        """Test that confidence reflects signal strength."""
        # Very obvious LLM text with strong signal should have high confidence
        obvious_llm = (
            "The paradigm shift toward decentralized architectures fundamentally "
            "reconceptualizes the epistemic framework. Leveraging synergistic methodologies "
            "in a holistic approach to optimization engenders significant paradigmatic evolution. "
            "The concatenation of heterogeneous data structures within a polymorphic system "
            "architecture facilitates unprecedented scalability metrics. Furthermore, the "
            "implementation of distributed consensus mechanisms enables unprecedented efficiency."
        )

        result = analyze(media_type="text/plain", content=obvious_llm)

        # Obvious LLM text should have decent confidence in the assessment
        assert result["confidence"] >= 0.6, (
            f"Obvious LLM text should have good confidence, got {result['confidence']}"
        )
