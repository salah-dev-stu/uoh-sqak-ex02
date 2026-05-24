# Per-Mechanism PRD — IPC Bus (Queues + Wire Protocol)

**Components:**
- `config/schemas/message-1.00.json` (the wire protocol)
- `src/agent_debate/shared/message_schema.py` (Message dataclass + validator)
- Queue topology owned by `DebateOrchestrator`

**Version:** 1.00

---

## Building-block docstring (Message dataclass)

```python
@dataclass(frozen=True)
class Message:
    """
    Input:  dict (parsed JSON; validated against config/schemas/message-1.00.json)
    Output: Message (frozen dataclass — immutable wire-protocol record)
    Setup:  msg_id (UUID), schema_version ('1.00'),
            from_role / to_role (AgentRole),
            role (MessageRole — one of 8),
            ping_index (int ≥ 0),
            text (str ≤ 4000),
            timestamp (ISO-8601),
            references_opponent (bool | None),
            citations (list[dict] — url + snippet),
            scoring (dict with 5 axes × 0–20, optional),
            tokens_in (int | None), tokens_out (int | None)
    """
```

---

## 1. Theoretical background

Lec05 L1437-1444 verbatim: *"ההמלצה שלי זה ג'ייסונים… ג'ייסונים זה תבניות"* — *"My recommendation is JSONs… JSONs are templates."* This phrase ties the wire protocol directly to Dr. Segal's Lec04 thesis (the LLM-as-text-to-template converter): every inter-agent message is a **template** that downstream consumers (Judge, Orchestrator, ScoringEngine, logger) can deterministically parse. No free-text-only channels exist.

Per-message validation happens on BOTH **send and recv** — defense in depth. A child might emit malformed JSON (LLM hallucination); the sender's `validate_message` catches it before queue insertion. A producer might also corrupt a payload (memory bug); the receiver's `validate_message` catches that too.

The Queue topology — 6 in/out queues + 1 heartbeat queue — is designed for the H4 audit: a static topology where `pro.out_queue` connects only to `judge.in_queue` (and vice-versa) makes the "all traffic through Judge" invariant obvious at the wiring level, not just at the runtime-routing level.

---

## 2. Functional requirements

| H/R-gate | Requirement |
|---|---|
| **H2** | All inter-agent messages serialize as JSON |
| **H4** | Pro↔Con direct queues do NOT exist; only `judge.in_queue` for incoming, `judge.out_queue` for outgoing |
| **R5** | Queues are FIFO; bounded `queue_capacity`; backpressure on overflow (Gatekeeper layer enforces) |
| **R6** | Schema versioned at 1.00; future shape changes bump to 1.01 etc. |
| **§A22** | jsonschema validation on send AND recv |
| **N5** | Schema captures `references_opponent: bool` — mandatory for H7 mutual-reference enforcement |

---

## 3. Eight message roles

| Role | Direction | Phase | Carries | Producer | Consumer |
|---|---|---|---|---|---|
| `setup_directive` | Judge → child | Boot | stance + rules + format | JudgeAgent | Pro/Con BaseAgent |
| `ack` | child → Judge | Boot | "ready" confirmation | Pro/Con | JudgeAgent (Phase-A barrier) |
| `argument` | child → Judge | Debate (odd pings) | new debate turn | Pro/Con | JudgeAgent.route() |
| `counter` | child → Judge | Debate (even pings) | rebuttal | Pro/Con | JudgeAgent.route() |
| `correction_request` | Judge → child | Drift detected (H20) | replay request + reason | JudgeAgent.DriftDetector | Pro/Con |
| `intervention` | Judge → child | PC violation (H16) | sanitization + replay | JudgeAgent.PCFilter | Pro/Con |
| `status` | any → main | Continuous | heartbeat ping + progress | All agents | Watchdog |
| `verdict` | Judge → main | End (H5) | scorecards + winner | JudgeAgent.ScoringEngine | DebateOrchestrator |

---

## 4. Performance metrics

| Metric | Target |
|---|---|
| `validate_message` latency | ≤ 5 ms (jsonschema compiled once) |
| Queue `put` / `get` latency | ≤ 1 ms (mp.Queue native) |
| Bytes per message (typical) | ≤ 3 KB (250-word text + ≤3 citations) |
| Queue depth in steady state | ≤ 5 messages |
| Schema-validation failures during a normal debate | 0 |

---

## 5. Alternatives considered

| Alternative | Rejected because |
|---|---|
| Protobuf for wire protocol | JSON is human-readable, trivial to debug, lecturer's stated preference (lec05) |
| MessagePack | Same readability argument; jsonschema tooling is mature |
| Validate only on receive (skip send-side check) | Defense-in-depth principle; cheap check catches LLM hallucinations early |
| Single broadcast queue | Complicates H4 audit; per-pair queues make routing topology static + obvious |
| Direct child-to-child queue if Judge "approves" | Spec §8.3 rule 7 is unconditional: *"לא ישירות בין הילדים"* |

---

## 6. Test scenarios

| # | Test | File |
|---|---|---|
| 1 | All 8 message roles validate against schema | `test_message_schema.py` |
| 2 | Invalid role → jsonschema rejection | `test_message_schema.py` |
| 3 | Missing required field → rejection | `test_message_schema.py` |
| 4 | Message dataclass round-trips dict ↔ Message via from_dict/to_dict | `test_message_schema.py` |
| 5 | Pro's out_queue is wired to Judge's in_queue (topology check) | `test_orchestrator.py` |
| 6 | No Pro→Con direct message during full debate | `test_full_debate_mocked.py` |
| 7 | Queue overflow triggers backpressure event in Gatekeeper | `test_gatekeeper.py` |

---

## 7. Cross-references

- **Spec:** §4 data flow + JSON wire protocol
- **PLAN:** §5, §8.1 (configuration architecture)
- **ADR-001:** IPC mechanism = mp.Queue
- **Related PRDs:** `PRD_orchestrator.md` (Queue topology owner), `PRD_gatekeeper.md` (backpressure enforcement)
