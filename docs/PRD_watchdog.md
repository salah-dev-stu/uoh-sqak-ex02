# Per-Mechanism PRD — Watchdog

**Component:** `src/agent_debate/orchestration/watchdog.py`
**Version:** 1.00
**Owns:** Heartbeat detection, restart-with-state-replay, fail-fast escalation
**Owned-by:** `DebateOrchestrator`

---

## Building-block docstring

```python
class Watchdog:
    """
    Input:  children (list[Process]), heartbeat_queue (Queue),
            lifecycle_registry (LifecycleRegistry)
    Output: process-health events; restart actions; final unrecoverable signal
    Setup:  poll_interval (float, default: 2.0 s),
            stuck_timeout (float, default: 30.0 s),
            max_restarts (int, default: 3),
            restart_backoff (list[float], default: [1, 2, 4])
    """
    def monitor(self) -> None: ...
    def _is_stuck(self, child) -> bool: ...
    def _restart(self, child, restart_idx) -> Optional[Process]: ...
    def _on_unrecoverable(self, child) -> None: ...
```

---

## 1. Theoretical background

The Watchdog implements H21 — *"You need watchdogs on your processes… set KPI to see the thing is alive and working, and if it gets stuck, kill the process and restart it"* (Lec05 L1302-1314). It's the reliability backbone that lets chaos-test scenarios (kill -9 mid-debate) recover instead of crashing the run.

**Two-signal detection** is the key design choice (PRD risk-register Open Question 1): an `is_alive()` poll catches *crashed* children (process died, exit code present), but misses *hung* children (process alive, but main thread stuck). Heartbeat staleness catches the latter. Either signal indicating failure triggers restart.

**State replay** preserves debate continuity. When a child is restarted, the new Process gets:
1. The same `shared_spend` Value + Lock (so budget tracking continues)
2. The same `skill_dir` path (so it reloads the same Skill)
3. The most-recent `setup_directive` from the in-memory transcript (so it boots into `[WAITING_TURN]` instead of `[INIT]`)

**Two-thread-per-child contract** (PLAN.md §9) resolves the heartbeat-vs-LLM-timeout interaction: each child runs (a) a main thread that emits heartbeats every 2 s + handles message I/O, and (b) a worker thread that handles the (up to 90 s) LLM call. The Watchdog's `stuck_timeout=30 s` therefore only fires when the **main thread** is hung — not when the LLM call is just slow.

---

## 2. Functional requirements

| H-gate | Requirement |
|---|---|
| **H9** | Watchdog with keep-alive — restart on stuck |
| **H21** | Heartbeat KPI; kill + restart on stuck (explicitly graded) |
| **R5** | No crashes on rate-limit / external failure — Watchdog rotates failed children out |
| **R7** | Test-driven: every state transition has at least one test |

---

## 3. Performance metrics

| Metric | Target |
|---|---|
| Heartbeat poll interval | 2.0 s (config-driven) |
| Stuck-detection latency | ≤ stuck_timeout (default 30 s) |
| Restart latency | ≤ restart_backoff[idx] + spawn time (≤ 5 s total) |
| Restart success rate (under chaos test) | 100% within max_restarts=3 |
| False-positive restart rate | 0 — two-signal detection prevents premature SIGKILL |
| Memory overhead | ≤ 50 MB (one heartbeat dict + one transcript snapshot) |

---

## 4. State-replay contract

After a child is restarted, the Orchestrator + Watchdog cooperate to restore state:

1. **Watchdog**: SIGKILL the stuck child; drain its queues; release any pending messages
2. **Watchdog**: Construct new Process with same kwargs (role, skill_dir, queues, shared_spend, lock)
3. **Watchdog**: After child is alive, re-inject the most recent `setup_directive` from transcript
4. **Watchdog**: Wait for the child's `ack` (with 5-s sub-timeout)
5. **Orchestrator**: Resume debate loop at the message that was in-flight when the crash happened

---

## 5. Fail-fast escalation

After `max_restarts=3` for the same child within one debate, the Watchdog calls `_on_unrecoverable(child)`:

1. Stop attempting further restarts
2. Fire `after_round` lifecycle hook with `{event: "unrecoverable", child: <role>}`
3. Instruct Judge to emit a `verdict` with `outcome=debate_aborted` and whatever partial scoring exists
4. Signal main to begin graceful shutdown

This bounds the worst-case behavior: a deterministically-broken child cannot cause an infinite restart loop.

---

## 6. Alternatives considered

| Alternative | Rejected because |
|---|---|
| Single-signal detection (just `is_alive()`) | Misses hung-but-alive failures (e.g., infinite loop, deadlock) |
| Single-signal detection (just heartbeat staleness) | Misses crashed processes (process is dead but heartbeat ages naturally) |
| Restart without state replay | Child boots into `[INIT]` instead of `[WAITING_TURN]` — re-issues setup_directive, doubles message count, breaks ping_index sequencing |
| max_restarts = ∞ (forever) | Risk of infinite loops on deterministic bugs |
| max_restarts = 1 (one strike) | Too aggressive — transient OOM or rate-limit shouldn't end the debate |
| Heartbeat via a Unix socket | macOS portability risk (ADR-004 deferral); Queue is consistent with the rest of the IPC layer |

---

## 7. Test scenarios

| # | Test | File | Verifies |
|---|---|---|---|
| 1 | Healthy child — no restart | `test_watchdog.py` | Idle path |
| 2 | `is_alive() == False` → restart fires | `test_watchdog.py` | Crashed-process detection |
| 3 | Heartbeat stale > 30 s → restart fires | `test_watchdog.py` | Hung-process detection |
| 4 | Backoff sequence [1, 2, 4] respected | `test_watchdog.py` | Restart pacing |
| 5 | State replay re-injects setup_directive | `test_watchdog.py` | Continuity |
| 6 | 4th restart attempt → `_on_unrecoverable` fires | `test_watchdog.py` | Fail-fast |
| 7 | Unrecoverable event → Judge emits debate_aborted verdict | `test_watchdog.py` | Escalation |
| 8 | SIGKILL chaos test → debate completes | `test_chaos_child_kill.py` | End-to-end |
| 9 | Hang chaos test → SIGKILL + restart | `test_chaos_child_hang.py` | End-to-end |

---

## 8. Cross-references

- **Spec:** §5 error handling + Watchdog
- **PLAN:** §9 thread-safety + two-thread-per-child contract
- **PRD:** §12 risk register Open Question 1 resolution
- **Related:** `PRD_orchestrator.md` (owner), `PRD_ipc_bus.md` (heartbeat queue topology)
