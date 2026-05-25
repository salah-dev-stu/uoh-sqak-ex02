"""DebateOrchestrator — spawns 3 child processes, owns IPC topology,
manages two-phase boot (H18), runs the debate loop, persists transcript,
and orchestrates graceful shutdown.

Phase 7 delivers the scaffolding: ctor, LifecycleRegistry wiring, the
setup_directive factory, transcript persistence, and graceful shutdown.
Phase 8 layers spawn_children + run_debate on top.
"""
from __future__ import annotations

import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from multiprocessing import Lock, Process, Value
from pathlib import Path

from agent_debate.constants import SCHEMA_VERSION, AgentRole, DebateOutcome, MessageRole
from agent_debate.orchestration.lifecycle_registry import LifecycleRegistry


@dataclass
class Transcript:
    """Full record of a debate run, written to transcripts/<slug>-<date>.json."""

    debate_id: str
    topic: str
    started_at: str
    finished_at: str | None = None
    messages: list[dict] = field(default_factory=list)
    verdict: dict | None = None
    outcome: DebateOutcome | None = None

    def to_dict(self) -> dict:
        return {
            "debate_id": self.debate_id,
            "topic": self.topic,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "messages": self.messages,
            "verdict": self.verdict,
            "outcome": self.outcome.value if self.outcome else None,
        }


class DebateOrchestrator:
    """
    Input:  llm_provider_factory (Callable[[], LLMProvider]),
            lifecycle (LifecycleRegistry | None),
            transcript_dir (Path | None),
            gatekeeper_config (dict | None)
    Output: Transcript (full debate record, via persist_transcript)
    Setup:  shared multiprocessing primitives (spend Value, Lock),
            child Process list, shutdown flag
    """

    def __init__(
        self,
        llm_provider_factory: Callable,
        lifecycle: LifecycleRegistry | None = None,
        transcript_dir: Path | None = None,
        gatekeeper_config: dict | None = None,
    ) -> None:
        self.llm_provider_factory = llm_provider_factory
        self.lifecycle = lifecycle or LifecycleRegistry()
        self.transcript_dir = transcript_dir or Path("./transcripts")
        self.gatekeeper_config = gatekeeper_config or {}
        self._children: list[Process] = []
        self._shared_spend = Value("i", 0)
        self._lock = Lock()
        self._shutdown_requested = False

    def make_setup_directive(self, to_role: str, stance: str) -> dict:
        """Build a Phase A setup_directive message (H18)."""
        return {
            "msg_id": str(uuid.uuid4()),
            "schema_version": SCHEMA_VERSION,
            "from": AgentRole.JUDGE.value,
            "to": to_role,
            "role": MessageRole.SETUP_DIRECTIVE.value,
            "ping_index": 0,
            "text": f"Your stance: {stance}.",
            "timestamp": datetime.now(tz=UTC).isoformat(),
        }

    def persist_transcript(self, transcript: Transcript) -> Path:
        """Write transcript to transcripts/<id>-<date>.json (acceptance #5)."""
        self.transcript_dir.mkdir(parents=True, exist_ok=True)
        slug = transcript.debate_id[:8]
        path = self.transcript_dir / f"{slug}-{transcript.started_at[:10]}.json"
        path.write_text(
            json.dumps(transcript.to_dict(), indent=2), encoding="utf-8"
        )
        return path

    def shutdown_gracefully(self) -> None:
        """Cascade SIGTERM to children with 10s drain; SIGKILL stragglers."""
        self._shutdown_requested = True
        for child in self._children:
            if child.is_alive():
                child.terminate()
        for child in self._children:
            child.join(timeout=10)
            if child.is_alive():
                child.kill()

    def _signal_handler(self, *_: object) -> None:
        self.shutdown_gracefully()
