"""Tests for DebateOrchestrator (construction + non-spawn paths).

Phase 7 delivers scaffolding only — spawn_children + run_debate runtime
land in Phase 8 alongside Watchdog. These tests cover ctor, transcript
persistence, setup_directive shape, and shutdown safety.
"""
from __future__ import annotations

import json
from pathlib import Path

from agent_debate.constants import AgentRole, DebateOutcome, MessageRole
from agent_debate.orchestration.lifecycle_registry import LifecycleRegistry
from agent_debate.orchestration.orchestrator import DebateOrchestrator, Transcript
from agent_debate.shared.message_schema import validate_message
from agent_debate.tools.mock_llm_provider import MockLLMProvider


def _factory():
    return MockLLMProvider()


def test_orchestrator_initializes_with_lifecycle_registry() -> None:
    orch = DebateOrchestrator(llm_provider_factory=_factory)
    assert isinstance(orch.lifecycle, LifecycleRegistry)
    assert len(orch.lifecycle.hook_names()) == 8


def test_make_setup_directive_returns_valid_message() -> None:
    orch = DebateOrchestrator(llm_provider_factory=_factory)
    msg = orch.make_setup_directive(
        to_role=AgentRole.PRO.value, stance="AI=ORIGINALITY"
    )
    # Validates against the JSON schema
    validate_message(msg)
    assert msg["from"] == AgentRole.JUDGE.value
    assert msg["to"] == AgentRole.PRO.value
    assert msg["role"] == MessageRole.SETUP_DIRECTIVE.value
    assert msg["ping_index"] == 0
    assert "AI=ORIGINALITY" in msg["text"]


def test_transcript_dataclass_roundtrip() -> None:
    t = Transcript(
        debate_id="abc12345-aaaa-bbbb-cccc-ddddeeeeffff",
        topic="ai-originality",
        started_at="2026-05-25T12:00:00+00:00",
        finished_at="2026-05-25T12:10:00+00:00",
        messages=[{"text": "hello"}],
        verdict={"winner": "pro"},
        outcome=DebateOutcome.PRO_WINS,
    )
    d = t.to_dict()
    assert d["debate_id"] == "abc12345-aaaa-bbbb-cccc-ddddeeeeffff"
    assert d["topic"] == "ai-originality"
    assert d["outcome"] == "pro_wins"
    assert d["verdict"] == {"winner": "pro"}
    assert d["messages"] == [{"text": "hello"}]


def test_persist_transcript_writes_file(tmp_path: Path) -> None:
    orch = DebateOrchestrator(
        llm_provider_factory=_factory, transcript_dir=tmp_path
    )
    t = Transcript(
        debate_id="deadbeef-1111-2222-3333-444455556666",
        topic="topic-x",
        started_at="2026-05-25T12:00:00+00:00",
        outcome=DebateOutcome.CON_WINS,
    )
    path = orch.persist_transcript(t)
    assert path.exists()
    parsed = json.loads(path.read_text(encoding="utf-8"))
    assert parsed["debate_id"] == "deadbeef-1111-2222-3333-444455556666"
    assert parsed["outcome"] == "con_wins"
    assert parsed["finished_at"] is None


def test_shutdown_gracefully_safe_on_empty_children() -> None:
    orch = DebateOrchestrator(llm_provider_factory=_factory)
    # No children → no errors
    orch.shutdown_gracefully()
    assert orch._shutdown_requested is True


def test_orchestrator_uses_shared_spend_value() -> None:
    orch = DebateOrchestrator(llm_provider_factory=_factory)
    # multiprocessing.Value wraps an int; check initial value is 0
    assert orch._shared_spend.value == 0
    with orch._lock:
        orch._shared_spend.value = 42
    assert orch._shared_spend.value == 42
