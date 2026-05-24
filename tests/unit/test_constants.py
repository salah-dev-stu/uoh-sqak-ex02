"""Constants are immutable and cover all domain enums."""
from agent_debate.constants import (
    AgentRole,
    DebateOutcome,
    MessageRole,
    Stance,
)


def test_agent_role_enum_has_three_members():
    assert {r.value for r in AgentRole} == {"pro", "con", "judge"}


def test_message_role_enum_has_eight_members():
    assert {r.value for r in MessageRole} == {
        "setup_directive", "ack", "argument", "counter",
        "correction_request", "intervention", "status", "verdict",
    }


def test_stance_enum_has_two_members():
    assert {s.value for s in Stance} == {"AI=ORIGINALITY", "AI=REMIX_ONLY"}


def test_debate_outcome_includes_aborted():
    assert "debate_aborted" in {o.value for o in DebateOutcome}
