"""Integration test (H21): Watchdog detects a dead child and respawns it.

Spawns a real Pro Process, kills it mid-flight with SIGKILL, asks the
Watchdog to step, and asserts: (1) is_stuck() observes the dead state,
(2) restart() spawns a fresh Process, (3) the role's restart counter
increments correctly.

Marked @pytest.mark.chaos because we intentionally kill processes.
"""
from __future__ import annotations

import multiprocessing as mp
import time

import pytest

from agent_debate.orchestration.watchdog import Watchdog, WatchdogConfig
from tests.integration._helpers import skip_if_fork_unavailable

_CTX = mp.get_context("fork")


def _idle_target(seconds: float = 30.0) -> None:
    """Target function for the Watchdog test — sits idle, no heartbeat."""
    time.sleep(seconds)


def _respawn_factory(role: str):  # noqa: ARG001
    """Spawn a replacement Process (same target) for Watchdog.restart."""
    proc = _CTX.Process(target=_idle_target, kwargs={"seconds": 5.0}, daemon=True)
    proc.start()
    return proc


@pytest.mark.chaos
@pytest.mark.timeout(30)
def test_watchdog_detects_killed_child_and_restarts() -> None:
    skip_if_fork_unavailable()
    pro = _CTX.Process(target=_idle_target, kwargs={"seconds": 30.0}, daemon=True)
    pro.start()
    hb_q = _CTX.Queue()
    wd = Watchdog(
        children={"pro": pro},
        heartbeat_queue=hb_q,
        spawn_fn=_respawn_factory,
        config=WatchdogConfig(
            poll_interval=0.1, stuck_timeout=1.0,
            max_restarts=2, restart_backoff=(0.05, 0.1),
        ),
    )
    pro.kill()
    pro.join(timeout=2)
    assert not pro.is_alive()
    assert wd.is_stuck("pro")
    new_proc = wd.restart("pro")
    assert new_proc is not None
    assert new_proc.is_alive()
    assert wd.restart_counts["pro"] == 1
    new_proc.kill()
    new_proc.join(timeout=2)


@pytest.mark.chaos
@pytest.mark.timeout(30)
def test_watchdog_fail_fast_after_max_restarts() -> None:
    """Watchdog returns None once restart_counts[role] >= max_restarts."""
    skip_if_fork_unavailable()
    pro = _CTX.Process(target=_idle_target, kwargs={"seconds": 1.0}, daemon=True)
    pro.start()
    hb_q = _CTX.Queue()
    wd = Watchdog(
        children={"pro": pro},
        heartbeat_queue=hb_q,
        spawn_fn=_respawn_factory,
        config=WatchdogConfig(
            poll_interval=0.05, stuck_timeout=0.5,
            max_restarts=1, restart_backoff=(0.05,),
        ),
    )
    new = wd.restart("pro")
    assert new is not None
    assert wd.restart_counts["pro"] == 1
    over_budget = wd.restart("pro")
    assert over_budget is None  # H21 fail-fast after max_restarts
    new.kill()
    new.join(timeout=2)
