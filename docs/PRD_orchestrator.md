# Per-Mechanism PRD — DebateOrchestrator

**Component:** `src/agent_debate/orchestration/orchestrator.py`
**Version:** 1.00
**Owns:** `Watchdog`, `LifecycleRegistry`, shared spend `Value` + `Lock`
**Spawns:** 3× `multiprocessing.Process` children (Judge + Pro + Con)

---

## Building-block docstring

```python
class DebateOrchestrator:
    """
    Input:  config (Config), llm_provider_factory (Callable),
            search_provider_factory (Callable), lifecycle_registry (LifecycleRegistry)
    Output: Transcript (debate record + verdict + spend)
    Setup:  watchdog (Watchdog, lazily constructed),
            shared_spend (Value, created on spawn),
            lock (Lock, created on spawn),
            queue_capacity (int, from config, default: 100)
    """
```

---

## 1. Theoretical background

The Orchestrator embodies the **Father+children process model** the lecturer described in Lec05 L1281-1297: *"I expect you to write a process for the main supervisor, a process for opponent A, opponent B, and that they manage and things work."* It is the **only** layer that touches process boundaries; everything above it (SDK, Menu) is purely in-process Python.

It also owns the `LifecycleRegistry` — the 8 hooks (rubric §A9) that constitute the extension surface HW1 was rated weak on. Hooks fire at well-defined boundaries (`before_round`, `after_round`, `before_verdict`, `after_verdict`, `before_llm_call`, `after_llm_call`, `before_search`, `after_search`); new behavior plugs in via `registry.register(name, fn)` with no core-code edit.

The Orchestrator is also the deliberate location for **two-phase boot** (H18): Phase A issues `setup_directive`s and awaits 2× `ack`; Phase B opens the debate loop. The Orchestrator owns the synchronization barrier between phases.

---

## 2. Functional requirements

| H-gate / R-gate | Behavior |
|---|---|
| **H4** | Children's `out_queue` is connected to Judge's `in_queue` only; Orchestrator owns the topology |
| **H18** | Orchestrator drives Phase A (issue setup_directives, await both acks) before opening Phase B |
| **H21** | Orchestrator constructs and starts `Watchdog`; routes child-death events through it |
| **R1** | Orchestrator is invoked ONLY by `DebateSDK`; never directly by menu/tests |
| **R3** | `llm_provider_factory` and `search_provider_factory` injected at construction — no direct provider knowledge |
| **R5** | FIFO queues with `queue_capacity` from config; raises `QueueFull` on overflow (caught by Gatekeeper backpressure) |
| **§A9** | All 8 lifecycle hooks registered before Phase A begins |

---

## 3. Performance metrics

| Metric | Target |
|---|---|
| Spawn-children latency | ≤ 1 s for 3 processes |
| Phase A duration (setup + 2 acks) | ≤ 2 s |
| Total debate runtime | ≤ 10 min for 10 pings/side |
| Transcript persistence | ≤ 200 ms |
| Graceful shutdown cascade | ≤ 12 s (SIGTERM + 10s drain + SIGKILL + flush) |

---

## 4. Alternatives considered

| Alternative | Rejected because |
|---|---|
| `subprocess.Popen` per agent + stdin/stdout JSON-lines | ADR-001 chose mp.Queue — lecturer's most-named primitive |
| `asyncio` coroutines instead of OS processes | Spec §8.1 specifically demands process-level isolation: *"שני סוכנים = שני תהליכים"* |
| Single shared queue (broadcast) instead of 6 in/out queues | Broadcast complicates H4 routing audit; per-pair queues make topology obvious |
| Lifecycle hooks fired by agents (decentralized) | Centralization in Orchestrator gives one canonical ordering, simplifies tests |

---

## 5. Test scenarios

| # | Test | File | Verifies |
|---|---|---|---|
| 1 | `spawn_children()` returns 3 alive Process objects | `test_orchestrator.py` | Process-level isolation |
| 2 | All 8 lifecycle hooks fire in correct order during a debate | `test_orchestrator.py` | §A9 |
| 3 | Phase B does NOT start until both acks received | `test_setup_directive_ack.py` | H18 |
| 4 | Transcript persisted to `transcripts/<id>.json` after verdict | `test_full_debate_mocked.py` | Acceptance #5 |
| 5 | Ctrl+C → all 3 children exit cleanly within 10s | `test_graceful_shutdown.py` | Reliability |
| 6 | Children's queues never connect Pro↔Con directly | `test_full_debate_mocked.py` | H4 |

---

## 6. Cross-references

- **Spec:** §1 architecture, §4 data flow (two-phase boot)
- **PLAN:** §2.2 C2 container diagram, §10 startup sequence, §11 ADR-001
- **Related PRDs:** `PRD_watchdog.md` (owned), `PRD_ipc_bus.md` (Queues topology)
