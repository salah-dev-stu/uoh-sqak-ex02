"""Load and validate the 5 JSON config files. Versioned per R6."""
from pathlib import Path

import pytest

from agent_debate.shared.config import Config, load_config


def _seed_config_dir(tmp_path: Path, setup_version: str = "1.00") -> Path:
    (tmp_path / "setup.json").write_text(
        '{"version": "' + setup_version + '", "project_name": "x", '
        '"debate_topic": "t", "pro_stance": "p", "con_stance": "c", '
        '"transcript_dir": "./t", "log_dir": "./l", "skills_dir": "./s"}'
    )
    for name in ("agents", "debate_rules", "rate_limits", "logging_config"):
        (tmp_path / f"{name}.json").write_text('{"version": "1.00"}')
    return tmp_path


def test_load_config_returns_dataclass(tmp_path: Path):
    cfg_dir = _seed_config_dir(tmp_path)
    cfg = load_config(cfg_dir)
    assert isinstance(cfg, Config)
    assert cfg.setup["debate_topic"] == "t"


def test_load_config_rejects_wrong_version(tmp_path: Path):
    cfg_dir = _seed_config_dir(tmp_path, setup_version="2.00")
    with pytest.raises(ValueError, match="version mismatch"):
        load_config(cfg_dir)


def test_config_exposes_all_five_files(tmp_path: Path):
    cfg_dir = _seed_config_dir(tmp_path)
    cfg = load_config(cfg_dir)
    assert cfg.setup is not None
    assert cfg.agents is not None
    assert cfg.debate_rules is not None
    assert cfg.rate_limits is not None
    assert cfg.logging_config is not None
