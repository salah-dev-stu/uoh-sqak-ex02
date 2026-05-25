"""BaseAgent — abstract parent for Judge/Pro/Con. Provides the testable `step()` seam.

Setup:  role (AgentRole), in_queue/out_queue/heartbeat_queue (mp.Queue),
        shared_spend (mp.Value), lock (mp.Lock), skill_dir (str),
        llm_provider (LLMProvider)
"""
from __future__ import annotations

import contextlib
import signal
import time
from abc import ABC, abstractmethod
from multiprocessing import Queue
from multiprocessing.sharedctypes import Synchronized
from multiprocessing.synchronize import Lock

from agent_debate.constants import AgentRole
from agent_debate.tools.llm_provider import LLMProvider


class BaseAgent(ABC):
    """Abstract base for every per-process agent.

    Input:  msg (dict from in_queue)
    Output: response (dict pushed to out_queue) — handled by subclass `handle_message`
    Setup:  see module docstring
    """

    def __init__(
        self,
        role: AgentRole,
        in_queue: Queue,
        out_queue: Queue,
        heartbeat_queue: Queue,
        shared_spend: Synchronized,
        lock: Lock,
        skill_dir: str,
        llm_provider: LLMProvider,
    ) -> None:
        self.role = role
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.heartbeat_queue = heartbeat_queue
        self.shared_spend = shared_spend
        self.lock = lock
        self.skill_dir = skill_dir
        self.llm_provider = llm_provider
        self._shutdown: bool = False
        self._install_sigterm_handler()

    def _install_sigterm_handler(self) -> None:
        """Register SIGTERM → graceful shutdown.

        Wrapped in try/except: signal handlers can only be installed from the
        main thread of the main interpreter, so unit tests running on worker
        threads must not crash.
        """
        with contextlib.suppress(ValueError, OSError):
            signal.signal(signal.SIGTERM, self._on_sigterm)

    def _on_sigterm(self, signum: int = 0, frame: object = None) -> None:
        """Set shutdown flag — main loop must observe and exit cleanly."""
        self._shutdown = True

    def emit_heartbeat(self) -> None:
        """Push a `{role, ts}` record to the heartbeat queue (Watchdog reads this)."""
        self.heartbeat_queue.put({"role": self.role, "ts": time.time()})

    def step(self, msg: dict) -> dict | None:
        """Test-seam wrapper around `handle_message`. The main loop calls this
        per message; unit tests can call it directly without spinning up an mp.Process.
        """
        return self.handle_message(msg)

    @abstractmethod
    def handle_message(self, msg: dict) -> dict | None:
        """Concrete subclasses define per-role behavior."""
        ...
