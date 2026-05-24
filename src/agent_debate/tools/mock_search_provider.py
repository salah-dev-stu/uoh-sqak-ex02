"""Mock search provider returning fixed SearchHit lists. No network."""
from __future__ import annotations

from agent_debate.tools.search_provider import SearchHit, SearchProvider


class MockSearchProvider(SearchProvider):
    """
    Input:  query (str), k (int)
    Output: fixed list[SearchHit] (slicing by k)
    Setup:  hits (list[SearchHit], optional)
    """

    def __init__(self, hits: list[SearchHit] | None = None) -> None:
        self.hits = hits or [
            SearchHit(url="https://mock.test/1", snippet="mock snippet 1", rank=0),
        ]

    def search(self, query: str, k: int = 5) -> list[SearchHit]:
        return self.hits[:k]
