"""JudgeAgent — topic-blind moderator (routing, drift, PC, no-tie scoring)."""
from __future__ import annotations

from multiprocessing import Lock, Queue, Value

from agent_debate.agents.judge_agent import JudgeAgent
from agent_debate.agents.scoring_engine import Scorecard
from agent_debate.constants import (
    SCHEMA_VERSION,
    AgentRole,
    DebateOutcome,
    MessageRole,
)
from agent_debate.tools.mock_llm_provider import MockLLMProvider


def _make_judge() -> JudgeAgent:
    return JudgeAgent(
        role=AgentRole.JUDGE,
        in_queue=Queue(),
        out_queue=Queue(),
        heartbeat_queue=Queue(),
        shared_spend=Value("i", 0),
        lock=Lock(),
        skill_dir="/tmp",
        llm_provider=MockLLMProvider(),
    )


def _argument_msg(text: str, from_role: str = "pro", ping_index: int = 1) -> dict:
    return {
        "msg_id": "00000000-0000-0000-0000-000000000001",
        "schema_version": SCHEMA_VERSION,
        "from": from_role,
        "to": AgentRole.JUDGE.value,
        "role": MessageRole.ARGUMENT.value,
        "ping_index": ping_index,
        "text": text,
        "timestamp": "2026-05-25T00:00:00+00:00",
    }


def test_judge_initializes_topic_blind():
    assert JudgeAgent.TOPIC_BLIND is True


def test_issue_setup_directive_has_right_role():
    judge = _make_judge()
    directive = judge.issue_setup_directive(
        to_role="pro", stance="AI=ORIGINALITY", ping_index=0
    )
    assert directive["role"] == MessageRole.SETUP_DIRECTIVE.value
    assert directive["to"] == "pro"
    assert directive["from"] == AgentRole.JUDGE.value


def test_clean_message_routes_to_opponent():
    judge = _make_judge()
    msg = _argument_msg(
        "Latent-space combinations refute the remix-only claim.", from_role="pro"
    )
    routed = judge.handle_message(msg)
    assert routed is not None
    assert routed["to"] == "con"
    assert routed["from"] == "pro"


def test_drift_text_triggers_correction_request():
    judge = _make_judge()
    msg = _argument_msg("Well, I concede — your point is stronger.", from_role="pro")
    response = judge.handle_message(msg)
    assert response is not None
    assert response["role"] == MessageRole.CORRECTION_REQUEST.value
    assert response["to"] == "pro"


def test_pc_violation_triggers_intervention():
    judge = _make_judge()
    msg = _argument_msg("That is a stupid line of reasoning.", from_role="con")
    response = judge.handle_message(msg)
    assert response is not None
    assert response["role"] == MessageRole.INTERVENTION.value
    assert response["to"] == "con"
    assert "******" in response["text"]


def test_declare_winner_no_tie():
    judge = _make_judge()
    card = Scorecard(
        clarity=15, evidence=15, rebuttal=15, novelty=15, role_fidelity=15
    )
    outcome = judge.declare_winner(card, card)
    assert outcome in (DebateOutcome.PRO_WINS, DebateOutcome.CON_WINS)
