"""ProAgent — confirm class constants only (logic is on PartisanAgent)."""
from agent_debate.agents.pro_agent import ProAgent
from agent_debate.constants import Stance


def test_stance_is_originality():
    assert ProAgent.STANCE == Stance.ORIGINALITY


def test_skill_name_is_pro_skill():
    assert ProAgent.SKILL_NAME == "pro_skill"
