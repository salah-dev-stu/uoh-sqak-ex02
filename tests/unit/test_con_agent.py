"""ConAgent — confirm class constants only (logic is on PartisanAgent)."""
from agent_debate.agents.con_agent import ConAgent
from agent_debate.constants import Stance


def test_stance_is_remix_only():
    assert ConAgent.STANCE == Stance.REMIX_ONLY


def test_skill_name_is_con_skill():
    assert ConAgent.SKILL_NAME == "con_skill"
