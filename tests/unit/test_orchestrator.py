"""Tests for DebateOrchestrator.

Phase 7 delivered scaffolding (ctor, transcript persistence,
setup_directive shape, shutdown safety). Phase 8 adds spawn_children +
run_child_loop coverage — we mock the multiprocessing primitives so the
unit tests stay fast and leak-free; real Process.start() lives in the
Phase 10 integration suite.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import time
from multiprocessing import Lock, Queue, Value
from pathlib import Path

from agent_debate.constants import AgentRole, DebateOutcome, MessageRole
from agent_debate.orchestration.lifecycle_registry import LifecycleRegistry
from agent_debate.orchestration.orchestrator import DebateOrchestrator, Transcript
from agent_debate.orchestration.orchestrator_runtime import run_child_loop
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


# -- Phase 8.2 additions ------------------------------------------------------

def test_spawn_children_creates_three_processes(tmp_path: Path) -> None:
    """spawn_children() returns a {role: Process} dict with pro/con/judge."""
    orch = DebateOrchestrator(llm_provider_factory=_factory)
    children = orch.spawn_children(topic="ai-originality", skill_dir=str(tmp_path))
    assert set(children.keys()) == {"pro", "con", "judge"}
    for proc in children.values():
        assert isinstance(proc, mp.Process)
        assert not proc.is_alive()  # not started yet


def test_spawn_children_creates_queues(tmp_path: Path) -> None:
    """spawn_children() builds the heartbeat/pro_in/con_in/judge_in queues."""
    orch = DebateOrchestrator(llm_provider_factory=_factory)
    orch.spawn_children(topic="topic-y", skill_dir=str(tmp_path))
    assert set(orch._queues.keys()) == {"heartbeat", "judge_in", "pro_in", "con_in"}


def test_run_child_loop_emits_heartbeat_at_start(tmp_path: Path) -> None:
    """Call run_child_loop with max_iterations=1; verify at least 1 heartbeat."""
    in_q: Queue = Queue()
    out_q: Queue = Queue()
    hb_q: Queue = Queue()
    shared = Value("i", 0)
    lock = Lock()
    # Pre-write a no-op msg so the in_queue.get() doesn't block forever
    in_q.put({"role": "ignored", "from": "judge", "to": "pro", "text": "x"})
    run_child_loop(
        role="pro", in_queue=in_q, out_queue=out_q, heartbeat_queue=hb_q,
        shared_spend=shared, lock=lock, skill_dir=str(tmp_path),
        llm_provider_factory=_factory, max_iterations=1,
    )
    # mp.Queue is pipe-backed; give the writer a tiny moment to flush
    time.sleep(0.1)
    rec = hb_q.get(timeout=2.0)
    assert rec is not None
    assert rec["role"] == AgentRole.PRO
    assert "ts" in rec


def test_topic_is_recorded_in_transcript() -> None:
    """Transcript dataclass carries the topic field intact."""
    t = Transcript(
        debate_id="topic-test-id-0000-0000-000000000000",
        topic="ai-vs-art",
        started_at="2026-05-25T00:00:00+00:00",
    )
    assert t.topic == "ai-vs-art"
    assert t.to_dict()["topic"] == "ai-vs-art"
