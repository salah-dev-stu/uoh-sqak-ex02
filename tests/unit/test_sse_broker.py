"""Tests for the thread-safe SSE broker (DebateSession + SessionRegistry)."""
from __future__ import annotations

import json
import re

import pytest

from agent_debate.web.sse_broker import DebateSession, SessionRegistry

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def test_session_emit_puts_event_on_queue() -> None:
    s = DebateSession()
    s.emit("message", {"hello": "world"})
    evt = s.events.get_nowait()
    assert evt["type"] == "message"
    assert evt["payload"] == {"hello": "world"}
    assert "ts" in evt


def test_session_stream_yields_sse_frames() -> None:
    s = DebateSession()
    s.emit("message", {"x": 1})
    s.emit_done()
    frames = list(s.stream(timeout=0.1))
    assert frames[0].startswith("data: ")
    body = frames[0][len("data: "):].rstrip("\n")
    parsed = json.loads(body)
    assert parsed["type"] == "message"
    # last frame should be the done event and the generator stops
    assert any('"type": "done"' in f for f in frames)


def test_session_stream_ends_on_done() -> None:
    s = DebateSession()
    s.emit_done()
    frames = list(s.stream(timeout=0.1))
    # exactly one frame (the done event) is yielded, then the generator returns
    assert len(frames) == 1
    assert "done" in frames[0]


def test_session_stream_emits_keepalive_on_idle() -> None:
    s = DebateSession()
    gen = s.stream(timeout=0.05)
    first = next(gen)
    assert first.startswith("event: keepalive")
    s.emit_done()
    # Drain remaining frames to clean up.
    for _ in gen:
        pass


def test_registry_create_returns_unique_uuid_ids() -> None:
    reg = SessionRegistry()
    a, b = reg.create(), reg.create()
    assert a.debate_id != b.debate_id
    assert _UUID_RE.match(a.debate_id)
    assert _UUID_RE.match(b.debate_id)
    assert set(reg.list_ids()) == {a.debate_id, b.debate_id}


def test_registry_get_returns_none_for_unknown_id() -> None:
    reg = SessionRegistry()
    assert reg.get("not-a-real-id") is None


def test_registry_remove_evicts_session() -> None:
    reg = SessionRegistry()
    s = reg.create()
    reg.remove(s.debate_id)
    assert reg.get(s.debate_id) is None
    # Removing an unknown id must be a no-op (don't raise).
    reg.remove("missing")


def test_request_stop_sets_flag() -> None:
    s = DebateSession()
    assert s.stop_requested is False
    s.request_stop()
    assert s.stop_requested is True


@pytest.mark.timeout(5)
def test_session_stream_works_with_multiple_events() -> None:
    s = DebateSession()
    s.emit("started", {"id": "x"})
    s.emit("message", {"text": "hi"})
    s.emit("verdict", {"winner": "pro"})
    s.emit_done()
    frames = list(s.stream(timeout=0.1))
    types = [json.loads(f[len("data: "):].rstrip("\n"))["type"] for f in frames]
    assert types == ["started", "message", "verdict", "done"]
