# ADR-006: Cross-process token-spend tracking via `multiprocessing.Value` + `Lock`

**Status:** Accepted — 2026-05-25

## Context

The token budget is a **global** invariant: 200,000 tokens per debate (`config/rate_limits.json`), 75% warn, 95% hard cap. The Gatekeeper enforces it.

But each child process (Judge / Pro / Con) has its own `ApiGatekeeper` instance running in its own address space. If each Gatekeeper had its own private counter, three independent Gatekeepers could each "approve" calls up to their own 95% threshold — collectively busting the global cap by 3× in the worst case.

We need a single source of truth that all three Gatekeepers consult.

## Decision

Create the spend counter in the **main process** using `multiprocessing.Value("i", 0)` and `multiprocessing.Lock()`. Inject **both** into each child process at spawn time. Every child's `ApiGatekeeper` reads from and writes to the same shared memory location, with the lock protecting the read-modify-write.

```python
# In Orchestrator
shared_spend = Value("i", 0)
lock = Lock()
# pass into each Process kwargs
Process(target=run_agent, kwargs={..., "shared_spend": shared_spend, "lock": lock})
```

```python
# In each Gatekeeper
def update_spend(self, tokens):
    with self.lock:
        self.shared_spend.value += tokens
def get_spend_so_far(self) -> int:
    with self.lock:
        return self.shared_spend.value
```

## Alternatives considered

| Alternative | Rejected because |
|---|---|
| Per-child counter (no shared state) | Allows independent cap violation — could bust budget 3× |
| Pipe-based aggregator (each child sends spend to main, main aggregates) | Adds latency to every LLM call; main becomes a hot path |
| Database-backed counter (SQLite) | Massive overkill; SQLite write lock is the same primitive, more complex |
| `threading.Lock` + threading model | Not applicable — children are processes, not threads |

## Consequences

### Positive

- True global budget enforcement.
- Lock-hold duration is <1 ms (just an integer increment) — no contention impact.
- Simple, debuggable.

### Negative

- All three children acquire the same lock on every LLM call. **Mitigation:** lock hold is tiny; no perf issue at our scale.
- Adds a parameter to every spawn signature. **Mitigation:** `Orchestrator.spawn_children()` is the only caller; complexity is local.

## Verification

- `tests/unit/test_gatekeeper.py::test_get_spend_so_far_reflects_shared_value` — verifies the spend Value is the single source
- `tests/unit/test_gatekeeper.py::test_budget_above_hard_cap_raises` — verifies cap enforcement happens against the shared counter
- `tests/integration/test_budget_exhausted.py` — full debate ending early at 95% threshold
