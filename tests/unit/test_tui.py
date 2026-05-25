"""TerminalMenu — letter-keyed dispatch tests (H11 + N8).

We mock the SDK so the menu tests stay fast and isolated from the
orchestrator. The dispatch table is the contract surface.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from agent_debate.menu.tui import TerminalMenu
from agent_debate.orchestration.orchestrator import DebateOrchestrator
from agent_debate.sdk.debate_sdk import DebateSDK
from agent_debate.tools.mock_llm_provider import MockLLMProvider


def _make_menu(tmp_path: Path) -> TerminalMenu:
    orch = DebateOrchestrator(
        llm_provider_factory=lambda: MockLLMProvider(), transcript_dir=tmp_path,
    )
    sdk = DebateSDK(orchestrator=orch, transcript_dir=tmp_path)
    return TerminalMenu(sdk=sdk, default_topic="test-topic")


def test_dispatch_x_returns_exit(tmp_path: Path) -> None:
    menu = _make_menu(tmp_path)
    assert menu.dispatch("X") == {"action": "exit", "result": 0}


def test_dispatch_e_returns_manual_mode(tmp_path: Path) -> None:
    menu = _make_menu(tmp_path)
    out = menu.dispatch("E")
    assert out["action"] == "manual_mode"
    assert "README" in out["result"]


def test_dispatch_c_returns_spend(tmp_path: Path) -> None:
    menu = _make_menu(tmp_path)
    out = menu.dispatch("C")
    assert out["action"] == "spend"
    assert "estimated_cost_usd" in out["result"]
    assert "pct_of_budget_used" in out["result"]


def test_dispatch_d_returns_health(tmp_path: Path) -> None:
    menu = _make_menu(tmp_path)
    out = menu.dispatch("D")
    assert out["action"] == "health"
    assert "children_alive" in out["result"]


def test_dispatch_unknown_returns_none(tmp_path: Path) -> None:
    menu = _make_menu(tmp_path)
    out = menu.dispatch("Q")
    assert out == {"action": "unknown", "result": None}


def test_render_contains_all_letters(tmp_path: Path) -> None:
    menu = _make_menu(tmp_path)
    legend = menu.render()
    for letter in ("A", "B", "C", "D", "E", "X"):
        assert f"[{letter}]" in legend


def test_dispatch_a_invokes_sdk_run_debate(tmp_path: Path) -> None:
    """Coverage for the A path (which spins a real dry-run debate)."""
    menu = _make_menu(tmp_path)
    menu.sdk = MagicMock(spec=DebateSDK)
    menu.sdk.run_debate.return_value = MagicMock(debate_id="abc-123")
    out = menu.dispatch("A")
    assert out["action"] == "start_debate"
    assert out["result"] == "abc-123"
    menu.sdk.run_debate.assert_called_once_with(topic="test-topic", n_pings=10)


def test_dispatch_b_returns_last_transcript_dict(tmp_path: Path) -> None:
    menu = _make_menu(tmp_path)
    fake = MagicMock()
    fake.to_dict.return_value = {"debate_id": "z"}
    menu.sdk._last_transcript = fake
    out = menu.dispatch("B")
    assert out["action"] == "view_last"
    assert out["result"] == {"debate_id": "z"}
