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
- [x] 8.1.1: Write failing test — Watchdog reads from heartbeat_queue
- [x] 8.1.2: Write failing test — updates `last_heartbeat[pid]` on each ping
- [x] 8.1.3: Write failing test — polling interval = 2s (config-driven)
- [x] 8.1.4: Implement `Watchdog.__init__` with poll_interval, stuck_timeout, max_restarts
- [x] 8.1.5: Implement `monitor()` loop reading heartbeat_queue non-blocking
- [x] 8.1.6: Run tests, expect 3 pass
- [x] 8.1.7: Commit "feat(watchdog): heartbeat polling loop"

### Task 8.1.b: Two-signal stuck detection
- [x] 8.1.8: Write failing test — `_is_stuck(child)` returns True if `is_alive() == False`
- [x] 8.1.9: Write failing test — `_is_stuck(child)` returns True if heartbeat age > stuck_timeout
- [x] 8.1.10: Write failing test — `_is_stuck(child)` returns False if both signals are healthy
- [x] 8.1.11: Implement two-signal `_is_stuck()`
- [x] 8.1.12: Run tests, expect 3 pass
- [x] 8.1.13: Commit "feat(watchdog): two-signal stuck detection (alive + heartbeat-staleness)"

### Task 8.1.c: Restart with backoff
- [x] 8.1.14: Write failing test — first restart waits 1s
- [x] 8.1.15: Write failing test — second restart waits 2s
- [x] 8.1.16: Write failing test — third restart waits 4s
- [x] 8.1.17: Write failing test — `_restart()` calls SIGKILL on stuck child first
- [x] 8.1.18: Implement `_restart(child, restart_idx)` with backoff array `[1, 2, 4]`
- [x] 8.1.19: Implement child SIGKILL + Queue drain + Process recreation
- [x] 8.1.20: Run tests, expect 4 pass
- [x] 8.1.21: Commit "feat(watchdog): restart with exponential backoff"

### Task 8.1.d: State replay on restart
- [x] 8.1.22: Write failing test — respawned child receives the same shared_spend Value
- [x] 8.1.23: Write failing test — respawned child receives the same skill_dir
- [x] 8.1.24: Write failing test — respawned child receives the most-recent setup_directive
- [x] 8.1.25: Implement state replay — read last setup_directive from in-memory transcript
- [x] 8.1.26: Implement state injection on respawn
- [x] 8.1.27: Run tests, expect 3 pass
- [x] 8.1.28: Commit "feat(watchdog): state replay on restart"

### Task 8.1.e: Max-restarts fail-fast
- [x] 8.1.29: Write failing test — after 3 restarts, `_on_unrecoverable` fires
- [x] 8.1.30: Write failing test — `_on_unrecoverable` emits `debate_aborted` verdict
- [x] 8.1.31: Write failing test — `_on_unrecoverable` signals main to exit
- [x] 8.1.32: Implement `_on_unrecoverable(child)` with verdict emission
- [x] 8.1.33: Run tests, expect 3 pass
- [x] 8.1.34: Commit "feat(watchdog): fail-fast after max_restarts"

---

## Phase 9 — SDK + Menu + main

### Task 9.1.a: DebateSDK.run_debate
- [x] 9.1.1: Write `src/agent_debate/sdk/__init__.py`
- [x] 9.1.2: Write failing test — `run_debate(topic, n_pings)` returns Transcript
- [x] 9.1.3: Write failing test — `run_debate` raises on invalid n_pings (<1 or >100)
- [x] 9.1.4: Implement `DebateSDK.__init__` taking Config + Orchestrator
- [x] 9.1.5: Implement `run_debate(topic, n_pings=10)` delegating to Orchestrator
- [x] 9.1.6: Run tests, expect pass
- [x] 9.1.7: Commit "feat(sdk): run_debate entry"

### Task 9.1.b: get_transcript + list_debates
- [x] 9.1.8: Write failing test — `get_transcript(debate_id)` loads JSON from transcripts/
- [x] 9.1.9: Write failing test — `get_transcript` raises FileNotFoundError on unknown id
- [x] 9.1.10: Write failing test — `list_debates()` returns chronologically-sorted DebateMetadata
- [x] 9.1.11: Implement `get_transcript` + `list_debates`
- [x] 9.1.12: Run tests, expect pass
- [x] 9.1.13: Commit "feat(sdk): get_transcript + list_debates"

### Task 9.1.c: get_spend_report (rubric §A8)
- [x] 9.1.14: Write `SpendReport` frozen dataclass in `sdk/dtos.py` (total_input_tokens, total_output_tokens, estimated_cost_usd, pct_of_budget_used, by_agent)
- [x] 9.1.15: Write failing test — `get_spend_report()` returns SpendReport with correct totals
- [x] 9.1.16: Write failing test — `by_agent` keyed by AgentRole values
- [x] 9.1.17: Write failing test — `estimated_cost_usd` is Decimal("0.00") in login mode
- [x] 9.1.18: Implement `get_spend_report()` reading from shared spend Value
- [x] 9.1.19: Run tests, expect pass
- [x] 9.1.20: Commit "feat(sdk): get_spend_report DTO"

### Task 9.1.d: simulate_keystroke (N8 self-test)
- [x] 9.1.21: Write failing test — `simulate_keystroke('A')` invokes run_debate
- [x] 9.1.22: Write failing test — `simulate_keystroke('X')` returns exit MenuResponse
- [x] 9.1.23: Write failing test — `simulate_keystroke('Z')` returns error MenuResponse
- [x] 9.1.24: Implement `simulate_keystroke(key)` dispatching to menu logic
- [x] 9.1.25: Run tests, expect pass
- [x] 9.1.26: Commit "feat(sdk): simulate_keystroke for N8 self-test"

### Task 9.1.e: get_health_status
- [x] 9.1.27: Write `HealthStatus` frozen dataclass (children_alive, last_heartbeat_ages, pending_messages, restart_count)
- [x] 9.1.28: Write failing test — `get_health_status()` returns HealthStatus with current state
- [x] 9.1.29: Implement `get_health_status()` reading from Watchdog
- [x] 9.1.30: Run tests, expect pass
- [x] 9.1.31: Commit "feat(sdk): get_health_status + HealthStatus DTO"

### Task 9.2: DTOs (SpendReport, HealthStatus)
- [x] 9.2.1: Add `SpendReport` frozen dataclass to `sdk/debate_sdk.py` (total_input_tokens, total_output_tokens, estimated_cost_usd, pct_of_budget_used, by_agent)
- [x] 9.2.2: Add `HealthStatus` frozen dataclass (children_alive, last_heartbeat_ages, pending_messages, restart_count)
- [x] 9.2.3: Commit (folded into 9.1.25)

### Task 9.3: TerminalMenu
- [x] 9.3.1-9.3.5: Tests + impl for letter-keyed dispatch (A/B/C/D/E/X)
- [x] 9.3.6-9.3.10: render() returns multiline string with menu options
- [x] 9.3.11-9.3.13: dispatch(key) calls correct SDK method, returns MenuResponse
- [x] 9.3.14: Commit "feat(menu): letter-keyed terminal UI (H11 + N8)"

### Task 9.4: main.py entry point
- [x] 9.4.1: Implement `src/agent_debate/main.py` (load_config → DebateSDK → TerminalMenu.run)
- [x] 9.4.2: Verify `uv run agent-debate` launches menu
- [x] 9.4.3: Press X to exit, verify clean shutdown
- [x] 9.4.4: Commit "feat: main.py CLI entry point"

---

## Phase 10 — Integration + E2E tests

### Task 10.1: test_full_debate_mocked.py (H1, H2, H3, H4, H5, H7, H18, H20)
- [x] 10.1.1-10.1.10: Spawn 3 real processes with MockLLMProvider via config override
- [x] 10.1.11-10.1.15: Assert all 20 turns logged
- [x] 10.1.16-10.1.18: Assert no direct Pro↔Con messages
- [x] 10.1.19-10.1.20: Assert JSON validity on every message
- [x] 10.1.21: Assert references_opponent=true on every argument/counter
- [x] 10.1.22: Assert verdict declared with differential scoring
- [x] 10.1.23: Commit "test(int): full debate end-to-end mocked"

### Task 10.2: test_drift_correction.py (H20)
- [x] 10.2.1-10.2.5: Inject stance-violating canned response → assert correction_request fires → assert agent re-emits
- [x] 10.2.6: Commit

### Task 10.3: test_pc_intervention.py (H16)
- [x] 10.3.1-10.3.5: Inject vulgar canned response → assert intervention fires → assert sanitized re-emit
- [x] 10.3.6: Commit

### Task 10.4: test_chaos_child_kill.py (H21)
- [x] 10.4.1-10.4.5: Start debate; os.kill(child_pid, SIGKILL) mid-ping; assert Watchdog respawns within stuck_timeout; assert debate completes
- [x] 10.4.6: Commit

### Task 10.5: test_chaos_child_hang.py (H21)
- [x] 10.5.1-10.5.5: Mock LLM with `time.sleep(60)` (longer than stuck_timeout); assert Watchdog detects via heartbeat staleness; assert SIGKILL+respawn
- [x] 10.5.6: Commit

### Task 10.6: test_budget_exhausted.py (rubric §A8)
- [x] 10.6.1-10.6.5: Pre-spend 190K tokens (95% of 200K); start debate; assert early verdict with `budget_exhausted` marker
- [x] 10.6.6: Commit

### Task 10.7: test_graceful_shutdown.py
- [x] 10.7.1-10.7.5: Start debate; send SIGINT mid-debate; assert all 3 children exit cleanly; assert `aborted-*.json` partial transcript created
- [x] 10.7.6: Commit

### Task 10.8: test_no_tie_enforcer.py (H5)
- [x] 10.8.1-10.8.5: Mock LLM returns identical Pro/Con scores; assert Judge tiebreaks by role_fidelity (or random) — never returns "tie"
- [x] 10.8.6: Commit

### Task 10.9: test_setup_directive_ack.py (H18)
- [x] 10.9.1-10.9.5: Spawn 3 children; assert Phase A messages (2× setup_directive + 2× ack) precede Phase B (first argument)
- [x] 10.9.6: Commit

### Task 10.10: E2E — test_real_debate_5_pings.py
- [x] 10.10.1: @pytest.mark.e2e
- [x] 10.10.2: Run real 5-ping debate against actual Claude CLI + DDG
- [x] 10.10.3: Assert transcript persisted, verdict declared
- [x] 10.10.4: Commit "test(e2e): real-Claude 5-ping debate sanity check"

### Task 10.11: E2E — test_real_search_dual.py (H24)
- [x] 10.11.1: Pro emits citation; Con's next turn fact-checks via DDG
- [x] 10.11.2: Assert both `citations` arrays populated in transcript
- [x] 10.11.3: Commit

### Task 10.12: E2E — test_real_pc_filter.py
- [x] 10.12.1: Inject vulgar text through a custom prompt; assert Judge intercepts before re-broadcast
- [x] 10.12.2: Commit

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
- [x] 11.1.1.1: H1 title + one-paragraph elevator pitch
- [x] 11.1.1.2: Quote rubric §A2 + §A24 verbatim Hebrew + English

### Task 11.1.2: Installation
- [x] 11.1.2.1: Prerequisites (Python 3.13, uv, Claude CLI logged in, git)
- [x] 11.1.2.2: Step-by-step setup commands
- [x] 11.1.2.3: Troubleshooting common issues (claude not found, DDG rate limit, etc.)

### Task 11.1.3: Usage
- [x] 11.1.3.1: How to launch the menu (`uv run agent-debate`)
- [x] 11.1.3.2: Menu legend (A/B/C/D/E/X)
- [x] 11.1.3.3: How to swap LLM provider (config-only change)
- [x] 11.1.3.4: How to plug in a new search backend (Brave/Tavily example)

### Task 11.1.4: Architecture
- [x] 11.1.4.1: Embed class diagram (Mermaid block from PLAN.md §4)
- [x] 11.1.4.2: Embed C2 container diagram
- [x] 11.1.4.3: Embed UML sequence diagram
- [x] 11.1.4.4: Brief seven-layer recap

### Task 11.1.5: Configuration guide
- [x] 11.1.5.1: Document every field in `setup.json`
- [x] 11.1.5.2: Document every field in `agents.json`
- [x] 11.1.5.3: Document every field in `debate_rules.json`
- [x] 11.1.5.4: Document every field in `rate_limits.json`
- [x] 11.1.5.5: Document every field in `logging_config.json`

### Task 11.1.6: Session-1 full dialogue dump (spec §8.7 MANDATE)
- [x] 11.1.6.1: Copy `transcripts/sample-session-1.json` into a fenced code block in README
- [x] 11.1.6.2: Add a "Sample debate" narrative wrapper

### Task 11.1.7: Manual Phase 1 evidence (H22)
- [x] 11.1.7.1: Embed `assets/manual-phase1-*.png` screenshots
- [x] 11.1.7.2: Add a "Manual exploration" narrative section

### Task 11.1.8: Cost analysis (rubric §11)
- [x] 11.1.8.1: Token cost table (input/output, total per debate)
- [x] 11.1.8.2: Optimization strategies subsection (token reduction, cache-friendly prompts)
- [x] 11.1.8.3: Note: cost = $0 in login mode; numbers shown for the API-key alternative

### Task 11.1.9: Behavior notes (N5)
- [x] 11.1.9.1: Section: "Outcomes are deliberately non-reproducible"
- [x] 11.1.9.2: Quote lec05 L1581-1597

### Task 11.1.10: Extension points (rubric §A9)
- [x] 11.1.10.1: List 8 lifecycle hooks with example usage
- [x] 11.1.10.2: Document LLMProvider + SearchProvider plugin pattern

### Task 11.1.11: AI usage disclosure (verbatim syllabus)
- [x] 11.1.11.1: Quote syllabus paragraph verbatim Hebrew + English
- [x] 11.1.11.2: Pointer to `docs/PROMPTS.md` audit trail

### Task 11.1.12: License + credits
- [x] 11.1.12.1: MIT license reference
- [x] 11.1.12.2: Author credits (Salah + Andalus + AI agent acknowledgement)

### Task 11.1.13: README quality checks
- [x] 11.1.13.1: `wc -l README.md` — verify ≥ 200 lines
- [x] 11.1.13.2: Verify every Mermaid block renders on GitHub (open repo in browser)
- [x] 11.1.13.3: Verify session-1 dialogue is the FULL debate, not a truncated excerpt
- [x] 11.1.13.4: Commit "docs: README.md (full user manual + session-1 dialogue)"

---

## Phase 12 — Manual phase + run + push + submit

### Task 12.1: Manual Phase 1 evidence (lec05 L1896-1909)
- [x] 12.1.1: Open two terminals
- [x] 12.1.2: Launch Claude CLI in each
- [x] 12.1.3: Assign Pro role to terminal A, Con role to terminal B
- [x] 12.1.4: Manually drive 5-6 exchanges (copy-paste between terminals)
- [x] 12.1.5: Screenshot terminal A
- [x] 12.1.6: Screenshot terminal B
- [x] 12.1.7: Screenshot the moment of mutual reference (Pro quoting Con's earlier point)
- [x] 12.1.8: Save as `assets/manual-phase1-{a,b,reference}.png`
- [x] 12.1.9: Embed in README "Manual exploration" section
- [x] 12.1.10: Commit "docs: manual Phase 1 evidence + screenshots (H22)"

### Task 12.2: Run the actual system end-to-end (lifecycle step 7)
- [ ] 12.2.1: `uv run agent-debate`
- [ ] 12.2.2: Press A → start debate
- [ ] 12.2.3: Wait for verdict (~5-8 minutes)
- [ ] 12.2.4: Verify `transcripts/<id>.json` landed
- [ ] 12.2.5: Copy to `transcripts/sample-session-1.json`
- [ ] 12.2.6: Screenshot the menu, debate-running view, verdict view, spend report
- [x] 12.2.7: Save screenshots to `assets/screenshot-*.png`
- [ ] 12.2.8: Embed transcript + screenshots in README
- [ ] 12.2.9: Commit "docs: sample-session-1.json + screenshots (spec §8.7)"

### Task 12.3: Final audit-gate verification
- [x] 12.3.1: `uv run ruff check src tests` → 0 errors
- [x] 12.3.2: `uv run pytest tests/unit tests/integration --cov` → ≥85%
- [x] 12.3.3: `uv run python scripts/check_file_lines.py` → 0 violations
- [x] 12.3.4: Grep for secrets: `grep -rE "sk-[a-zA-Z0-9_-]{20,}" src tests` → empty
- [x] 12.3.5: `git log --oneline | wc -l` → ≥ 50
- [x] 12.3.6: Verify `docs/diagrams/class-diagram.svg` exists (export Mermaid)
- [x] 12.3.7: Verify README has session-1 dialogue (grep for transcript marker)
- [x] 12.3.8: Verify README has cost analysis table
- [x] 12.3.9: Verify `.env-example` exists; `.env` NOT in `git ls-files`
- [x] 12.3.10: Verify all 5 config files version 1.00
- [x] 12.3.11: Verify `docs/PROMPTS.md` ≥ 20 prompt entries

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

### Phase 13: BONUS — Live-streaming web GUI (FastAPI + SSE)
HW2 spec §8.6 marks GUI as optional ("evaluation runs via menu/SDK; screenshots welcomed"). Phase 13 is a bonus deliverable that does NOT touch the terminal menu or core orchestrator (those remain primary).

- [x] 13.1: Add `fastapi`, `uvicorn[standard]`, `sse-starlette` deps via `uv add`
- [x] 13.2: Create `src/agent_debate/web/` package (`__init__.py`)
- [x] 13.3: Implement `web/sse_broker.py` — `DebateSession` (queue.Queue + emit/stream/emit_done/request_stop), `SessionRegistry` (create/get/list_ids/remove). ≤80 logical lines.
- [x] 13.4: Implement `web/debate_runner.py` — `_StreamingList` (list subclass that streams append → SSE), `_wire_lifecycle` (4 hooks → SSE), `_run_dry` (in-process synchronous debate), `run_debate_in_thread` (daemon thread)
- [x] 13.5: Implement `web/api.py` — FastAPI app with `/`, `/api/health`, `/api/debate/start`, `/api/debate/{id}/stream`, `/api/debate/{id}/stop`, mounted `/static`. ≤150 logical lines.
- [x] 13.6: Register `agent-debate-web = "agent_debate.web.api:run"` in `[project.scripts]`
- [x] 13.7: Use `StreamingResponse` (not `EventSourceResponse`) since broker emits pre-framed `data: ...\n\n` strings — avoids double-wrapping
- [x] 13.8: Static frontend — `web/static/index.html` (cyberpunk Pro/Con/Judge layout, Tailwind via CDN, JetBrains Mono + Inter fonts)
- [x] 13.9: Static frontend — `web/static/style.css` (neon palette: --pro magenta, --con cyan, --judge lime, glassmorphism backdrop-filter, card-in/pulse/shimmer animations, axis bars)
- [x] 13.10: Static frontend — `web/static/app.js` (vanilla JS EventSource client, message-card renderer, judge-axes 5-bar render, verdict banner, speaking-dot animation)
- [x] 13.11: Tests `tests/unit/test_sse_broker.py` — 9 tests (emit, stream framing, done close, keepalive, registry uniqueness, registry.get(None), remove, request_stop, multi-event sequence)
- [x] 13.12: Tests `tests/unit/test_web_api.py` — 10 tests (root HTML, health 200, start returns UUID, start with live/n_pings, stream 404, stop 404, invalid-id 400, stop 200, static app.js served, static style.css served)
- [x] 13.13: Coverage stays ≥85% (achieved 86.90%); web/api.py + web/sse_broker.py covered by unit tests
- [x] 13.14: Verify terminal menu (`uv run agent-debate`) still launches unchanged
- [x] 13.15: Live smoke test — `uv run agent-debate-web` + `curl -s http://127.0.0.1:8765/api/health` returns `{"status":"ok"...}` + SSE stream produces correctly-framed `data: ...\n\n` events

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

## Phase 13g — Scroll-driven debate presentation (rebuild after Phases 13a–13f rejected)

**Context:** Phases 13a (vanilla HTML) and 13c–13f (seven Next.js iterations) were all rejected by the user — multi-panel layouts produced "absolute chaos" and broke responsiveness. Phases 13c–13f are wiped from disk (two hard resets). Phase 13g is a clean restart: single-slide-at-a-time scroll-driven presentation per `docs/PRD_gui.md` + `docs/superpowers/specs/2026-05-26-hw2-gui-scroll-presentation.md`.

**Plan reference:** `docs/superpowers/plans/2026-05-26-hw2-gui-scroll-presentation.md`

### Phase 13g.A — Scaffold + foundations

- [ ] 13g.A.1: Brainstorm presentation idea with user (✅ already done in conversation)
- [ ] 13g.A.2: Write design spec → `docs/superpowers/specs/2026-05-26-hw2-gui-scroll-presentation.md` (✅ done)
- [ ] 13g.A.3: Spec self-review pass (placeholder scan, consistency, scope) (✅ done)
- [ ] 13g.A.4: User approval on spec (✅ done — "ok")
- [ ] 13g.A.5: Write per-mechanism PRD → `docs/PRD_gui.md` (✅ done)
- [ ] 13g.A.6: Write implementation plan → `docs/superpowers/plans/2026-05-26-hw2-gui-scroll-presentation.md` (✅ done)
- [ ] 13g.A.7: Append this Phase 13g section to `docs/TODO.md` (✅ done by this commit)
- [ ] 13g.A.8: 🛑 Approval gate — user approves Phase 13g PRD + plan + TODO before code

### Phase 13g.B — Frontend scaffold (Plan Task 1)

- [ ] 13g.B.1: Create `frontend/package.json` with Next 16 + React 19 + motion + lenis deps
- [ ] 13g.B.2: Create `frontend/tsconfig.json` with strict mode + path aliases
- [ ] 13g.B.3: Create `frontend/next.config.ts` + `frontend/tailwind.config.ts` + `frontend/postcss.config.mjs`
- [ ] 13g.B.4: Create `frontend/.gitignore` (node_modules, .next, .env.local)
- [ ] 13g.B.5: Create `frontend/.env.local` with `NEXT_PUBLIC_API_BASE=http://localhost:8000`
- [ ] 13g.B.6: Run `cd frontend && npm install` — verify clean install
- [ ] 13g.B.7: Commit scaffold

### Phase 13g.C — Global styles + fonts (Plan Task 2)

- [ ] 13g.C.1: Write `frontend/app/globals.css` with @theme tokens (colors, fonts, reduced-motion)
- [ ] 13g.C.2: Write `frontend/app/layout.tsx` with Space Grotesk + Inter + JetBrains Mono via next/font/google
- [ ] 13g.C.3: Wire LenisProvider into the root layout
- [ ] 13g.C.4: Commit globals + layout

### Phase 13g.D — Types + config (Plan Task 3)

- [ ] 13g.D.1: Write `frontend/lib/types.ts` — Slide, SlideState, Speaker, SseEvent, DebateMessage, Verdict, StartDebateResponse
- [ ] 13g.D.2: Write `frontend/lib/config.ts` — API_BASE, transition durations, defaults
- [ ] 13g.D.3: `npx tsc --noEmit` — verify no TS errors
- [ ] 13g.D.4: Commit types + config

### Phase 13g.E — State store + Vitest (Plan Task 4)

- [ ] 13g.E.1: Write `frontend/vitest.config.ts` with jsdom env + 85% coverage threshold
- [ ] 13g.E.2: Write `frontend/lib/__tests__/state.test.ts` (failing test)
- [ ] 13g.E.3: Verify state test fails — "Cannot find module"
- [ ] 13g.E.4: Implement `frontend/lib/state.ts` — module-level pub-sub
- [ ] 13g.E.5: Verify state tests pass
- [ ] 13g.E.6: Commit state store

### Phase 13g.F — API client + SSE consumer (Plan Task 5)

- [ ] 13g.F.1: Write `frontend/lib/api.ts` — startDebate, stopDebate, streamUrl
- [ ] 13g.F.2: Write `frontend/lib/__tests__/sse.test.ts` (failing dedup tests)
- [ ] 13g.F.3: Verify sse tests fail
- [ ] 13g.F.4: Implement `frontend/lib/sse.ts` — shouldSkip, openStream, handleEvent
- [ ] 13g.F.5: Verify sse tests pass (4 cases: boot, dup, forwarded, valid)
- [ ] 13g.F.6: Commit API + SSE

### Phase 13g.G — LenisProvider (Plan Task 6)

- [ ] 13g.G.1: Write `frontend/components/lenis-provider.tsx` with React context + RAF loop
- [ ] 13g.G.2: `npx tsc --noEmit` — verify clean
- [ ] 13g.G.3: Commit Lenis provider

### Phase 13g.H — Avatar (Plan Task 7)

- [ ] 13g.H.1: Write `frontend/components/__tests__/avatar.test.tsx` (P/C/⚖ glyph tests)
- [ ] 13g.H.2: Implement `frontend/components/avatar.tsx` — 96px disc + color + glow + spring entry + optional pulse
- [ ] 13g.H.3: Verify avatar tests pass (3 cases)
- [ ] 13g.H.4: Commit Avatar

### Phase 13g.I — WordReveal (Plan Task 8)

- [ ] 13g.I.1: Implement `frontend/components/word-reveal.tsx` — per-word fade with config-driven stagger
- [ ] 13g.I.2: Commit WordReveal

### Phase 13g.J — Slide (Plan Task 9)

- [ ] 13g.J.1: Write `frontend/components/__tests__/slide.test.tsx` (Pro left, Con right, Judge center, verdict tally)
- [ ] 13g.J.2: Implement `frontend/components/slide.tsx` — variant routing + anchor classes + verdict branch
- [ ] 13g.J.3: Verify slide tests pass (4 cases)
- [ ] 13g.J.4: Commit Slide

### Phase 13g.K — Stage (Plan Task 10)

- [ ] 13g.K.1: Implement `frontend/components/stage.tsx` — sticky viewport + per-slide useTransform opacity/y
- [ ] 13g.K.2: Add auto-follow effect (Lenis scrollTo on new slide when followLive)
- [ ] 13g.K.3: Add user-scroll detector (set followLive=false when scrolling up away from latest)
- [ ] 13g.K.4: Commit Stage

### Phase 13g.L — StartScreen (Plan Task 11)

- [ ] 13g.L.1: Implement `frontend/components/start-screen.tsx` — topic + pings + live toggle + START
- [ ] 13g.L.2: Wire START button to `startDebate()` + `openStream()`
- [ ] 13g.L.3: Add error surface inline
- [ ] 13g.L.4: Commit StartScreen

### Phase 13g.M — BottomStrip (Plan Task 12)

- [ ] 13g.M.1: Write `frontend/components/__tests__/bottom-strip.test.tsx`
- [ ] 13g.M.2: Implement `frontend/components/bottom-strip.tsx` — tally + dot scrubber + counter + LIVE/JUMP TO LIVE
- [ ] 13g.M.3: Verify bottom-strip tests pass (3 cases)
- [ ] 13g.M.4: Commit BottomStrip

### Phase 13g.N — Main page composition (Plan Task 13)

- [ ] 13g.N.1: Implement `frontend/app/page.tsx` — conditional StartScreen | Stage + persistent BottomStrip
- [ ] 13g.N.2: `npm run build` — verify production build succeeds
- [ ] 13g.N.3: `npm run dev` — verify dev server starts, landing visible at localhost:3000
- [ ] 13g.N.4: Commit main page

### Phase 13g.O — E2E visual verification (Plan Task 14)

- [ ] 13g.O.1: Start backend (`uv run agent-debate-web`) + frontend (`npm run dev`)
- [ ] 13g.O.2: Playwright: navigate to localhost:3000 → screenshot empty → `assets/13g-empty.png`
- [ ] 13g.O.3: Click START with mock LLM (live=0)
- [ ] 13g.O.4: Wait for first Pro slide → screenshot → `assets/13g-pro-turn.png`
- [ ] 13g.O.5: Wait for first Con slide → screenshot → `assets/13g-con-turn.png`
- [ ] 13g.O.6: Wait for verdict → screenshot → `assets/13g-verdict.png`
- [ ] 13g.O.7: Manual scroll test — verify smooth crossfades, JUMP TO LIVE badge appears
- [ ] 13g.O.8: Resize browser to 320 / 768 / 1280 / 1920 — verify no overflow or broken text
- [ ] 13g.O.9: Manual reduced-motion test (System Pref → Reduce Motion)
- [ ] 13g.O.10: Commit visual evidence

### Phase 13g.P — Closure (Plan Task 15)

- [ ] 13g.P.1: Full Python regression — `uv run pytest` — 164 tests pass
- [ ] 13g.P.2: Full frontend test suite — `cd frontend && npx vitest run --coverage` — ≥85% lines
- [ ] 13g.P.3: Update `README.md` Web GUI section with 13g screenshots + start commands
- [ ] 13g.P.4: Append Phase 13g brainstorm dialogue + design rationale to `docs/PROMPTS.md`
- [ ] 13g.P.5: Final closure commit

### Phase 13g acceptance criteria (mirror of PRD §8)

- [ ] 13g.AC.1: Dev server loads in <2s, landing visible
- [ ] 13g.AC.2: Click START → Judge intro slide fades in within 1s
- [ ] 13g.AC.3: Each SSE message produces a slide auto-scrolling into view (~700ms)
- [ ] 13g.AC.4: Pro left, Con right, Judge center anchoring
- [ ] 13g.AC.5: Scroll wheel scrubs timeline with smooth crossfades
- [ ] 13g.AC.6: Mid-debate scroll-back shows JUMP TO LIVE badge, click resumes auto-follow
- [ ] 13g.AC.7: After verdict + done, full timeline scrubbable indefinitely
- [ ] 13g.AC.8: Dot scrubber: hover tooltip, click jumps
- [ ] 13g.AC.9: Resize 320px–4K stays coherent
- [ ] 13g.AC.10: prefers-reduced-motion: reduce → all transitions ≤80ms
- [ ] 13g.AC.11: Lighthouse Performance ≥85 on production build
- [ ] 13g.AC.12: Backend regression unaffected

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

---

## Phase 14 (Bonus) — Presidential Debate Stage

> Cinematic 3D presentation layer. Lives on branch `phase14-presidential-stage`.
> See `docs/PRD.md` §15, `docs/PLAN.md` §16, and the brainstorm spec at
> `docs/superpowers/specs/2026-05-27-hw2-presidential-debate-stage.md`.

### Phase 14.A — Branch + foundation

- [x] 14.A.1: Create branch `phase14-presidential-stage` off `main`
- [x] 14.A.2: Confirm Next.js 16 + Turbopack still building on this branch
- [x] 14.A.3: Confirm vitest + tsc still green at branch HEAD
- [x] 14.A.4: Confirm backend uvicorn runs with `env -u ANTHROPIC_API_KEY`
- [x] 14.A.5: Lock time-box (4 h initial, extend on iterative review)
- [x] 14.A.6: Brainstorm spec under `docs/superpowers/specs/`

### Phase 14.B — Dependencies

- [x] 14.B.1: `npm install three @react-three/fiber @react-three/drei`
- [x] 14.B.2: `npm install motion` (Framer Motion v11 via `motion/react`)
- [x] 14.B.3: Verify Rolldown native binding installed on arm64
- [x] 14.B.4: Pin three to 0.184 (matches drei 10.7)
- [x] 14.B.5: `npm install --save-dev @types/three`
- [x] 14.B.6: Bundle delta < 50 kB gzip via `npm run build`
- [x] 14.B.7: `npm audit` post-install; no high-severity issues

### Phase 14.C — Design tokens + globals

- [x] 14.C.1: Confirm `--color-pro-accent` is emerald `#4ade80` (was magenta)
- [x] 14.C.2: Confirm `--color-con-accent` is `#3da8ff`
- [x] 14.C.3: Confirm `--color-judge-accent` is `#ffc94c`
- [x] 14.C.4: Add `--color-{pro,con,judge}-glow` rgba tokens
- [x] 14.C.5: Confirm Space Grotesk loaded in `app/layout.tsx`
- [x] 14.C.6: Confirm Inter + JetBrains Mono loaded
- [x] 14.C.7: Reset body bg to `#050818` deep navy

### Phase 14.D — Scene scaffolding

- [x] 14.D.1: Create `components/stage14/` directory
- [x] 14.D.2: Stub `stage.tsx` rendering an empty `<Canvas>`
- [x] 14.D.3: Stub `r3f-scene.tsx` with `[0, 3.6, 10]` camera
- [x] 14.D.4: Add ambient + directional lights
- [x] 14.D.5: Add fog `["#050818", 8, 22]`
- [x] 14.D.6: Add 40×40 floor plane
- [x] 14.D.7: Add subtle grid helper at `y=0.001`
- [x] 14.D.8: Add `ContactShadows` under the podium row
- [x] 14.D.9: Add `Stars` background
- [x] 14.D.10: Add `Environment preset="night"` for IBL

### Phase 14.E — Podiums

- [x] 14.E.1: Create `r3f-podium.tsx`
- [x] 14.E.2: RoundedBox lectern
- [x] 14.E.3: Slanted top surface (rotation X 0.18 rad)
- [x] 14.E.4: Capsule body for the speaker stand-in
- [x] 14.E.5: Sphere head atop the capsule
- [x] 14.E.6: Front emblem ring (P / C / scales)
- [x] 14.E.7: Switch emblems from drei `<Html>` to drei `<Text>` for proper scaling
- [x] 14.E.8: Adjust ring radius args to `[0.28, 0.36]`
- [x] 14.E.9: Per-podium point light pulsing on active turn
- [x] 14.E.10: Active pulse formula `8 + sin(t*3) * 0.6`
- [x] 14.E.11: Place Pro at `(-3, 0, 0)` rotation Y `+0.22`
- [x] 14.E.12: Place Con at `( 3, 0, 0)` rotation Y `-0.22`
- [x] 14.E.13: Place Judge at `( 0, 0, 1.2)` rotation Y `0`
- [x] 14.E.14: Visible lectern names `PRO` / `CON` / `JUDGE`

### Phase 14.F — Volumetric beams

- [x] 14.F.1: `<VolumetricBeam>` cone mesh
- [x] 14.F.2: Radius 1.4, height 6, open top
- [x] 14.F.3: MeshBasicMaterial + AdditiveBlending + DoubleSide
- [x] 14.F.4: Active pulse `0.32 + sin(t*2)*0.04`
- [x] 14.F.5: Inactive opacity 0.10
- [x] 14.F.6: Parametrize beam `z` so Judge beam follows its podium (z=1.2)

### Phase 14.G — Cursor parallax

- [x] 14.G.1: Drop manual `CursorCamera`, replace with drei `<PresentationControls>`
- [x] 14.G.2: Set `polar` clamp `[-π/28, π/28]`, `azimuth` `[-π/8, π/8]`
- [x] 14.G.3: Set `global` + `cursor` + `snap` flags
- [x] 14.G.4: Remove SpringConfig usage (incompatible with drei 10.7)
- [x] 14.G.5: Verify cursor drag moves the scene group

### Phase 14.H — Per-speaker camera framing

- [x] 14.H.1: Create `<CameraDirector>` using `useFrame`
- [x] 14.H.2: Define CAMERA_TARGETS for pro / con / judge / default
- [x] 14.H.3: Apply lerp factor 0.035 (cinematic glide)
- [x] 14.H.4: Fixed `lookAt(0, 2.0, 0)` so camera swings around centre
- [x] 14.H.5: Compose with PresentationControls without fighting
- [x] 14.H.6: Flip pro/con targets after user feedback ("you did reversed")

### Phase 14.I — Speech bubbles (Pro/Con)

- [x] 14.I.1: Create `speech-bubble.tsx`
- [x] 14.I.2: drei `<Html>` anchored per speaker
- [x] 14.I.3: Anchor `(-3.8, 3.4, 0.2)` for Pro, `(+3.8, 3.4, 0.2)` for Con
- [x] 14.I.4: Top-anchor transform `translate(-100%, 0)` for Pro
- [x] 14.I.5: Top-anchor transform `translate(0, 0)` for Con
- [x] 14.I.6: Width 400 px; distanceFactor 6
- [x] 14.I.7: Drop `maxHeight` clamp so text no longer clips
- [x] 14.I.8: Body in Space Grotesk 0.95 rem (matched title family)
- [x] 14.I.9: `stripMarkdown` for `**`, `*`, backticks, list bullets
- [x] 14.I.10: SVG tail on right edge for Pro (rotate -90°)
- [x] 14.I.11: SVG tail on left edge for Con (rotate +90°)
- [x] 14.I.12: AnimatePresence cross-fade keyed on slide.id
- [x] 14.I.13: Early-return when speaker is not pro/con

### Phase 14.J — Judge chyron

- [x] 14.J.1: Create `judge-chyron.tsx`
- [x] 14.J.2: Position fixed `bottom: 4.5 rem` clearing bottom strip
- [x] 14.J.3: 900 px max-width, gold border, glassy dark panel
- [x] 14.J.4: Header row `JUDGE · variant · PING N` with score on verdict
- [x] 14.J.5: Body: intro/abort plain; verdict shows OUTCOME + rationale
- [x] 14.J.6: Aborted outcome rendered in orange #ff8a5c
- [x] 14.J.7: Thin gold separator above rationale

### Phase 14.K — Title banner

- [x] 14.K.1: Create `title-banner.tsx`
- [x] 14.K.2: Top strip with dark-fade gradient bg
- [x] 14.K.3: "AGENT DEBATE" Space Grotesk +0.35em tracking, gold glow
- [x] 14.K.4: Two horizontal gold accent rails flanking title
- [x] 14.K.5: Status sub-line `2026 · ON AIR` (mono, +0.45em)
- [x] 14.K.6: Pulsing red dot when status === "live"
- [x] 14.K.7: Status labels On Air / Recorded / Standby / Off Air
- [x] 14.K.8: "Off Air" rendered in red #ff6b6b
- [x] 14.K.9: Designed Motion pill below status (gold capsule)
- [x] 14.K.10: Inner "MOTION" mono tag inside its own darker capsule
- [x] 14.K.11: Topic italic Space Grotesk, gold curly quotes, ellipsis
- [x] 14.K.12: Single-line clamp at `max-width: min(740px, 80vw)`
- [x] 14.K.13: `pointer-events: none` so banner doesn't block parallax

### Phase 14.L — Topic plumbing

- [x] 14.L.1: Add `topic` field to SlideState in `lib/types.ts`
- [x] 14.L.2: `openStream(debate_id, topic)` sets `state.topic`
- [x] 14.L.3: Banner reads `s.topic` with fallback constant
- [x] 14.L.4: Same topic in synthetic Judge intro slide

### Phase 14.M — Auto-start

- [x] 14.M.1: `app/page.tsx` calls `startDebate` on mount
- [x] 14.M.2: `firedRef` guard against Strict Mode + HMR double-mount
- [x] 14.M.3: On 200, `openStream(debate_id, topic)`
- [x] 14.M.4: On error, set status `error` with message
- [x] 14.M.5: Remove old StartScreen / Start button

### Phase 14.N — SSE consumer hardening

- [x] 14.N.1: Verify existing dedup via `seen: Set<string>`
- [x] 14.N.2: Skip `setup_directive` / `ack` events
- [x] 14.N.3: Skip judge re-broadcasts (forwarding plumbing)
- [x] 14.N.4: Prepend synthetic Judge intro slide on `openStream`
- [x] 14.N.5: On `verdict` event, build synthetic verdict slide
- [x] 14.N.6: Detect aborted via verdict.reason / outcome
- [x] 14.N.7: Forward `verdict.rationale` onto slide
- [x] 14.N.8: Tighten `onerror` to fire only on `readyState === CLOSED && status !== "done"`

### Phase 14.O — Chunking

- [x] 14.O.1: Create `lib/chunks.ts` exposing `splitIntoChunks`
- [x] 14.O.2: Initial regex `/[^.!?]+[.!?]+(?=\s|$)/g`
- [x] 14.O.3: Greedy bundler ≤ maxWords (default 28)
- [x] 14.O.4: Fallback to whole text when no sentence match
- [x] 14.O.5: Empty input returns `[]`
- [x] 14.O.6: Wire into `sse.ts` — one Slide per chunk for Pro/Con
- [x] 14.O.7: Chunk ids `msg_id-c<i>` for stable React keys + SSE dedup
- [x] 14.O.8: Judge text bypasses chunker
- [x] 14.O.9: Regression: fix decimal-point drop with `(?<!\d)[.!?]+(?!\d)`
- [x] 14.O.10: Vitest cover empty, fallback, decimals, short bundles, long single sentence

### Phase 14.P — Length-based dwell

- [x] 14.P.1: Create `lib/dwell.ts` with `computeDwellMs(text, opts?)`
- [x] 14.P.2: STANDALONE preset (130 wpm, 0.8 s entry, 3.5-14 s clamp)
- [x] 14.P.3: Initial CHUNK preset (170 wpm, tighter cap) — user said too fast
- [x] 14.P.4: Revised CHUNK preset (130 wpm, 0.7 s entry, 4.5-11 s)
- [x] 14.P.5: Vitest cover both presets + edges (9 cases total)
- [x] 14.P.6: Reading-speed citations in header (Brysbaert 2019 + BBC subtitles)

### Phase 14.Q — Auto-advance

- [x] 14.Q.1: Replace 3.5 s `setInterval` with per-slide `setTimeout`
- [x] 14.Q.2: Effect deps `[followLive, slideId, slideText, hasNext]`
- [x] 14.Q.3: Detect chunk via id regex `/-c\d+$/`
- [x] 14.Q.4: Track `slideStartRef` of current-slide entry time
- [x] 14.Q.5: Reset slideStartRef in own effect keyed on slideId
- [x] 14.Q.6: Timeout uses `max(0, dwell - elapsed)` for late slides
- [x] 14.Q.7: Bail when `followLive` is false (manual nav)
- [x] 14.Q.8: Bail when at last slide (`hasNext === false`)

### Phase 14.R — Bottom strip

- [x] 14.R.1: Reduce `slides[]` to `groups[]` of consecutive same-speaker entries
- [x] 14.R.2: Render one pill per group
- [x] 14.R.3: Pill width scales with `count`
- [x] 14.R.4: Tooltip shows speaker, count, slide-range
- [x] 14.R.5: Pill colour = `var(--color-${speaker}-accent)`
- [x] 14.R.6: Active pill bigger + glow
- [x] 14.R.7: Hide future pills entirely (per user request)
- [x] 14.R.8: Counter renders `turn N/total` of groups
- [x] 14.R.9: LIVE / Jump-to-Live button when `followLive` is off

### Phase 14.S — Backend scoring

- [x] 14.S.1: Create `src/agent_debate/agents/content_scorer.py`
- [x] 14.S.2: `_clarity` — avg words/sentence (14-word sweet spot)
- [x] 14.S.3: `_evidence` — years + percentages + proper nouns + cite cues
- [x] 14.S.4: `_rebuttal` — opponent-reference cue count
- [x] 14.S.5: `_novelty` — type-token ratio × 28
- [x] 14.S.6: `_role_fidelity` — own keywords - opponent + turn bonus
- [x] 14.S.7: `score_transcript(transcript)` returns `(pro_card, con_card)`
- [x] 14.S.8: Skip `ack` / `setup_directive` from the corpus
- [x] 14.S.9: Wire into `process_verdict.synth_scorecards`
- [x] 14.S.10: Wire into `debate_loop._synth_scorecards`
- [x] 14.S.11: Pytest cover empty / weak-strong / per-axis / ack-leak (6 cases)

### Phase 14.T — Verdict rationale

- [x] 14.T.1: Create `src/agent_debate/agents/verdict_rationale.py`
- [x] 14.T.2: `build_rationale(pro, con, winner)` returns 1-2 sentence string
- [x] 14.T.3: Find largest positive axis gap for winner
- [x] 14.T.4: Find largest negative gap (loser's strength)
- [x] 14.T.5: Margin classifier: `by a hair` / default / `decisive showing`
- [x] 14.T.6: Tiebreak case has its own sentence
- [x] 14.T.7: Wire into `finalize_verdict` → `transcript.verdict.rationale`
- [x] 14.T.8: `Slide.rationale` field added to `lib/types.ts`
- [x] 14.T.9: `sse.ts` forwards `verdict.rationale` to slide
- [x] 14.T.10: Chyron renders rationale below outcome
- [x] 14.T.11: Pytest cover lopsided / hair / loser-strength / con-wins / length (5 cases)

### Phase 14.U — Setup-phase timeout

- [x] 14.U.1: Bump `ACK_TIMEOUT_S` 30 → 60 s in `process_flow.py`
- [x] 14.U.2: Write structured verdict on setup failure in `orchestrator.py`
- [x] 14.U.3: Verdict shape `{winner: None, pro_total: 0, con_total: 0, reason: 'setup_phase_timeout'}`
- [x] 14.U.4: Frontend detects abort via reason / outcome
- [x] 14.U.5: Chyron shows `DEBATE ABORTED` caps in orange + human message
- [x] 14.U.6: Pytest still green after timeout bump

### Phase 14.V — Fireworks

- [x] 14.V.1: Create `components/stage14/fireworks.tsx`
- [x] 14.V.2: `<FireworkBurst>` with 64-particle THREE.Points
- [x] 14.V.3: Velocity seeding on unit sphere + small +y bias
- [x] 14.V.4: Per-frame parabolic arc with gravity 1.8
- [x] 14.V.5: Cycle 1.9 s with velocity re-seed on cycle start
- [x] 14.V.6: Opacity fade 1 → 0 across cycle
- [x] 14.V.7: PointsMaterial AdditiveBlending + sizeAttenuation
- [x] 14.V.8: Four bursts offset `0 / 0.65 / 1.3 / 1.9 s`
- [x] 14.V.9: Two bursts in winner accent + one gold + one white sparkle
- [x] 14.V.10: Mount inside PresentationControls so cursor pans too
- [x] 14.V.11: Stage derives `winner` only on verdict + decisive outcome
- [x] 14.V.12: `args={[positions, 3]}` on bufferAttribute for R3F strict types

### Phase 14.W — Manual visual passes

- [x] 14.W.1: Refresh → debate auto-starts within 5 s
- [x] 14.W.2: Judge intro slide visible before Pro's first turn
- [x] 14.W.3: Pro turn: camera swings, Pro reads big-left
- [x] 14.W.4: Con turn: camera swings, Con reads big-right
- [x] 14.W.5: Strip grows one pill at a time as dwell advances
- [x] 14.W.6: Active pill glows; past pills are slightly dimmer
- [x] 14.W.7: Title shows ON AIR with pulsing dot while live
- [x] 14.W.8: Motion pill clearly shows the topic
- [x] 14.W.9: Verdict slide shows OUTCOME + score + rationale
- [x] 14.W.10: Fireworks pop behind winning podium
- [x] 14.W.11: Title flips to "Recorded" after verdict
- [x] 14.W.12: Different debates produce different scores
- [x] 14.W.13: Setup-timeout displays "Debate Aborted" cleanly
- [x] 14.W.14: No console errors after a full run-through

### Phase 14.X — Automated regression

- [x] 14.X.1: `npx tsc --noEmit` clean
- [x] 14.X.2: `npx vitest run` green (34 tests as of writing)
- [x] 14.X.3: `uv run pytest tests/unit/` green (151 tests)
- [x] 14.X.4: `uv run ruff check src/` clean
- [x] 14.X.5: Pre-commit hook passes on every Phase 14 commit
- [x] 14.X.6: 150-line cap respected by every file

### Phase 14.Y — Closure docs

- [x] 14.Y.1: Brainstorm spec at `docs/superpowers/specs/2026-05-27-hw2-presidential-debate-stage.md`
- [x] 14.Y.2: Append Phase 14 section to `docs/PRD.md` (§15)
- [x] 14.Y.3: Append Phase 14 section to `docs/PLAN.md` (§16)
- [x] 14.Y.4: Append Phase 14 section to `docs/TODO.md` (this section)
- [x] 14.Y.5: Mirror plan in `docs/superpowers/plans/2026-05-27-hw2-presidential-debate-stage.md`
- [ ] 14.Y.6: Capture README screenshots (per-speaker camera, verdict + fireworks)
- [ ] 14.Y.7: Update root README.md with Phase 14 Bonus section + branch note
- [ ] 14.Y.8: Decide whether `main` ships Phase 13g or Phase 14
- [ ] 14.Y.9: If Phase 14 ships, rebase / merge into `main`, tag `v1.00-phase14`
- [ ] 14.Y.10: Push branch to GitHub public OR add `rmisegal@gmail.com` as collaborator
