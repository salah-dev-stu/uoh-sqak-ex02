"""Integration test (H16): PC filter intervenes with sanitized text.

Feeds a Pro message containing a PC-filter keyword ("stupid"); verifies
the Judge emits an intervention message addressed back to Pro with a
sanitized text body.
"""
from __future__ import annotations

from multiprocessing import Lock, Queue, Value

import pytest

from agent_debate.agents.judge_agent import JudgeAgent
from agent_debate.constants import SCHEMA_VERSION, AgentRole, MessageRole
from agent_debate.tools.mock_llm_provider import MockLLMProvider


@pytest.mark.timeout(10)
def test_judge_emits_intervention_on_pc_keyword(tmp_path) -> None:
    judge = JudgeAgent(
        role=AgentRole.JUDGE,
        in_queue=Queue(), out_queue=Queue(), heartbeat_queue=Queue(),
        shared_spend=Value("i", 0), lock=Lock(),
        skill_dir=str(tmp_path),
        llm_provider=MockLLMProvider(),
    )
    vulgar = {
        "msg_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
        "schema_version": SCHEMA_VERSION,
        "from": "pro", "to": "judge", "role": MessageRole.ARGUMENT.value,
        "ping_index": 1,
        "text": "Con's whole argument is stupid and misguided.",
        "timestamp": "2026-05-25T00:00:00+00:00",
    }
    response = judge.handle_message(vulgar)
    assert response is not None
    assert response["role"] == MessageRole.INTERVENTION.value
    assert response["to"] == "pro"
    assert "PC violation" in response["text"]
    # Sanitized body must NOT contain the raw vulgar token.
    assert "stupid" not in response["text"].lower().split("sanitized:")[1].split(".")[0]


@pytest.mark.timeout(10)
def test_judge_passes_polite_text_through(tmp_path) -> None:
    judge = JudgeAgent(
        role=AgentRole.JUDGE,
        in_queue=Queue(), out_queue=Queue(), heartbeat_queue=Queue(),
        shared_spend=Value("i", 0), lock=Lock(),
        skill_dir=str(tmp_path),
        llm_provider=MockLLMProvider(),
    )
    polite = {
        "msg_id": "dddddddd-dddd-dddd-dddd-dddddddddddd",
        "schema_version": SCHEMA_VERSION,
        "from": "pro", "to": "judge", "role": MessageRole.ARGUMENT.value,
        "ping_index": 1,
        "text": "Con argues training data dominates; the latent space disagrees.",
        "timestamp": "2026-05-25T00:00:00+00:00",
    }
    response = judge.handle_message(polite)
    assert response is not None
    assert response["role"] != MessageRole.INTERVENTION.value
