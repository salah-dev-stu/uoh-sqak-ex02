"""Abstract search provider. Concrete: DuckDuckGoProvider, MockSearchProvider."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class SearchHit:
    url: str
    snippet: str
    rank: int


class SearchProvider(ABC):
    """
    Input:  query (str), k (int)
    Output: list[SearchHit] (may be empty)
    Setup:  (subclass-specific)
    """

    @abstractmethod
    def search(self, query: str, k: int = 5) -> list[SearchHit]:
        ...
