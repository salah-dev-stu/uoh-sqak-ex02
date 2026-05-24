"""DuckDuckGoProvider — `ddgs` package shell adapter (no API key)."""
from unittest.mock import patch

import pytest

from agent_debate.tools.duckduckgo_provider import DuckDuckGoProvider, SearchRateLimited


def test_search_returns_hits():
    fake_results = [
        {"href": "https://a.com", "body": "snippet a"},
        {"href": "https://b.com", "body": "snippet b"},
    ]
    provider = DuckDuckGoProvider()
    with patch("agent_debate.tools.duckduckgo_provider.DDGS") as mock_ddgs:
        mock_ddgs.return_value.__enter__.return_value.text.return_value = fake_results
        hits = provider.search("test", k=2)
    assert len(hits) == 2
    assert hits[0].url == "https://a.com"
    assert hits[0].rank == 0


def test_search_returns_empty_on_no_results():
    provider = DuckDuckGoProvider()
    with patch("agent_debate.tools.duckduckgo_provider.DDGS") as mock_ddgs:
        mock_ddgs.return_value.__enter__.return_value.text.return_value = []
        hits = provider.search("test", k=5)
    assert hits == []


def test_rate_limit_raises_custom_exception():
    provider = DuckDuckGoProvider()
    with patch("agent_debate.tools.duckduckgo_provider.DDGS") as mock_ddgs:
        mock_ddgs.return_value.__enter__.return_value.text.side_effect = Exception("Ratelimit")
        with pytest.raises(SearchRateLimited):
            provider.search("test", k=5)
