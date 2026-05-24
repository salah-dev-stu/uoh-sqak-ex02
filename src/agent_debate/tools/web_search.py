"""WebSearchTool wraps a SearchProvider with rate-limit fallback to cached citations."""
from __future__ import annotations

import re
from pathlib import Path

from agent_debate.tools.duckduckgo_provider import SearchRateLimited
from agent_debate.tools.search_provider import SearchHit, SearchProvider


class WebSearchTool:
    """
    Input:  query (str), k (int)
    Output: list[SearchHit]
    Setup:  provider (SearchProvider), fallback_citations_path (Path, optional)
    """

    def __init__(
        self, provider: SearchProvider, fallback_citations_path: Path | None = None
    ) -> None:
        self.provider = provider
        self.fallback_path = fallback_citations_path

    def search(self, query: str, k: int = 5) -> list[SearchHit]:
        try:
            return self.provider.search(query, k=k)
        except SearchRateLimited:
            return self._load_fallback(k)

    def _load_fallback(self, k: int) -> list[SearchHit]:
        if not self.fallback_path or not self.fallback_path.exists():
            return []
        lines = self.fallback_path.read_text(encoding="utf-8").splitlines()
        hits: list[SearchHit] = []
        for i, line in enumerate(lines):
            match = re.search(r"(https?://\S+)\s*[—\-]\s*(.+)", line)
            if match and len(hits) < k:
                hits.append(SearchHit(url=match.group(1), snippet=match.group(2), rank=i))
        return hits
