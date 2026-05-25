"""Integration test for H5 — ScoringEngine never returns a tie. We force
equal totals and verify the tiebreak chain (role_fidelity → evidence →
default to 'pro') produces a clean winner.
"""
from __future__ import annotations

import pytest

from agent_debate.agents.scoring_engine import Scorecard, ScoringEngine
from agent_debate.constants import DebateOutcome
from agent_debate.orchestration.process_verdict import finalize_verdict


@pytest.mark.timeout(10)
def test_equal_totals_resolve_via_role_fidelity_tiebreak() -> None:
    """Pro and Con tie on total; Pro wins role_fidelity → Pro wins."""
    engine = ScoringEngine()
    pro = Scorecard(clarity=15, evidence=10, rebuttal=15, novelty=15, role_fidelity=20)
    con = Scorecard(clarity=15, evidence=15, rebuttal=15, novelty=15, role_fidelity=15)
    assert pro.total == con.total
    assert engine.declare_winner(pro, con) == "pro"


@pytest.mark.timeout(10)
def test_equal_totals_and_equal_role_fidelity_resolve_via_evidence() -> None:
    """Tied on total AND role_fidelity → evidence breaks the tie."""
    engine = ScoringEngine()
    pro = Scorecard(clarity=15, evidence=20, rebuttal=15, novelty=10, role_fidelity=15)
    con = Scorecard(clarity=15, evidence=10, rebuttal=15, novelty=20, role_fidelity=15)
    assert pro.total == con.total
    assert pro.role_fidelity == con.role_fidelity
    assert engine.declare_winner(pro, con) == "pro"


@pytest.mark.timeout(10)
def test_perfect_tie_defaults_to_pro() -> None:
    """Every axis equal → final tiebreaker (affirmative wins) kicks in."""
    engine = ScoringEngine()
    pro = Scorecard(clarity=15, evidence=15, rebuttal=15, novelty=15, role_fidelity=15)
    con = Scorecard(clarity=15, evidence=15, rebuttal=15, novelty=15, role_fidelity=15)
    assert engine.declare_winner(pro, con) == "pro"


@pytest.mark.timeout(10)
def test_finalize_verdict_never_emits_tie_outcome() -> None:
    """The DebateOutcome enum has no 'tie' member, but verify finalize_verdict
    never produces anything outside {PRO_WINS, CON_WINS}."""
    class _FakeJudge:
        scoring_engine = ScoringEngine()

        def declare_winner(self, pro, con):
            winner = self.scoring_engine.declare_winner(pro, con)
            return (
                DebateOutcome.PRO_WINS if winner == "pro" else DebateOutcome.CON_WINS
            )

    class _Transcript:
        messages = [{"from": "pro"}, {"from": "con"}]
        outcome = None
        verdict = None

    outcome = finalize_verdict(_FakeJudge(), _Transcript())
    assert outcome in (DebateOutcome.PRO_WINS, DebateOutcome.CON_WINS)
