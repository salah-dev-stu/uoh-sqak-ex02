"""ConAgent — loads con_skill, stance is AI=REMIX_ONLY."""
from __future__ import annotations

from agent_debate.agents.partisan_agent import PartisanAgent
from agent_debate.constants import Stance


class ConAgent(PartisanAgent):
    """
    Setup:  STANCE = Stance.REMIX_ONLY
            SKILL_NAME = "con_skill"
    """

    STANCE = Stance.REMIX_ONLY
    SKILL_NAME = "con_skill"
