from shared.routing import get_active_agents, should_process


def test_get_active_agents_for_image() -> None:
    agents = get_active_agents("image/jpeg")
    assert agents == ("provenance", "heuristics", "web_consensus")


def test_get_active_agents_for_text() -> None:
    agents = get_active_agents("text/plain")
    assert agents == ("provenance", "heuristics", "web_consensus")


def test_should_process() -> None:
    active_agents = ["heuristics", "provenance"]
    assert should_process("heuristics", active_agents) is True
    assert should_process("web_consensus", active_agents) is False
