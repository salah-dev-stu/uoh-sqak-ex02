"""JudgeAgent — topic-blind moderator. Routes child↔father↔child (H4),
runs drift detection (H20), PC filter (H16), 5-axis scoring (H5),
issues setup_directives (H18). Composes DriftDetector + PCFilter + ScoringEngine.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from agent_debate.agents.base_agent import BaseAgent
from agent_debate.agents.drift_detector import DriftDetector
from agent_debate.agents.pc_filter import PCFilter
from agent_debate.agents.scoring_engine import Scorecard, ScoringEngine
from agent_debate.constants import (
    SCHEMA_VERSION,
    AgentRole,
    DebateOutcome,
    MessageRole,
)


class JudgeAgent(BaseAgent):
    """
    Input:  message (dict, jsonschema-valid Message)
    Output: routed message OR correction_request OR intervention OR verdict
    Setup:  drift_keywords (set[str]), pc_keywords (set[str]),
            topic_blind (bool, default True),
            scoring_engine (ScoringEngine, optional — auto-constructed)
    """

    TOPIC_BLIND: bool = True
    SKILL_NAME: str = "judge_skill"
    temperature: float = 0.30

    def __init__(
        self,
        *args,
        drift_keywords: set[str] | None = None,
        pc_keywords: set[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.drift_detector = DriftDetector(
            drift_keywords or self._default_drift_keywords()
        )
        self.pc_filter = PCFilter(pc_keywords or self._default_pc_keywords())
        self.scoring_engine = ScoringEngine()
        self._scorecards: dict[str, list[Scorecard]] = {"pro": [], "con": []}

    @staticmethod
    def _default_drift_keywords() -> set[str]:
        return {
            "actually you're right",
            "i concede",
            "fair point",
            "good argument",
            "i agree with you",
            "you've convinced me",
            "i was wrong",
        }

    @staticmethod
    def _default_pc_keywords() -> set[str]:
        # Minimal sample; real list lives in judge_skill/SKILL.md
        return {"stupid", "idiot", "moron", "shut up"}

    def issue_setup_directive(
        self, to_role: str, stance: str, ping_index: int = 0
    ) -> dict:
        """H18: build a setup_directive message for one child."""
        return {
            "msg_id": str(uuid.uuid4()),
            "schema_version": SCHEMA_VERSION,
            "from": AgentRole.JUDGE.value,
            "to": to_role,
            "role": MessageRole.SETUP_DIRECTIVE.value,
            "ping_index": ping_index,
            "text": (
                f"Your stance: {stance}. Rules: 250-word turns, JSON format, "
                "reference opponent's prior point."
            ),
            "timestamp": datetime.now(tz=UTC).isoformat(),
        }

    def handle_message(self, msg: dict) -> dict | None:
        """H4/H16/H20: validate inbound → route or correct/intervene."""
        text = msg.get("text", "")
        if self.drift_detector.is_drift(text):
            return self._build_correction(msg)
        is_violation, sanitized = self.pc_filter.check(text)
        if is_violation:
            return self._build_intervention(msg, sanitized or "")
        return self._route(msg)

    def _route(self, msg: dict) -> dict:
        """Forward Pro→Con or Con→Pro (H4)."""
        from_role = msg["from"]
        to_role = "con" if from_role == "pro" else "pro"
        routed = dict(msg)
        routed["to"] = to_role
        return routed

    def _build_correction(self, msg: dict) -> dict:
        return {
            "msg_id": str(uuid.uuid4()),
            "schema_version": SCHEMA_VERSION,
            "from": AgentRole.JUDGE.value,
            "to": msg["from"],
            "role": MessageRole.CORRECTION_REQUEST.value,
            "ping_index": msg["ping_index"],
            "text": "Drift detected. Restate without concession phrases.",
            "timestamp": datetime.now(tz=UTC).isoformat(),
        }

    def _build_intervention(self, msg: dict, sanitized: str) -> dict:
        return {
            "msg_id": str(uuid.uuid4()),
            "schema_version": SCHEMA_VERSION,
            "from": AgentRole.JUDGE.value,
            "to": msg["from"],
            "role": MessageRole.INTERVENTION.value,
            "ping_index": msg["ping_index"],
            "text": f"PC violation. Sanitized: {sanitized}. Resubmit.",
            "timestamp": datetime.now(tz=UTC).isoformat(),
        }

    def declare_winner(
        self, pro_card: Scorecard, con_card: Scorecard
    ) -> DebateOutcome:
        """H5 no-tie enforcement via ScoringEngine."""
        winner = self.scoring_engine.declare_winner(pro_card, con_card)
        return DebateOutcome.PRO_WINS if winner == "pro" else DebateOutcome.CON_WINS
