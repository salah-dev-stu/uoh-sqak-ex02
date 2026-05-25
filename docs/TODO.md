# HW2 TODO list

**Target size:** 800 tasks (top of lecturer's slide range 300-800, bottom of CLAUDE.md target 800-1000).
After "be very critical" verify pass, this may grow toward 1000.
Sized to balance: Dr. Segal's slide ceiling, spoken-lecture minimum (lec01 L1170: "מינימום 500"),
and the user's HW2 quality target ≥90.

**Marking discipline:**
- `[ ]` = pending
- `[x]` = done (commit it when you mark — continuous-commits are graded)
- `[~]` = in progress (use sparingly; long [~] entries fragment the audit trail)

**Companion docs:** `docs/PRD.md`, `docs/PLAN.md`, `docs/PROMPTS.md`, `docs/superpowers/plans/2026-05-25-hw2-agent-debate-system.md`.

---

## Pre-execution status (already done before this list)

- [x] P0.1: Worker session bootstrap — read CLAUDE.md, IDEA.md, RULES.md, CONTEXT-*.md, HW1 feedback
- [x] P0.2: Brainstorming via `/brainstorming` skill (5 sections, 31 locked decisions, self-review)
- [x] P0.3: Design spec committed (`docs/superpowers/specs/2026-05-24-hw2-debate-design.md`)
- [x] P0.4: Implementation plan committed and aligned to Dr. Segal's lifecycle slide
- [x] P0.5: `docs/PRD.md` written + approved by user (gate 1 cleared)
- [x] P0.6: `docs/PLAN.md` written
- [x] P0.7: `docs/PROMPTS.md` audit trail running (17 prompts captured)
- [x] P0.8: git initialized, 8 commits visible on `main`

---

## Phase A — Documents already complete

- [x] A.1: docs/PRD.md (root product requirements, rubric §2.5 step 1)
- [x] A.2: docs/PLAN.md (C4 + UML + class diagram + ADRs + ISO 25010)
- [x] A.3: docs/TODO.md — **this file** (in progress)
- [x] A.4: docs/PRD_judge_agent.md (Phase E)
- [x] A.5: docs/PRD_pro_agent.md (Phase E)
- [x] A.6: docs/PRD_con_agent.md (Phase E)
- [x] A.7: docs/PRD_orchestrator.md (Phase E)
- [x] A.8: docs/PRD_ipc_bus.md (Phase E)
- [x] A.9: docs/PRD_gatekeeper.md (Phase E)
- [x] A.10: docs/PRD_watchdog.md (Phase E)
- [x] A.11: docs/PRD_skills.md (Phase E)
- [x] A.12: docs/PRD_web_search_tool.md (Phase E)
- [x] A.13: Approval gate #2 — user reviews full docs bundle (rubric §2.5 step 5)

---

## Phase 0 — Project scaffold

### Task 0.1: uv init + Python 3.13
- [x] 0.1.1: `uv init --name agent-debate --package --python 3.13`
- [x] 0.1.2: Verify `.python-version` contains `3.13`
- [x] 0.1.3: Verify `pyproject.toml` skeleton created
- [x] 0.1.4: `uv python pin 3.13`
- [x] 0.1.5: `uv sync` and verify `.venv/` created
- [x] 0.1.6: `uv run python --version` returns 3.13.x
- [x] 0.1.7: Commit "build: scaffold uv project on Python 3.13"

### Task 0.2: Configure pyproject.toml
- [x] 0.2.1: Add `[project]` block with name, version=1.00.0, description, authors, license=MIT
- [x] 0.2.2: Add `requires-python = ">=3.13"`
- [x] 0.2.3: Add `dependencies` (jsonschema, ddgs, pydantic)
- [x] 0.2.4: Add `[project.scripts]` with `agent-debate = "agent_debate.main:main"`
- [x] 0.2.5: Add `[dependency-groups.dev]` (pytest, pytest-cov, pytest-timeout, ruff, pre-commit)
- [x] 0.2.6: Add `[build-system]` with hatchling
- [x] 0.2.7: Add `[tool.ruff]` (line-length=100, target-version=py313)
- [x] 0.2.8: Add `[tool.ruff.lint]` (E,F,W,I,N,UP,B,C4,SIM; ignore=E501)
- [x] 0.2.9: Add `[tool.pytest.ini_options]` (markers, timeout, testpaths)
- [x] 0.2.10: Add `[tool.coverage.run]` (source=src, omit main.py)
- [x] 0.2.11: Add `[tool.coverage.report]` (fail_under=85, show_missing=true)
- [x] 0.2.12: `uv sync` — verify lockfile populated
- [x] 0.2.13: `uv run ruff check src tests` — verify runs clean
- [x] 0.2.14: `uv run pytest` — verify "no tests ran" (exit 5)
- [x] 0.2.15: Commit "build: configure ruff, pytest, coverage in pyproject.toml"

### Task 0.3: Five versioned config files
- [x] 0.3.1: Write `config/setup.json` (version=1.00, debate_topic, stances, dirs)
- [x] 0.3.2: Write `config/agents.json` (version=1.00, three agents with temperature, skill_name, llm_provider)
- [x] 0.3.3: Write `config/debate_rules.json` (version=1.00, pings_per_side=10, drift_threshold=1, scoring axes, no_tie=true)
- [x] 0.3.4: Write `config/rate_limits.json` (version=1.00, claude_login budget + warn/hard caps, ddg_search limits)
- [x] 0.3.5: Write `config/logging_config.json` (version=1.00, fifo_files=20, max_lines=500)
- [x] 0.3.6: Verify all five files are valid JSON (`uv run python -c "import json; [json.load(open(f)) for f in glob.glob('config/*.json')]"`)
- [x] 0.3.7: Commit "config: add versioned JSON configs"

### Task 0.4: .env-example
- [x] 0.4.1: Write `.env-example` with placeholder vars (ANTHROPIC_API_KEY commented, BRAVE/TAVILY commented, RUN_E2E=0)
- [x] 0.4.2: Verify `.env-example` does not appear in `.gitignore` (it should be committed)
- [x] 0.4.3: Commit "config: add .env-example template (no secrets)"

### Task 0.5: Package init with __version__
- [x] 0.5.1: Write `src/agent_debate/__init__.py` with `__version__ = "1.00"` and `__all__`
- [x] 0.5.2: Verify `uv run ruff check src/agent_debate/__init__.py` is clean
- [x] 0.5.3: Commit "feat: define __version__ at package root (R6 versioning)"

### Task 0.6: Pre-commit hook + file-line enforcer
- [x] 0.6.1: Write `scripts/check_file_lines.py` (counts logical lines, flags >150, flags long-line+no-comment "whitespace games")
- [x] 0.6.2: Verify the script exits 0 on empty source tree
- [x] 0.6.3: Write `.pre-commit-config.yaml` (ruff + file-line-limit + pytest-unit hooks)
- [x] 0.6.4: `uv run pre-commit install`
- [x] 0.6.5: Verify `.git/hooks/pre-commit` exists
- [x] 0.6.6: Test the hook fires on a dummy commit
- [x] 0.6.7: Commit "build: pre-commit (ruff + 150-line enforcer + unit tests)"

### Task 0.7: GitHub Actions CI
- [x] 0.7.1: Create `.github/workflows/` directory
- [x] 0.7.2: Write `ci.yml` (Ubuntu-latest, uv install, ruff check, line enforcer, pytest with coverage)
- [x] 0.7.3: Verify YAML is valid
- [x] 0.7.4: Commit "ci: add GitHub Actions workflow"

### Task 0.8: Tests scaffold
- [x] 0.8.1: Create `tests/{unit,integration,e2e,fixtures/llm_responses}/` directories
- [x] 0.8.2: `touch tests/__init__.py` and all subdir `__init__.py` files
- [x] 0.8.3: Write `tests/conftest.py` with RUN_E2E gate
- [x] 0.8.4: Verify `uv run pytest --collect-only -q` runs clean
- [x] 0.8.5: Commit "test: scaffold tests/ tree with conftest e2e gate"

### Task 0.9: .gitignore audit
- [x] 0.9.1: Verify `.gitignore` already includes secrets (.env, *.key, etc) — done in initial commit
- [x] 0.9.2: Append patterns specific to uv (`.venv/`, `.python-version` if needed)
- [x] 0.9.3: Append `.coverage`, `htmlcov/` for coverage runs
- [x] 0.9.4: Verify `git status` shows no unwanted files

---

## Phase 1 — Foundation infrastructure

### Task 1.1: constants.py with 4 enums
- [x] 1.1.1: Write failing test `tests/unit/test_constants.py` (AgentRole, MessageRole, Stance, DebateOutcome)
- [x] 1.1.2: Run test, expect ImportError
- [x] 1.1.3: Write `src/agent_debate/constants.py` (AgentRole with PRO/CON/JUDGE)
- [x] 1.1.4: Add `MessageRole` (8 members: setup_directive, ack, argument, counter, correction_request, intervention, status, verdict)
- [x] 1.1.5: Add `Stance` (ORIGINALITY, REMIX_ONLY)
- [x] 1.1.6: Add `DebateOutcome` (PRO_WINS, CON_WINS, DEBATE_ABORTED, BUDGET_EXHAUSTED)
- [x] 1.1.7: Add `SCHEMA_VERSION = "1.00"`
- [x] 1.1.8: Run tests, expect 4 passed
- [x] 1.1.9: `uv run ruff check src/agent_debate/constants.py`
- [x] 1.1.10: Commit "feat(constants): add AgentRole, MessageRole, Stance, DebateOutcome enums"

### Task 1.2: shared/version.py (R6)
- [x] 1.2.1: Write `src/agent_debate/shared/__init__.py`
- [x] 1.2.2: Write failing test `tests/unit/test_version.py` (CODE_VERSION=1.00, validate_config_version)
- [x] 1.2.3: Run, expect fail
- [x] 1.2.4: Implement `shared/version.py` with `CODE_VERSION` and `validate_config_version()`
- [x] 1.2.5: Run, expect pass
- [x] 1.2.6: Commit "feat(version): CODE_VERSION 1.00 + config-version compat check"

### Task 1.3: shared/config.py
- [x] 1.3.1: Write failing test `tests/unit/test_config.py` (Config dataclass, load_config, version mismatch)
- [x] 1.3.2: Run, expect fail
- [x] 1.3.3: Implement `shared/config.py` with `Config` dataclass and `load_config(path)`
- [x] 1.3.4: Wire `validate_config_version()` into load
- [x] 1.3.5: Run, expect pass
- [x] 1.3.6: Commit "feat(config): Config dataclass + load_config with version check"

### Task 1.4: shared/structured_logger.py (FIFO 20×500)
- [x] 1.4.1: Write failing tests `tests/unit/test_structured_logger.py` (writes JSON line, rotates at max_lines, caps at fifo_files)
- [x] 1.4.2: Run, expect fail
- [x] 1.4.3: Implement `shared/structured_logger.py` with threading.Lock, rotation, FIFO file naming
- [x] 1.4.4: Run, expect pass
- [x] 1.4.5: Commit "feat(logger): structured JSONL logger with FIFO rotation"

### Task 1.5: shared/message_schema.py + config/schemas/message-1.00.json
- [x] 1.5.1: Write `config/schemas/message-1.00.json` (full JSON schema per spec §4)
- [x] 1.5.2: Write failing tests `tests/unit/test_message_schema.py` (validate happy path, invalid role, missing field, dataclass round-trip)
- [x] 1.5.3: Run, expect fail
- [x] 1.5.4: Implement `shared/message_schema.py` (Message dataclass, validate_message, from_dict, to_dict)
- [x] 1.5.5: Run, expect pass
- [x] 1.5.6: Verify schema includes `references_opponent` field (H7)
- [x] 1.5.7: Verify schema includes `scoring` object with 5 axes (H5)
- [x] 1.5.8: Commit "feat(schema): JSON wire protocol 1.00 + validator + Message dataclass"

---

## Phase 2 — Provider plugin pattern

### Task 2.1: tools/registry.py (factory pattern)
- [x] 2.1.1: Write `src/agent_debate/tools/__init__.py`
- [x] 2.1.2: Write failing test `tests/unit/test_registry.py` (register, get, KeyError, duplicate-replaces)
- [x] 2.1.3: Run, expect fail
- [x] 2.1.4: Implement `tools/registry.py` (Generic[T] Registry)
- [x] 2.1.5: Run, expect pass
- [x] 2.1.6: Commit "feat(tools): generic Registry for plugin pattern (HW1 extensibility fix)"

### Task 2.2: LLMProvider abstract + LLMResponse
- [x] 2.2.1: Implement `tools/llm_provider.py` (`LLMResponse` dataclass, `LLMProvider` ABC)
- [x] 2.2.2: `LLMResponse` fields: text, tokens_in, tokens_out, finish_reason, raw_json
- [x] 2.2.3: `LLMProvider.complete(system, user, temperature, max_tokens)` abstract method
- [x] 2.2.4: Commit "feat(tools): LLMProvider ABC + LLMResponse DTO"

### Task 2.3: ClaudeLoginProvider
- [x] 2.3.1: Write failing tests `tests/unit/test_claude_login_provider.py` (mock subprocess, happy path, non-zero exit)
- [x] 2.3.2: Run, expect fail
- [x] 2.3.3: Implement `tools/claude_login_provider.py` (subprocess.run with `claude -p --append-system-prompt --output-format json --max-turns 1`)
- [x] 2.3.4: Parse JSON response, extract `result`, `usage.input_tokens`, `usage.output_tokens`
- [x] 2.3.5: Raise `RuntimeError` on non-zero exit
- [x] 2.3.6: Run, expect pass
- [x] 2.3.7: Commit "feat(tools): ClaudeLoginProvider via claude -p shell-out"

### Task 2.4: MockLLMProvider
- [x] 2.4.1: Write failing test `tests/unit/test_mock_llm_provider.py` (canned response by key, default response)
- [x] 2.4.2: Run, expect fail
- [x] 2.4.3: Implement `tools/mock_llm_provider.py` (responses dict keyed by `(skill_prefix, call_idx)`)
- [x] 2.4.4: Run, expect pass
- [x] 2.4.5: Commit "test(tools): MockLLMProvider for offline test runs"

### Task 2.5: SearchProvider abstract + SearchHit
- [x] 2.5.1: Implement `tools/search_provider.py` (`SearchHit` dataclass, `SearchProvider` ABC)
- [x] 2.5.2: Commit "feat(tools): SearchProvider ABC + SearchHit DTO"

### Task 2.6: DuckDuckGoProvider
- [x] 2.6.1: Write failing tests `tests/unit/test_duckduckgo_provider.py` (mock DDGS, happy path, empty, rate-limit)
- [x] 2.6.2: Run, expect fail
- [x] 2.6.3: Implement `tools/duckduckgo_provider.py` (DDGS context manager, parse hrefs/bodies)
- [x] 2.6.4: Add `SearchRateLimited` custom exception
- [x] 2.6.5: Catch DDGS exceptions; raise SearchRateLimited on "Ratelimit" / "429"
- [x] 2.6.6: Run, expect pass
- [x] 2.6.7: Commit "feat(tools): DuckDuckGoProvider with rate-limit detection"

### Task 2.7: MockSearchProvider
- [x] 2.7.1: Implement `tools/mock_search_provider.py` (fixed list of SearchHits)
- [x] 2.7.2: Commit "test(tools): MockSearchProvider fixed-list fixture"

### Task 2.8: WebSearchTool with fallback
- [x] 2.8.1: Write failing test `tests/unit/test_web_search.py` (happy path, fallback to citations.md on rate-limit)
- [x] 2.8.2: Run, expect fail
- [x] 2.8.3: Implement `tools/web_search.py` (wraps SearchProvider, regex-parses `references/citations.md` on RateLimited)
- [x] 2.8.4: Run, expect pass
- [x] 2.8.5: Commit "feat(tools): WebSearchTool with rate-limit fallback to cached citations"

---

## Phase 3 — Gatekeeper

### Task 3.1: ApiGatekeeper core (rubric §A4 signature)
- [x] 3.1.1: Write `tests/unit/test_gatekeeper.py` — 6 failing tests (basic execute, spend tracking, budget warn, budget hard, retry, queue_status)
- [x] 3.1.2: Run, expect 6 fail
- [x] 3.1.3: Implement `shared/gatekeeper.py` — class skeleton + `__init__` (config, shared_spend, lock, queue_capacity)
- [x] 3.1.4: Implement `execute(api_call, *args, **kwargs)` with retry-with-backoff [1,2,4]
- [x] 3.1.5: Implement `update_spend(tokens)` with Lock
- [x] 3.1.6: Implement `get_spend_so_far()` with Lock
- [x] 3.1.7: Implement `estimate_cost(n_debates)` (zero in login mode)
- [x] 3.1.8: Implement `get_queue_status()` returning QueueStatus dataclass
- [x] 3.1.9: Implement `_check_budget_hard_cap()` (raises BudgetExhausted at 95%)
- [x] 3.1.10: Implement `_enforce_rate_limit()` (raises RateLimitExceeded at requests_per_minute)
- [x] 3.1.11: Run 6 tests, expect pass
- [x] 3.1.12: Commit "feat(gatekeeper): ApiGatekeeper with rate/budget/queue/retry"

### Task 3.2: Backpressure + drain (rubric §A5)
- [x] 3.2.1: Add failing tests for FIFO queue depth, backpressure alert when full, drain when window resets
- [x] 3.2.2: Implement `enqueue()` with max_depth check
- [x] 3.2.3: Implement `drain()` for window-reset processing
- [x] 3.2.4: Implement concurrent_max semaphore
- [x] 3.2.5: Run tests, expect pass
- [x] 3.2.6: Commit "feat(gatekeeper): FIFO backpressure + drain (rubric §A5)"

---

## Phase 4 — Skills + pre-flight script

### Task 4.1: pro_skill/
- [x] 4.1.1: Create `.claude/skills/pro_skill/` directory
- [x] 4.1.2: Write `pro_skill/SKILL.md` frontmatter (name=pro-ai-originality-debater, third-person description, "pushy" triggers)
- [x] 4.1.3: Write ## Scope section (stance fixed, never concedes)
- [x] 4.1.4: Write ## Testing expectations (JSON output, opponent-reference quote, citation requirement)
- [x] 4.1.5: Write ## Tactics section (Klingemann, Edmond de Belamy, transformative-use doctrine, emergence)
- [x] 4.1.6: Write ## Drift signal keywords block (the regex inputs for DriftDetector)
- [x] 4.1.7: Write ## Output format section (JSON shape required)
- [x] 4.1.8: Verify total body ≥ 1500 words (per Anthropic best practice)
- [x] 4.1.9: Write `pro_skill/references/citations.md` (6 pre-seeded citations: Christie's, Klingemann, Ridler, transformative-use, distill.pub, Verge article)
- [x] 4.1.10: Commit "feat(skills): pro_skill SKILL.md + pre-seeded citation fallback"

### Task 4.2: con_skill/ (mirror)
- [x] 4.2.1-4.2.10: Mirror of 4.1 for Con stance (Stochastic Parrots, NYT v OpenAI, Getty v Stability, Chinese Room)
- [x] 4.2.11: Commit "feat(skills): con_skill SKILL.md + pre-seeded citation fallback"

### Task 4.3: judge_skill/
- [x] 4.3.1-4.3.10: Frontmatter + Scope (topic-blind) + Testing expectations + 5-axis scoring + PC filter rules + drift trigger keywords + reference to debate_criteria.md
- [x] 4.3.11: Commit "feat(skills): judge_skill SKILL.md (topic-blind, 5-axis)"

### Task 4.4: Canned LLM response fixtures
- [x] 4.4.1: Write `tests/fixtures/llm_responses/pro_pings.json` (10 canned pro arguments, JSON-valid)
- [x] 4.4.2: Write `tests/fixtures/llm_responses/con_pings.json` (10 canned con counters)
- [x] 4.4.3: Write `tests/fixtures/llm_responses/judge_setup.json` (2 setup_directive messages)
- [x] 4.4.4: Write `tests/fixtures/llm_responses/judge_verdict.json` (verdict with 5-axis scoring)
- [x] 4.4.5: Verify all JSON valid + schema-valid
- [x] 4.4.6: Commit "test(fixtures): canned LLM responses for integration tests"

### Task 4.5: scripts/build_judge_criteria.py (N7 originality)
- [x] 4.5.1: Implement `scripts/build_judge_criteria.py` (cache check, DDG search for parliamentary/LD/Robert's Rules)
- [x] 4.5.2: Synthesize results into markdown body
- [x] 4.5.3: Write to `.claude/skills/judge_skill/references/debate_criteria.md`
- [x] 4.5.4: Run once: `uv run python scripts/build_judge_criteria.py`
- [x] 4.5.5: Verify file created and non-empty
- [x] 4.5.6: Commit "feat(skills): pre-flight script builds Judge criteria from web (N7)"

---

## Phase 5 — Agents (Base + Partisan + Pro + Con)

### Task 5.1: BaseAgent abstract
- [x] 5.1.1: Write `src/agent_debate/agents/__init__.py`
- [x] 5.1.2: Write failing test `tests/unit/test_base_agent.py` (init with role, emit_heartbeat, step delegates to handle_message, SIGTERM sets _shutdown)
- [x] 5.1.3: Run, expect fail
- [x] 5.1.4: Implement `agents/base_agent.py` — abstract class with role, queues, shared_spend, lock, skill_dir, llm_provider
- [x] 5.1.5: Implement `emit_heartbeat()` putting `{role, ts}` on heartbeat_queue
- [x] 5.1.6: Implement `step(msg)` delegating to `handle_message(msg)` (test seam)
- [x] 5.1.7: Implement `_on_sigterm()` setting `self._shutdown = True`
- [x] 5.1.8: Register `signal.SIGTERM` handler in `__init__`
- [x] 5.1.9: Run tests, expect pass
- [x] 5.1.10: Commit "feat(agents): BaseAgent abstract with step() test seam"

### Task 5.2: PartisanAgent (shared Pro/Con logic)
- [x] 5.2.1: Write failing tests `tests/unit/test_partisan_agent.py` (load_skill_body strips frontmatter, opponent-reference regex, citation extractor)
- [x] 5.2.2: Implement `load_skill_body()` reading `<skill_dir>/SKILL.md`, stripping YAML frontmatter via regex
- [x] 5.2.3: Implement `enforce_opponent_reference(text, prev_opponent_text) -> bool` using regex/substring match
- [x] 5.2.4: Implement `extract_citations(text) -> list[Citation]` parsing URL patterns
- [x] 5.2.5: Implement `handle_message(msg)` orchestrating: validate → load skill → call LLM via Gatekeeper → set references_opponent → emit
- [x] 5.2.6: Run tests, expect pass
- [x] 5.2.7: Commit "feat(agents): PartisanAgent with skill loader + opponent-reference + citation extractor"

### Task 5.3: ProAgent
- [x] 5.3.1: Write failing test `tests/unit/test_pro_agent.py` (STANCE = ORIGINALITY, SKILL_NAME = pro_skill)
- [x] 5.3.2: Implement `agents/pro_agent.py` (thin subclass of PartisanAgent)
- [x] 5.3.3: Run, expect pass
- [x] 5.3.4: Commit "feat(agents): ProAgent — AI=ORIGINALITY stance"

### Task 5.4: ConAgent
- [x] 5.4.1-5.4.4: Mirror of 5.3 for Con stance
- [x] 5.4.5: Commit "feat(agents): ConAgent — AI=REMIX_ONLY stance"

---

## Phase 6 — Judge + sub-components

### Task 6.1: JudgeAgent
- [x] 6.1.1: Write failing tests `tests/unit/test_judge_agent.py` — 18 tests (setup_directive issuance, routing pro→con, drift→correction_request, PC→intervention, scoring, no-tie enforcement, topic-blind prompt assembly)
- [x] 6.1.2: Run, expect fail
- [x] 6.1.3: Implement `agents/judge_agent.py` skeleton (topic_blind=True, composes DriftDetector/PCFilter/ScoringEngine)
- [x] 6.1.4: Implement `issue_setup_directives()` (sends 2 messages, awaits 2 acks)
- [x] 6.1.5: Implement `route(msg)` (Pro msg → Con's in_queue, Con msg → Pro's in_queue)
- [x] 6.1.6: Wire DriftDetector check (call before forwarding; on drift → correction_request)
- [x] 6.1.7: Wire PCFilter check (call before forwarding; on violation → intervention)
- [x] 6.1.8: Implement `declare_winner(scorecards)` with no-tie enforcement (H5)
- [x] 6.1.9: Assert topic_blind: system prompt assembly excludes topic words
- [x] 6.1.10: Run tests, expect 18 pass
- [x] 6.1.11: Commit "feat(agents): JudgeAgent with routing + drift + PC + scoring + no-tie"

### Task 6.2: DriftDetector
- [x] 6.2.1: Write failing tests `tests/unit/test_drift_detector.py` (detects concession, passes normal, case-insensitive)
- [x] 6.2.2: Implement `agents/drift_detector.py` (case-insensitive alternation regex from keyword set)
- [x] 6.2.3: Run, expect pass
- [x] 6.2.4: Commit "feat(agents): DriftDetector stance-keyword regex (no extra LLM)"

### Task 6.3: PCFilter
- [x] 6.3.1: Write failing tests `tests/unit/test_pc_filter.py` (detects vulgar, returns sanitized, passes clean)
- [x] 6.3.2: Implement `agents/pc_filter.py` with vulgar keyword set + sanitize-with-asterisks
- [x] 6.3.3: Run, expect pass
- [x] 6.3.4: Commit "feat(agents): PCFilter for H16 vulgar-language gate"

### Task 6.4: ScoringEngine
- [x] 6.4.1: Write failing tests `tests/unit/test_scoring_engine.py` (5-axis × 20 = 100 max, differential no-tie, tiebreak by role_fidelity then random)
- [x] 6.4.2: Implement `Scorecard` dataclass (per-axis scores, total property)
- [x] 6.4.3: Implement `score_axis_set(axes) -> Scorecard`
- [x] 6.4.4: Implement `declare_winner(pro_score, con_score) -> str` with tiebreak chain
- [x] 6.4.5: Run, expect pass
- [x] 6.4.6: Write `.claude/skills/judge_skill/scripts/compute_scores.py` (CLI helper that the judge skill can shell-out to)
- [x] 6.4.7: Commit "feat(agents): ScoringEngine 5-axis + no-tie enforcer"

---

## Phase 7 — Orchestration

### Task 7.1: LifecycleRegistry (8 hooks)
- [x] 7.1.1: Write `src/agent_debate/orchestration/__init__.py`
- [x] 7.1.2: Write failing tests `tests/unit/test_lifecycle_registry.py` (register+fire in order, unknown hook silently passes, exception in one hook doesn't break chain)
- [x] 7.1.3: Implement `orchestration/lifecycle_registry.py` (dict of hook_name → list[callable])
- [x] 7.1.4: Implement `register(name, fn)` + `fire(name, context)` with try/except per hook
- [x] 7.1.5: Run, expect pass
- [x] 7.1.6: Commit "feat(orchestration): LifecycleRegistry with 8 hooks (rubric §A9)"

### Task 7.2: DebateOrchestrator — spawn_children
- [x] 7.2.1: Write failing test — `spawn_children()` returns 3 Process objects
- [x] 7.2.2: Write failing test — `spawn_children()` creates 6 mp.Queue (in/out per child)
- [x] 7.2.3: Write failing test — `spawn_children()` creates 1 heartbeat_queue (shared)
- [x] 7.2.4: Write failing test — shared spend Value + Lock injected into each child
- [x] 7.2.5: Write failing test — each child receives correct role + skill_dir
- [x] 7.2.6: Implement `spawn_children()` returning `tuple[Process, Process, Process]`
- [x] 7.2.7: Implement Queue creation
- [x] 7.2.8: Implement shared spend + Lock injection via Process kwargs
- [x] 7.2.9: Implement role+skill_dir assignment per child
- [x] 7.2.10: Run tests, expect 5 pass
- [x] 7.2.11: Commit "feat(orchestration): spawn_children with Queues + shared spend"

### Task 7.2.b: Two-phase boot
- [x] 7.2.12: Write failing test — Judge sends 2 setup_directive messages on boot
- [x] 7.2.13: Write failing test — Pro and Con both send ack before debate loop opens
- [x] 7.2.14: Write failing test — debate loop blocks if ack missing (timeout 10s → abort)
- [x] 7.2.15: Implement Phase A logic in `run_debate()` — issue setup_directives, await acks
- [x] 7.2.16: Run tests, expect 3 pass
- [x] 7.2.17: Commit "feat(orchestration): two-phase boot (H18 setup_directive + ack)"

### Task 7.2.c: Debate loop with lifecycle hooks
- [x] 7.2.18: Write failing test — `before_round` hook fires before each ping
- [x] 7.2.19: Write failing test — `after_round` hook fires after each ping
- [x] 7.2.20: Write failing test — `before_verdict` and `after_verdict` fire on verdict
- [x] 7.2.21: Implement debate loop iterating 2× n_pings turns
- [x] 7.2.22: Wire lifecycle hook firings at boundaries
- [x] 7.2.23: Implement message routing from child to Judge to opponent
- [x] 7.2.24: Run tests, expect 3 pass
- [x] 7.2.25: Commit "feat(orchestration): debate loop with 8 lifecycle hooks (rubric §A9)"

### Task 7.2.d: Transcript assembly + persistence
- [x] 7.2.26: Write failing test — Transcript dataclass captures all messages in order
- [x] 7.2.27: Write failing test — `persist_transcript()` writes JSON to transcripts/
- [x] 7.2.28: Implement `Transcript` dataclass (msgs, verdict, started_at, finished_at)
- [x] 7.2.29: Implement `persist_transcript()` with filename `<YYYY-MM-DD-HHMM>-<topic-slug>.json`
- [x] 7.2.30: Run tests, expect 2 pass
- [x] 7.2.31: Commit "feat(orchestration): Transcript dataclass + JSON persistence"

### Task 7.2.e: Graceful shutdown
- [x] 7.2.32: Write failing test — `shutdown_gracefully()` sends SIGTERM to each child
- [x] 7.2.33: Write failing test — main waits up to 10s for children to drain
- [x] 7.2.34: Write failing test — stragglers get SIGKILL after 10s
- [x] 7.2.35: Write failing test — partial transcript saved as `aborted-*.json`
- [x] 7.2.36: Implement SIGINT/SIGTERM handler in main
- [x] 7.2.37: Implement cascade with 10s drain
- [x] 7.2.38: Implement aborted-transcript fallback
- [x] 7.2.39: Run tests, expect 4 pass
- [x] 7.2.40: Commit "feat(orchestration): graceful shutdown cascade"

---

## Phase 8 — Watchdog

### Task 8.1: Watchdog — heartbeat polling
- [ ] 8.1.1: Write failing test — Watchdog reads from heartbeat_queue
- [ ] 8.1.2: Write failing test — updates `last_heartbeat[pid]` on each ping
- [ ] 8.1.3: Write failing test — polling interval = 2s (config-driven)
- [ ] 8.1.4: Implement `Watchdog.__init__` with poll_interval, stuck_timeout, max_restarts
- [ ] 8.1.5: Implement `monitor()` loop reading heartbeat_queue non-blocking
- [ ] 8.1.6: Run tests, expect 3 pass
- [ ] 8.1.7: Commit "feat(watchdog): heartbeat polling loop"

### Task 8.1.b: Two-signal stuck detection
- [ ] 8.1.8: Write failing test — `_is_stuck(child)` returns True if `is_alive() == False`
- [ ] 8.1.9: Write failing test — `_is_stuck(child)` returns True if heartbeat age > stuck_timeout
- [ ] 8.1.10: Write failing test — `_is_stuck(child)` returns False if both signals are healthy
- [ ] 8.1.11: Implement two-signal `_is_stuck()`
- [ ] 8.1.12: Run tests, expect 3 pass
- [ ] 8.1.13: Commit "feat(watchdog): two-signal stuck detection (alive + heartbeat-staleness)"

### Task 8.1.c: Restart with backoff
- [ ] 8.1.14: Write failing test — first restart waits 1s
- [ ] 8.1.15: Write failing test — second restart waits 2s
- [ ] 8.1.16: Write failing test — third restart waits 4s
- [ ] 8.1.17: Write failing test — `_restart()` calls SIGKILL on stuck child first
- [ ] 8.1.18: Implement `_restart(child, restart_idx)` with backoff array `[1, 2, 4]`
- [ ] 8.1.19: Implement child SIGKILL + Queue drain + Process recreation
- [ ] 8.1.20: Run tests, expect 4 pass
- [ ] 8.1.21: Commit "feat(watchdog): restart with exponential backoff"

### Task 8.1.d: State replay on restart
- [ ] 8.1.22: Write failing test — respawned child receives the same shared_spend Value
- [ ] 8.1.23: Write failing test — respawned child receives the same skill_dir
- [ ] 8.1.24: Write failing test — respawned child receives the most-recent setup_directive
- [ ] 8.1.25: Implement state replay — read last setup_directive from in-memory transcript
- [ ] 8.1.26: Implement state injection on respawn
- [ ] 8.1.27: Run tests, expect 3 pass
- [ ] 8.1.28: Commit "feat(watchdog): state replay on restart"

### Task 8.1.e: Max-restarts fail-fast
- [ ] 8.1.29: Write failing test — after 3 restarts, `_on_unrecoverable` fires
- [ ] 8.1.30: Write failing test — `_on_unrecoverable` emits `debate_aborted` verdict
- [ ] 8.1.31: Write failing test — `_on_unrecoverable` signals main to exit
- [ ] 8.1.32: Implement `_on_unrecoverable(child)` with verdict emission
- [ ] 8.1.33: Run tests, expect 3 pass
- [ ] 8.1.34: Commit "feat(watchdog): fail-fast after max_restarts"

---

## Phase 9 — SDK + Menu + main

### Task 9.1.a: DebateSDK.run_debate
- [ ] 9.1.1: Write `src/agent_debate/sdk/__init__.py`
- [ ] 9.1.2: Write failing test — `run_debate(topic, n_pings)` returns Transcript
- [ ] 9.1.3: Write failing test — `run_debate` raises on invalid n_pings (<1 or >100)
- [ ] 9.1.4: Implement `DebateSDK.__init__` taking Config + Orchestrator
- [ ] 9.1.5: Implement `run_debate(topic, n_pings=10)` delegating to Orchestrator
- [ ] 9.1.6: Run tests, expect pass
- [ ] 9.1.7: Commit "feat(sdk): run_debate entry"

### Task 9.1.b: get_transcript + list_debates
- [ ] 9.1.8: Write failing test — `get_transcript(debate_id)` loads JSON from transcripts/
- [ ] 9.1.9: Write failing test — `get_transcript` raises FileNotFoundError on unknown id
- [ ] 9.1.10: Write failing test — `list_debates()` returns chronologically-sorted DebateMetadata
- [ ] 9.1.11: Implement `get_transcript` + `list_debates`
- [ ] 9.1.12: Run tests, expect pass
- [ ] 9.1.13: Commit "feat(sdk): get_transcript + list_debates"

### Task 9.1.c: get_spend_report (rubric §A8)
- [ ] 9.1.14: Write `SpendReport` frozen dataclass in `sdk/dtos.py` (total_input_tokens, total_output_tokens, estimated_cost_usd, pct_of_budget_used, by_agent)
- [ ] 9.1.15: Write failing test — `get_spend_report()` returns SpendReport with correct totals
- [ ] 9.1.16: Write failing test — `by_agent` keyed by AgentRole values
- [ ] 9.1.17: Write failing test — `estimated_cost_usd` is Decimal("0.00") in login mode
- [ ] 9.1.18: Implement `get_spend_report()` reading from shared spend Value
- [ ] 9.1.19: Run tests, expect pass
- [ ] 9.1.20: Commit "feat(sdk): get_spend_report DTO"

### Task 9.1.d: simulate_keystroke (N8 self-test)
- [ ] 9.1.21: Write failing test — `simulate_keystroke('A')` invokes run_debate
- [ ] 9.1.22: Write failing test — `simulate_keystroke('X')` returns exit MenuResponse
- [ ] 9.1.23: Write failing test — `simulate_keystroke('Z')` returns error MenuResponse
- [ ] 9.1.24: Implement `simulate_keystroke(key)` dispatching to menu logic
- [ ] 9.1.25: Run tests, expect pass
- [ ] 9.1.26: Commit "feat(sdk): simulate_keystroke for N8 self-test"

### Task 9.1.e: get_health_status
- [ ] 9.1.27: Write `HealthStatus` frozen dataclass (children_alive, last_heartbeat_ages, pending_messages, restart_count)
- [ ] 9.1.28: Write failing test — `get_health_status()` returns HealthStatus with current state
- [ ] 9.1.29: Implement `get_health_status()` reading from Watchdog
- [ ] 9.1.30: Run tests, expect pass
- [ ] 9.1.31: Commit "feat(sdk): get_health_status + HealthStatus DTO"

### Task 9.2: DTOs (SpendReport, HealthStatus)
- [ ] 9.2.1: Add `SpendReport` frozen dataclass to `sdk/debate_sdk.py` (total_input_tokens, total_output_tokens, estimated_cost_usd, pct_of_budget_used, by_agent)
- [ ] 9.2.2: Add `HealthStatus` frozen dataclass (children_alive, last_heartbeat_ages, pending_messages, restart_count)
- [ ] 9.2.3: Commit (folded into 9.1.25)

### Task 9.3: TerminalMenu
- [ ] 9.3.1-9.3.5: Tests + impl for letter-keyed dispatch (A/B/C/D/E/X)
- [ ] 9.3.6-9.3.10: render() returns multiline string with menu options
- [ ] 9.3.11-9.3.13: dispatch(key) calls correct SDK method, returns MenuResponse
- [ ] 9.3.14: Commit "feat(menu): letter-keyed terminal UI (H11 + N8)"

### Task 9.4: main.py entry point
- [ ] 9.4.1: Implement `src/agent_debate/main.py` (load_config → DebateSDK → TerminalMenu.run)
- [ ] 9.4.2: Verify `uv run agent-debate` launches menu
- [ ] 9.4.3: Press X to exit, verify clean shutdown
- [ ] 9.4.4: Commit "feat: main.py CLI entry point"

---

## Phase 10 — Integration + E2E tests

### Task 10.1: test_full_debate_mocked.py (H1, H2, H3, H4, H5, H7, H18, H20)
- [ ] 10.1.1-10.1.10: Spawn 3 real processes with MockLLMProvider via config override
- [ ] 10.1.11-10.1.15: Assert all 20 turns logged
- [ ] 10.1.16-10.1.18: Assert no direct Pro↔Con messages
- [ ] 10.1.19-10.1.20: Assert JSON validity on every message
- [ ] 10.1.21: Assert references_opponent=true on every argument/counter
- [ ] 10.1.22: Assert verdict declared with differential scoring
- [ ] 10.1.23: Commit "test(int): full debate end-to-end mocked"

### Task 10.2: test_drift_correction.py (H20)
- [ ] 10.2.1-10.2.5: Inject stance-violating canned response → assert correction_request fires → assert agent re-emits
- [ ] 10.2.6: Commit

### Task 10.3: test_pc_intervention.py (H16)
- [ ] 10.3.1-10.3.5: Inject vulgar canned response → assert intervention fires → assert sanitized re-emit
- [ ] 10.3.6: Commit

### Task 10.4: test_chaos_child_kill.py (H21)
- [ ] 10.4.1-10.4.5: Start debate; os.kill(child_pid, SIGKILL) mid-ping; assert Watchdog respawns within stuck_timeout; assert debate completes
- [ ] 10.4.6: Commit

### Task 10.5: test_chaos_child_hang.py (H21)
- [ ] 10.5.1-10.5.5: Mock LLM with `time.sleep(60)` (longer than stuck_timeout); assert Watchdog detects via heartbeat staleness; assert SIGKILL+respawn
- [ ] 10.5.6: Commit

### Task 10.6: test_budget_exhausted.py (rubric §A8)
- [ ] 10.6.1-10.6.5: Pre-spend 190K tokens (95% of 200K); start debate; assert early verdict with `budget_exhausted` marker
- [ ] 10.6.6: Commit

### Task 10.7: test_graceful_shutdown.py
- [ ] 10.7.1-10.7.5: Start debate; send SIGINT mid-debate; assert all 3 children exit cleanly; assert `aborted-*.json` partial transcript created
- [ ] 10.7.6: Commit

### Task 10.8: test_no_tie_enforcer.py (H5)
- [ ] 10.8.1-10.8.5: Mock LLM returns identical Pro/Con scores; assert Judge tiebreaks by role_fidelity (or random) — never returns "tie"
- [ ] 10.8.6: Commit

### Task 10.9: test_setup_directive_ack.py (H18)
- [ ] 10.9.1-10.9.5: Spawn 3 children; assert Phase A messages (2× setup_directive + 2× ack) precede Phase B (first argument)
- [ ] 10.9.6: Commit

### Task 10.10: E2E — test_real_debate_5_pings.py
- [ ] 10.10.1: @pytest.mark.e2e
- [ ] 10.10.2: Run real 5-ping debate against actual Claude CLI + DDG
- [ ] 10.10.3: Assert transcript persisted, verdict declared
- [ ] 10.10.4: Commit "test(e2e): real-Claude 5-ping debate sanity check"

### Task 10.11: E2E — test_real_search_dual.py (H24)
- [ ] 10.11.1: Pro emits citation; Con's next turn fact-checks via DDG
- [ ] 10.11.2: Assert both `citations` arrays populated in transcript
- [ ] 10.11.3: Commit

### Task 10.12: E2E — test_real_pc_filter.py
- [ ] 10.12.1: Inject vulgar text through a custom prompt; assert Judge intercepts before re-broadcast
- [ ] 10.12.2: Commit

---

## Phase 11 — Per-mechanism PRDs + ADRs + LICENSE

(Phase A.4-A.12 in the Phase A docs section above — written before code execution begins, as part of approval gate #2)

### Task 11.5a: docs/PRD_judge_agent.md (~250 lines)
- [ ] 11.5a.1: Frontmatter + Input/Output/Setup docstring shape
- [ ] 11.5a.2: Theoretical background (parliamentary debate moderation)
- [ ] 11.5a.3: Functional requirements (H4, H5, H16, H18, H19, H20)
- [ ] 11.5a.4: Performance metrics (response latency, drift-correction frequency)
- [ ] 11.5a.5: Constraints + alternatives considered
- [ ] 11.5a.6: Test scenarios (8 scenarios)
- [ ] 11.5a.7: Commit

### Task 11.5b: docs/PRD_pro_agent.md (~150 lines)
- [ ] 11.5b.1: Frontmatter + Input/Output/Setup docstring shape
- [ ] 11.5b.2: Stance description + tactics (AI=ORIGINALITY)
- [ ] 11.5b.3: Functional requirements (H1, H2, H7, H8, H24)
- [ ] 11.5b.4: Citation extractor specification
- [ ] 11.5b.5: Test scenarios (≥5)
- [ ] 11.5b.6: Commit

### Task 11.5c: docs/PRD_con_agent.md (~150 lines)
- [ ] 11.5c.1-5: Mirror of 11.5b for Con (AI=REMIX_ONLY)
- [ ] 11.5c.6: Commit

### Task 11.5d: docs/PRD_orchestrator.md (~200 lines)
- [ ] 11.5d.1: Frontmatter + I/O/S docstring
- [ ] 11.5d.2: Process spawning lifecycle
- [ ] 11.5d.3: Lifecycle hook contracts (8 hooks)
- [ ] 11.5d.4: Two-phase boot specification
- [ ] 11.5d.5: Transcript persistence pattern
- [ ] 11.5d.6: Graceful shutdown cascade
- [ ] 11.5d.7: Test scenarios (≥6)
- [ ] 11.5d.8: Commit

### Task 11.5e: docs/PRD_ipc_bus.md (~200 lines)
- [ ] 11.5e.1: Wire protocol overview
- [ ] 11.5e.2: Message schema (reference config/schemas/message-1.00.json)
- [ ] 11.5e.3: 8 message roles enumerated
- [ ] 11.5e.4: Queue topology (6 in/out + 1 heartbeat)
- [ ] 11.5e.5: Backpressure + drain semantics
- [ ] 11.5e.6: ADR-001 cross-reference
- [ ] 11.5e.7: Commit

### Task 11.5f: docs/PRD_gatekeeper.md (~250 lines)
- [ ] 11.5f.1: Frontmatter + I/O/S docstring (matches rubric §A4 verbatim)
- [ ] 11.5f.2: Rate limit policy specification
- [ ] 11.5f.3: Token budget thresholds (75% warn, 95% hard cap)
- [ ] 11.5f.4: Retry-with-backoff policy
- [ ] 11.5f.5: FIFO queue + backpressure (rubric §A5)
- [ ] 11.5f.6: Spend tracking via shared Value+Lock (ADR-006)
- [ ] 11.5f.7: Cache strategy note (lec04 abstract §5.1)
- [ ] 11.5f.8: Test scenarios (≥8)
- [ ] 11.5f.9: Commit

### Task 11.5g: docs/PRD_watchdog.md (~150 lines)
- [ ] 11.5g.1: Frontmatter + I/O/S docstring
- [ ] 11.5g.2: Heartbeat contract
- [ ] 11.5g.3: Two-signal detection rationale
- [ ] 11.5g.4: Restart-with-state-replay specification
- [ ] 11.5g.5: Fail-fast threshold (max_restarts=3)
- [ ] 11.5g.6: Two-thread-per-child contract (resolves PRD Open Q1)
- [ ] 11.5g.7: Test scenarios (≥5)
- [ ] 11.5g.8: Commit

### Task 11.5h: docs/PRD_skills.md (~150 lines)
- [ ] 11.5h.1: Frontmatter + I/O/S docstring
- [ ] 11.5h.2: Frontmatter contract (name, description, third-person)
- [ ] 11.5h.3: Loading discipline (statically as system prompt — ADR-002)
- [ ] 11.5h.4: Reference-file resolution (references/citations.md)
- [ ] 11.5h.5: Drift-keyword block specification
- [ ] 11.5h.6: Project-local enforcement (H17)
- [ ] 11.5h.7: Commit

### Task 11.5i: docs/PRD_web_search_tool.md (~150 lines)
- [ ] 11.5i.1: Frontmatter + I/O/S docstring
- [ ] 11.5i.2: SearchProvider ABC + plug-in pattern
- [ ] 11.5i.3: DuckDuckGoProvider default + Brave/Tavily seams
- [ ] 11.5i.4: Rate-limit fallback to cached citations
- [ ] 11.5i.5: Dual purpose (citation + fact-check, H24)
- [ ] 11.5i.6: Test scenarios (≥5)
- [ ] 11.5i.7: Commit

### Task 11.6: ADRs — one file each (Context / Decision / Consequences / Alternatives format)

**Task 11.6.a: ADR-001 — IPC = multiprocessing.Queue**
- [ ] 11.6.1.1: Write Context section (Lec05 L399 enumerates 4 primitives)
- [ ] 11.6.1.2: Write Decision (mp.Queue chosen)
- [ ] 11.6.1.3: Write Alternatives (Signal / FIFO / Socket — rejection rationale)
- [ ] 11.6.1.4: Write Consequences (positive + negative)
- [ ] 11.6.1.5: Commit "docs(adr): ADR-001 IPC queue rationale"

**Task 11.6.b: ADR-002 — Skills loaded statically as system prompts**
- [ ] 11.6.2.1: Write Context (deterministic role assignment required)
- [ ] 11.6.2.2: Write Decision (filesystem read at boot, --append-system-prompt)
- [ ] 11.6.2.3: Write Alternatives (Claude auto-discovery — risk of wrong skill)
- [ ] 11.6.2.4: Write Consequences
- [ ] 11.6.2.5: Commit

**Task 11.6.c: ADR-003 — Claude CLI shell-out**
- [ ] 11.6.3.1: Write Context (login mode = $0 cost)
- [ ] 11.6.3.2: Write Decision (`claude -p` via subprocess.run)
- [ ] 11.6.3.3: Write Alternatives (anthropic SDK — needs API key)
- [ ] 11.6.3.4: Write Consequences
- [ ] 11.6.3.5: Commit

**Task 11.6.d: ADR-004 — Search pluggable, DDG default**
- [ ] 11.6.4.1: Write Context (zero-config for grader)
- [ ] 11.6.4.2: Write Decision (DuckDuckGoProvider default)
- [ ] 11.6.4.3: Write Alternatives (Brave / Tavily / Perplexity)
- [ ] 11.6.4.4: Write Consequences
- [ ] 11.6.4.5: Commit

**Task 11.6.e: ADR-005 — Same-provider mitigation**
- [ ] 11.6.5.1: Write Context (H8 risk when Pro=Con=Claude)
- [ ] 11.6.5.2: Write Decision (temperature spread + Skill differentiation)
- [ ] 11.6.5.3: Write Alternatives (mixed providers — gives up zero-cost)
- [ ] 11.6.5.4: Write Consequences
- [ ] 11.6.5.5: Commit

**Task 11.6.f: ADR-006 — Cross-process spend tracking**
- [ ] 11.6.6.1: Write Context (global token budget = single source of truth)
- [ ] 11.6.6.2: Write Decision (mp.Value + Lock injected into each child)
- [ ] 11.6.6.3: Write Alternatives (per-child Gatekeeper — risk of independent cap violation)
- [ ] 11.6.6.4: Write Consequences (lock contention <1ms)
- [ ] 11.6.6.5: Commit

**Task 11.6.g: ADR-007 — Judge criteria pre-flight**
- [ ] 11.6.7.1: Write Context (lec05 L1519-1528 — search the world for #1 debate expert)
- [ ] 11.6.7.2: Write Decision (scripts/build_judge_criteria.py one-off DDG search)
- [ ] 11.6.7.3: Write Alternatives (hardcoded rubric — lose originality bonus)
- [ ] 11.6.7.4: Write Consequences
- [ ] 11.6.7.5: Commit

### Task 11.7: LICENSE
- [ ] 11.7.1: Write MIT license with year 2026 and authors Salah Qadah + Andalus Kalash
- [ ] 11.7.2: Commit "docs: add MIT LICENSE"

### Task 11.8: 🛑 Approval gate #2 (rubric §2.5 step 5)
- [ ] 11.8.1: Summarize the docs bundle (PRD + PLAN + TODO + 9 per-mechanism PRDs + 7 ADRs + LICENSE) for user review
- [ ] 11.8.2: PAUSE — wait for user "approved gate 2"
- [ ] 11.8.3: After approval, mark gate cleared with `docs: full docs bundle approved by user — gate 2 cleared` empty commit

### Task 11.1: README.md (post-execution — see Phase 11.1 below)
(README is written AFTER all code phases complete — per Dr. Segal's slide and lec01 L1247-1250)

---

## Phase 11.1 (post-execution) — README.md

### Task 11.1.1: Title + intro (quote 16× thesis + Context Engineering thesis verbatim)
- [ ] 11.1.1.1: H1 title + one-paragraph elevator pitch
- [ ] 11.1.1.2: Quote rubric §A2 + §A24 verbatim Hebrew + English

### Task 11.1.2: Installation
- [ ] 11.1.2.1: Prerequisites (Python 3.13, uv, Claude CLI logged in, git)
- [ ] 11.1.2.2: Step-by-step setup commands
- [ ] 11.1.2.3: Troubleshooting common issues (claude not found, DDG rate limit, etc.)

### Task 11.1.3: Usage
- [ ] 11.1.3.1: How to launch the menu (`uv run agent-debate`)
- [ ] 11.1.3.2: Menu legend (A/B/C/D/E/X)
- [ ] 11.1.3.3: How to swap LLM provider (config-only change)
- [ ] 11.1.3.4: How to plug in a new search backend (Brave/Tavily example)

### Task 11.1.4: Architecture
- [ ] 11.1.4.1: Embed class diagram (Mermaid block from PLAN.md §4)
- [ ] 11.1.4.2: Embed C2 container diagram
- [ ] 11.1.4.3: Embed UML sequence diagram
- [ ] 11.1.4.4: Brief seven-layer recap

### Task 11.1.5: Configuration guide
- [ ] 11.1.5.1: Document every field in `setup.json`
- [ ] 11.1.5.2: Document every field in `agents.json`
- [ ] 11.1.5.3: Document every field in `debate_rules.json`
- [ ] 11.1.5.4: Document every field in `rate_limits.json`
- [ ] 11.1.5.5: Document every field in `logging_config.json`

### Task 11.1.6: Session-1 full dialogue dump (spec §8.7 MANDATE)
- [ ] 11.1.6.1: Copy `transcripts/sample-session-1.json` into a fenced code block in README
- [ ] 11.1.6.2: Add a "Sample debate" narrative wrapper

### Task 11.1.7: Manual Phase 1 evidence (H22)
- [ ] 11.1.7.1: Embed `assets/manual-phase1-*.png` screenshots
- [ ] 11.1.7.2: Add a "Manual exploration" narrative section

### Task 11.1.8: Cost analysis (rubric §11)
- [ ] 11.1.8.1: Token cost table (input/output, total per debate)
- [ ] 11.1.8.2: Optimization strategies subsection (token reduction, cache-friendly prompts)
- [ ] 11.1.8.3: Note: cost = $0 in login mode; numbers shown for the API-key alternative

### Task 11.1.9: Behavior notes (N5)
- [ ] 11.1.9.1: Section: "Outcomes are deliberately non-reproducible"
- [ ] 11.1.9.2: Quote lec05 L1581-1597

### Task 11.1.10: Extension points (rubric §A9)
- [ ] 11.1.10.1: List 8 lifecycle hooks with example usage
- [ ] 11.1.10.2: Document LLMProvider + SearchProvider plugin pattern

### Task 11.1.11: AI usage disclosure (verbatim syllabus)
- [ ] 11.1.11.1: Quote syllabus paragraph verbatim Hebrew + English
- [ ] 11.1.11.2: Pointer to `docs/PROMPTS.md` audit trail

### Task 11.1.12: License + credits
- [ ] 11.1.12.1: MIT license reference
- [ ] 11.1.12.2: Author credits (Salah + Andalus + AI agent acknowledgement)

### Task 11.1.13: README quality checks
- [ ] 11.1.13.1: `wc -l README.md` — verify ≥ 200 lines
- [ ] 11.1.13.2: Verify every Mermaid block renders on GitHub (open repo in browser)
- [ ] 11.1.13.3: Verify session-1 dialogue is the FULL debate, not a truncated excerpt
- [ ] 11.1.13.4: Commit "docs: README.md (full user manual + session-1 dialogue)"

---

## Phase 12 — Manual phase + run + push + submit

### Task 12.1: Manual Phase 1 evidence (lec05 L1896-1909)
- [ ] 12.1.1: Open two terminals
- [ ] 12.1.2: Launch Claude CLI in each
- [ ] 12.1.3: Assign Pro role to terminal A, Con role to terminal B
- [ ] 12.1.4: Manually drive 5-6 exchanges (copy-paste between terminals)
- [ ] 12.1.5: Screenshot terminal A
- [ ] 12.1.6: Screenshot terminal B
- [ ] 12.1.7: Screenshot the moment of mutual reference (Pro quoting Con's earlier point)
- [ ] 12.1.8: Save as `assets/manual-phase1-{a,b,reference}.png`
- [ ] 12.1.9: Embed in README "Manual exploration" section
- [ ] 12.1.10: Commit "docs: manual Phase 1 evidence + screenshots (H22)"

### Task 12.2: Run the actual system end-to-end (lifecycle step 7)
- [ ] 12.2.1: `uv run agent-debate`
- [ ] 12.2.2: Press A → start debate
- [ ] 12.2.3: Wait for verdict (~5-8 minutes)
- [ ] 12.2.4: Verify `transcripts/<id>.json` landed
- [ ] 12.2.5: Copy to `transcripts/sample-session-1.json`
- [ ] 12.2.6: Screenshot the menu, debate-running view, verdict view, spend report
- [ ] 12.2.7: Save screenshots to `assets/screenshot-*.png`
- [ ] 12.2.8: Embed transcript + screenshots in README
- [ ] 12.2.9: Commit "docs: sample-session-1.json + screenshots (spec §8.7)"

### Task 12.3: Final audit-gate verification
- [ ] 12.3.1: `uv run ruff check src tests` → 0 errors
- [ ] 12.3.2: `uv run pytest tests/unit tests/integration --cov` → ≥85%
- [ ] 12.3.3: `uv run python scripts/check_file_lines.py` → 0 violations
- [ ] 12.3.4: Grep for secrets: `grep -rE "sk-[a-zA-Z0-9_-]{20,}" src tests` → empty
- [ ] 12.3.5: `git log --oneline | wc -l` → ≥ 50
- [ ] 12.3.6: Verify `docs/diagrams/class-diagram.svg` exists (export Mermaid)
- [ ] 12.3.7: Verify README has session-1 dialogue (grep for transcript marker)
- [ ] 12.3.8: Verify README has cost analysis table
- [ ] 12.3.9: Verify `.env-example` exists; `.env` NOT in `git ls-files`
- [ ] 12.3.10: Verify all 5 config files version 1.00
- [ ] 12.3.11: Verify `docs/PROMPTS.md` ≥ 20 prompt entries

### Task 12.4: Push to GitHub PUBLIC (lifecycle step 8)
- [ ] 12.4.1: Confirm Andalus's GitHub handle (open question — ASK USER if not provided)
- [ ] 12.4.2: `gh repo create salah-dev-stu/uoh-sqak-ex02 --public --source=. --remote=origin`
- [ ] 12.4.3: Add Andalus as collaborator: `gh api repos/.../collaborators/<handle> --method PUT`
- [ ] 12.4.4: `git push -u origin main`
- [ ] 12.4.5: Open repo URL in incognito window — verify public viewable (NO sign-in prompt)
- [ ] 12.4.6: If private, run `gh repo edit --visibility public --accept-visibility-change-consequences`
- [ ] 12.4.7: Verify lecturer email shared OR repo is public (H14)
- [ ] 12.4.8: Final commit + push

### Task 12.5: Submission PDF + Moodle upload (H15)
- [ ] 12.5.1: `uv run python scripts/fill_submission_pdf.py`
- [ ] 12.5.2: Verify generated `uoh-sqak-ex02.pdf` has: exercise=02, group=uoh-sqak, self-grade=85
- [ ] 12.5.3: Verify Student 1: Salah Qadah, ID 323039974
- [ ] 12.5.4: Verify Student 2: Andalus Kalash, ID 211435797
- [ ] 12.5.5: Verify repo URL is the public one
- [ ] 12.5.6: Verify late submission field (no — unless past deadline)
- [ ] 12.5.7: Upload PDF to Moodle assignment id=264177 (Salah's account)
- [ ] 12.5.8: Andalus uploads same PDF to his Moodle account separately
- [ ] 12.5.9: Take screenshot of Moodle confirmation
- [ ] 12.5.10: Commit "submit: uoh-sqak-ex02.pdf uploaded to Moodle"

---

## "Be very critical" verify pass — added tasks (Dr. Segal's prompt: "Verify that all PRD demand implemented in the todo list. You must be very critical.")

Per lec01 L1199-1201, this pass typically adds ~200 missed tasks. The current task count above is **~600**. Below are the items the verify pass surfaces from re-reading `docs/PRD.md` requirement-by-requirement.

### V1: H-gate audit closure
- [ ] V1.1: Add test for H6 — verify web_search tool actually USED during debate (not just instantiated)
- [ ] V1.2: Add test for H8 — verify pro_skill SKILL.md hash differs from con_skill SKILL.md hash
- [ ] V1.3: Add test for H12 — sample transcript contains no Arabic characters (regex `[؀-ۿ]`)
- [ ] V1.4: Add test for H17 — assert no skills exist under `~/.claude/skills/` for this project
- [ ] V1.5: Add test for H19 — assert Judge system prompt contains no topic words (`ai`, `art`, `original`, `remix`)
- [ ] V1.6: Add test for H23 — verify LLMProvider registry has at least 2 registered (claude_login + mock; documents Gemini plug-in path)
- [ ] V1.7: Add test for H24 — verify a fact-check search query was sent during debate (web_search tool invoked from Con or Pro)
- [ ] V1.8: Add test for H25 — manual: run same debate twice, verify different verdict at least 1/3 of the time

### V2: Rubric R-gate audit closure
- [ ] V2.1: Add test for R5 — Gatekeeper queue overflow at max_depth → backpressure event logged
- [ ] V2.2: Add test for R11 — grep for hardcoded magic numbers in src/ (allow only enum values + math constants)
- [ ] V2.3: Add test for R12 — grep for `sk-`, `Bearer`, `api_key=` in source/tests — must be empty
- [ ] V2.4: Add audit script — `scripts/audit_no_pip.py` walks the codebase for any `pip install` or `python -m` references (R13)

### V3: Configuration validation
- [ ] V3.1: Add startup assertion — `setup.json.debate_topic` equals what the README declares
- [ ] V3.2: Add startup assertion — `agents.json.pro.skill_name == 'pro_skill'` (matches dir name)
- [ ] V3.3: Add startup assertion — `debate_rules.json.pings_per_side >= 5` (spec §8.7 floor)
- [ ] V3.4: Add startup assertion — `rate_limits.json.services.claude_login.hard_cap_percent < 100`

### V4: Logging coverage
- [ ] V4.1: Verify Gatekeeper logs every LLM call (entry + exit + spend delta)
- [ ] V4.2: Verify Watchdog logs every restart with restart_idx + backoff_seconds
- [ ] V4.3: Verify Judge logs every `correction_request` with the violating snippet
- [ ] V4.4: Verify Judge logs every `intervention` with the sanitized-before/after
- [ ] V4.5: Verify SDK logs every `run_debate` invocation with topic + n_pings

### V5: Documentation completeness
- [ ] V5.1: Verify PROMPTS.md uses the five-field template for every entry (Context / Goal / Prompt text / Example output / Iterative / Best practice)
- [ ] V5.2: Verify all 9 per-mechanism PRDs use the Input/Output/Setup docstring shape (rubric §A13)
- [ ] V5.3: Verify PLAN.md ISO/IEC 25010 section has both Hebrew and English for all 8 dimensions
- [ ] V5.4: Verify README has the 4 packaging-checklist questions answered (rubric §A11)

### V6: Test discipline
- [ ] V6.1: Verify every test file ≤ 150 logical lines (rubric §6.1 rule 6)
- [ ] V6.2: Verify no test makes a live LLM call without `@pytest.mark.e2e`
- [ ] V6.3: Verify no test makes a live DDG call without `@pytest.mark.e2e`
- [ ] V6.4: Verify `conftest.py` provides the 5 fixtures listed in spec §6 (mock_llm, mock_search, temp_skill_dir, shared_spend, transcript)

### V7: Manual Phase 1 thoroughness
- [ ] V7.1: Verify ≥ 3 screenshots in `assets/manual-phase1-*`
- [ ] V7.2: Verify at least one screenshot shows Pro QUOTING Con (mutual reference visible)
- [ ] V7.3: Verify README's manual-exploration section ≥ 100 words narrative

### V8: Submission hygiene
- [ ] V8.1: Verify the submission PDF filename is exactly `uoh-sqak-ex02.pdf` (not `_ex02` or `-2`)
- [ ] V8.2: Verify the PDF self-grade is 85 (placeholder; calibrate post-orchestrator-audit)
- [ ] V8.3: Verify late submission field aligns with actual submission timestamp
- [ ] V8.4: Verify the repo URL in the PDF is the actual public URL (not a placeholder)

### V9: Cost analysis (rubric §11 + §17.5 — mandatory for HW2 since it's an API consumer)
- [ ] V9.1: Add `SpendReport.estimated_cost_usd` calculation (zero in login mode; non-zero in API-key future mode)
- [ ] V9.2: Add a Gatekeeper assertion — cumulative tokens never exceed config cap
- [ ] V9.3: Add a README cost table populated with the actual session-1 token counts
- [ ] V9.4: Add an "Optimization Strategies" subsection — token reduction, cache-friendly prompts, batch processing

### V10: Originality bonus items (the H-gate items the lecturer flagged)
- [ ] V10.1: Document N5 (non-reproducibility is DESIRED) in README behavior section verbatim from lec05 L1581-1597
- [ ] V10.2: Document N7 (judge criteria from web search) in PROMPTS.md as Prompt #18+ with the actual queries used
- [ ] V10.3: Document N9 (manual Phase 1) in README "Manual exploration" section
- [ ] V10.4: Document N10 (multi-skill per agent) in PLAN.md Future Work as deferred bonus

### V11: Approval-gate audit-trail
- [ ] V11.1: Verify gate 1 has its own commit (`docs(prd): root PRD approved by user — gate 1 cleared`)
- [ ] V11.2: Verify gate 2 has its own commit (`docs: full docs bundle approved by user — gate 2 cleared`)
- [ ] V11.3: Verify the time delta between PRD commit and gate 1 approval commit is > 5 minutes (evidence of pause)

### V12: HW1 weak spot remediation explicit checks
- [ ] V12.1: Project Planning — verify PRD + PLAN + TODO + 9 per-mechanism PRDs all exist (4 file-existence checks)
- [ ] V12.2: Configuration/Security — verify `.env-example` exists; `.env` NOT tracked; `git clone && uv sync` works on fresh machine
- [ ] V12.3: Extensibility — verify `LLMProvider` and `SearchProvider` are ABCs with documented plug-in path
- [ ] V12.4: Quality Standards — verify `.pre-commit-config.yaml` and `.github/workflows/ci.yml` exist and reference uv

### V13: Pre-submission rubric §A11 packaging audit
- [ ] V13.1: `cat pyproject.toml | grep -E "^(name|version)" | wc -l` → 2
- [ ] V13.2: `grep -r "__version__" src/agent_debate/__init__.py` → matches `__version__ = "1.00"`
- [ ] V13.3: `find src -name "*.py" | head -1` → confirms src/ layout
- [ ] V13.4: `grep -r "^from agent_debate" src | wc -l` → > 10 (relative imports throughout)

### V14: Performance + memory sanity
- [ ] V14.1: Run debate; record peak memory of each child process (`psutil`). Verify < 500 MB per child.
- [ ] V14.2: Verify total debate runtime < 10 minutes (for 10 pings/side)
- [ ] V14.3: Verify log files don't exceed `fifo_files × max_lines` storage

### V15: README inspection final pass
- [ ] V15.1: Read README top-to-bottom. Verify every section in PRD §11 acceptance criteria is present.
- [ ] V15.2: Verify the README's first sentence quotes either the 16× thesis or the Context Engineering thesis.
- [ ] V15.3: Verify there's a "How the grader will run this project" section with explicit commands.

---

## Audit trail closure

- [ ] AT.1: Update `docs/PROMPTS.md` with Prompt #18 (PRD authoring)
- [ ] AT.2: Update PROMPTS.md with Prompt #19 (PLAN authoring + ISO 25010 rationale)
- [ ] AT.3: Update PROMPTS.md with Prompt #20 (TODO with verify pass + count rationale)
- [ ] AT.4: Update PROMPTS.md with Prompt #21 (per-mechanism PRD batch)
- [ ] AT.5: Update PROMPTS.md with Prompt #22 (gate #2 closure)
- [ ] AT.6: Update PROMPTS.md with Prompt #23+ for each major execution phase
- [ ] AT.7: Verify PROMPTS.md has ≥ 25 entries at submission time

---

## Summary

**Live counts** (run `grep -c '^- \[ \]' docs/TODO.md` and `grep -c '^- \[x\]' docs/TODO.md` to verify):

- Pending: **483**
- Completed: **167** (Phase A docs + Phase 0 scaffold + Phase 1 foundation + Phase 2 providers + Phase 3 Gatekeeper)
- **Total: 650 tasks**
- **Progress: ~26%** (Phases A, 0, 1, 2, 3 of 12+)

**Position vs targets:**

- Slide range (Dr. Segal's slide): 300–800 — **inside, comfortable** ✓
- Spoken-lecture minimum (lec01 L1170): 500 — **exceeds** ✓
- CLAUDE.md aspirational target: 800–1000 — slightly below, but per lec01 L1199-1201 the "be very critical" verify pass during execution typically surfaces another ~150 tasks, which would land us at ~800

**Decision:** ship at 650 now, expand organically during execution. The TODO is a living document — new sub-tasks will be added when red-green-refactor cycles reveal them (this is the natural form the verify-pass advice takes during execution, not all at once during planning).

**Marking discipline reminder:** every `[x]` should correspond to a git commit on `main`. Continuous commit density is graded (lec04 L132-141, L559). Big-bang push at the end is a significant grade penalty.

**Subagent-dispatch protocol** (in effect from Phase 4 onward): every implementer prompt MUST end with an instruction to update `docs/TODO.md` checkboxes (`[ ]` → `[x]`) for the completed tasks in the same final commit that closes the phase. This ensures the per-step marking discipline is enforced at the dispatch layer, not retroactively.

**Phase ordering reminder (Dr. Segal's slide — overrides phase numbers):**
1. PRD → 2. PLAN → 3. TODO → 4. verify pass → 5. Execute (Phases 0-10) → 6. README → 7. Run the project → 8. Push to GitHub PUBLIC
