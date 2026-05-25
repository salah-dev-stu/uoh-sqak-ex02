"""Real-process IPC flow helpers (Phase 10).

Helpers called by `DebateOrchestrator._run_with_processes` when
`dry_run=False`. JudgeAgent runs in the main process so routing is direct;
Pro and Con run as real multiprocessing.Process children.

Split into this + `process_flow_verdict.py` so each module stays ≤150 lines.
"""
from __future__ import annotations

import queue as _queue
import time
import uuid
from datetime import UTC, datetime
from multiprocessing import Queue

from agent_debate.agents.judge_agent import JudgeAgent
from agent_debate.constants import (
    SCHEMA_VERSION,
    AgentRole,
    MessageRole,
    Stance,
)

ACK_TIMEOUT_S = 30.0
TURN_TIMEOUT_S = 90.0
MAX_REPLAYS_PER_TURN = 1


def _envelope(from_role: str, to_role: str, role: str, text: str, ping_index: int) -> dict:
    """Schema-valid wire-protocol envelope (used for cues + verdict messages)."""
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


def make_setup_directive(to_role: str, stance: str) -> dict:
    """Phase A: Judge → child setup_directive message (H18)."""
    return _envelope(
        from_role=AgentRole.JUDGE.value, to_role=to_role,
        role=MessageRole.SETUP_DIRECTIVE.value, ping_index=0,
        text=f"Your stance: {stance}. Open the debate when cued.",
    )


def _drain_until(judge_in_queue: Queue, deadline: float, accept) -> dict | None:
    """Pop messages until `accept(msg)` is True or deadline lapses."""
    while time.time() < deadline:
        remaining = max(0.05, deadline - time.time())
        try:
            msg = judge_in_queue.get(timeout=remaining)
        except (_queue.Empty, OSError):
            continue
        except Exception:  # noqa: BLE001
            continue
        if accept(msg):
            return msg
    return None


def wait_for_ack(
    judge_in_queue: Queue, expected_from: str, timeout: float = ACK_TIMEOUT_S
) -> dict | None:
    """Drain judge_in_queue until an ack from `expected_from` is observed."""
    return _drain_until(
        judge_in_queue, time.time() + timeout,
        lambda m: m.get("role") == MessageRole.ACK.value and m.get("from") == expected_from,
    )


def run_setup_phase(queues: dict[str, Queue], transcript) -> bool:
    """Phase A: emit two setup_directives + collect both acks."""
    pro_dir = make_setup_directive(AgentRole.PRO.value, Stance.ORIGINALITY.value)
    con_dir = make_setup_directive(AgentRole.CON.value, Stance.REMIX_ONLY.value)
    queues["pro_in"].put(pro_dir)
    queues["con_in"].put(con_dir)
    transcript.messages.append(pro_dir)
    transcript.messages.append(con_dir)
    pro_ack = wait_for_ack(queues["judge_in"], AgentRole.PRO.value)
    con_ack = wait_for_ack(queues["judge_in"], AgentRole.CON.value)
    if pro_ack is None or con_ack is None:
        return False
    transcript.messages.append(pro_ack)
    transcript.messages.append(con_ack)
    return True


def _turn_roster(ping_index: int, queues: dict[str, Queue]) -> tuple[str, str, Queue]:
    if ping_index % 2 == 1:
        return AgentRole.PRO.value, AgentRole.CON.value, queues["pro_in"]
    return AgentRole.CON.value, AgentRole.PRO.value, queues["con_in"]


def _await_partisan(
    judge_in_queue: Queue, expected_from: str, timeout: float = TURN_TIMEOUT_S
) -> dict | None:
    """Block until a non-ack message arrives from expected_from."""
    return _drain_until(
        judge_in_queue, time.time() + timeout,
        lambda m: m.get("from") == expected_from
        and m.get("role") != MessageRole.ACK.value,
    )


def _forward(msg: dict, to_role: str) -> dict:
    routed = dict(msg)
    routed["to"] = to_role
    return routed


def _route_with_replay(
    judge: JudgeAgent, partisan_out: dict, speaker_in_q: Queue, judge_in_q: Queue
) -> tuple[dict, dict | None]:
    """Judge inspects; on correction/intervention, ask speaker once for a replay."""
    routed = judge.handle_message(partisan_out)
    if routed and routed.get("role") in (
        MessageRole.CORRECTION_REQUEST.value, MessageRole.INTERVENTION.value
    ):
        speaker_in_q.put(routed)
        replay = _await_partisan(judge_in_q, expected_from=partisan_out["from"])
        return routed, replay
    if routed is None:
        routed = _forward(partisan_out, "con" if partisan_out["from"] == "pro" else "pro")
    return routed, None


def run_ping_loop(
    queues: dict[str, Queue], judge: JudgeAgent, transcript, n_pings: int
) -> None:
    """Phase B: 2*n_pings turns. Odd = Pro, even = Con. Judge in main routes."""
    last_text = f"Open the debate on: {transcript.topic}."
    for ping_index in range(1, 2 * n_pings + 1):
        speaker, opponent, in_q = _turn_roster(ping_index, queues)
        cue_role = (
            MessageRole.ARGUMENT.value if ping_index == 1 else MessageRole.COUNTER.value
        )
        cue = _envelope(AgentRole.JUDGE.value, speaker, cue_role, last_text, ping_index)
        in_q.put(cue)
        transcript.messages.append(cue)
        partisan = _await_partisan(queues["judge_in"], expected_from=speaker)
        if partisan is None:
            return
        transcript.messages.append(partisan)
        routed, replayed = _route_with_replay(judge, partisan, in_q, queues["judge_in"])
        if replayed is not None:
            transcript.messages.append(replayed)
            routed = judge.handle_message(replayed) or _forward(replayed, opponent)
        transcript.messages.append(routed)
        last_text = routed.get("text", "")
