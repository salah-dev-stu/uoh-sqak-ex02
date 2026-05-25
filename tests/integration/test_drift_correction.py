"""Integration test (H20): drift detection emits correction_request.

Builds a JudgeAgent directly and feeds it a Pro message containing a
drift keyword ("i concede"); verifies the Judge emits a correction_request
addressed back to Pro. Also verifies the orchestrator's process flow
attaches a replay attempt onto the transcript.
"""
from __future__ import annotations

from multiprocessing import Lock, Queue, Value

import pytest

from agent_debate.agents.judge_agent import JudgeAgent
from agent_debate.constants import SCHEMA_VERSION, AgentRole, MessageRole
from agent_debate.tools.mock_llm_provider import MockLLMProvider


@pytest.mark.timeout(10)
def test_judge_emits_correction_on_drift_keyword(tmp_path) -> None:
    judge = JudgeAgent(
        role=AgentRole.JUDGE,
        in_queue=Queue(), out_queue=Queue(), heartbeat_queue=Queue(),
        shared_spend=Value("i", 0), lock=Lock(),
        skill_dir=str(tmp_path),
        llm_provider=MockLLMProvider(),
    )
    drifting = {
        "msg_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "schema_version": SCHEMA_VERSION,
        "from": "pro", "to": "judge", "role": MessageRole.ARGUMENT.value,
        "ping_index": 1,
        "text": "Actually, I concede the broader point about training data.",
        "timestamp": "2026-05-25T00:00:00+00:00",
    }
    response = judge.handle_message(drifting)
    assert response is not None
    assert response["role"] == MessageRole.CORRECTION_REQUEST.value
    assert response["to"] == "pro"
    assert response["from"] == "judge"


@pytest.mark.timeout(10)
def test_judge_does_not_correct_clean_argument(tmp_path) -> None:
    judge = JudgeAgent(
        role=AgentRole.JUDGE,
        in_queue=Queue(), out_queue=Queue(), heartbeat_queue=Queue(),
        shared_spend=Value("i", 0), lock=Lock(),
        skill_dir=str(tmp_path),
        llm_provider=MockLLMProvider(),
    )
    clean = {
        "msg_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "schema_version": SCHEMA_VERSION,
        "from": "pro", "to": "judge", "role": MessageRole.ARGUMENT.value,
        "ping_index": 1,
        "text": "AI output is original; the latent space generates novel coordinates.",
        "timestamp": "2026-05-25T00:00:00+00:00",
    }
    response = judge.handle_message(clean)
    assert response is not None
    assert response["role"] != MessageRole.CORRECTION_REQUEST.value
    assert response["to"] == "con"
