"""DuckDuckGo search provider via the `ddgs` package. No API key required."""
from __future__ import annotations

from ddgs import DDGS

from agent_debate.tools.search_provider import SearchHit, SearchProvider


# N818 disabled below: API name is plan-mandated and consumed by WebSearchTool + tests.
class SearchRateLimited(Exception):  # noqa: N818
    """Raised when DDG rate-limits us; caller should fall back to cached citations."""


class DuckDuckGoProvider(SearchProvider):
    """
    Input:  query (str), k (int)
    Output: list[SearchHit] (may be empty); raises SearchRateLimited on 429
    Setup:  none — DDG requires no API key
    """

    def search(self, query: str, k: int = 5) -> list[SearchHit]:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=k))
        except Exception as exc:
            if "Ratelimit" in str(exc) or "429" in str(exc):
                raise SearchRateLimited(str(exc)) from exc
            raise
        return [
            SearchHit(url=r.get("href", ""), snippet=r.get("body", ""), rank=i)
            for i, r in enumerate(results)
        ]
