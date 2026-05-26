"""FastAPI app exposing the debate orchestrator over HTTP + SSE.

Endpoints
---------
- GET  /                            -> static index.html
- GET  /static/*                    -> static assets (app.js, style.css)
- GET  /api/health                  -> service health
- POST /api/debate/start            -> launch a debate in a background thread
- GET  /api/debate/{id}/stream      -> Server-Sent Events of debate progress
- POST /api/debate/{id}/stop        -> cooperative cancel

Run via: `uv run agent-debate-web` (see [project.scripts] in pyproject.toml).
"""
from __future__ import annotations

import re
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from agent_debate.shared.config import load_config
from agent_debate.web.debate_runner import run_debate_in_thread
from agent_debate.web.sse_broker import SessionRegistry

_PKG_DIR = Path(__file__).parent
_STATIC_DIR = _PKG_DIR / "static"
_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

app = FastAPI(title="HW2 Agent Debate — Live GUI", version="1.00")
# CORS for Next.js dev server (localhost:3000) — production build would be same-origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
registry = SessionRegistry()


def _load_topic() -> str:
    try:
        cfg = load_config(Path("config"))
        return cfg.setup["debate_topic"]
    except Exception:  # noqa: BLE001 — config absence shouldn't crash the web layer
        return "Can AI agents create genuinely original art, or only remix human work?"


def _validate_debate_id(debate_id: str) -> None:
    if not _UUID_RE.match(debate_id):
        raise HTTPException(status_code=400, detail="invalid debate_id format")


@app.get("/api/health")
def health() -> dict:
    """Liveness/readiness probe."""
    return {
        "status": "ok",
        "n_active_sessions": len(registry.list_ids()),
        "default_topic": _load_topic(),
    }


@app.post("/api/debate/start")
def start_debate(
    live: int = Query(default=0, description="1 -> real Claude, 0 -> mock"),
    n_pings: int = Query(default=10, ge=1, le=20),
    topic: str | None = Query(default=None),
) -> dict:
    """Kick off a debate. Returns the new debate_id. Stream via /api/debate/{id}/stream."""
    session = registry.create()
    chosen_topic = topic or _load_topic()
    transcript_dir = Path("./transcripts")
    run_debate_in_thread(
        session=session,
        topic=chosen_topic,
        n_pings=n_pings,
        live=bool(live),
        transcript_dir=transcript_dir,
    )
    return {
        "debate_id": session.debate_id,
        "topic": chosen_topic,
        "n_pings": n_pings,
        "live": bool(live),
    }


@app.get("/api/debate/{debate_id}/stream")
def stream_debate(debate_id: str):
    """text/event-stream of structured events for one debate."""
    _validate_debate_id(debate_id)
    session = registry.get(debate_id)
    if session is None:
        raise HTTPException(status_code=404, detail="debate_id not found")
    headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    return StreamingResponse(
        session.stream(), media_type="text/event-stream", headers=headers
    )


@app.post("/api/debate/{debate_id}/stop")
def stop_debate(debate_id: str) -> dict:
    """Signal cooperative cancel. The runner thread checks `session.stop_requested`."""
    _validate_debate_id(debate_id)
    session = registry.get(debate_id)
    if session is None:
        raise HTTPException(status_code=404, detail="debate_id not found")
    session.request_stop()
    session.emit("stop_requested", {"debate_id": debate_id})
    return {"ok": True, "debate_id": debate_id}


# Static index — must be defined AFTER all /api routes so it doesn't shadow them.
@app.get("/")
def index() -> FileResponse:
    """Serve the single-page UI."""
    return FileResponse(_STATIC_DIR / "index.html", media_type="text/html")


# Static files (app.js, style.css). The CDN handles Tailwind & fonts.
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


def run() -> None:
    """Console-script entry point: `uv run agent-debate-web`."""
    import uvicorn  # local import keeps cold-start lean for tests

    uvicorn.run(
        "agent_debate.web.api:app",
        host="127.0.0.1",
        port=8765,
        reload=False,
        log_level="info",
    )
