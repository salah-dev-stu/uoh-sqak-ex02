"""DebateSDK — sole public entry point. Menu, tests, and external Claude CLI
self-test (N8) all go through this. Rubric R1: no business logic anywhere else.
"""
from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from agent_debate.constants import AgentRole
from agent_debate.orchestration.orchestrator import DebateOrchestrator
from agent_debate.orchestration.transcript import Transcript
from agent_debate.sdk.dtos import (
    DebateMetadata,
    HealthStatus,
    MenuResponse,
    SpendReport,
)


class DebateSDK:
    """
    Input:  topic (str), n_pings (int), key (str for keystrokes)
    Output: Transcript, SpendReport, HealthStatus, list[DebateMetadata], MenuResponse
    Setup:  orchestrator (DebateOrchestrator), transcript_dir (Path), budget_cap (int)
    """

    def __init__(
        self,
        orchestrator: DebateOrchestrator,
        transcript_dir: Path | None = None,
        budget_cap: int = 200_000,
    ) -> None:
        self.orchestrator = orchestrator
        self.transcript_dir = transcript_dir or Path("./transcripts")
        self.budget_cap = budget_cap
        self._last_transcript: Transcript | None = None

    def run_debate(self, topic: str, n_pings: int = 10) -> Transcript:
        """Drive a full debate via the orchestrator. dry_run=True keeps the
        SDK runnable from the menu without spinning real child processes."""
        transcript = self.orchestrator.run_debate(
            topic=topic, n_pings=n_pings, dry_run=True,
        )
        self._last_transcript = transcript
        return transcript

    def get_transcript(self, debate_id: str) -> Transcript:
        """Look up a persisted transcript by id prefix."""
        for path in self.transcript_dir.glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("debate_id", "").startswith(debate_id):
                payload = {k: v for k, v in data.items() if k != "outcome"}
                return Transcript(**payload)
        raise FileNotFoundError(f"transcript {debate_id} not found")

    def list_debates(self) -> list[DebateMetadata]:
        results: list[DebateMetadata] = []
        if not self.transcript_dir.exists():
            return results
        for path in sorted(self.transcript_dir.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            results.append(DebateMetadata(
                debate_id=data.get("debate_id", path.stem),
                topic=data.get("topic", ""),
                started_at=data.get("started_at", ""),
                finished_at=data.get("finished_at"),
                outcome=data.get("outcome"),
                n_messages=len(data.get("messages", [])),
            ))
        return results

    def get_spend_report(self) -> SpendReport:
        """Read the shared spend Value + render a SpendReport DTO."""
        spent = self.orchestrator._shared_spend.value
        pct = (spent / self.budget_cap) * 100 if self.budget_cap else 0.0
        return SpendReport(
            total_input_tokens=spent,
            total_output_tokens=0,
            estimated_cost_usd=Decimal("0.00"),
            pct_of_budget_used=pct,
            by_agent={r.value: {"tokens": 0} for r in AgentRole},
        )

    def get_health_status(self) -> HealthStatus:
        """Phase 9: scaffold; Phase 10 wires this against Watchdog."""
        return HealthStatus(
            children_alive={},
            last_heartbeat_ages={},
            pending_messages={},
            restart_count={},
        )

    def simulate_keystroke(self, key: str) -> MenuResponse:
        """N8 self-test entry point. Maps a single letter to an SDK action."""
        key = (key or "").upper().strip()
        if key == "A":
            return MenuResponse(True, "Use sdk.run_debate(topic) to start; this simulates A.")
        if key == "B":
            t = self._last_transcript
            return MenuResponse(True, "Last transcript", payload=t.to_dict() if t else None)
        if key == "C":
            return MenuResponse(True, "spend", payload=self.get_spend_report().__dict__)
        if key == "D":
            return MenuResponse(True, "health", payload=self.get_health_status().__dict__)
        if key == "E":
            return MenuResponse(True, "manual phase-1 mode — see README")
        if key == "X":
            return MenuResponse(True, "exit")
        return MenuResponse(False, f"unknown key: {key!r}")
