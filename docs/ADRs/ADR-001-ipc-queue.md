# ADR-001: IPC mechanism — `multiprocessing.Queue` over Signal / FIFO / Socket

**Status:** Accepted — 2026-05-25
**Deciders:** Salah Qadah (with Claude Opus 4.7 as design partner)
**Cross-reference:** `docs/PLAN.md` §11

---

## Context

Lec05 L399 enumerates four IPC primitives the lecturer expects students to know — Signal, FIFO/Pipe, Queue, Sockets. The HW2 spec requires inter-process communication between three child processes (Judge + Pro + Con) routing through a parent. The chosen mechanism must:

- Match the lecturer's named expectation (Signal/FIFO/Queue/Socket).
- Work cross-platform (macOS for development, Linux on CI).
- Be thread-safe / process-safe by construction.
- Survive ≥5 minutes of high-throughput JSON messaging without OOM.
- Be testable in isolated unit tests (not requiring a real OS daemon).

## Decision

Use **`multiprocessing.Queue`** for all inter-process messaging. Use `multiprocessing.Value("i", 0)` + `multiprocessing.Lock()` for the shared token-spend counter (see ADR-006). Use `signal.SIGTERM` for graceful shutdown (one of the four primitives, used minimally) — so the implementation touches **Signal + Queue** (2 of 4 primitives).

## Alternatives considered

| Alternative | Rejected because |
|---|---|
| Signal-only custom protocol (`os.kill(pid, SIGUSR1)` + shared file) | Brittle; no payload support beyond signal number; would need a side-channel for JSON. |
| POSIX FIFOs (`os.mkfifo`) | Works on Unix; Windows-WSL portability quirks; lower-level than necessary for our usage. |
| `subprocess.Popen` + stdin/stdout JSON-lines | Simpler debugging but doesn't fit the lecturer's "Signal/FIFO/Queue/Sockets" enumeration cleanly; less idiomatic for multi-process Python. |
| Unix-domain sockets (`socket.AF_UNIX`) | Fastest IPC option; macOS portability quirks; rejected to keep the system cross-platform without conditional code paths. |
| `asyncio` coroutines instead of OS processes | Spec §8.1 specifically demands process-level isolation: *"שני סוכנים = שני תהליכים"*. |

## Consequences

### Positive

- Cross-platform out of the box.
- Thread-safe and process-safe by construction (CPython's `mp.Queue` uses a pipe + lock under the hood).
- Trivial to instantiate in unit tests: `multiprocessing.Queue()` in a fixture.
- Lecturer pattern-matches "Queue" as one of the four named primitives.

### Negative

- Only demonstrates **one** of the four IPC primitives. **Mitigation:** this ADR enumerates all four with rationale; signals are used for SIGTERM shutdown, so the implementation effectively touches 2 of 4.
- `mp.Queue` has slight serialization overhead (pickling). At our message rate (~1 msg/s in steady state), this is negligible.

## Verification

- `tests/integration/test_full_debate_mocked.py` — end-to-end with real `mp.Process` + `mp.Queue`.
- `tests/integration/test_chaos_child_kill.py` — verifies SIGKILL propagation works.
- `tests/integration/test_graceful_shutdown.py` — verifies SIGTERM cascade.
