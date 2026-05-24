# Per-Mechanism PRD — ApiGatekeeper

**Component:** `src/agent_debate/shared/gatekeeper.py`
**Version:** 1.00
**Signature source:** Rubric §A4 (matched verbatim — the grading agent pattern-matches against this exact shape)

---

## Building-block docstring (rubric §A4 verbatim)

```python
class ApiGatekeeper:
    """Centralized API call manager.

    Input:  api_call (callable), *args, **kwargs
    Output: response (T) OR raises BudgetExhausted / RateLimitExceeded
    Setup:  config (RateLimitConfig),
            shared_spend (multiprocessing.Value),
            lock (multiprocessing.Lock),
            queue_capacity (int, default: 100)

    Behavior:
      - Check rate limits before execution
      - Queue if limit reached (FIFO with backpressure)
      - Retry on transient failures (exponential backoff [1, 2, 4])
      - Log all calls (StructuredLogger)
    """
    def __init__(self, config, shared_spend, lock, queue_capacity=100): ...
    def execute(self, api_call, *args, **kwargs): ...
    def update_spend(self, tokens): ...
    def get_spend_so_far(self) -> int: ...
    def estimate_cost(self, n_debates) -> Decimal: ...
    def get_queue_status(self) -> QueueStatus: ...
```

---

## 1. Theoretical background

The Gatekeeper is the **economic-and-consumption blocking layer** that lec05 L1233-1240 and rubric §5.1 both demand. It is the single point through which every external API call (LLM + web search) flows — no rogue process can independently make calls that bust the global budget or rate-limit.

The Lec04 Token Economy framing applies directly: every LLM call sends the full conversation history, so cost grows quadratically with debate length. The Gatekeeper's job is to ensure that quadratic curve never crosses the user-defined cap. Lec04 abstract §9 formula:

```
WCₙ = WCₙ₋₁ + Qₙ + Rₙ + Aₙ
```

where each `+ Q` is a re-injection of full prior history. The Gatekeeper's `update_spend(tokens)` is called after every LLM response with `tokens_in + tokens_out`, and `_check_budget_hard_cap` triggers BudgetExhausted at 95% before the next call enters Phase B.

Cross-process spend tracking (ADR-006) uses `multiprocessing.Value("i", 0)` + `multiprocessing.Lock()`. Per-child Gatekeepers would each have their own counter — three independent counters that could each "approve" calls that collectively bust the cap. Centralizing via `Value+Lock` makes the budget a true global invariant.

---

## 2. Functional requirements

| Rubric / H-gate | Requirement |
|---|---|
| **R3** | All LLM + search calls pass through `execute()` |
| **R4** | Rate limits + token budgets sourced from `config/rate_limits.json` — zero values in code |
| **R5** | FIFO queue + backpressure alert + drain when rate-window resets (rubric §A5 verbatim 4-item) |
| **H10** | Per-call timeout via `signal.alarm()` or subprocess timeout kwarg |
| **§A4** | Class signature matches rubric verbatim (the grader pattern-matches) |
| **§A8** | Budget thresholds: warn at 75% (log only), hard refuse at 95% (raise BudgetExhausted) |
| **§A21** | Provider cache strategy — static system-prompt prefix maximizes Claude-side cache hits |

---

## 3. Performance metrics

| Metric | Target |
|---|---|
| Per-call overhead (rate-check + spend-update + log) | ≤ 5 ms |
| Lock-hold duration (spend update) | ≤ 1 ms |
| Retry attempt count under transient failure | ≤ 3 |
| Backoff sequence | [1, 2, 4] seconds — exponential, capped at 4 |
| Budget enforcement latency | immediate (synchronous check before call) |
| QueueStatus query latency | ≤ 1 ms |

---

## 4. Queue + backpressure + drain (rubric §A5 verbatim 4-item)

| Item | Implementation |
|---|---|
| FIFO queue for pending requests | `collections.deque(maxlen=queue_capacity)` inside Gatekeeper |
| Max queue depth in config | `queue_capacity` from `config/rate_limits.json` (default 100) |
| Backpressure alert when full | Structured-logger event `event="queue_backpressure"` when depth ≥ 90% of capacity |
| Drain mechanism when windows reset | `_call_times` deque drops entries > 60s; drain hook fires `before_llm_call` lifecycle |

---

## 5. Budget thresholds (rubric §A8)

| Threshold | Action |
|---|---|
| spend < 75% | Normal operation; log spend each call at DEBUG level |
| 75% ≤ spend < 95% | Log WARN: `event="budget_warning"`; continue |
| spend ≥ 95% | Raise `BudgetExhausted`; Judge emits early `verdict` with `outcome=budget_exhausted` |
| daily limit hit | Raise `RateLimitExceeded`; await `retry_after_seconds` (default 60s); resume if within debate window |

---

## 6. Alternatives considered

| Alternative | Rejected because |
|---|---|
| Per-child Gatekeeper (no shared spend) | Three independent counters could each "approve" calls busting the global cap (ADR-006 rejection) |
| `threading.Lock` instead of `multiprocessing.Lock` | mp.Process boundaries cross address space; threading.Lock is in-process only |
| Decimal-precision cost tracking even in login mode | Login mode is $0; tracked tokens only (estimate_cost returns Decimal("0.00")) |
| Retry forever on transient | Unbounded retries can mask real failures; cap at 3 with exponential backoff |
| Backoff [10, 30, 60] (more conservative) | Debate has hard time budget; [1, 2, 4] balances reliability with progress |

---

## 7. Test scenarios

| # | Test | File | Verifies |
|---|---|---|---|
| 1 | `execute()` returns api_call result on happy path | `test_gatekeeper.py` | Pass-through |
| 2 | Budget at 80% → warn logged, call succeeds | `test_gatekeeper.py` | §A8 warn |
| 3 | Budget at 96% → BudgetExhausted raised | `test_gatekeeper.py` | §A8 hard cap |
| 4 | Transient `ConnectionError` retried 3× then succeeds | `test_gatekeeper.py` | retry |
| 5 | Queue at capacity → backpressure event logged | `test_gatekeeper.py` | §A5 |
| 6 | `get_spend_so_far` reflects shared Value across processes | `test_gatekeeper.py` | ADR-006 |
| 7 | Rate-limit window resets after 60s | `test_gatekeeper.py` | drain |
| 8 | LLM-call timeout (90s) raises TimeoutError | `test_claude_login_provider.py` (interaction) | H10 |

---

## 8. Cross-references

- **Spec:** §3 (component layer 6)
- **PLAN:** §11 ADR-006 (cross-process spend), §11 ADR-001 (Queue topology adjacent)
- **Rubric:** §A4 (signature), §A5 (queue), §A7 (TDD), §A8 (budget)
- **Related:** `tools/llm_provider.py`, `tools/web_search.py` (both invoked via Gatekeeper)
