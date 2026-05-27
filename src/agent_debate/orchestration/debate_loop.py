"""Synchronous debate-loop driver used by `DebateOrchestrator.run_debate(dry_run=True)`.

Phase 9 deliverable: complete the message-routing loop the spec calls for —
spawn child agents, run two-phase boot, iterate 2*n_pings turns through the
Judge, score, and return a populated Transcript. The dry_run path skips
Process.start() and instantiates the three agents in-process so unit tests
can drive the full loop without multiprocessing.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
from multiprocessing import Lock, Queue, Value

from agent_debate.agents.con_agent import ConAgent
from agent_debate.agents.content_scorer import score_transcript
from agent_debate.agents.judge_agent import JudgeAgent
from agent_debate.agents.pro_agent import ProAgent
from agent_debate.agents.scoring_engine import Scorecard
from agent_debate.constants import (
    SCHEMA_VERSION,
    AgentRole,
    MessageRole,
    Stance,
)
from agent_debate.orchestration.process_verdict import finalize_verdict

_MAX_REPLAY_PER_TURN = 1


def _build_agents(llm_provider_factory, skill_dir: str, shared_spend, lock):
    """Construct one Pro, Con, Judge for synchronous (in-process) execution."""
    common = {
        "in_queue": Queue(),
        "out_queue": Queue(),
        "heartbeat_queue": Queue(),
        "shared_spend": shared_spend,
        "lock": lock,
        "skill_dir": skill_dir,
        "llm_provider": llm_provider_factory(),
    }
    pro = ProAgent(role=AgentRole.PRO, **common)
    con = ConAgent(role=AgentRole.CON, **common)
    judge = JudgeAgent(role=AgentRole.JUDGE, **common)
    return pro, con, judge


def _make_message(from_role: str, to_role: str, role: str, text: str, ping_index: int) -> dict:
    return {
        "msg_id": str(uuid.uuid4()),
        "schema_version": SCHEMA_VERSION,
        "from": from_role,
        "to": to_role,
        "role": role,
        "ping_index": ping_index,
        "text": text,
        "timestamp": datetime.now(tz=UTC).isoformat(),
    }


def _initial_kickoff(judge: JudgeAgent, topic: str) -> dict:
    """Judge fires the first 'start' message to Pro on ping 1."""
    return _make_message(
        from_role=AgentRole.JUDGE.value,
        to_role=AgentRole.PRO.value,
        role=MessageRole.SETUP_DIRECTIVE.value,
        text=f"Open the debate on: {topic}. State your case for AI=ORIGINALITY.",
        ping_index=1,
    )


def _partisan_step(agent, inbound: dict, ping_index: int) -> dict:
    """Drive one partisan turn: produce ARGUMENT (Pro) / COUNTER (Con) reply."""
    from_role = AgentRole.PRO.value if isinstance(agent, ProAgent) else AgentRole.CON.value
    role = MessageRole.ARGUMENT.value if from_role == "pro" else MessageRole.COUNTER.value
    response = agent.step(inbound)
    text = response["text"] if isinstance(response, dict) and "text" in response else (
        f"({from_role} replies to: {inbound.get('text', '')[:60]})"
    )
    return _make_message(
        from_role=from_role,
        to_role=AgentRole.JUDGE.value,
        role=role,
        text=text,
        ping_index=ping_index,
    )


def _judge_route(judge: JudgeAgent, msg: dict, replays: int) -> tuple[dict, int]:
    """Judge inspects an incoming partisan message; may correct/intervene
    (allowing ONE replay per turn) or forward to the opponent."""
    routed = judge.handle_message(msg)
    if routed is None:
        routed = dict(msg)
        routed["to"] = "con" if msg["from"] == "pro" else "pro"
    if routed["role"] in (
        MessageRole.CORRECTION_REQUEST.value, MessageRole.INTERVENTION.value
    ) and replays < _MAX_REPLAY_PER_TURN:
        return routed, replays + 1
    return routed, replays


def _synth_scorecards(transcript) -> tuple[Scorecard, Scorecard]:
    """Real content-derived scoring (see agents/content_scorer.py)."""
    return score_transcript(transcript)


def run_debate_dry_run(
    transcript, llm_provider_factory, lifecycle, skill_dir: str,
    n_pings: int, judge_factory=None,
) -> None:
    """Drive the full debate loop in a single process. Mutates `transcript`.

    Steps: build agents → two-phase boot acks → 2*n_pings ping loop with
    Judge routing → scoring + verdict → finished_at stamp.
    """
    shared_spend, lock = Value("i", 0), Lock()
    pro, con, judge = _build_agents(llm_provider_factory, skill_dir, shared_spend, lock)
    if judge_factory is not None:
        judge = judge_factory(shared_spend, lock, skill_dir, llm_provider_factory)
    transcript.messages.append({
        "phase": "boot",
        "directive": MessageRole.SETUP_DIRECTIVE.value,
        "stance_pro": Stance.ORIGINALITY.value,
        "stance_con": Stance.REMIX_ONLY.value,
    })
    lifecycle.fire("before_round", {"transcript": transcript})
    last_msg = _initial_kickoff(judge, transcript.topic)
    transcript.messages.append(last_msg)
    for ping_index in range(1, 2 * n_pings + 1):
        speaker = pro if ping_index % 2 == 1 else con
        replays = 0
        partisan_out = _partisan_step(speaker, last_msg, ping_index)
        transcript.messages.append(partisan_out)
        routed, replays = _judge_route(judge, partisan_out, replays)
        transcript.messages.append(routed)
        last_msg = routed
    lifecycle.fire("after_round", {"transcript": transcript})
    lifecycle.fire("before_verdict", {"transcript": transcript})
    finalize_verdict(judge, transcript)
    lifecycle.fire("after_verdict", {"transcript": transcript})
    transcript.finished_at = datetime.now(tz=UTC).isoformat()
