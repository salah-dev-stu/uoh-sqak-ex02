"""PartisanAgent — skill loader, opponent-reference enforcer, citation extractor."""
from __future__ import annotations

from multiprocessing import Lock, Queue, Value
from pathlib import Path

from agent_debate.agents.partisan_agent import PartisanAgent
from agent_debate.constants import AgentRole, Stance
from agent_debate.tools.mock_llm_provider import MockLLMProvider


class _TestPartisan(PartisanAgent):
    STANCE = Stance.ORIGINALITY
    SKILL_NAME = "pro_skill"

    def handle_message(self, msg: dict) -> dict | None:
        return None


def _make(skill_dir: str) -> _TestPartisan:
    return _TestPartisan(
        role=AgentRole.PRO,
        in_queue=Queue(),
        out_queue=Queue(),
        heartbeat_queue=Queue(),
        shared_spend=Value("i", 0),
        lock=Lock(),
        skill_dir=skill_dir,
        llm_provider=MockLLMProvider(),
    )


def test_load_skill_body_strips_frontmatter(tmp_path: Path):
    skill = tmp_path / "pro_skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: pro\ndescription: ai\n---\n# Pro Body\nargue originally.",
        encoding="utf-8",
    )
    agent = _make(str(tmp_path))
    body = agent.load_skill_body()
    assert body.startswith("# Pro Body")
    assert "name: pro" not in body


def test_opponent_reference_passes_with_overlap():
    agent = _make("/tmp")
    prev = "Stochastic parrots merely remix training data sources."
    text = "The parrots argument ignores latent training combinations."
    assert agent.enforce_opponent_reference(text, prev) is True


def test_opponent_reference_fails_without_overlap():
    agent = _make("/tmp")
    prev = "Christie's auction validated AI-generated art."
    text = "Cats are nice animals today."
    assert agent.enforce_opponent_reference(text, prev) is False


def test_extract_citations_finds_urls_and_snippets():
    agent = _make("/tmp")
    text = "See https://example.com/foo for the auction context, also https://x.org/bar."
    cites = agent.extract_citations(text)
    assert len(cites) == 2
    assert cites[0]["url"] == "https://example.com/foo"
    assert "auction" in cites[0]["snippet"]
    assert cites[1]["url"] == "https://x.org/bar"


def test_extract_citations_returns_empty_on_no_urls():
    agent = _make("/tmp")
    assert agent.extract_citations("plain text with no links here") == []
