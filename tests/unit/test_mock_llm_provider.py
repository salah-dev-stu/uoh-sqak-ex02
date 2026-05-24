"""MockLLMProvider — offline test fixture."""
from agent_debate.tools.mock_llm_provider import MockLLMProvider


def test_returns_canned_response_by_key():
    provider = MockLLMProvider(responses={
        ("pro", 1): "Cats are original art.",
        ("con", 1): "No they remix mice.",
    })
    resp = provider.complete(system="pro_skill stuff", user="round 1", temperature=0.85)
    assert isinstance(resp.text, str)


def test_default_response_on_unknown_key():
    provider = MockLLMProvider(responses={}, default_text="(mock)")
    resp = provider.complete(system="unknown_skill", user="x", temperature=0.7)
    assert resp.text == "(mock)"
    assert resp.finish_reason == "stop"


def test_call_counter_increments():
    provider = MockLLMProvider(responses={})
    provider.complete(system="pro stuff", user="a", temperature=0.5)
    provider.complete(system="pro stuff", user="b", temperature=0.5)
    assert provider._call_counts.get("pro") == 2
