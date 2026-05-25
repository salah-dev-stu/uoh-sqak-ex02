"""Transcript dataclass — debate's persisted record. Lives in its own module
so DebateOrchestrator stays within the 150-line budget."""
from __future__ import annotations

from dataclasses import dataclass, field

from agent_debate.constants import DebateOutcome


@dataclass
class Transcript:
    """Full record of a debate run, written to transcripts/<slug>-<date>.json.

    Input:  debate_id, topic, started_at (constructor)
    Output: to_dict() — JSON-serializable shape used by persist_transcript
    Setup:  default empty messages list + None verdict/outcome
    """

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
