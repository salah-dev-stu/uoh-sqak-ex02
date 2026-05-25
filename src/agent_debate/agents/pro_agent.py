"""ProAgent — loads pro_skill, stance is AI=ORIGINALITY."""
from __future__ import annotations

from agent_debate.agents.partisan_agent import PartisanAgent
from agent_debate.constants import Stance


class ProAgent(PartisanAgent):
    """
    Setup:  STANCE = Stance.ORIGINALITY
            SKILL_NAME = "pro_skill"
    """

    STANCE = Stance.ORIGINALITY
    SKILL_NAME = "pro_skill"
