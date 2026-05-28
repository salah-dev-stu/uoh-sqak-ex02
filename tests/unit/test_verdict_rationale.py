"""Tests for the human-readable Judge rationale string."""
from __future__ import annotations

from agent_debate.agents.scoring_engine import Scorecard
from agent_debate.agents.verdict_rationale import build_rationale


def _card(c: int, e: int, r: int, n: int, f: int) -> Scorecard:
    return Scorecard(clarity=c, evidence=e, rebuttal=r, novelty=n, role_fidelity=f)


def test_pro_wins_lopsided_calls_out_dominant_axis() -> None:
    pro = _card(18, 18, 16, 16, 16)  # 84
    con = _card(12, 10, 10, 11, 12)  # 55
    r = build_rationale(pro, con, "pro")
    assert "Pro took it 84-55" in r
    assert "decisive showing" in r
    assert "clarity" in r or "evidence" in r  # one of the high-gap axes


def test_close_verdict_says_by_a_hair() -> None:
    pro = _card(15, 14, 13, 14, 16)  # 72
    con = _card(15, 14, 13, 14, 15)  # 71
    r = build_rationale(pro, con, "pro")
    assert "Pro took it 72-71" in r
    assert "by a hair" in r


def test_loser_strength_is_acknowledged_when_present() -> None:
    # Pro wins overall but Con leads on one axis.
    pro = _card(18, 16, 14, 15, 13)  # 76
    con = _card(15, 14, 12, 13, 18)  # 72 (leads role_fidelity 18 vs 13)
    r = build_rationale(pro, con, "pro")
    assert "Pro took it 76-72" in r
    assert "Con held the lead" in r
    assert "adherence to its assigned stance" in r


def test_con_wins_uses_con_label() -> None:
    pro = _card(12, 12, 12, 12, 12)  # 60
    con = _card(16, 16, 14, 15, 14)  # 75
    r = build_rationale(pro, con, "con")
    assert r.startswith("Con took it 75-60")


def test_rationale_is_one_or_two_sentences() -> None:
    pro = _card(18, 16, 14, 15, 13)
    con = _card(15, 14, 12, 13, 18)
    r = build_rationale(pro, con, "pro")
    # Should be 1 or 2 sentences max so it fits in the chyron.
    assert r.count(".") <= 3
    assert len(r) <= 280
