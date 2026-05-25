"""compute_scores.py — CLI helper the judge_skill shells out to.

Reads a JSON object on stdin with two keys ("pro", "con"); each holds a
5-axis scorecard (clarity, evidence, rebuttal, novelty, role_fidelity).
Prints a JSON object {totals: {...}, winner: "pro"|"con"} to stdout.

Stateless wrapper around `agent_debate.agents.scoring_engine` — keeps the
judge skill's runtime deterministic and out of the LLM's persuasion path.
"""
from __future__ import annotations

import json
import sys

from agent_debate.agents.scoring_engine import ScoringEngine


def main() -> int:
    payload = json.load(sys.stdin)
    engine = ScoringEngine()
    pro = engine.score_axis_set(payload["pro"])
    con = engine.score_axis_set(payload["con"])
    winner = engine.declare_winner(pro, con)
    json.dump(
        {"totals": {"pro": pro.total, "con": con.total}, "winner": winner},
        sys.stdout,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
