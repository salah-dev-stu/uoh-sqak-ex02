# ADR-004: Search provider is pluggable; DuckDuckGo is the default

**Status:** Accepted — 2026-05-25 (locked at Prompt #6)

## Context

Four candidate web-search backends:

1. **DuckDuckGo via `ddgs` package** — no API key, free, rate-limited.
2. **Brave Search API** — better quality; free tier (2000 queries/month) but requires signup.
3. **Tavily AI Search** — LLM-optimized results; $10 free credit; requires key.
4. **Perplexity API** — same friction (key + paid).

H6 makes the tool's presence a graded gate. The choice is between zero-friction (DDG) and better quality with grader-side setup friction.

## Decision

`SearchProvider` is an **abstract base class** with a factory `Registry`. The default concrete adapter is **`DuckDuckGoProvider`** — zero-config, no API key.

The plug-in pattern (HW1 extensibility weak spot fix) means swapping in Brave or Tavily is **one new adapter file + one config-key change**. The plumbing is already in place.

## Alternatives considered

| Alternative | Rejected because |
|---|---|
| Hardcode DDG without ABC | Loses extensibility signal (rubric §12.1 + HW1 weak spot) |
| Brave as default | Grader friction — signup + key provision before running tests |
| Tavily as default | $0.01/query feels wasteful for the grading run; key friction |
| Custom HTTP scraping | Fragile; ToS risk; over-engineered |
| Hybrid (DDG + Brave fallback) | Over-complicates the default path; defer to future-work if DDG rate-limits become a real problem |

## Consequences

### Positive

- Grader can clone repo and run debate with zero external setup.
- `SearchProvider` ABC is the explicit extensibility surface.
- Adding Brave / Tavily / Perplexity later is a single-file change.

### Negative

- DDG rate-limits aggressively. **Mitigation:** `WebSearchTool` falls back to pre-seeded `references/citations.md` (each Skill has 6+ curated citations). Graceful degradation, not failure.
- DDG result quality is lower than paid alternatives. **Mitigation:** for HW2's specific topic (AI art originality), DDG has abundant general-web content.

## Verification

- `tests/unit/test_duckduckgo_provider.py` — happy path, 0 results, rate-limit detection
- `tests/unit/test_web_search.py` — fallback path engages when SearchRateLimited fires
- `tests/e2e/test_real_search_dual.py` — live DDG with real queries, H24 dual-purpose check
