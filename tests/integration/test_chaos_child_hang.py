"""Integration test (H21): Watchdog two-signal detection — child is still
alive but its heartbeat is stale.

We mock a child whose heartbeat hasn't refreshed in `stuck_timeout` seconds
and verify that `Watchdog.is_stuck()` returns True even though the
Process.is_alive() check would say it's running.
"""
from __future__ import annotations

import multiprocessing as mp
import time

import pytest

from agent_debate.orchestration.watchdog import Watchdog, WatchdogConfig
from tests.integration._helpers import skip_if_fork_unavailable

_CTX = mp.get_context("fork")


def _long_sleeper(seconds: float) -> None:
    """Stay alive for `seconds` but never emit a heartbeat."""
    time.sleep(seconds)


def _spawn_replacement(role: str):  # noqa: ARG001
    proc = _CTX.Process(target=_long_sleeper, kwargs={"seconds": 0.5}, daemon=True)
    proc.start()
    return proc


@pytest.mark.chaos
@pytest.mark.timeout(20)
def test_watchdog_flags_stale_heartbeat_as_stuck() -> None:
    """Child alive but no heartbeat for >stuck_timeout → is_stuck() True."""
    skip_if_fork_unavailable()
    child = _CTX.Process(target=_long_sleeper, kwargs={"seconds": 10.0}, daemon=True)
    child.start()
    hb_q = _CTX.Queue()
    wd = Watchdog(
        children={"pro": child},
        heartbeat_queue=hb_q,
        spawn_fn=_spawn_replacement,
        config=WatchdogConfig(
            poll_interval=0.1, stuck_timeout=0.5,
            max_restarts=2, restart_backoff=(0.05, 0.1),
        ),
    )
    assert child.is_alive()
    time.sleep(1.0)
    assert wd.is_stuck("pro"), "stale heartbeat should mark child stuck"
    actions = wd.step()
    assert actions.get("pro") == "restarted"
    new = wd.children["pro"]
    new.kill()
    new.join(timeout=2)
    child.kill()
    child.join(timeout=2)


@pytest.mark.chaos
@pytest.mark.timeout(10)
def test_fresh_heartbeat_does_not_trip_watchdog() -> None:
    """Heartbeat within timeout window → not stuck."""
    skip_if_fork_unavailable()
    child = _CTX.Process(target=_long_sleeper, kwargs={"seconds": 5.0}, daemon=True)
    child.start()
    hb_q = _CTX.Queue()
    hb_q.put({"role": "pro", "ts": time.time()})
    wd = Watchdog(
        children={"pro": child},
        heartbeat_queue=hb_q,
        spawn_fn=_spawn_replacement,
        config=WatchdogConfig(
            poll_interval=0.1, stuck_timeout=3.0,
            max_restarts=2, restart_backoff=(0.05, 0.1),
        ),
    )
    wd.drain_heartbeats()
    assert not wd.is_stuck("pro")
    child.kill()
    child.join(timeout=2)
