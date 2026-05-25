"""Watchdog with two-signal detection (is_alive + heartbeat-staleness),
restart-with-state-replay, and max_restarts fail-fast (H21).

Polled by the Orchestrator. Calls `spawn_fn(role)` to respawn a stuck child.
"""
from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from multiprocessing import Process, Queue


@dataclass
class WatchdogConfig:
    """Tunables for Watchdog behavior (H21).

    Setup: poll_interval (s), stuck_timeout (s), max_restarts,
           restart_backoff (per-attempt delay tuple).
    """

    poll_interval: float = 2.0
    stuck_timeout: float = 30.0
    max_restarts: int = 3
    restart_backoff: tuple[float, ...] = (1.0, 2.0, 4.0)


@dataclass
class Watchdog:
    """Two-signal liveness detector + bounded restart loop.

    Input:  children (dict[role, Process]), heartbeat_queue (Queue)
    Output: dict[role, action] from step(); action ∈ {restarted, unrecoverable}
    Setup:  spawn_fn (Callable[[str], Process]), config (WatchdogConfig)
    """

    children: dict[str, Process]
    heartbeat_queue: Queue
    spawn_fn: Callable[[str], Process]
    config: WatchdogConfig = field(default_factory=WatchdogConfig)
    last_heartbeats: dict[str, float] = field(default_factory=dict)
    restart_counts: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        now = time.time()
        for role in self.children:
            self.last_heartbeats[role] = now
            self.restart_counts[role] = 0

    def drain_heartbeats(self) -> None:
        """Pull every pending heartbeat record and refresh last_heartbeats."""
        while True:
            try:
                rec = self.heartbeat_queue.get_nowait()
            except Exception:  # noqa: BLE001 — queue.Empty differs across versions
                break
            role = rec.get("role")
            ts = rec.get("ts")
            if role in self.last_heartbeats and isinstance(ts, int | float):
                self.last_heartbeats[role] = ts

    def is_stuck(self, role: str) -> bool:
        """Two-signal detection: process dead OR heartbeat stale."""
        child = self.children.get(role)
        if child is None:
            return False
        if not child.is_alive():
            return True
        age = time.time() - self.last_heartbeats[role]
        return age > self.config.stuck_timeout

    def restart(self, role: str) -> Process | None:
        """SIGKILL stale child + respawn with backoff. Returns None at max."""
        idx = self.restart_counts[role]
        if idx >= self.config.max_restarts:
            return None
        backoff = self.config.restart_backoff[
            min(idx, len(self.config.restart_backoff) - 1)
        ]
        old = self.children[role]
        if old.is_alive():
            old.kill()
            old.join(timeout=5)
        time.sleep(backoff)
        new = self.spawn_fn(role)
        self.children[role] = new
        self.restart_counts[role] = idx + 1
        self.last_heartbeats[role] = time.time()
        return new

    def step(self) -> dict[str, str]:
        """One poll cycle. Returns {role: action} for restart events only."""
        self.drain_heartbeats()
        actions: dict[str, str] = {}
        for role in list(self.children.keys()):
            if self.is_stuck(role):
                result = self.restart(role)
                actions[role] = "restarted" if result else "unrecoverable"
        return actions
