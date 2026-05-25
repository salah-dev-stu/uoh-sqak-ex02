"""Shared pytest fixtures and collection hooks.

Adds Phase 10 integration fixtures: mock LLM/search providers, a temp
skill dir scaffold, and a helper to keep multi-process tests bounded.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from agent_debate.tools.mock_llm_provider import MockLLMProvider
from agent_debate.tools.mock_search_provider import MockSearchProvider

_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "llm_responses"


def pytest_collection_modifyitems(config, items):
    """Skip e2e tests unless RUN_E2E=1."""
    if os.environ.get("RUN_E2E") == "1":
        return
    skip_e2e = pytest.mark.skip(reason="requires RUN_E2E=1")
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(skip_e2e)


def _load_pings(name: str) -> list[dict]:
    return json.loads((_FIXTURE_DIR / name).read_text(encoding="utf-8"))


@pytest.fixture
def fixture_pro_pings() -> list[dict]:
    return _load_pings("pro_pings.json")


@pytest.fixture
def fixture_con_pings() -> list[dict]:
    return _load_pings("con_pings.json")


def _mock_factory_default():
    """Module-level callable safe for multiprocessing.Process pickling."""
    return MockLLMProvider(default_text="(mock argument)")


@pytest.fixture
def mock_llm_provider_factory():
    return _mock_factory_default


@pytest.fixture
def mock_search_provider():
    return MockSearchProvider()


@pytest.fixture
def temp_skill_dir(tmp_path: Path) -> Path:
    """Create a minimal pro/con/judge skill scaffold under tmp."""
    for role in ("pro_skill", "con_skill", "judge_skill"):
        sub = tmp_path / role
        sub.mkdir()
        (sub / "SKILL.md").write_text(
            f"---\nname: {role}\n---\nMock skill body for {role}.\n",
            encoding="utf-8",
        )
    return tmp_path
