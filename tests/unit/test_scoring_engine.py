"""ScoringEngine — 5-axis scorecards + H5 no-tie tiebreak chain."""
from __future__ import annotations

import pytest

from agent_debate.agents.scoring_engine import Scorecard, ScoringEngine


def _card(
    clarity: int = 10,
    evidence: int = 10,
    rebuttal: int = 10,
    novelty: int = 10,
    role_fidelity: int = 10,
) -> Scorecard:
    return Scorecard(
        clarity=clarity,
        evidence=evidence,
        rebuttal=rebuttal,
        novelty=novelty,
        role_fidelity=role_fidelity,
    )


def test_scorecard_total_sums_axes():
    card = _card(clarity=18, evidence=17, rebuttal=15, novelty=12, role_fidelity=19)
    assert card.total == 81


def test_scorecard_rejects_out_of_range():
    with pytest.raises(ValueError, match="clarity=25"):
        Scorecard(clarity=25, evidence=10, rebuttal=10, novelty=10, role_fidelity=10)


def test_declare_winner_higher_total_wins():
    engine = ScoringEngine()
    pro = _card(clarity=20, evidence=20, rebuttal=20, novelty=10, role_fidelity=10)
    con = _card(clarity=15, evidence=15, rebuttal=15, novelty=15, role_fidelity=10)
    assert engine.declare_winner(pro, con) == "pro"


def test_declare_winner_tiebreak_by_role_fidelity():
    engine = ScoringEngine()
    pro = _card(clarity=15, evidence=15, rebuttal=15, novelty=15, role_fidelity=20)
    con = _card(clarity=15, evidence=15, rebuttal=15, novelty=20, role_fidelity=15)
    # equal totals (80 vs 80) — pro role_fidelity higher → pro
    assert pro.total == con.total == 80
    assert engine.declare_winner(pro, con) == "pro"


def test_declare_winner_tiebreak_by_evidence():
    engine = ScoringEngine()
    pro = _card(clarity=15, evidence=20, rebuttal=15, novelty=15, role_fidelity=15)
    con = _card(clarity=20, evidence=15, rebuttal=15, novelty=15, role_fidelity=15)
    # equal totals (80) + equal role_fidelity (15) — pro evidence higher → pro
    assert pro.total == con.total == 80
    assert pro.role_fidelity == con.role_fidelity
    assert engine.declare_winner(pro, con) == "pro"


def test_declare_winner_final_tiebreak_pro_wins():
    engine = ScoringEngine()
    pro = _card(clarity=15, evidence=15, rebuttal=15, novelty=15, role_fidelity=15)
    con = _card(clarity=15, evidence=15, rebuttal=15, novelty=15, role_fidelity=15)
    # everything equal — affirmative wins as final tiebreaker
    assert engine.declare_winner(pro, con) == "pro"
