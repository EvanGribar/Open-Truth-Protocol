import pytest

from shared.errors import ValidationError
from shared.routing import get_active_agents, should_process


def test_get_active_agents_for_image() -> None:
    agents = get_active_agents("image/jpeg")
    assert agents == ("provenance", "heuristics", "web_consensus")


def test_get_active_agents_for_image_png() -> None:
    agents = get_active_agents("image/png")
    assert agents == ("provenance", "heuristics", "web_consensus")


def test_get_active_agents_for_image_gif() -> None:
    agents = get_active_agents("image/gif")
    assert agents == ("provenance", "heuristics", "web_consensus")


def test_get_active_agents_for_video() -> None:
    agents = get_active_agents("video/mp4")
    assert agents == ("provenance", "heuristics", "web_consensus")


def test_get_active_agents_for_video_quicktime() -> None:
    agents = get_active_agents("video/quicktime")
    assert agents == ("provenance", "heuristics", "web_consensus")


def test_get_active_agents_for_audio() -> None:
    agents = get_active_agents("audio/mp3")
    assert agents == ("provenance", "heuristics", "web_consensus")


def test_get_active_agents_for_audio_wav() -> None:
    agents = get_active_agents("audio/wav")
    assert agents == ("provenance", "heuristics", "web_consensus")


def test_get_active_agents_for_text_plain() -> None:
    agents = get_active_agents("text/plain")
    assert agents == ("provenance", "heuristics", "web_consensus")


def test_get_active_agents_for_text_html() -> None:
    agents = get_active_agents("text/html")
    assert agents == ("provenance", "heuristics", "web_consensus")


def test_get_active_agents_for_text_markdown() -> None:
    agents = get_active_agents("text/markdown")
    assert agents == ("provenance", "heuristics", "web_consensus")


def test_get_active_agents_raises_for_unsupported_media_type() -> None:
    with pytest.raises(ValidationError, match="Unsupported media_type"):
        get_active_agents("application/json")


def test_get_active_agents_raises_for_completely_invalid() -> None:
    with pytest.raises(ValidationError, match="Unsupported media_type"):
        get_active_agents("unknown/type")


def test_should_process() -> None:
    active_agents = ["heuristics", "provenance"]
    assert should_process("heuristics", active_agents) is True
    assert should_process("web_consensus", active_agents) is False


def test_should_process_empty_active_agents() -> None:
    active_agents: list[str] = []
    assert should_process("heuristics", active_agents) is False
    assert should_process("web_consensus", active_agents) is False


def test_should_process_single_agent() -> None:
    active_agents = ["heuristics"]
    assert should_process("heuristics", active_agents) is True
    assert should_process("provenance", active_agents) is False
    assert should_process("web_consensus", active_agents) is False


def test_should_process_with_tuple() -> None:
    active_agents = ("heuristics", "provenance", "web_consensus")
    assert should_process("heuristics", active_agents) is True
    assert should_process("provenance", active_agents) is True
    assert should_process("web_consensus", active_agents) is True
    assert should_process("ledger", active_agents) is False
