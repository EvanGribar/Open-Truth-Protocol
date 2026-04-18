from __future__ import annotations

from collections.abc import Sequence

from shared.errors import ValidationError

_MEDIA_ROUTING: dict[str, tuple[str, ...]] = {
    "image/": ("provenance", "heuristics", "web_consensus"),
    "video/": ("provenance", "heuristics", "web_consensus"),
    "audio/": ("provenance", "heuristics", "web_consensus"),
    "text/": ("provenance", "heuristics", "web_consensus"),
}


def get_active_agents(media_type: str) -> tuple[str, ...]:
    for prefix, agents in _MEDIA_ROUTING.items():
        if media_type.startswith(prefix):
            return agents
    raise ValidationError(f"Unsupported media_type: {media_type}")


def should_process(agent_name: str, active_agents: Sequence[str]) -> bool:
    return agent_name in set(active_agents)
