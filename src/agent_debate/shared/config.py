"""Load and validate the five JSON config files. Version-compatible per R6."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from agent_debate.shared.version import validate_config_version

_CONFIG_FILES = ("setup", "agents", "debate_rules", "rate_limits", "logging_config")


@dataclass(frozen=True)
class Config:
    setup: dict
    agents: dict
    debate_rules: dict
    rate_limits: dict
    logging_config: dict


def load_config(config_dir: Path) -> Config:
    loaded: dict[str, dict] = {}
    for name in _CONFIG_FILES:
        path = config_dir / f"{name}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        validate_config_version(data["version"], source=path.name)
        loaded[name] = data
    return Config(**loaded)
