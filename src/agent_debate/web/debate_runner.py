"""Background-thread debate runner. Bridges orchestrator -> SSE broker.

Strategy: subclass `list` so every `append` on `transcript.messages` fires
an event to the SSE queue. This keeps full compatibility with the existing
orchestrator (which expects `messages` to behave like a list) without
patching read-only built-in methods.
"""
from __future__ import annotations

import contextlib
import threading
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from agent_debate.orchestration.debate_loop import run_debate_dry_run
from agent_debate.orchestration.lifecycle_registry import LifecycleRegistry
from agent_debate.orchestration.orchestrator import DebateOrchestrator
from agent_debate.orchestration.transcript import Transcript
from agent_debate.web.sse_broker import DebateSession


class _StreamingList(list):
    """list subclass that invokes `on_append(item)` whenever an item is added."""

    def __init__(self, on_append: Callable[[object], None]) -> None:
        super().__init__()
        self._on_append = on_append

    def append(self, item: object) -> None:  # type: ignore[override]
        super().append(item)
        with contextlib.suppress(Exception):
            self._on_append(item)


def _make_provider_factory(live: bool) -> Callable:
    """Return an LLMProvider factory. `live=False` -> mock; `live=True` -> Claude."""
    if live:
        from agent_debate.tools.claude_login_provider import ClaudeLoginProvider
        return lambda: ClaudeLoginProvider()
    from agent_debate.tools.mock_llm_provider import MockLLMProvider
    return lambda: MockLLMProvider(default_text="(mock LLM response - demo mode)")


def _wire_lifecycle(session: DebateSession) -> LifecycleRegistry:
    """Register hooks so every lifecycle event reaches the SSE queue."""
    lc = LifecycleRegistry()

    def _emit_event(event_name: str) -> Callable:
        def _hook(ctx: dict) -> None:
            t = ctx.get("transcript")
            payload: dict = {}
            if t is not None:
                payload["n_messages"] = len(t.messages)
                if t.verdict is not None:
                    payload["verdict"] = t.verdict
                if t.outcome is not None:
                    payload["outcome"] = t.outcome.value
            session.emit(event_name, payload)
        return _hook

    for name in ("before_round", "after_round", "before_verdict", "after_verdict"):
        lc.register(name, _emit_event(name))
    return lc


def _build_streaming_transcript(topic: str, session: DebateSession) -> Transcript:
    """Construct a Transcript whose messages list streams to the SSE queue."""
    t = Transcript(
        debate_id=str(uuid.uuid4()),
        topic=topic,
        started_at=datetime.now(tz=UTC).isoformat(),
    )

    def _on_append(msg: object) -> None:
        if isinstance(msg, dict):
            session.emit("message", msg)
        else:
            session.emit("message", {"raw": str(msg)})

    t.messages = _StreamingList(_on_append)
    return t


def _run_dry(
    session: DebateSession,
    orch: DebateOrchestrator,
    topic: str,
    n_pings: int,
) -> Transcript:
    """Dry-run path: in-process synchronous debate with streamed events."""
    t = _build_streaming_transcript(topic, session)
    session.emit("started", {"debate_id": t.debate_id, "topic": t.topic, "n_pings": n_pings})
    run_debate_dry_run(
        transcript=t,
        llm_provider_factory=orch.llm_provider_factory,
        lifecycle=orch.lifecycle,
        skill_dir="./.claude/skills",
        n_pings=n_pings,
    )
    orch.persist_transcript(t)
    return t


def run_debate_in_thread(
    session: DebateSession,
    topic: str,
    n_pings: int,
    live: bool,
    transcript_dir: Path,
) -> threading.Thread:
    """Spawn a daemon thread driving the orchestrator. Returns the Thread."""

    def _target() -> None:
        try:
            lc = _wire_lifecycle(session)
            orch = DebateOrchestrator(
                llm_provider_factory=_make_provider_factory(live),
                lifecycle=lc,
                transcript_dir=transcript_dir,
            )
            if not live:
                t = _run_dry(session, orch, topic, n_pings)
            else:
                t = _build_streaming_transcript(topic, session)
                session.emit("started", {
                    "debate_id": t.debate_id, "topic": t.topic, "n_pings": n_pings,
                })
                orch.run_debate(
                    topic=topic, n_pings=n_pings, dry_run=False, transcript=t,
                )
            session.emit("verdict", {
                "verdict": t.verdict,
                "outcome": t.outcome.value if t.outcome else None,
            })
        except Exception as exc:  # noqa: BLE001 — surface errors to UI
            session.emit("error", {"message": str(exc), "type": type(exc).__name__})
        finally:
            session.emit_done()

    thread = threading.Thread(target=_target, daemon=True, name=f"debate-{session.debate_id[:8]}")
    thread.start()
    return thread
