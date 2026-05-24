# HW2 Multi-Agent Debate System — Design Spec

**Status**: Brainstorming complete (2026-05-24 / 25). All sections locked. Ready for user review → writing-plans → formal PRD/PLAN/TODO.
**Authoring agent**: Claude Opus 4.7 via brainstorming skill
**Audit trail**: see `docs/PROMPTS.md`

---

## 0. Locked decisions (one-line summary)

| Topic | Lock | Why |
|---|---|---|
| Debate topic | "Can AI agents create genuinely original art, or only remix human work?" | Meta — course-perfect; originality bonus |
| Stance assignment | Pro = AI=ORIGINALITY; Con = AI=REMIX_ONLY | Stronger contradiction; Pro's burden of proof matches the affirmative |
| LLM provider | Claude-only via login CLI bundle | Zero API spend; mitigates same-provider auto-agreement via differentiated Skills |
| Pings per side | 10 | Meets H3 directly; no README footnote |
| Web-search backend | DuckDuckGo (pluggable `SearchProvider` interface) | No API key for grader; Brave/Tavily pluggable |
| IPC | `multiprocessing.Process` + `multiprocessing.Queue` | Lecturer's most-named primitive; ADR enumerates all 4 |
| Word cap per turn | 250 words | Balance richness vs token cost |
| Judge drift threshold | 1 (per-message check + `correct_and_replay`) | Lec05 L1182-1184: per-message role-faithfulness |
| Scoring rubric | 5 axes × 20 = 100 (clarity, evidence, rebuttal, novelty, role-fidelity) | Lec05 L1576 added role-fidelity 5th axis |
| Logging | FIFO 20 files × 500 lines structured JSON | HW2 spec §8.6 default verbatim |
| Pair | Salah Qadah + Andalus Kalash, group `uoh-sqak` | Pre-confirmed from HW1 |

---

## 1. Architecture overview

```
┌──────────────────────────────────────────────────────────────────┐
│ main.py  (Orchestrator process — sole entry point)               │
│ - parses config; runs scripts/build_judge_criteria.py if missing │
│   (one-off N7 pre-flight)                                        │
│ - spawns 3 children, owns Watchdog, holds shared spend Value     │
│ - hosts DebateSDK — letter-keyed terminal menu calls it directly │
└──────────────────────────────────────────────────────────────────┘
            │  spawn × 3  +  inject shared spend Value + Lock
       ┌────┼─────────────────────────┬─────────────────────────┐
       ▼    ▼                         ▼                         ▼
┌─────────────┐               ┌─────────────┐           ┌─────────────┐
│  JudgeProc  │               │   ProProc   │           │   ConProc   │
│             │               │  AI=Original│           │  AI=Remix   │
│  judge_skill│               │  pro_skill  │           │  con_skill  │
│             │               │             │           │             │
│  ┌────────┐ │               │ ┌─────────┐ │           │ ┌─────────┐ │
│  │drift   │ │               │ │  Gate-  │ │           │ │  Gate-  │ │
│  │detector│ │               │ │ keeper  │ │           │ │ keeper  │ │
│  └────────┘ │               │ │ (shared │ │           │ │ (shared │ │
│  ┌────────┐ │               │ │  spend) │ │           │ │  spend) │ │
│  │PC      │ │               │ └─────────┘ │           │ └─────────┘ │
│  │filter  │ │               │             │           │             │
│  └────────┘ │               │ web_search  │           │ web_search  │
│  ┌────────┐ │               │ tool        │           │ tool        │
│  │scoring │ │               │             │           │             │
│  │engine  │ │               │             │           │             │
│  └────────┘ │               │             │           │             │
└─────┬───────┘               └─────┬───────┘           └─────┬───────┘
      │                             │                         │
      └─── multiprocessing.Queue × 6 (in/out per child) ──────┘
            +  heartbeat_queue (child → main, for Watchdog)
            +  shared spend Value + Lock (main ↔ all children)

Two-phase boot:
  Phase A — setup_directive  Judge → Pro:  "you argue ORIGINALITY, JSON format X, rules Y"
                              Judge → Con:  "you argue REMIX-ONLY, JSON format X, rules Y"
                              both children ack
  Phase B — debate loop      10 ping/side, drift check per message, PC filter per message,
                              correct_and_replay on drift/PC violation, web-search on demand,
                              verdict at end (no ties, differential scoring)

LifecycleRegistry exposes 8 hooks:
  before_round, after_round, before_verdict, after_verdict,
  before_llm_call, after_llm_call, before_search, after_search
```

### Seven layers (top-down)

1. **Terminal menu** (`menu/tui.py`) — letter-keyed (A=start debate, B=show transcript, C=spend report, …) so Claude CLI can self-test per N8 / lec05 L1736-1745
2. **SDK** (`sdk/debate_sdk.py`) — sole entry point; exposes `run_debate()`, `get_transcript()`, `get_spend_report()`, `simulate_keystroke()`
3. **Orchestrator** (`orchestration/orchestrator.py`) — spawns processes, owns Watchdog + LifecycleRegistry + shared spend Value
4. **Watchdog** (`orchestration/watchdog.py`) — heartbeat poller, `is_alive()` check, kill+restart with backoff (H21)
5. **Agents** (`agents/{judge,pro,con}_agent.py` + `base_agent.py`) — `BaseAgent.step(message) -> Response` is the testable seam
6. **Gatekeeper + Tools** (`shared/gatekeeper.py`, `tools/web_search.py`) — all LLM + search calls; reads/writes shared spend Value
7. **Skills + Structured logger** (`.claude/skills/*` + `shared/structured_logger.py`) — project-local Skills, FIFO 20×500

---

## 2. Skills design (locked)

Three project-local skills under `.claude/skills/` (H17). Loaded **statically as system prompts** (ADR-002) — each child reads its SKILL.md body via filesystem on boot and passes it as `--append-system-prompt` to `claude -p`.

```
.claude/skills/
├── pro_skill/
│   ├── SKILL.md
│   └── references/
│       └── citations.md         # pre-seeded: Klingemann, Edmond de Belamy, transformative use
├── con_skill/
│   ├── SKILL.md
│   └── references/
│       └── citations.md         # Stochastic Parrots, NYT v OpenAI, Getty v Stability, Chinese Room
└── judge_skill/
    ├── SKILL.md
    ├── references/
    │   └── debate_criteria.md   # generated by scripts/build_judge_criteria.py (N7)
    └── scripts/
        └── compute_scores.py    # 5-axis aggregation helper
```

### Frontmatter discipline (per Anthropic best practices)

- `name`: ≤64 chars, lowercase-kebab, project-local-prefixed
- `description`: ≤1024 chars, third person, states WHAT + WHEN, "pushy" trigger phrasing
- Body: 1500–2000 words, scope + testing-expectations at top, standing-instructions style
- Progressive disclosure: references loaded on demand by the child agent via filesystem read

### Stance assignment

- **Pro**: AI agents CAN create genuinely original art. Tactics: emergence, latent-space exploration, Christie's $432K Edmond de Belamy auction, Klingemann + Ridler, transformative-use doctrine, "all human art is also remixing prior work."
- **Con**: AI agents fundamentally remix; nothing is novel. Tactics: training-data dependency, Stochastic Parrots (Bender 2021), NYT v OpenAI, Getty v Stability AI, lack of intentionality / inner experience, the Chinese Room.
- **Judge**: topic-blind (H19) — system prompt contains NO topic words, only debate rules + scoring criteria. Issues setup directives (H18), polices PC (H16), checks drift per message (H20), declares winner with differential scoring (H5).

---

## 3. Components — class hierarchy

```
BaseAgent  (abstract — agents/base_agent.py)
├── attrs: in_queue, out_queue, heartbeat_queue, shared_spend, lock,
│          skill_dir, llm_provider, lifecycle_registry
├── send/recv JSON (jsonschema-validated)
├── timeout per LLM call (H10 enforced by Gatekeeper)
├── graceful SIGTERM handler
└── step(message: Message) -> Response          ← TEST SEAM (DI-friendly)

PartisanAgent(BaseAgent)  (abstract — agents/partisan_agent.py)
├── stance loaded from SKILL.md body
├── web_search tool (via Gatekeeper)
├── enforce_opponent_reference()                 ← H7
├── extract_citations(text) -> list[Citation]
└── temperature default 0.85

  ProAgent(PartisanAgent)   — loads .claude/skills/pro_skill/SKILL.md
  ConAgent(PartisanAgent)   — loads .claude/skills/con_skill/SKILL.md

JudgeAgent(BaseAgent)  (agents/judge_agent.py)
├── topic_blind = True                            ← H19
├── DriftDetector  (per-message check)            ← H20
├── PCFilter       (post-process before re-broadcast) ← H16
├── ScoringEngine  (5 axes × 20)
├── issue_setup_directives()                      ← H18
├── route(msg)     (child → father → child)       ← H4
├── declare_winner(differential_required=True)    ← H5
└── temperature default 0.30
```

### Orthogonal mixins (one concern each, rubric §4.2)

```
LoggingMixin       — structured JSON log per significant action
LifecycleMixin     — registers/fires the 8 hooks
HeartbeatMixin     — emit alive ping every 2s to heartbeat_queue
```

Retry policy lives inside `ApiGatekeeper` only (single source of truth) — `RetryMixin` was considered then dropped.

### Gatekeeper + provider plugin pattern

```python
class ApiGatekeeper:
    """
    Input:  api_call (callable), *args, **kwargs
    Output: response, or RateLimitExceeded / BudgetExhausted exception
    Setup:  config (RateLimitConfig), shared_spend (Value), lock (Lock)
    """
    def execute(self, api_call, *args, **kwargs): ...
    def get_queue_status(self) -> QueueStatus: ...
    def estimate_cost(self, n_debates: int) -> Decimal: ...
    def get_spend_so_far(self) -> Decimal: ...

class LLMProvider(ABC):       # plugin point
    @abstractmethod
    def complete(self, system, user, temperature) -> LLMResponse: ...

class ClaudeLoginProvider(LLMProvider):
    """Shells out to `claude -p --append-system-prompt ... --output-format json`"""

class SearchProvider(ABC):    # plugin point
    @abstractmethod
    def search(self, query, k) -> list[SearchHit]: ...

class DuckDuckGoProvider(SearchProvider):
    """Uses ddgs.text() — no API key required"""
```

`LLMProvider` and `SearchProvider` register via `tools/registry.py` keyed by config string — adding Gemini or Brave is one class + one config line, zero core-code change.

### Orchestrator, Watchdog, SDK, Menu

```python
class DebateOrchestrator:
    def spawn_children(self) -> tuple[Process, Process, Process]: ...
    def run_debate(self, topic, n_pings=10) -> Transcript: ...
    def shutdown_gracefully(self): ...

class Watchdog:
    """Setup: poll_interval=2s, stuck_timeout=30s, max_restarts=3"""
    def monitor(self): ...                              # H21
    def on_stuck(self, child): ...

class LifecycleRegistry:
    """8 hooks: before_round, after_round, before_verdict, after_verdict,
       before_llm_call, after_llm_call, before_search, after_search"""

class DebateSDK:
    """Sole entry point — menu/tests/external Claude CLI go through this only."""
    def run_debate(self, topic, n_pings=10) -> Transcript: ...
    def get_transcript(self, debate_id) -> Transcript: ...
    def get_spend_report(self) -> SpendReport: ...
    def list_debates(self) -> list[DebateMetadata]: ...
    def simulate_keystroke(self, key) -> MenuResponse: ...   # N8
    def get_health_status(self) -> HealthStatus: ...
```

Terminal menu is letter-keyed (`A` start debate, `B` view transcript, `C` spend report, `D` health, `E` manual phase-1 instructions, `X` exit).

### Per-mechanism PRDs

| File | Component | Approx |
|------|-----------|--------|
| `PRD_judge_agent.md` | Moderation, drift, scoring, PC, no-tie, topic-blind | ~250 |
| `PRD_pro_agent.md` | AI=originality stance, citations, rebuttal | ~150 |
| `PRD_con_agent.md` | AI=remix stance | ~150 |
| `PRD_orchestrator.md` | Process spawning, IPC, lifecycle, shutdown | ~200 |
| `PRD_ipc_bus.md` | Queue protocol, JSON schema, message types | ~200 |
| `PRD_gatekeeper.md` | Rate limits, budget, FIFO, backpressure, retry, spend | ~250 |
| `PRD_watchdog.md` | Heartbeat, is_alive, SIGKILL+restart | ~150 |
| `PRD_skills.md` | Loading, frontmatter contract, ADR-002 | ~150 |
| `PRD_web_search_tool.md` | SearchProvider interface, DDG default, dual purpose | ~150 |

---

## 4. Data flow + JSON wire protocol

### Message schema (`config/schemas/message-1.00.json`)

Versioned at `1.00`, jsonschema-validated on both send AND recv. Required fields: `msg_id` (uuid), `schema_version`, `from`, `to`, `role`, `ping_index`, `text` (max 4000 chars), `timestamp` (ISO-8601). Optional: `references_opponent` (bool, H7), `citations` (array of `{url, snippet}`), `scoring` (5-axis 0-20 each), `tokens_in`, `tokens_out`.

### Eight message roles

| Role | Direction | Phase | Purpose |
|---|---|---|---|
| `setup_directive` | Judge → Pro / Con | Boot | Stance, rules, JSON format (H18) |
| `ack` | Pro / Con → Judge | Boot | Ready confirmation |
| `argument` | Pro / Con → Judge | Debate (odd) | Opening of turn |
| `counter` | Pro / Con → Judge | Debate (even) | Rebuttal |
| `correction_request` | Judge → Pro / Con | Drift detected | Stance-faithful replay (H20) |
| `intervention` | Judge → Pro / Con | PC violation | Sanitize + replay (H16) |
| `status` | Pro/Con/Judge → Main | Continuous | Heartbeat + progress |
| `verdict` | Judge → Main | End | Final scores + winner (H5) |

### Two-phase boot timeline

```
T+0.0s   main spawns Pro, Con, Judge processes
T+0.2s   Judge runs scripts/build_judge_criteria.py if cache miss (N7)
T+0.3s   Judge → Pro: setup_directive(stance=ORIGINALITY, rules, fmt)
T+0.3s   Judge → Con: setup_directive(stance=REMIX_ONLY, rules, fmt)
T+0.5s   Pro → Judge: ack
T+0.5s   Con → Judge: ack
T+0.6s   Debate loop opens (Judge cues Pro: argument ping=1)
...
T+~5min  Ping 20 complete (10/side)
T+~5min  Judge.ScoringEngine across all 20 messages
T+~5min  Judge → Main: verdict
T+~5min  Main writes Transcript JSON; signals children SIGTERM
```

### Agent state machines

**Pro / Con** (mirrored stance):
```
[INIT] ─(recv setup_directive)─> [WAITING_TURN]
[WAITING_TURN] ─(recv opponent forward OR start-cue)─> [GENERATING]
[GENERATING] ─(emit argument/counter)─> [AWAITING_VALIDATION]
[AWAITING_VALIDATION] ─(recv correction_request)─> [GENERATING]
[AWAITING_VALIDATION] ─(recv intervention)─> [GENERATING]
[AWAITING_VALIDATION] ─(recv opponent's forwarded msg)─> [GENERATING]
[any] ─(SIGTERM)─> [SHUTDOWN]
```

**Judge**:
```
[INIT] ─> [BOOTING] ─(both acks)─> [DEBATE_LOOP]
[DEBATE_LOOP] ─(recv argument/counter)─> [VALIDATING]
[VALIDATING] ─(pass)─> [FORWARDING] ─> [DEBATE_LOOP]
[VALIDATING] ─(drift)─> [SEND_CORRECTION] ─> [DEBATE_LOOP]
[VALIDATING] ─(PC violation)─> [SEND_INTERVENTION] ─> [DEBATE_LOOP]
[DEBATE_LOOP] ─(20 turns)─> [SCORING] ─> [EMIT_VERDICT] ─> [SHUTDOWN]
```

### Mutual-reference enforcement (H7)

Each `argument`/`counter` must quote at least one phrase from the opponent's last message. Schema's `references_opponent: bool` is set true only if the emitter's own regex check confirms; Judge's `DriftDetector` re-verifies. Either signal false → `correction_request`.

### Transcript persistence

After verdict, main writes `transcripts/<YYYY-MM-DD-HHMM>-<topic-slug>.json` (all messages + verdict). README pulls the first session into a fenced block (spec §8.7 mandate). `.gitignore` lets `transcripts/sample-session-1.json` through, ignores the rest.

---

## 5. Error handling + Watchdog

### Failure-mode catalog

| Layer | Failure | Detected by | Action |
|---|---|---|---|
| LLM provider | Claude CLI not on PATH | `__init__()` existence check | Fail-fast at boot |
| LLM provider | Per-call timeout (H10) | `signal.alarm(N)` in Gatekeeper | 3× exponential backoff, then `LLMTimeoutError` |
| LLM provider | Rate-limit / quota | stderr scan + non-zero exit | Retry after `Retry-After` (default 60s), capped at 3 |
| LLM provider | Malformed JSON | `jsonschema.validate()` post-parse | Re-prompt once with format hint; second fail → `MalformedResponseError` |
| Web search | DDG rate-limit (429) | `ddgs.RatelimitException` | Fall back to pre-seeded `references/citations.md` |
| Web search | 0 results / network error | Returns empty list / connection err | Agent proceeds w/o citation (log warning) |
| IPC bus | `Queue.get(timeout=N)` empty | `Queue.Empty` | "Child stuck" → Watchdog escalation |
| IPC bus | Schema validation fail | `jsonschema.validate()` | Reject, log error, request re-emit |
| Child process | Crashed (segfault, unhandled) | `Process.is_alive() == False` | Watchdog kill+respawn+replay setup_directive |
| Child process | Hung but alive | No heartbeat in 30s | SIGKILL + respawn + restore state from transcript |
| Budget | 75% threshold | `Gatekeeper.check_budget()` | Soft warn (log only) |
| Budget | 95% threshold | Same | Hard refuse + emit early verdict |
| User | Ctrl+C / SIGTERM | `signal` handler in main | Cascade SIGTERM to children → 10s drain → SIGKILL stragglers → flush transcript |

### Watchdog (H21)

```python
class Watchdog:
    """
    Setup: poll_interval=2s, stuck_timeout=30s,
           max_restarts=3, restart_backoff=[1, 2, 4]
    """
    def monitor(self): ...        # polls heartbeat_queue + is_alive() in main proc
    def _is_stuck(self, child) -> bool: ...
    def _restart(self, child, restart_idx) -> Process | None: ...
    def _on_unrecoverable(self, child): ...   # → emit debate_aborted verdict
```

**Two-signal detection**: a child is dead-or-stuck only if `is_alive() == False` OR `last_heartbeat_age > stuck_timeout`. Single-signal would miss either crashed-vs-hung failure class.

**Restart with state replay**: respawned child receives (a) same shared spend Value/Lock, (b) same skill_dir, (c) the most-recent `setup_directive` from the transcript — so it boots into `[WAITING_TURN]`, not `[INIT]`.

**Fail-fast**: 3 restarts of the same child within one debate caps. Beyond that, Judge emits `verdict` with `debate_aborted` outcome and partial scoring; main shuts down cleanly.

### Graceful shutdown cascade

```
User: Ctrl+C
  → main's SIGINT handler sets shutdown_event
  → Sends SIGTERM to each child (10s drain window)
  → Each child: cancel in-flight LLM call, flush log buffer,
      send final "shutting down" status, exit(0)
  → Watchdog .join(timeout=10); SIGKILL any stragglers
  → Main writes partial transcript → transcripts/aborted-<id>.json
  → Main prints summary + exit
```

### Chaos-test edge cases (per rubric §6.3)

1. `kill -9` child mid-ping → Watchdog detects ≤ 30s, respawns, debate resumes
2. Both children agree → DriftDetector fires `correction_request` to whoever drifted first
3. Lying allowed; opponent fact-checks via web search (Judge does NOT fact-check — H17)
4. Web search 0 results → `citations: []` + warning log
5. Web search 30s timeout → same as 0 results
6. LLM returns valid JSON but wrong stance → DriftDetector via stance regex
7. LLM exceeds 250-word cap → truncate with ellipsis + `text_truncated: true` flag
8. Ctrl+C during ping 7 → clean exit, `aborted-*.json` partial transcript
9. Token budget 95% → early verdict, `budget_exhausted` marker
10. Malformed JSON from Pro → re-prompt once → second fail = `correction_request`

### Logging discipline (rubric §A14)

FIFO 20 files × 500 lines, JSON-lines, no `print()`, no unstructured stderr. Example:
```json
{"ts":"2026-05-25T14:33:21.452Z","level":"WARN","component":"watchdog",
 "event":"child_stuck","pid":14823,"child_role":"pro",
 "last_heartbeat_age_s":34.2,"action":"sigkill_and_restart","restart_idx":1}
```

---

## 6. Testing strategy

### Test pyramid

```
                          ┌──────────────────────────┐
                          │ E2E debate (real Claude) │  ~3 tests
                          │ tests/e2e/               │  manual + 1-shot in CI
                          └──────────────────────────┘
                       ┌──────────────────────────────────┐
                       │ Integration (mock LLM + search)  │  ~9 tests
                       │ tests/integration/               │  spawn real processes
                       └──────────────────────────────────┘
                  ┌──────────────────────────────────────────┐
                  │ Unit (per class, DI-mocked dependencies) │  ~124 tests
                  │ tests/unit/                              │  ≥85% coverage
                  └──────────────────────────────────────────┘
```

### Unit layer — `tests/unit/`

Mirrors `src/` structure (rubric §6.1 rule 1). Every public method gets ≥1 happy + ≥1 error test (rule 3). Dependencies injected via `BaseAgent.step(message)`-style seams; LLM and search mocked via `MockLLMProvider` / `MockSearchProvider` in `tests/conftest.py`. **No live external calls in tests** (rule 7). Test files obey the 150-line rule (rule 6).

| File | Tests |
|---|---|
| `test_base_agent.py` | JSON send/recv, SIGTERM handler, timeout — 8 |
| `test_partisan_agent.py` | Skill load, opponent-reference regex, citation extract — 10 |
| `test_pro_agent.py` / `test_con_agent.py` | Stance-regex match — 4 each |
| `test_judge_agent.py` | DriftDetector, PCFilter, ScoringEngine, no-tie, setup_directive — 18 |
| `test_orchestrator.py` | Spawn/teardown, hook order, shutdown — 12 |
| `test_watchdog.py` | Heartbeat poll, stuck detect, restart+backoff, fail-fast — 14 |
| `test_gatekeeper.py` | Rate limit, FIFO queue, backpressure, retry, budget thresholds — 16 |
| `test_lifecycle_registry.py` | Register/fire order, errors in hooks — 6 |
| `test_search_providers.py` | DDG happy, 0-results, rate-limit fallback — 6 |
| `test_llm_providers.py` | Shell-out, malformed JSON, timeout — 8 |
| `test_structured_logger.py` | FIFO rotation 500 lines, 20-file cap — 6 |
| `test_message_schema.py` | jsonschema for all 8 roles + invalid shapes — 12 |

Total: **~124 unit tests**. Coverage target: ≥85% (R10), aim ≥90%.

### Integration layer — `tests/integration/`

Spawns real `multiprocessing.Process` children, but with `MockLLMProvider` and `MockSearchProvider` injected via config override.

| File | Scenario | H-gates verified |
|---|---|---|
| `test_full_debate_mocked.py` | 10-ping debate end-to-end with canned LLM | H1, H2, H3, H4, H5, H7, H18, H20 |
| `test_drift_correction.py` | Stance-violating text → `correction_request` → re-emit | H20 |
| `test_pc_intervention.py` | PC-violating text → `intervention` | H16 |
| `test_chaos_child_kill.py` | `SIGKILL` mid-debate → Watchdog recovers | H21, chaos §6.3 |
| `test_chaos_child_hang.py` | Infinite loop → heartbeat-stale → kill+restart | H21 |
| `test_budget_exhausted.py` | 95% threshold → early verdict | rubric §A8 |
| `test_graceful_shutdown.py` | SIGINT → clean exit + aborted-*.json | §6.3 |
| `test_no_tie_enforcer.py` | Identical scores → Judge tiebreaks | H5 |
| `test_setup_directive_ack.py` | Phase A — both children ack before debate loop | H18 |

### E2E layer — `tests/e2e/`

Real Claude CLI, real DDG. `@pytest.mark.e2e` + `RUN_E2E=1` env gate.

| Test | Purpose |
|---|---|
| `test_real_debate_5_pings.py` | 5-ping debate at the real provider — sanity check |
| `test_real_search_dual_purpose.py` | Pro cites; Con fact-checks via DDG; both `citations` arrays in transcript |
| `test_real_pc_filter.py` | Vulgar prompt injected; Judge intercepts before re-broadcast |

### CI — `.github/workflows/ci.yml`

```yaml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - run: uv sync
      - run: uv run ruff check src tests
      - run: uv run pytest tests/unit tests/integration --cov --cov-fail-under=85
      - run: uv run python scripts/check_file_lines.py
```

E2E NOT in CI (cost). Grader can opt-in with `RUN_E2E=1 uv run pytest tests/e2e`.

### Pre-commit (`.pre-commit-config.yaml`) — fixes HW1's Quality Standards weak spot

```yaml
repos:
  - repo: local
    hooks:
      - { id: ruff,             name: ruff,                entry: uv run ruff check, language: system, types: [python] }
      - { id: file-line-limit,  name: 150-line check,      entry: uv run python scripts/check_file_lines.py, language: system, pass_filenames: false }
      - { id: pytest-unit,      name: pytest (unit fast),  entry: uv run pytest tests/unit -x -q, language: system, pass_filenames: false }
```

### File-line enforcer — `scripts/check_file_lines.py`

Walks `src/` + `tests/`, counts non-blank non-comment lines per `.py`, exits 1 if any > 150. Also flags `line > 100 chars + no comments` to catch the "whitespace games" Dr. Segal's agent looks for.

### Fixtures — `tests/conftest.py`

- `mock_llm_provider` — canned JSON keyed by `(role, ping_index)`
- `mock_search_provider` — fixed `SearchHit` lists
- `temp_skill_dir` — tmp_path with minimal SKILL.md
- `shared_spend_fixture` — `multiprocessing.Value` + `Lock` pair
- `transcript_fixture` — canned 4-message transcript for replay-tests

Canned LLM responses: `tests/fixtures/llm_responses/<scenario>.json`, versioned alongside tests.

---

## 7. Spec self-review pass (rubric §6.4, brainstorming step 7)

Run on 2026-05-25 after §6 locked. Four-axis check.

### 7.1 Placeholder scan

Findings (all resolved inline):
- §0 table referenced "Pro = originality side; Con = remix-only side" but the topic table didn't repeat the stance assignment — added.
- §3 referenced `LLMResponse` and `SearchHit` types without defining them — added DTO note (see §7.5 below).
- "Token budget" mentioned without a concrete number — added concrete numbers (see §7.5).

### 7.2 Internal consistency

No contradictions found between sections. Cross-references verified:
- Class hierarchy in §3 matches state machines in §4 (BaseAgent → all three concrete agents).
- Watchdog's `max_restarts=3` consistent across §4 and §5.
- Lifecycle hooks named in §3 match the 8 listed in the architecture diagram.

### 7.3 Scope check

Scope is large but coherent — single implementation plan can drive it. Estimated artifact sizes for the writing-plans output:
- `docs/PRD.md` ~500 lines
- `docs/PLAN.md` ~800 lines (incl. C4, UML, 7 ADRs, ISO/IEC 25010)
- `docs/TODO.md` 800–1000 tasks
- 9 per-mechanism PRDs ~150-250 lines each
- ~20-30 `.py` source files × ≤150 lines
- ~136 tests (124 unit + 9 integration + 3 e2e)

Fits a single 4-day execution window. No decomposition needed.

### 7.4 Ambiguity check

Resolved inline:
- "claude -p" exact flags — specified in §7.5 (DTO + commands note).
- DriftDetector mechanism — stance-keyword regex (deterministic, no extra LLM call). Documented in §7.5.
- Token budget concrete numbers — added in §7.5.

### 7.5 DTO + Commands cheatsheet (added during self-review)

**DTOs** (to be Pydantic models or dataclasses):

```python
@dataclass(frozen=True)
class LLMResponse:
    text: str
    tokens_in: int
    tokens_out: int
    finish_reason: Literal["stop", "length", "timeout", "error"]
    raw_json: dict  # for debugging

@dataclass(frozen=True)
class SearchHit:
    url: str
    snippet: str
    rank: int

@dataclass(frozen=True)
class SpendReport:
    total_input_tokens: int
    total_output_tokens: int
    estimated_cost_usd: Decimal       # zero in login-CLI mode
    pct_of_budget_used: float
    by_agent: dict[str, dict]         # per-agent breakdown

@dataclass(frozen=True)
class HealthStatus:
    children_alive: dict[str, bool]   # {"pro": True, "con": True, "judge": True}
    last_heartbeat_ages: dict[str, float]
    pending_messages: dict[str, int]  # queue depths
    restart_count: dict[str, int]
```

**ClaudeLoginProvider exact invocation**:

```bash
claude -p \
  --append-system-prompt "$(cat .claude/skills/<role>_skill/SKILL.md)" \
  --output-format json \
  --max-turns 1 \
  "<user prompt>"
```

`--output-format json` returns the structured response; `--max-turns 1` prevents Claude from running multi-turn agentic loops inside a single LLM call.

**DriftDetector mechanism**:

Stance-keyword regex per Skill (defined in `SKILL.md` body under `## Drift signal keywords`). For example, Pro's drift-trigger keywords are `{"actually you're right", "I concede", "fair point", "good argument", "I agree", "you've convinced me"}`. Con's are the same. The detector runs `re.search()` against the candidate text; on match → `correct_and_replay`. Deterministic, cheap, requires no extra LLM call.

**Token budget concrete numbers** (`config/rate_limits.json`):

```json
{
  "version": "1.00",
  "services": {
    "claude_login": {
      "tokens_per_debate": 200000,
      "tokens_per_day": 1000000,
      "warn_at_percent": 75,
      "hard_cap_percent": 95,
      "requests_per_minute": 30,
      "concurrent_max": 3,
      "retry_after_seconds": 60,
      "max_retries": 3
    },
    "ddg_search": {
      "requests_per_minute": 10,
      "requests_per_hour": 100,
      "concurrent_max": 2
    }
  }
}
```

In login-CLI mode, cost = $0 — but token tracking still happens for the rate/spend report. README documents this as "API-mode-ready: switch the LLMProvider config to `claude_api_key` and the same budget caps apply with dollar accounting."

---

## Next steps

1. ✅ §1-§6 brainstorming sections locked
2. ✅ Self-review pass complete; inline fixes applied
3. ⏳ **User reviews this spec file** — last gate before writing-plans
4. ⏳ Invoke `writing-plans` skill — produces formal `docs/PRD.md`, `docs/PLAN.md`, `docs/TODO.md` (800-1000 tasks) + 9 per-mechanism PRDs from this approved design
5. ⏳ User approval gate #1 (PRD only) — rubric §2.5 step 1
6. ⏳ User approval gate #2 (full docs package) — rubric §2.5 step 5
7. ⏳ Begin execution (TDD red-green-refactor) per `docs/TODO.md`

---

## ADRs (will be expanded into separate files under `docs/ADRs/`)

| # | Decision | Rationale (one-liner) |
|---|----------|----------------------|
| ADR-001 | IPC = `multiprocessing.Queue` (over Signal, FIFO, Sockets) | Lecturer's most-named primitive; cross-platform; thread-safe by construction |
| ADR-002 | Skills loaded statically as system prompts (not Claude-auto-discovered) | Each child process is a single deterministic role; auto-discovery would risk wrong-skill assignment |
| ADR-003 | LLM via `claude -p` shell-out (not anthropic SDK) | Uses user's login bundle, zero API spend; trade-off is grader needs Claude CLI installed |
| ADR-004 | Web search default = DuckDuckGo via `ddgs` package | Zero-config for grader; `SearchProvider` interface keeps Brave/Tavily pluggable |
| ADR-005 | Same-provider mitigation: temperature spread + Skill differentiation | Compensates for H8 risk when Pro=Con=Claude |
| ADR-006 | Cross-process spend tracking via `multiprocessing.Value` + Lock | Global token budget must be the single source of truth; per-child Gatekeepers update via lock |
| ADR-007 | Judge scoring criteria sourced via pre-flight web search (N7) | Lecturer-specific request (lec05 L1519-1528); originality bonus signal |

---

## YAGNI cuts (documented for transparency)

| Idea | Status | Why deferred |
|------|--------|--------------|
| Multi-skill per agent (argument_generator + opponent_analyzer) | Mention in PLAN.md Future Work | 3× combinatorial test matrix; ~2 days I don't have. Mentioning earns half the bonus |
| Compaction strategy in Gatekeeper | Mention in PRD_gatekeeper.md | Math: 250 words × 20 turns × 3 voices ≈ 20K tokens vs Claude 200K context. Not needed at this scale |
| Mixed providers (Gemini for Con) | LLMProvider interface stays abstract | User picked Claude-only; one-adapter swap leaves the door open |
| Unix-domain socket watchdog (3rd primitive) | ADR enumerates but doesn't implement | macOS portability risk; marginal grade signal vs implementation hours |

---

## Next steps (in this brainstorming session)

1. ✅ §1 architecture — APPROVED with revisions
2. ✅ Skills design — APPROVED
3. 🔄 §2 components — TODO
4. ⏳ §3 data flow + JSON schema — TODO
5. ⏳ §4 error handling + watchdog — TODO
6. ⏳ §5 testing strategy — TODO
7. ⏳ Spec self-review pass (placeholder scan, internal consistency, scope, ambiguity)
8. ⏳ User reviews spec
9. ⏳ Transition to writing-plans skill → formal `docs/PRD.md`, `docs/PLAN.md`, `docs/TODO.md` (≥500 tasks, target 800-1000)
