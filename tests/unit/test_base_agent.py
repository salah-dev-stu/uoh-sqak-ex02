"""BaseAgent abstract — init wiring, heartbeat, step() seam, SIGTERM hook."""
from __future__ import annotations

from multiprocessing import Lock, Queue, Value

from agent_debate.agents.base_agent import BaseAgent
from agent_debate.constants import AgentRole
from agent_debate.tools.mock_llm_provider import MockLLMProvider


class _Concrete(BaseAgent):
    """Minimal subclass that echoes the user message text back."""

    def handle_message(self, msg: dict) -> dict | None:
        return {"echo": msg.get("text", "")}


def _make_agent() -> _Concrete:
    return _Concrete(
        role=AgentRole.PRO,
        in_queue=Queue(),
        out_queue=Queue(),
        heartbeat_queue=Queue(),
        shared_spend=Value("i", 0),
        lock=Lock(),
        skill_dir="/tmp/skills",
        llm_provider=MockLLMProvider(),
    )


def test_initializes_with_role():
    agent = _make_agent()
    assert agent.role == AgentRole.PRO
    assert agent.skill_dir == "/tmp/skills"
    assert isinstance(agent.llm_provider, MockLLMProvider)


def test_emit_heartbeat_puts_record():
    agent = _make_agent()
    agent.emit_heartbeat()
    record = agent.heartbeat_queue.get(timeout=1)
    assert record["role"] == AgentRole.PRO
    assert isinstance(record["ts"], float)


def test_step_delegates_to_handle_message():
    agent = _make_agent()
    result = agent.step({"text": "hello"})
    assert result == {"echo": "hello"}


def test_shutdown_default_false():
    agent = _make_agent()
    assert agent._shutdown is False
