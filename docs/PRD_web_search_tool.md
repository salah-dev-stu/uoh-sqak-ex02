# Per-Mechanism PRD — WebSearchTool

**Components:**
- `src/agent_debate/tools/search_provider.py` (ABC + `SearchHit` DTO)
- `src/agent_debate/tools/duckduckgo_provider.py` (default concrete)
- `src/agent_debate/tools/mock_search_provider.py` (test fixture)
- `src/agent_debate/tools/web_search.py` (the wrapper with fallback)

**Version:** 1.00

---

## Building-block docstring

```python
class WebSearchTool:
    """
    Input:  query (str), k (int, default: 5)
    Output: list[SearchHit] (url, snippet, rank) — may be empty
    Setup:  provider (SearchProvider — injected, plug-in pattern),
            fallback_citations_path (Path | None) — used when provider rate-limits
    """
    def search(self, query, k=5) -> list[SearchHit]: ...
    def _load_fallback(self, k) -> list[SearchHit]: ...
```

---

## 1. Theoretical background

H6 (lec05 L1233-1239) makes web search a **graded enforcement gate**: *"חיפוש חייב להיות, כדי שלא יהיה בעיות בבדיקה"* — *"search MUST exist, so there are no problems in grading."* Absent web search = automatic point loss.

H24 (lec05 L1483-1491) gives the tool a **dual purpose**: agents cite their OWN evidence and fact-check OPPONENT'S claims. The Pro/Con skills authorize both usages; the tool itself is purpose-agnostic — it just returns hits.

**ADR-004** chose DuckDuckGo as the default because it requires no API key — the grader can clone the repo and run a debate without provisioning anything. The `SearchProvider` ABC keeps Brave / Tavily / Perplexity available as one-adapter swap-ins, which is the HW1-extensibility fix.

**Rate-limit fallback** is a defensive feature: DDG aggressively rate-limits aggregators. When `DuckDuckGoProvider` raises `SearchRateLimited`, the `WebSearchTool` falls back to a pre-seeded `references/citations.md` file from the calling Skill — graceful degradation that keeps debates moving even when the live search is throttled.

---

## 2. Functional requirements

| H-gate / R-gate | Requirement |
|---|---|
| **H6** | Web-search tool exists and is invoked during debate |
| **H24** | Tool serves dual purpose (citation + fact-check); invocation is Skill-driven |
| **R3** | Search calls flow through `ApiGatekeeper.execute()` |
| **R4** | DDG rate limits (requests/min, requests/hour) sourced from `config/rate_limits.json` |
| **§12.1** | Plug-in pattern — `SearchProvider` ABC + factory registry; new providers register without core-code edits |

---

## 3. SearchHit DTO

```python
@dataclass(frozen=True)
class SearchHit:
    url: str       # validated by message schema citation.url field
    snippet: str   # max 500 chars (truncated if longer)
    rank: int      # 0-based, matches DDG result order
```

---

## 4. Performance metrics

| Metric | Target |
|---|---|
| Per-query latency (DDG happy path) | ≤ 3 s |
| Per-query latency (cached fallback) | ≤ 50 ms |
| Hits returned per query | k (default 5); may be < k on sparse topics |
| Rate-limit fallback rate (steady state) | ≤ 10% of queries |
| Empty-result rate (no hits) | ≤ 5% |

---

## 5. Rate-limit fallback specification

When `DuckDuckGoProvider.search()` raises `SearchRateLimited`:

1. `WebSearchTool.search()` catches the exception
2. Calls `_load_fallback(k)` which reads `fallback_citations_path`
3. Parses lines matching `(https?://\S+)\s*[—-]\s*(.+)` from the markdown bullet list
4. Returns up to `k` `SearchHit` entries
5. Logs `event="search_fallback_used"` at WARN level

The Skill author is responsible for seeding `references/citations.md` with 6+ high-quality bullets. This ensures the debate can proceed even when DDG is throttled.

---

## 6. Alternatives considered

| Alternative | Rejected because |
|---|---|
| Brave Search API as default | Requires API key signup — friction for grader |
| Tavily as default | $0.01/query + key requirement |
| Perplexity SDK as default | Same key requirement |
| No fallback (hard fail on rate-limit) | Debate would abort on flaky network — poor UX |
| LLM-generated citations (no real web call) | H6 explicit — *"a tool of internet search is mandatory"* |
| Cache live results (not just fallback) | Over-complicates the design; DDG is cheap enough at our query rate |

---

## 7. Test scenarios

| # | Test | File | Verifies |
|---|---|---|---|
| 1 | DDG happy path returns parsed SearchHits | `test_duckduckgo_provider.py` | Happy path |
| 2 | DDG 0 results → empty list | `test_duckduckgo_provider.py` | Edge case |
| 3 | DDG raises `Ratelimit` → `SearchRateLimited` | `test_duckduckgo_provider.py` | Detection |
| 4 | `WebSearchTool` happy path with MockSearchProvider | `test_web_search.py` | Wrapper |
| 5 | `WebSearchTool` falls back to citations.md on rate-limit | `test_web_search.py` | Fallback |
| 6 | Fallback parses URL + snippet from markdown bullet | `test_web_search.py` | Parser |
| 7 | E2E — Pro cites, Con fact-checks; both citation arrays populated | `test_real_search_dual.py` | H24 |

---

## 8. Cross-references

- **Spec:** §3 (tools layer)
- **PLAN:** §11 ADR-004 (search pluggable)
- **Rubric:** §A19 (lies-allowed → opponent catches via search)
- **Related:** `PRD_gatekeeper.md` (rate-limit enforcement), `PRD_pro_agent.md` + `PRD_con_agent.md` (consumers)
