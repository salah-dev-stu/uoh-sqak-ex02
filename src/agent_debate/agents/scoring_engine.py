"""5-axis scoring engine for the Judge (clarity, evidence, rebuttal,
novelty, role_fidelity — 20 each, 100 max). H5 no-tie enforcement via
tiebreak chain: role_fidelity → evidence → "pro" wins.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scorecard:
    """
    Input:  per-axis integer scores (0-20)
    Output: total property = sum of axes
    Setup:  clarity, evidence, rebuttal, novelty, role_fidelity (int, 0-20)
    """

    clarity: int
    evidence: int
    rebuttal: int
    novelty: int
    role_fidelity: int

    def __post_init__(self) -> None:
        for axis in ("clarity", "evidence", "rebuttal", "novelty", "role_fidelity"):
            v = getattr(self, axis)
            if not (0 <= v <= 20):
                raise ValueError(f"axis {axis}={v} out of range [0, 20]")

    @property
    def total(self) -> int:
        return (
            self.clarity
            + self.evidence
            + self.rebuttal
            + self.novelty
            + self.role_fidelity
        )


class ScoringEngine:
    """
    Input:  axes (dict[str, int]) → Scorecard;  pro/con Scorecards → winner
    Output: Scorecard (from axes), or "pro"/"con" string (from winner)
    Setup:  none — stateless aggregator
    """

    def score_axis_set(self, axes: dict[str, int]) -> Scorecard:
        return Scorecard(
            clarity=axes["clarity"],
            evidence=axes["evidence"],
            rebuttal=axes["rebuttal"],
            novelty=axes["novelty"],
            role_fidelity=axes["role_fidelity"],
        )

    def declare_winner(self, pro: Scorecard, con: Scorecard) -> str:
        """H5: no tie. Tiebreak chain: total → role_fidelity → evidence → 'pro'."""
        if pro.total > con.total:
            return "pro"
        if con.total > pro.total:
            return "con"
        # Tied on total — tiebreak chain
        if pro.role_fidelity != con.role_fidelity:
            return "pro" if pro.role_fidelity > con.role_fidelity else "con"
        if pro.evidence != con.evidence:
            return "pro" if pro.evidence > con.evidence else "con"
        return "pro"  # final tiebreaker — affirmative wins by default
