"""Tests for Watchdog two-signal detection + restart loop (H21).

We mock Process objects rather than spawning real ones — avoids fork-leaks
and keeps each test sub-millisecond. The dummy_target helper is provided
for any future integration test that wants a real process.
"""
from __future__ import annotations

import time
from queue import Empty
from unittest.mock import MagicMock

import pytest

from agent_debate.orchestration.watchdog import Watchdog, WatchdogConfig


class _FakeQueue:
    """Minimal queue stub honoring get_nowait()/put() semantics."""

    def __init__(self) -> None:
        self._items: list = []

    def put(self, item) -> None:
        self._items.append(item)

    def get_nowait(self):
        if not self._items:
            raise Empty
        return self._items.pop(0)


def _alive_process_mock() -> MagicMock:
    p = MagicMock()
    p.is_alive.return_value = True
    p.kill = MagicMock()
    p.join = MagicMock()
    return p


def _dead_process_mock() -> MagicMock:
    p = MagicMock()
    p.is_alive.return_value = False
    return p


def _build_watchdog(
    children: dict | None = None,
    queue: _FakeQueue | None = None,
    spawn_fn=None,
    config: WatchdogConfig | None = None,
) -> Watchdog:
    children = children or {"pro": _alive_process_mock()}
    queue = queue or _FakeQueue()
    spawn_fn = spawn_fn or (lambda _role: _alive_process_mock())
    # Tiny backoff so tests run fast
    cfg = config or WatchdogConfig(
        poll_interval=0.01,
        stuck_timeout=0.5,
        max_restarts=3,
        restart_backoff=(0.0, 0.0, 0.0),
    )
    return Watchdog(
        children=children, heartbeat_queue=queue, spawn_fn=spawn_fn, config=cfg
    )


def test_watchdog_initializes_heartbeats_to_now() -> None:
    wd = _build_watchdog(
        children={"pro": _alive_process_mock(), "con": _alive_process_mock()}
    )
    now = time.time()
    assert abs(wd.last_heartbeats["pro"] - now) < 1.0
    assert abs(wd.last_heartbeats["con"] - now) < 1.0
    assert wd.restart_counts == {"pro": 0, "con": 0}


def test_drain_heartbeats_updates_last_seen() -> None:
    q = _FakeQueue()
    wd = _build_watchdog(queue=q)
    future = time.time() + 100
    q.put({"role": "pro", "ts": future})
    wd.drain_heartbeats()
    assert wd.last_heartbeats["pro"] == future


def test_is_stuck_returns_false_for_fresh_heartbeat() -> None:
    wd = _build_watchdog()
    # Fresh by virtue of __post_init__
    assert wd.is_stuck("pro") is False


def test_is_stuck_returns_true_for_stale_heartbeat() -> None:
    wd = _build_watchdog()
    # Backdate the last heartbeat
    wd.last_heartbeats["pro"] = time.time() - 999
    assert wd.is_stuck("pro") is True


def test_is_stuck_returns_true_for_dead_process() -> None:
    wd = _build_watchdog(children={"pro": _dead_process_mock()})
    assert wd.is_stuck("pro") is True


def test_restart_increments_count() -> None:
    wd = _build_watchdog()
    new = wd.restart("pro")
    assert new is not None
    assert wd.restart_counts["pro"] == 1


def test_restart_returns_none_at_max() -> None:
    wd = _build_watchdog()
    wd.restart_counts["pro"] = wd.config.max_restarts
    assert wd.restart("pro") is None


def test_step_returns_actions_on_stuck() -> None:
    wd = _build_watchdog()
    wd.last_heartbeats["pro"] = time.time() - 999  # force stale
    actions = wd.step()
    assert actions.get("pro") == "restarted"


def test_step_returns_unrecoverable_when_max_hit() -> None:
    wd = _build_watchdog()
    wd.last_heartbeats["pro"] = time.time() - 999
    wd.restart_counts["pro"] = wd.config.max_restarts
    actions = wd.step()
    assert actions.get("pro") == "unrecoverable"


def test_watchdog_config_defaults() -> None:
    cfg = WatchdogConfig()
    assert cfg.poll_interval == pytest.approx(2.0)
    assert cfg.stuck_timeout == pytest.approx(30.0)
    assert cfg.max_restarts == 3
    assert cfg.restart_backoff == (1.0, 2.0, 4.0)
