"""Runtime helpers for DebateOrchestrator — spawn_children + run_child_loop.

Split out of orchestrator.py to keep each module ≤150 logical lines.
The Process target (`run_child_loop`) is a module-level function so it
remains picklable across the fork/spawn boundary.

NOTE: Uses the `fork` start method explicitly. macOS Python 3.13 defaults
to `spawn`, which trips a known named-semaphore FileNotFoundError when
mp.Queue + mp.Lock primitives are passed across the pickling boundary
with daemon=True children. `fork` sidesteps the issue.
"""
from __future__ import annotations

import multiprocessing as _mp
import time
from collections.abc import Callable
from multiprocessing import Process, Queue
from multiprocessing.sharedctypes import Synchronized
from multiprocessing.synchronize import Lock

from agent_debate.constants import AgentRole

_CTX = _mp.get_context("fork")
_ROLE_CLASSES = ("pro", "con", "judge")
_HEARTBEAT_PERIOD = 2.0
_POLL_TIMEOUT = 1.0


def build_queue_topology() -> dict[str, Queue]:
    """Create the 4 queues used by the 3 processes (fork-context)."""
    return {
        "heartbeat": _CTX.Queue(),
        "judge_in": _CTX.Queue(),
        "pro_in": _CTX.Queue(),
        "con_in": _CTX.Queue(),
    }


def build_child_processes(
    target: Callable,
    queues: dict[str, Queue],
    shared_spend: Synchronized,
    lock: Lock,
    skill_dir: str,
    llm_provider_factory: Callable,
) -> dict[str, Process]:
    """Construct (but do not start) the 3 child Processes (fork-context)."""
    procs: dict[str, Process] = {}
    role_queues = {
        "pro": (queues["pro_in"], queues["judge_in"]),
        "con": (queues["con_in"], queues["judge_in"]),
        "judge": (queues["judge_in"], queues["pro_in"]),
    }
    for role in _ROLE_CLASSES:
        in_q, out_q = role_queues[role]
        procs[role] = _CTX.Process(
            target=target,
            kwargs={
                "role": role,
                "in_queue": in_q,
                "out_queue": out_q,
                "heartbeat_queue": queues["heartbeat"],
                "shared_spend": shared_spend,
                "lock": lock,
                "skill_dir": skill_dir,
                "llm_provider_factory": llm_provider_factory,
            },
            daemon=True,
        )
    return procs


def _agent_for_role(role: str):
    """Lazy import to keep the spawn picklability boundary clean."""
    from agent_debate.agents.con_agent import ConAgent
    from agent_debate.agents.judge_agent import JudgeAgent
    from agent_debate.agents.pro_agent import ProAgent

    return {"pro": ProAgent, "con": ConAgent, "judge": JudgeAgent}[role]


def _role_enum(role: str) -> AgentRole:
    return {"pro": AgentRole.PRO, "con": AgentRole.CON, "judge": AgentRole.JUDGE}[role]


def run_child_loop(
    role: str,
    in_queue: Queue,
    out_queue: Queue,
    heartbeat_queue: Queue,
    shared_spend: Synchronized,
    lock: Lock,
    skill_dir: str,
    llm_provider_factory: Callable,
    max_iterations: int | None = None,
) -> None:
    """Per-process entry point. Constructs the role's Agent, emits heartbeats,
    polls in_queue, calls step(), forwards responses to out_queue.

    Exits when `agent._shutdown` is True (SIGTERM handler set by BaseAgent)
    or when `max_iterations` is reached (unit-test bound — None for prod).
    """
    cls = _agent_for_role(role)
    agent = cls(
        role=_role_enum(role),
        in_queue=in_queue,
        out_queue=out_queue,
        heartbeat_queue=heartbeat_queue,
        shared_spend=shared_spend,
        lock=lock,
        skill_dir=skill_dir,
        llm_provider=llm_provider_factory(),
    )
    agent.emit_heartbeat()
    last_hb = time.time()
    iters = 0
    while not agent._shutdown:
        if max_iterations is not None and iters >= max_iterations:
            break
        iters += 1
        if time.time() - last_hb >= _HEARTBEAT_PERIOD:
            agent.emit_heartbeat()
            last_hb = time.time()
        try:
            msg = in_queue.get(timeout=_POLL_TIMEOUT)
        except Exception:  # noqa: BLE001 — queue.Empty differs across versions
            continue
        response = agent.step(msg)
        if response is not None:
            out_queue.put(response)
