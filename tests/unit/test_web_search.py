"""WebSearchTool wraps SearchProvider with rate-limit fallback to cached citations."""
from pathlib import Path

from agent_debate.tools.duckduckgo_provider import SearchRateLimited
from agent_debate.tools.mock_search_provider import MockSearchProvider
from agent_debate.tools.search_provider import SearchHit, SearchProvider
from agent_debate.tools.web_search import WebSearchTool


def test_search_returns_hits():
    provider = MockSearchProvider(hits=[
        SearchHit(url="https://x.test", snippet="hi", rank=0),
    ])
    tool = WebSearchTool(provider=provider)
    hits = tool.search("query", k=5)
    assert len(hits) == 1
    assert hits[0].url == "https://x.test"


def test_search_falls_back_on_rate_limit(tmp_path: Path):
    class RateLimitedProvider(SearchProvider):
        def search(self, query: str, k: int = 5) -> list[SearchHit]:
            raise SearchRateLimited("test")

    fallback_md = tmp_path / "citations.md"
    fallback_md.write_text(
        "- https://cached.test/a — cached snippet a\n"
        "- https://cached.test/b — cached snippet b\n",
        encoding="utf-8",
    )
    tool = WebSearchTool(provider=RateLimitedProvider(), fallback_citations_path=fallback_md)
    hits = tool.search("query", k=5)
    assert len(hits) >= 1
    assert any("cached.test" in h.url for h in hits)


def test_no_fallback_returns_empty_on_rate_limit():
    class RateLimitedProvider(SearchProvider):
        def search(self, query: str, k: int = 5) -> list[SearchHit]:
            raise SearchRateLimited("test")

    tool = WebSearchTool(provider=RateLimitedProvider(), fallback_citations_path=None)
    hits = tool.search("query", k=5)
    assert hits == []
