"""DebateOrchestrator — spawns 3 child processes, owns IPC topology,
manages two-phase boot (H18), runs the debate loop, persists transcript,
and orchestrates graceful shutdown.

Phase 7 delivered the scaffolding. Phase 8 layers spawn_children +
run_debate on top via orchestrator_runtime helpers (keeps each file
≤150 logical lines).
"""
from __future__ import annotations

import json
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from multiprocessing import Lock, Process, Queue, Value
from pathlib import Path

from agent_debate.constants import (
    SCHEMA_VERSION,
    AgentRole,
    DebateOutcome,
    MessageRole,
    Stance,
)
from agent_debate.orchestration.debate_loop import run_debate_dry_run
from agent_debate.orchestration.lifecycle_registry import LifecycleRegistry
from agent_debate.orchestration.orchestrator_runtime import (
    build_child_processes,
    build_queue_topology,
    run_child_loop,
)
from agent_debate.orchestration.transcript import Transcript

__all__ = ["DebateOrchestrator", "Transcript"]


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
        self._child_map: dict[str, Process] = {}
        self._queues: dict[str, Queue] = {}
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

    def spawn_children(
        self, topic: str, skill_dir: str = "./.claude/skills"
    ) -> dict[str, Process]:
        """Create queue topology + 3 child Processes (NOT started)."""
        self._topic = topic
        self._queues = build_queue_topology()
        self._child_map = build_child_processes(
            target=run_child_loop, queues=self._queues,
            shared_spend=self._shared_spend, lock=self._lock,
            skill_dir=skill_dir, llm_provider_factory=self.llm_provider_factory,
        )
        self._children = list(self._child_map.values())
        return self._child_map

    def run_debate(
        self, topic: str, n_pings: int = 10,
        skill_dir: str = "./.claude/skills", dry_run: bool = False,
    ) -> Transcript:
        """Full debate loop. `dry_run=True` drives synchronously for tests.
        Phase 10 hardens the real-process branch with full IPC routing."""
        transcript = Transcript(
            debate_id=str(uuid.uuid4()), topic=topic,
            started_at=datetime.now(tz=UTC).isoformat(),
        )
        if dry_run:
            run_debate_dry_run(
                transcript=transcript,
                llm_provider_factory=self.llm_provider_factory,
                lifecycle=self.lifecycle, skill_dir=skill_dir, n_pings=n_pings,
            )
        else:
            self._run_with_processes(transcript, skill_dir=skill_dir)
        self.persist_transcript(transcript)
        return transcript

    def _run_with_processes(self, transcript: Transcript, skill_dir: str) -> None:
        """Real-process path: spawn, start, boot, shutdown (Phase 10 expands)."""
        self.spawn_children(topic=transcript.topic, skill_dir=skill_dir)
        for child in self._children:
            child.start()
        self._queues["pro_in"].put(
            self.make_setup_directive("pro", Stance.ORIGINALITY.value)
        )
        self._queues["con_in"].put(
            self.make_setup_directive("con", Stance.REMIX_ONLY.value)
        )
        self.shutdown_gracefully()
        transcript.finished_at = datetime.now(tz=UTC).isoformat()
        transcript.outcome = DebateOutcome.PRO_WINS
        transcript.verdict = {"winner": "pro", "note": "real-process path stub"}
