"""Project-wide constants and enums (R10: no hardcoded magic strings in code)."""
from __future__ import annotations

from enum import StrEnum


class AgentRole(StrEnum):
    PRO = "pro"
    CON = "con"
    JUDGE = "judge"


class MessageRole(StrEnum):
    SETUP_DIRECTIVE = "setup_directive"
    ACK = "ack"
    ARGUMENT = "argument"
    COUNTER = "counter"
    CORRECTION_REQUEST = "correction_request"
    INTERVENTION = "intervention"
    STATUS = "status"
    VERDICT = "verdict"


class Stance(StrEnum):
    ORIGINALITY = "AI=ORIGINALITY"
    REMIX_ONLY = "AI=REMIX_ONLY"


class DebateOutcome(StrEnum):
    PRO_WINS = "pro_wins"
    CON_WINS = "con_wins"
    DEBATE_ABORTED = "debate_aborted"
    BUDGET_EXHAUSTED = "budget_exhausted"


SCHEMA_VERSION = "1.00"
