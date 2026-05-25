"""DebateSDK — Phase 9.3 unit tests covering the sole-public-entry-point
contract (rubric R1) and the N8 keystroke self-test surface.
"""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from agent_debate.orchestration.orchestrator import DebateOrchestrator
from agent_debate.sdk.debate_sdk import DebateSDK
from agent_debate.sdk.dtos import HealthStatus, MenuResponse, SpendReport
from agent_debate.tools.mock_llm_provider import MockLLMProvider


def _factory():
    return MockLLMProvider()


def _make_sdk(tmp_path: Path) -> DebateSDK:
    orch = DebateOrchestrator(
        llm_provider_factory=_factory, transcript_dir=tmp_path,
    )
    return DebateSDK(orchestrator=orch, transcript_dir=tmp_path, budget_cap=200_000)


def test_sdk_initializes_with_orchestrator(tmp_path: Path) -> None:
    sdk = _make_sdk(tmp_path)
    assert isinstance(sdk.orchestrator, DebateOrchestrator)
    assert sdk.budget_cap == 200_000
    assert sdk._last_transcript is None


def test_get_spend_report_returns_dto(tmp_path: Path) -> None:
    sdk = _make_sdk(tmp_path)
    report = sdk.get_spend_report()
    assert isinstance(report, SpendReport)
    assert report.estimated_cost_usd == Decimal("0.00")
    assert "pro" in report.by_agent
    assert "con" in report.by_agent
    assert "judge" in report.by_agent


def test_get_health_status_returns_dto(tmp_path: Path) -> None:
    sdk = _make_sdk(tmp_path)
    health = sdk.get_health_status()
    assert isinstance(health, HealthStatus)
    assert health.children_alive == {}
    assert health.restart_count == {}


def test_list_debates_empty_when_no_transcripts(tmp_path: Path) -> None:
    sdk = _make_sdk(tmp_path)
    # tmp_path exists but has no JSON files yet
    assert sdk.list_debates() == []


def test_simulate_keystroke_x_returns_exit(tmp_path: Path) -> None:
    sdk = _make_sdk(tmp_path)
    response = sdk.simulate_keystroke("X")
    assert isinstance(response, MenuResponse)
    assert response.success is True
    assert response.message == "exit"


def test_simulate_keystroke_unknown_returns_failure(tmp_path: Path) -> None:
    sdk = _make_sdk(tmp_path)
    response = sdk.simulate_keystroke("Z")
    assert response.success is False
    assert "unknown" in response.message.lower()


def test_get_transcript_raises_when_missing(tmp_path: Path) -> None:
    sdk = _make_sdk(tmp_path)
    with pytest.raises(FileNotFoundError):
        sdk.get_transcript("does-not-exist")
