"""Tests for the FastAPI web layer (/, /api/health, /api/debate/*).

Uses fastapi.testclient.TestClient so no real uvicorn server is started.
"""
from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from agent_debate.web import api as api_module

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


@pytest.fixture
def client(monkeypatch) -> TestClient:
    # Avoid actually starting a debate thread during tests — stub the runner.
    def _stub_runner(session, topic, n_pings, live, transcript_dir):
        session.emit("started", {"debate_id": session.debate_id, "topic": topic})
        session.emit_done()

    monkeypatch.setattr(api_module, "run_debate_in_thread", _stub_runner)
    # Fresh registry per test so id-namespaces don't leak across cases.
    api_module.registry = api_module.SessionRegistry()
    return TestClient(api_module.app)


def test_root_returns_html(client: TestClient) -> None:
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "<title>HW2" in res.text


def test_health_returns_ok(client: TestClient) -> None:
    res = client.get("/api/health")
    assert res.status_code == 200
    payload = res.json()
    assert payload["status"] == "ok"
    assert "n_active_sessions" in payload
    assert "default_topic" in payload


def test_start_debate_returns_uuid_debate_id(client: TestClient) -> None:
    res = client.post("/api/debate/start")
    assert res.status_code == 200
    data = res.json()
    assert _UUID_RE.match(data["debate_id"]), f"not a uuid: {data['debate_id']}"
    assert data["live"] is False
    assert data["n_pings"] == 10


def test_start_debate_honors_live_and_n_pings(client: TestClient) -> None:
    res = client.post("/api/debate/start?live=0&n_pings=5")
    assert res.status_code == 200
    data = res.json()
    assert data["n_pings"] == 5
    assert data["live"] is False


def test_stream_unknown_id_returns_404(client: TestClient) -> None:
    fake = "00000000-0000-0000-0000-000000000000"
    res = client.get(f"/api/debate/{fake}/stream")
    assert res.status_code == 404


def test_stop_unknown_id_returns_404(client: TestClient) -> None:
    fake = "00000000-0000-0000-0000-000000000000"
    res = client.post(f"/api/debate/{fake}/stop")
    assert res.status_code == 404


def test_invalid_debate_id_format_returns_400(client: TestClient) -> None:
    res = client.get("/api/debate/not-a-uuid/stream")
    assert res.status_code == 400


def test_stop_known_id_returns_ok(client: TestClient) -> None:
    start = client.post("/api/debate/start").json()
    res = client.post(f"/api/debate/{start['debate_id']}/stop")
    assert res.status_code == 200
    assert res.json()["ok"] is True


def test_static_app_js_is_served(client: TestClient) -> None:
    res = client.get("/static/app.js")
    assert res.status_code == 200
    assert "EventSource" in res.text  # we know the file uses this API


def test_static_style_css_is_served(client: TestClient) -> None:
    res = client.get("/static/style.css")
    assert res.status_code == 200
    assert "--bg:" in res.text  # cyberpunk palette variable
