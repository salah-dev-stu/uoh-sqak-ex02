"""Thread-safe broker bridging the orchestrator's lifecycle events to SSE.

The orchestrator runs in a worker thread and `emit()`s structured events
onto a `queue.Queue`; the FastAPI SSE generator drains the queue and
yields properly framed `data: <json>\\n\\n` text/event-stream chunks.
"""
from __future__ import annotations

import json
import queue
import time
import uuid
from dataclasses import dataclass, field


@dataclass
class DebateSession:
    """One active debate stream. The frontend connects to /api/debate/<id>/stream."""

    debate_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    events: queue.Queue = field(default_factory=queue.Queue)
    done: bool = False
    stop_requested: bool = False

    def emit(self, event_type: str, payload: dict) -> None:
        """Push one event onto the queue. Safe to call from any thread."""
        self.events.put({"type": event_type, "payload": payload, "ts": time.time()})

    def emit_done(self) -> None:
        """Signal the stream to close after draining."""
        self.done = True
        self.events.put({"type": "done", "payload": {}, "ts": time.time()})

    def request_stop(self) -> None:
        """Mark the session for cooperative shutdown."""
        self.stop_requested = True

    def stream(self, timeout: float = 15.0):
        """Generator yielding SSE-framed strings. Emits `event: keepalive` on
        idle so proxies don't drop the connection. Ends after a `done` event."""
        while True:
            try:
                evt = self.events.get(timeout=timeout)
            except queue.Empty:
                yield "event: keepalive\ndata: {}\n\n"
                continue
            yield f"data: {json.dumps(evt)}\n\n"
            if evt["type"] == "done":
                return


class SessionRegistry:
    """Holds active DebateSession objects keyed by debate_id."""

    def __init__(self) -> None:
        self._sessions: dict[str, DebateSession] = {}

    def create(self) -> DebateSession:
        s = DebateSession()
        self._sessions[s.debate_id] = s
        return s

    def get(self, debate_id: str) -> DebateSession | None:
        return self._sessions.get(debate_id)

    def list_ids(self) -> list[str]:
        return list(self._sessions.keys())

    def remove(self, debate_id: str) -> None:
        self._sessions.pop(debate_id, None)
