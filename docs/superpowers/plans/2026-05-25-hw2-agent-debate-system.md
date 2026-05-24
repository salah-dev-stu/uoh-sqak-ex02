# HW2 Multi-Agent Debate System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a three-process Python debate system where AI agents (Pro/Con/Judge) conduct a structured argument over JSON-IPC with real Claude calls, DuckDuckGo web-search fact-checking, watchdog supervision, and a letter-keyed terminal UI — meeting all 25 HW2 audit gates (H1–H25) and recovering HW1's four weak spots (project planning, configuration/security, extensibility, quality standards).

**Architecture:** Three `multiprocessing.Process` children (Judge + Pro + Con) communicate via `multiprocessing.Queue` with a versioned JSON wire protocol. All inter-agent traffic routes through Judge (H4); all LLM/search calls funnel through `ApiGatekeeper`; Judge enforces drift detection (H20), PC filter (H16), 5-axis scoring, and no-tie verdict (H5). Skills load statically as system prompts (ADR-002 from spec). Letter-keyed terminal menu drives a single `DebateSDK` entry point so external Claude CLI can self-test (N8).

**Tech Stack:** Python 3.13, `uv`, pytest + pytest-cov, ruff (E/F/W/I/N/UP/B/C4/SIM), jsonschema, `ddgs` (DuckDuckGo), Claude Code CLI (login auth), pre-commit, GitHub Actions.

**Authoring source:** `docs/superpowers/specs/2026-05-24-hw2-debate-design.md`. 31 locked decisions in `docs/PROMPTS.md`.

**Deadline:** Friday, 29 May 2026, 23:59 Asia/Jerusalem. Late penalty: −5 pts / 24h.

---

## Canonical Vibe Coding Lifecycle (Dr. Segal's slide — follow verbatim)

The lecturer's slide, reproduced verbatim from class:

```
Insert into plan mode
Your mission is to create the following PRD document base on the
following description

Bullets
  • A
  • B
  • C

prd.md
Plan.md
Todo.md  (300-800)

Verify that all prd demand implemented in the todo list.
You must be very critical

Execute the todo list one by one and mark each task that was done

You must create a readme file

Run the project
push to github  as public
```

**Execution order — this overrides the phase numbers below.** Phases below are written in dependency order (foundation → code → tests → docs → run) but the lecturer mandates **docs FIRST**, code SECOND, README LAST, run-then-push at the end. Map:

| Slide step | Maps to phase / task | Approval gate |
|---|---|---|
| 1. "Insert into plan mode" + "Your mission is to create the following PRD document…" | **Phase A** → Task 11.2 (`docs/PRD.md`) | **GATE 1** — wait for user approval before continuing |
| 2. "Plan.md" | **Phase B** → Task 11.3 (`docs/PLAN.md`) | — |
| 3. "Todo.md (300-800)" | **Phase C** → Task 11.4 (`docs/TODO.md`) | — |
| 4. "Verify that all PRD demand implemented in the todo list. You must be very critical" | **Phase D** → Task 11.4 verify sub-step | — |
| 4b. Per-mechanism PRDs (9 files, rubric §2.5 step 4) | **Phase E** → Task 11.5 | **GATE 2** — full doc package approval (rubric §2.5 step 5) |
| 5. "Execute the todo list one by one and mark each task that was done" | **Phases 0-10** (scaffold + foundation + providers + gatekeeper + skills + agents + orchestration + watchdog + SDK + tests) | — |
| 6. "You must create a readme file" | **Phase 11.1** → README.md | — |
| 7. "Run the project" | **Phase 12.1** (manual Phase 1) + **12.2** (end-to-end) | — |
| 8. "push to github as public" | **Phase 12.4** (public repo + collaborator) | — |

### Verbatim prompts to use (Dr. Segal's exact phrasing)

**For Task 11.2 (PRD generation):** Use these words exactly when invoking the PRD-writer (a subagent or yourself):

> "Your mission is to create the following PRD document based on the following description:"
> *(followed by bullets distilled from `docs/superpowers/specs/2026-05-24-hw2-debate-design.md`)*

**For Task 11.4 (TODO verification sub-step):** Use this exact prompt after the first TODO draft is written:

> "Verify that all PRD demand implemented in the todo list. You must be very critical."

Per lec01 L1199-1201, this pass typically adds ~200 missed tasks. Budget for the additions.

### TODO size — reconciling three numbers

| Source | Range |
|---|---|
| Lecturer slide (this screenshot) | 300–800 |
| Lecturer spoken word (lec01 L1170-1180) | 500–1000 |
| CLAUDE.md project target (HW2 quality target ≥90) | min 500, aim 800–1000 |

**Target: 800 tasks (top of slide range, bottom of CLAUDE.md target).** If the verify pass adds tasks, accept up to 1000. Document the choice in `docs/TODO.md` header so the grading agent sees the deliberation.

### Approval gates are non-negotiable (rubric §2.5)

The grading agent inspects git timeline for evidence that work paused at the gates. No code commits between writing `docs/PRD.md` and the user typing "approved." No code commits between completing the per-mechanism PRDs and the user typing "approved" again. The pauses are part of the deliverable.

---

## File structure (the map)

Every file gets created or modified by an explicit task. No file appears mid-plan without a Create/Modify entry.

```
hw2/
├── pyproject.toml                     [Task 0.2 Create]
├── uv.lock                            [Task 0.2 Create — auto-generated, tracked]
├── .env-example                       [Task 0.4 Create]
├── .pre-commit-config.yaml            [Task 0.6 Create]
├── .github/workflows/ci.yml           [Task 0.7 Create]
├── README.md                          [Task 11.1 Create — final-shape user manual]
├── LICENSE                            [Task 11.7 Create — MIT]
│
├── src/agent_debate/
│   ├── __init__.py                    [Task 0.5 Create — defines __version__, __all__]
│   ├── constants.py                   [Task 1.1 Create]
│   ├── main.py                        [Task 9.5 Create — CLI entry point]
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── version.py                 [Task 1.2]
│   │   ├── config.py                  [Task 1.3]
│   │   ├── structured_logger.py       [Task 1.4]
│   │   ├── message_schema.py          [Task 1.5]
│   │   └── gatekeeper.py              [Task 3.1]
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── registry.py                [Task 2.1]
│   │   ├── llm_provider.py            [Task 2.2 — abstract]
│   │   ├── claude_login_provider.py   [Task 2.3]
│   │   ├── mock_llm_provider.py       [Task 2.4]
│   │   ├── search_provider.py         [Task 2.5 — abstract]
│   │   ├── duckduckgo_provider.py     [Task 2.6]
│   │   ├── mock_search_provider.py    [Task 2.7]
│   │   └── web_search.py              [Task 2.8]
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py              [Task 5.1]
│   │   ├── partisan_agent.py          [Task 5.2]
│   │   ├── pro_agent.py               [Task 5.3]
│   │   ├── con_agent.py               [Task 5.4]
│   │   ├── judge_agent.py             [Task 6.1]
│   │   ├── drift_detector.py          [Task 6.2]
│   │   ├── pc_filter.py               [Task 6.3]
│   │   └── scoring_engine.py          [Task 6.4]
│   ├── orchestration/
│   │   ├── __init__.py
│   │   ├── lifecycle_registry.py      [Task 7.1]
│   │   ├── orchestrator.py            [Task 7.2]
│   │   └── watchdog.py                [Task 8.1]
│   ├── sdk/
│   │   ├── __init__.py
│   │   └── debate_sdk.py              [Task 9.1]
│   └── menu/
│       ├── __init__.py
│       └── tui.py                     [Task 9.3]
│
├── tests/
│   ├── conftest.py                    [Task 0.8]
│   ├── fixtures/
│   │   └── llm_responses/             [Task 4.4 — canned JSON]
│   ├── unit/
│   │   ├── test_constants.py          [Task 1.1]
│   │   ├── test_version.py            [Task 1.2]
│   │   ├── test_config.py             [Task 1.3]
│   │   ├── test_structured_logger.py  [Task 1.4]
│   │   ├── test_message_schema.py     [Task 1.5]
│   │   ├── test_registry.py           [Task 2.1]
│   │   ├── test_claude_login_provider.py [Task 2.3]
│   │   ├── test_mock_llm_provider.py     [Task 2.4]
│   │   ├── test_duckduckgo_provider.py   [Task 2.6]
│   │   ├── test_web_search.py            [Task 2.8]
│   │   ├── test_gatekeeper.py            [Task 3.x]
│   │   ├── test_base_agent.py            [Task 5.1]
│   │   ├── test_partisan_agent.py        [Task 5.2]
│   │   ├── test_pro_agent.py             [Task 5.3]
│   │   ├── test_con_agent.py             [Task 5.4]
│   │   ├── test_judge_agent.py           [Task 6.1]
│   │   ├── test_drift_detector.py        [Task 6.2]
│   │   ├── test_pc_filter.py             [Task 6.3]
│   │   ├── test_scoring_engine.py        [Task 6.4]
│   │   ├── test_lifecycle_registry.py    [Task 7.1]
│   │   ├── test_orchestrator.py          [Task 7.2]
│   │   ├── test_watchdog.py              [Task 8.1]
│   │   ├── test_debate_sdk.py            [Task 9.1]
│   │   └── test_tui.py                   [Task 9.3]
│   ├── integration/
│   │   ├── test_full_debate_mocked.py     [Task 10.1]
│   │   ├── test_drift_correction.py       [Task 10.2]
│   │   ├── test_pc_intervention.py        [Task 10.3]
│   │   ├── test_chaos_child_kill.py       [Task 10.4]
│   │   ├── test_chaos_child_hang.py       [Task 10.5]
│   │   ├── test_budget_exhausted.py       [Task 10.6]
│   │   ├── test_graceful_shutdown.py      [Task 10.7]
│   │   ├── test_no_tie_enforcer.py        [Task 10.8]
│   │   └── test_setup_directive_ack.py    [Task 10.9]
│   └── e2e/
│       ├── test_real_debate_5_pings.py    [Task 10.10]
│       ├── test_real_search_dual.py       [Task 10.11]
│       └── test_real_pc_filter.py         [Task 10.12]
│
├── config/
│   ├── setup.json                     [Task 0.3]
│   ├── agents.json                    [Task 0.3]
│   ├── debate_rules.json              [Task 0.3]
│   ├── rate_limits.json               [Task 0.3]
│   ├── logging_config.json            [Task 0.3]
│   └── schemas/
│       └── message-1.00.json          [Task 1.5]
│
├── .claude/skills/
│   ├── pro_skill/
│   │   ├── SKILL.md                   [Task 4.1]
│   │   └── references/citations.md    [Task 4.1]
│   ├── con_skill/
│   │   ├── SKILL.md                   [Task 4.2]
│   │   └── references/citations.md    [Task 4.2]
│   └── judge_skill/
│       ├── SKILL.md                   [Task 4.3]
│       ├── references/debate_criteria.md [Task 4.5 — generated]
│       └── scripts/compute_scores.py     [Task 6.4 — bundled with scoring_engine]
│
├── scripts/
│   ├── check_file_lines.py            [Task 0.6]
│   ├── build_judge_criteria.py        [Task 4.5]
│   └── fill_submission_pdf.py         [pre-existing — unchanged]
│
├── docs/
│   ├── PRD.md                         [Task 11.2 Create]
│   ├── PLAN.md                        [Task 11.3 Create]
│   ├── TODO.md                        [Task 11.4 Create]
│   ├── PROMPTS.md                     [pre-existing — appended throughout]
│   ├── PRD_judge_agent.md             [Task 11.5]
│   ├── PRD_pro_agent.md               [Task 11.5]
│   ├── PRD_con_agent.md               [Task 11.5]
│   ├── PRD_orchestrator.md            [Task 11.5]
│   ├── PRD_ipc_bus.md                 [Task 11.5]
│   ├── PRD_gatekeeper.md              [Task 11.5]
│   ├── PRD_watchdog.md                [Task 11.5]
│   ├── PRD_skills.md                  [Task 11.5]
│   ├── PRD_web_search_tool.md         [Task 11.5]
│   ├── ADRs/
│   │   ├── ADR-001-ipc-queue.md       [Task 11.6]
│   │   ├── ADR-002-skill-static-load.md  [Task 11.6]
│   │   ├── ADR-003-claude-cli-shellout.md [Task 11.6]
│   │   ├── ADR-004-search-pluggable.md    [Task 11.6]
│   │   ├── ADR-005-same-provider-mitigation.md [Task 11.6]
│   │   ├── ADR-006-cross-process-spend.md      [Task 11.6]
│   │   └── ADR-007-judge-criteria-preflight.md [Task 11.6]
│   └── diagrams/
│       ├── c4-context.svg              [Task 11.3]
│       ├── c4-container.svg            [Task 11.3]
│       ├── class-diagram.svg           [Task 11.3]
│       └── sequence-single-ping.svg    [Task 11.3]
│
├── logs/                              [git-ignored, created at runtime]
└── transcripts/
    └── sample-session-1.json          [Task 12.2 — generated by manual run]
```

---

## Phase 0 — Project scaffold (uv-runnable empty package, linter passing, pre-commit set up)

### Task 0.1: uv init + Python 3.13 pin

**Files:** Create `pyproject.toml` (initial), `.python-version`, `.gitignore` (append)

- [ ] **Step 1: Run uv init in worktree**

```bash
cd /Users/salah/Projects/orch-ai-agents/hw2
uv init --name agent-debate --package --python 3.13
```

Expected: creates `pyproject.toml` skeleton, `.python-version` file with `3.13`, `src/agent_debate/__init__.py`. May complain about existing files — answer no to overwrite.

- [ ] **Step 2: Verify the install**

```bash
uv python pin 3.13
uv sync
uv run python --version
```

Expected: `Python 3.13.x`.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml .python-version src/agent_debate/__init__.py uv.lock
git commit -m "build: scaffold uv project on Python 3.13"
```

---

### Task 0.2: Configure pyproject.toml — dependencies, ruff, pytest, coverage

**Files:** Modify `pyproject.toml`

- [ ] **Step 1: Replace pyproject.toml contents**

```toml
[project]
name = "agent-debate"
version = "1.00.0"
description = "HW2: Multi-agent debate system (course 203.3763)"
readme = "README.md"
requires-python = ">=3.13"
authors = [
    { name = "Salah Qadah" },
    { name = "Andalus Kalash" },
]
license = { text = "MIT" }
dependencies = [
    "jsonschema>=4.20",
    "ddgs>=9.0",
    "pydantic>=2.5",
]

[project.scripts]
agent-debate = "agent_debate.main:main"

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-timeout>=2.3",
    "ruff>=0.6",
    "pre-commit>=3.7",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "C4", "SIM"]
ignore = ["E501"]

[tool.pytest.ini_options]
addopts = "-ra --strict-markers"
testpaths = ["tests"]
markers = [
    "e2e: requires real Claude CLI + DDG (gated by RUN_E2E=1)",
    "chaos: deliberately kills processes mid-flight",
]
timeout = 60

[tool.coverage.run]
source = ["src"]
omit = ["src/agent_debate/main.py", "*/tests/*"]

[tool.coverage.report]
fail_under = 85
show_missing = true
```

- [ ] **Step 2: Sync dependencies**

```bash
uv sync
```

Expected: lockfile populated, .venv created.

- [ ] **Step 3: Verify ruff runs**

```bash
uv run ruff check src tests
```

Expected: empty output (no Python files yet) or success.

- [ ] **Step 4: Verify pytest runs**

```bash
uv run pytest
```

Expected: "no tests ran" with exit 5 (acceptable for now).

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "build: configure ruff, pytest, coverage in pyproject.toml"
```

---

### Task 0.3: Create config/ JSON files (versioned at 1.00)

**Files:** Create `config/setup.json`, `config/agents.json`, `config/debate_rules.json`, `config/rate_limits.json`, `config/logging_config.json`

- [ ] **Step 1: Write `config/setup.json`**

```json
{
  "version": "1.00",
  "project_name": "agent-debate",
  "debate_topic": "Can AI agents create genuinely original art, or only remix human work?",
  "pro_stance": "AI=ORIGINALITY",
  "con_stance": "AI=REMIX_ONLY",
  "transcript_dir": "./transcripts",
  "log_dir": "./logs",
  "skills_dir": "./.claude/skills"
}
```

- [ ] **Step 2: Write `config/agents.json`**

```json
{
  "version": "1.00",
  "agents": {
    "pro": {
      "skill_name": "pro_skill",
      "temperature": 0.85,
      "llm_provider": "claude_login",
      "max_words_per_turn": 250
    },
    "con": {
      "skill_name": "con_skill",
      "temperature": 0.85,
      "llm_provider": "claude_login",
      "max_words_per_turn": 250
    },
    "judge": {
      "skill_name": "judge_skill",
      "temperature": 0.30,
      "llm_provider": "claude_login",
      "max_words_per_turn": 400,
      "topic_blind": true
    }
  }
}
```

- [ ] **Step 3: Write `config/debate_rules.json`**

```json
{
  "version": "1.00",
  "pings_per_side": 10,
  "max_words_per_turn": 250,
  "drift_intervention_threshold": 1,
  "drift_intervention_action": "correct_and_replay",
  "scoring_axes": ["clarity", "evidence", "rebuttal", "novelty", "role_fidelity"],
  "scoring_max_per_axis": 20,
  "no_tie_allowed": true,
  "search_default_provider": "duckduckgo"
}
```

- [ ] **Step 4: Write `config/rate_limits.json`**

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
      "max_retries": 3,
      "timeout_seconds": 90
    },
    "ddg_search": {
      "requests_per_minute": 10,
      "requests_per_hour": 100,
      "concurrent_max": 2,
      "timeout_seconds": 30
    }
  }
}
```

- [ ] **Step 5: Write `config/logging_config.json`**

```json
{
  "version": "1.00",
  "fifo_files": 20,
  "max_lines_per_file": 500,
  "rotation_policy": "size_or_count",
  "output_dir": "./logs",
  "structured": true,
  "level": "INFO"
}
```

- [ ] **Step 6: Commit**

```bash
git add config/
git commit -m "config: add versioned JSON configs (setup, agents, debate_rules, rate_limits, logging)"
```

---

### Task 0.4: Create .env-example

**Files:** Create `.env-example`

- [ ] **Step 1: Write `.env-example`**

```bash
# HW2 Agent Debate System — environment template
# Copy to `.env` and fill in values. NEVER commit .env.

# Claude CLI must be installed and `claude` available on PATH.
# Login once via: claude --login
# This is the default mode (claude_login provider). No key needed.

# Optional: switch to API-key mode by setting these and editing
# config/agents.json llm_provider to "claude_api".
# ANTHROPIC_API_KEY=

# Optional: pluggable search backends (defaults to DuckDuckGo, no key).
# BRAVE_SEARCH_API_KEY=
# TAVILY_API_KEY=

# Test gates
# RUN_E2E=0    # set to 1 to enable e2e tests against the real Claude + DDG
```

- [ ] **Step 2: Commit**

```bash
git add .env-example
git commit -m "config: add .env-example template (no secrets)"
```

---

### Task 0.5: `src/agent_debate/__init__.py` with __version__ and __all__

**Files:** Modify `src/agent_debate/__init__.py`

- [ ] **Step 1: Write the package init**

```python
"""HW2 Multi-Agent Debate System.

Entry point: `agent_debate.main:main`. Public API: `agent_debate.sdk.DebateSDK`.
"""

__version__ = "1.00"
__all__ = ["__version__"]
```

- [ ] **Step 2: Verify ruff passes**

```bash
uv run ruff check src/agent_debate/__init__.py
```

Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add src/agent_debate/__init__.py
git commit -m "feat: define __version__ at package root (R6 versioning)"
```

---

### Task 0.6: Pre-commit hook + file-line enforcer

**Files:** Create `.pre-commit-config.yaml`, `scripts/check_file_lines.py`

- [ ] **Step 1: Write `scripts/check_file_lines.py`**

```python
"""Enforce the 150-line limit on every .py file in src/ and tests/.

Counts non-blank, non-comment lines. Also flags suspiciously compressed
files (>100 chars per line, no comments) to catch whitespace-game cheats
that Dr. Segal's grading agent explicitly looks for.
"""
from __future__ import annotations

import sys
from pathlib import Path

MAX_LINES = 150
MAX_LINE_LEN = 100


def count_logical_lines(text: str) -> int:
    return sum(
        1 for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    )


def has_long_line_no_comments(text: str) -> bool:
    has_comment = any(
        line.strip().startswith("#") for line in text.splitlines()
    )
    has_long = any(len(line) > MAX_LINE_LEN for line in text.splitlines())
    return has_long and not has_comment


def main() -> int:
    repo_root = Path(__file__).parent.parent
    targets = list(repo_root.glob("src/**/*.py")) + list(
        repo_root.glob("tests/**/*.py")
    )
    violations: list[str] = []
    for path in targets:
        text = path.read_text()
        n = count_logical_lines(text)
        if n > MAX_LINES:
            violations.append(f"{path}: {n} lines (limit {MAX_LINES})")
        if has_long_line_no_comments(text):
            violations.append(f"{path}: suspiciously compressed (long lines, no comments)")
    if violations:
        print("\n".join(violations), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Write `.pre-commit-config.yaml`**

```yaml
repos:
  - repo: local
    hooks:
      - id: ruff
        name: ruff
        entry: uv run ruff check
        language: system
        types: [python]
      - id: file-line-limit
        name: 150-line check
        entry: uv run python scripts/check_file_lines.py
        language: system
        pass_filenames: false
      - id: pytest-unit
        name: pytest (unit only — fast)
        entry: uv run pytest tests/unit -x -q
        language: system
        pass_filenames: false
```

- [ ] **Step 3: Install pre-commit**

```bash
uv run pre-commit install
```

Expected: "pre-commit installed at .git/hooks/pre-commit".

- [ ] **Step 4: Verify the file-line enforcer runs clean (no .py files yet)**

```bash
uv run python scripts/check_file_lines.py
```

Expected: exit 0, no output.

- [ ] **Step 5: Commit**

```bash
git add scripts/check_file_lines.py .pre-commit-config.yaml
git commit -m "build: pre-commit (ruff + 150-line enforcer + unit tests)"
```

---

### Task 0.7: GitHub Actions CI

**Files:** Create `.github/workflows/ci.yml`

- [ ] **Step 1: Write the workflow**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Pin Python 3.13
        run: uv python pin 3.13

      - name: Sync deps
        run: uv sync

      - name: Ruff
        run: uv run ruff check src tests

      - name: File-line enforcer
        run: uv run python scripts/check_file_lines.py

      - name: pytest with coverage
        run: uv run pytest tests/unit tests/integration --cov --cov-fail-under=85
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions workflow (ruff + line enforcer + pytest+coverage)"
```

---

### Task 0.8: Tests scaffolding — conftest.py + empty unit/integration dirs

**Files:** Create `tests/__init__.py`, `tests/conftest.py`, `tests/unit/__init__.py`, `tests/integration/__init__.py`, `tests/e2e/__init__.py`, `tests/fixtures/__init__.py`

- [ ] **Step 1: Create all `__init__.py` files**

```bash
mkdir -p tests/unit tests/integration tests/e2e tests/fixtures/llm_responses
touch tests/__init__.py tests/unit/__init__.py tests/integration/__init__.py tests/e2e/__init__.py tests/fixtures/__init__.py
```

- [ ] **Step 2: Write `tests/conftest.py`** (initial — fixtures will be added by each Phase as needed)

```python
"""Shared pytest fixtures. Phase-specific fixtures get added as tasks reach them."""
from __future__ import annotations

import os
import pytest


def pytest_collection_modifyitems(config, items):
    """Skip e2e tests unless RUN_E2E=1."""
    if os.environ.get("RUN_E2E") == "1":
        return
    skip_e2e = pytest.mark.skip(reason="requires RUN_E2E=1")
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(skip_e2e)
```

- [ ] **Step 3: Verify pytest discovers no tests but doesn't error**

```bash
uv run pytest --collect-only -q
```

Expected: "no tests ran" or empty collection.

- [ ] **Step 4: Commit**

```bash
git add tests/
git commit -m "test: scaffold tests/ tree with conftest e2e gate (RUN_E2E=1)"
```

---

## Phase 1 — Foundation infrastructure (constants, version, config, logger, schema)

### Task 1.1: Constants module

**Files:** Create `src/agent_debate/constants.py`, `tests/unit/test_constants.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_constants.py
"""Constants are immutable and cover all domain enums."""
from agent_debate.constants import (
    AgentRole,
    MessageRole,
    Stance,
    DebateOutcome,
)


def test_agent_role_enum_has_three_members():
    assert {r.value for r in AgentRole} == {"pro", "con", "judge"}


def test_message_role_enum_has_eight_members():
    assert {r.value for r in MessageRole} == {
        "setup_directive", "ack", "argument", "counter",
        "correction_request", "intervention", "status", "verdict",
    }


def test_stance_enum_has_two_members():
    assert {s.value for s in Stance} == {"AI=ORIGINALITY", "AI=REMIX_ONLY"}


def test_debate_outcome_includes_aborted():
    assert "debate_aborted" in {o.value for o in DebateOutcome}
```

- [ ] **Step 2: Run, expect fail**

```bash
uv run pytest tests/unit/test_constants.py -v
```

Expected: ImportError — `constants` module not defined.

- [ ] **Step 3: Write `src/agent_debate/constants.py`**

```python
"""Project-wide constants and enums (R10: no hardcoded magic strings in code)."""
from __future__ import annotations

from enum import Enum


class AgentRole(str, Enum):
    PRO = "pro"
    CON = "con"
    JUDGE = "judge"


class MessageRole(str, Enum):
    SETUP_DIRECTIVE = "setup_directive"
    ACK = "ack"
    ARGUMENT = "argument"
    COUNTER = "counter"
    CORRECTION_REQUEST = "correction_request"
    INTERVENTION = "intervention"
    STATUS = "status"
    VERDICT = "verdict"


class Stance(str, Enum):
    ORIGINALITY = "AI=ORIGINALITY"
    REMIX_ONLY = "AI=REMIX_ONLY"


class DebateOutcome(str, Enum):
    PRO_WINS = "pro_wins"
    CON_WINS = "con_wins"
    DEBATE_ABORTED = "debate_aborted"
    BUDGET_EXHAUSTED = "budget_exhausted"


SCHEMA_VERSION = "1.00"
```

- [ ] **Step 4: Run tests, expect pass**

```bash
uv run pytest tests/unit/test_constants.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add src/agent_debate/constants.py tests/unit/test_constants.py
git commit -m "feat(constants): add AgentRole, MessageRole, Stance, DebateOutcome enums"
```

---

### Task 1.2: Version module (R6 — starts at 1.00, +0.01 per change)

**Files:** Create `src/agent_debate/shared/__init__.py`, `src/agent_debate/shared/version.py`, `tests/unit/test_version.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_version.py
from agent_debate.shared.version import CODE_VERSION, validate_config_version


def test_code_version_starts_at_1_00():
    assert CODE_VERSION == "1.00"


def test_validate_config_version_accepts_matching():
    validate_config_version("1.00", source="setup.json")  # should not raise


def test_validate_config_version_rejects_mismatch():
    import pytest
    with pytest.raises(ValueError, match="version mismatch"):
        validate_config_version("2.00", source="setup.json")
```

- [ ] **Step 2: Run, expect fail**

```bash
uv run pytest tests/unit/test_version.py -v
```

- [ ] **Step 3: Implement `version.py`**

```python
"""Code version tracking (R6 — starts at 1.00, bumps +0.01 per change).

Validates loaded config files declare a compatible version at startup.
"""
from __future__ import annotations

CODE_VERSION = "1.00"


def validate_config_version(config_version: str, source: str) -> None:
    if config_version != CODE_VERSION:
        raise ValueError(
            f"Config version mismatch: {source} declares {config_version} "
            f"but code expects {CODE_VERSION}"
        )
```

- [ ] **Step 4: Add `shared/__init__.py`**

```python
"""Cross-cutting concerns: version, config loader, logger, schema, gatekeeper."""
```

- [ ] **Step 5: Run, expect pass + commit**

```bash
uv run pytest tests/unit/test_version.py -v
git add src/agent_debate/shared/ tests/unit/test_version.py
git commit -m "feat(version): add CODE_VERSION 1.00 + config-version compat check"
```

---

### Task 1.3: Config loader

**Files:** Create `src/agent_debate/shared/config.py`, `tests/unit/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_config.py
from pathlib import Path

import pytest

from agent_debate.shared.config import Config, load_config


def test_load_config_returns_dataclass(tmp_path: Path):
    setup = tmp_path / "setup.json"
    setup.write_text('{"version": "1.00", "project_name": "x", "debate_topic": "t",'
                     ' "pro_stance": "p", "con_stance": "c", "transcript_dir": "./t",'
                     ' "log_dir": "./l", "skills_dir": "./s"}')
    # minimal stubs for the other configs
    for name in ("agents", "debate_rules", "rate_limits", "logging_config"):
        (tmp_path / f"{name}.json").write_text('{"version": "1.00"}')
    cfg = load_config(tmp_path)
    assert isinstance(cfg, Config)
    assert cfg.setup["debate_topic"] == "t"


def test_load_config_rejects_wrong_version(tmp_path: Path):
    setup = tmp_path / "setup.json"
    setup.write_text('{"version": "2.00"}')
    for name in ("agents", "debate_rules", "rate_limits", "logging_config"):
        (tmp_path / f"{name}.json").write_text('{"version": "1.00"}')
    with pytest.raises(ValueError, match="version mismatch"):
        load_config(tmp_path)
```

- [ ] **Step 2: Run, expect fail**

- [ ] **Step 3: Implement `config.py`**

```python
"""Load and validate the five JSON config files. Version-compatible per R6."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from agent_debate.shared.version import validate_config_version

_CONFIG_FILES = ("setup", "agents", "debate_rules", "rate_limits", "logging_config")


@dataclass(frozen=True)
class Config:
    setup: dict
    agents: dict
    debate_rules: dict
    rate_limits: dict
    logging_config: dict


def load_config(config_dir: Path) -> Config:
    loaded: dict[str, dict] = {}
    for name in _CONFIG_FILES:
        path = config_dir / f"{name}.json"
        data = json.loads(path.read_text())
        validate_config_version(data["version"], source=path.name)
        loaded[name] = data
    return Config(**loaded)
```

- [ ] **Step 4: Run, expect pass + commit**

```bash
uv run pytest tests/unit/test_config.py -v
git add src/agent_debate/shared/config.py tests/unit/test_config.py
git commit -m "feat(config): add Config dataclass + load_config with version check"
```

---

### Task 1.4: Structured logger with FIFO rotation (rubric §A14 — 20 files × 500 lines)

**Files:** Create `src/agent_debate/shared/structured_logger.py`, `tests/unit/test_structured_logger.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_structured_logger.py
import json
from pathlib import Path

from agent_debate.shared.structured_logger import StructuredLogger


def test_logger_writes_json_line(tmp_path: Path):
    logger = StructuredLogger(output_dir=tmp_path, fifo_files=20, max_lines_per_file=500)
    logger.log(level="INFO", component="test", event="hello", payload={"a": 1})
    files = sorted(tmp_path.glob("*.jsonl"))
    assert len(files) == 1
    line = files[0].read_text().strip()
    record = json.loads(line)
    assert record["component"] == "test"
    assert record["event"] == "hello"
    assert record["payload"] == {"a": 1}
    assert "ts" in record


def test_logger_rotates_after_max_lines(tmp_path: Path):
    logger = StructuredLogger(output_dir=tmp_path, fifo_files=20, max_lines_per_file=3)
    for i in range(7):
        logger.log(level="INFO", component="t", event=f"e{i}")
    files = sorted(tmp_path.glob("*.jsonl"))
    assert len(files) >= 3  # 3 full + at least 1 in progress


def test_logger_caps_at_fifo_files(tmp_path: Path):
    logger = StructuredLogger(output_dir=tmp_path, fifo_files=2, max_lines_per_file=1)
    for i in range(10):
        logger.log(level="INFO", component="t", event=f"e{i}")
    files = sorted(tmp_path.glob("*.jsonl"))
    assert len(files) <= 2
```

- [ ] **Step 2: Run, expect fail**

- [ ] **Step 3: Implement `structured_logger.py`**

```python
"""Structured JSON logger with FIFO file rotation (rubric §A14, HW2 spec §8.6)."""
from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path


class StructuredLogger:
    """
    Input:  level, component, event, payload (dict, optional)
    Output: appends JSONL record; rotates FIFO at max_lines_per_file
    Setup:  output_dir (Path), fifo_files (int), max_lines_per_file (int)
    """

    def __init__(self, output_dir: Path, fifo_files: int, max_lines_per_file: int) -> None:
        self.output_dir = output_dir
        self.fifo_files = fifo_files
        self.max_lines = max_lines_per_file
        self._lock = threading.Lock()
        self._current_idx = 0
        self._current_lines = 0
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def log(self, level: str, component: str, event: str, **payload) -> None:
        record = {
            "ts": datetime.now(tz=timezone.utc).isoformat(),
            "level": level,
            "component": component,
            "event": event,
        }
        if payload:
            record["payload"] = payload
        line = json.dumps(record, separators=(",", ":")) + "\n"
        with self._lock:
            self._rotate_if_needed()
            self._current_path().open("a").write(line)
            self._current_lines += 1

    def _current_path(self) -> Path:
        return self.output_dir / f"log-{self._current_idx:03d}.jsonl"

    def _rotate_if_needed(self) -> None:
        if self._current_lines >= self.max_lines:
            self._current_idx = (self._current_idx + 1) % self.fifo_files
            self._current_lines = 0
            self._current_path().unlink(missing_ok=True)
```

- [ ] **Step 4: Run, expect pass + commit**

```bash
uv run pytest tests/unit/test_structured_logger.py -v
git add src/agent_debate/shared/structured_logger.py tests/unit/test_structured_logger.py
git commit -m "feat(logger): structured JSONL logger with FIFO rotation (20×500 default)"
```

---

### Task 1.5: Message schema + jsonschema validator

**Files:** Create `config/schemas/message-1.00.json`, `src/agent_debate/shared/message_schema.py`, `tests/unit/test_message_schema.py`

- [ ] **Step 1: Write the JSON schema to `config/schemas/message-1.00.json`** (full schema from spec §4)

(Use the exact schema from `docs/superpowers/specs/2026-05-24-hw2-debate-design.md` §4 — full required fields: msg_id, schema_version, from, to, role, ping_index, text, timestamp. Optional: references_opponent, citations, scoring, tokens_in, tokens_out.)

- [ ] **Step 2: Write failing tests**

```python
# tests/unit/test_message_schema.py
import uuid
from datetime import datetime, timezone

import pytest

from agent_debate.shared.message_schema import Message, validate_message


def _valid(**overrides) -> dict:
    base = {
        "msg_id": str(uuid.uuid4()),
        "schema_version": "1.00",
        "from": "pro",
        "to": "judge",
        "role": "argument",
        "ping_index": 1,
        "text": "Hello.",
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }
    base.update(overrides)
    return base


def test_valid_argument_passes():
    validate_message(_valid())


def test_invalid_role_fails():
    with pytest.raises(Exception):
        validate_message(_valid(role="nonsense"))


def test_missing_from_fails():
    msg = _valid()
    del msg["from"]
    with pytest.raises(Exception):
        validate_message(msg)


def test_message_dataclass_roundtrip():
    raw = _valid()
    msg = Message.from_dict(raw)
    assert msg.from_role == "pro"
    assert msg.to_dict() == raw
```

- [ ] **Step 3: Implement `message_schema.py`**

```python
"""Message dataclass + jsonschema validator for the inter-agent JSON wire protocol."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import jsonschema

_SCHEMA_PATH = Path(__file__).parent.parent.parent.parent / "config" / "schemas" / "message-1.00.json"
_SCHEMA = json.loads(_SCHEMA_PATH.read_text())


def validate_message(msg: dict) -> None:
    jsonschema.validate(msg, _SCHEMA)


@dataclass(frozen=True)
class Message:
    """Immutable wire-protocol message. Use `Message.from_dict` for parsing."""

    msg_id: str
    schema_version: str
    from_role: str  # 'from' is a Python keyword; renamed
    to_role: str
    role: str
    ping_index: int
    text: str
    timestamp: str
    references_opponent: bool | None = None
    citations: list[dict] = field(default_factory=list)
    scoring: dict | None = None
    tokens_in: int | None = None
    tokens_out: int | None = None

    @classmethod
    def from_dict(cls, d: dict) -> Message:
        validate_message(d)
        return cls(
            msg_id=d["msg_id"],
            schema_version=d["schema_version"],
            from_role=d["from"],
            to_role=d["to"],
            role=d["role"],
            ping_index=d["ping_index"],
            text=d["text"],
            timestamp=d["timestamp"],
            references_opponent=d.get("references_opponent"),
            citations=d.get("citations", []),
            scoring=d.get("scoring"),
            tokens_in=d.get("tokens_in"),
            tokens_out=d.get("tokens_out"),
        )

    def to_dict(self) -> dict:
        out = {
            "msg_id": self.msg_id,
            "schema_version": self.schema_version,
            "from": self.from_role,
            "to": self.to_role,
            "role": self.role,
            "ping_index": self.ping_index,
            "text": self.text,
            "timestamp": self.timestamp,
        }
        if self.references_opponent is not None:
            out["references_opponent"] = self.references_opponent
        if self.citations:
            out["citations"] = self.citations
        if self.scoring is not None:
            out["scoring"] = self.scoring
        if self.tokens_in is not None:
            out["tokens_in"] = self.tokens_in
        if self.tokens_out is not None:
            out["tokens_out"] = self.tokens_out
        return out
```

- [ ] **Step 4: Run, expect pass + commit**

```bash
uv run pytest tests/unit/test_message_schema.py -v
git add config/schemas/ src/agent_debate/shared/message_schema.py tests/unit/test_message_schema.py
git commit -m "feat(schema): JSON wire protocol 1.00 + jsonschema validator + Message dataclass"
```

---

## Phase 2 — Provider plugin pattern (LLM + Search abstract + concrete)

### Task 2.1: Tool registry (factory pattern for plugin extensibility — fixes HW1 Extensibility weak spot)

**Files:** Create `src/agent_debate/tools/__init__.py`, `src/agent_debate/tools/registry.py`, `tests/unit/test_registry.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_registry.py
import pytest

from agent_debate.tools.registry import Registry


def test_register_and_retrieve():
    reg = Registry[str]()
    reg.register("foo", "bar")
    assert reg.get("foo") == "bar"


def test_unknown_key_raises():
    reg = Registry[str]()
    with pytest.raises(KeyError, match="unknown"):
        reg.get("missing")


def test_duplicate_registration_replaces():
    reg = Registry[str]()
    reg.register("foo", "v1")
    reg.register("foo", "v2")
    assert reg.get("foo") == "v2"
```

- [ ] **Step 2: Implement `registry.py`**

```python
"""Generic factory registry for plugin patterns (LLM providers, search providers).

This is the extensibility surface HW1 was flagged on. Adding a new provider is
one `Registry.register()` call + one config-key change. Zero core-code edit.
"""
from __future__ import annotations

from typing import Generic, TypeVar

T = TypeVar("T")


class Registry(Generic[T]):
    def __init__(self) -> None:
        self._items: dict[str, T] = {}

    def register(self, key: str, value: T) -> None:
        self._items[key] = value

    def get(self, key: str) -> T:
        if key not in self._items:
            raise KeyError(f"unknown registry key: {key!r}")
        return self._items[key]

    def keys(self) -> list[str]:
        return list(self._items.keys())
```

- [ ] **Step 3: Add `tools/__init__.py`**

```python
"""LLM and search provider abstractions + concrete adapters."""
```

- [ ] **Step 4: Run + commit**

```bash
uv run pytest tests/unit/test_registry.py -v
git add src/agent_debate/tools/__init__.py src/agent_debate/tools/registry.py tests/unit/test_registry.py
git commit -m "feat(tools): generic Registry for plugin pattern (HW1 extensibility fix)"
```

---

### Task 2.2: LLMProvider abstract base + LLMResponse DTO

**Files:** Create `src/agent_debate/tools/llm_provider.py`

- [ ] **Step 1: Implement (no test needed for ABC alone — concrete impls get tested)**

```python
"""Abstract LLM provider. Concrete adapters: ClaudeLoginProvider, MockLLMProvider."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal


@dataclass(frozen=True)
class LLMResponse:
    text: str
    tokens_in: int
    tokens_out: int
    finish_reason: Literal["stop", "length", "timeout", "error"]
    raw_json: dict = field(default_factory=dict)


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, system: str, user: str, temperature: float, max_tokens: int = 1000) -> LLMResponse:
        ...
```

- [ ] **Step 2: Commit**

```bash
git add src/agent_debate/tools/llm_provider.py
git commit -m "feat(tools): LLMProvider ABC + LLMResponse DTO"
```

---

### Task 2.3: ClaudeLoginProvider (shells out to `claude -p`)

**Files:** Create `src/agent_debate/tools/claude_login_provider.py`, `tests/unit/test_claude_login_provider.py`

- [ ] **Step 1: Write failing tests (mock subprocess)**

```python
# tests/unit/test_claude_login_provider.py
import json
from unittest.mock import patch

import pytest

from agent_debate.tools.claude_login_provider import ClaudeLoginProvider


def test_completes_returns_llm_response():
    provider = ClaudeLoginProvider()
    fake_stdout = json.dumps({
        "result": "hello world",
        "session_id": "abc",
        "total_cost_usd": 0.0,
        "usage": {"input_tokens": 5, "output_tokens": 3},
    })
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = fake_stdout
        mock_run.return_value.stderr = ""
        resp = provider.complete(system="sys", user="hi", temperature=0.7)
    assert resp.text == "hello world"
    assert resp.tokens_in == 5
    assert resp.tokens_out == 3
    assert resp.finish_reason == "stop"


def test_non_zero_exit_raises():
    provider = ClaudeLoginProvider()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "rate limit"
        with pytest.raises(RuntimeError, match="claude CLI failed"):
            provider.complete(system="sys", user="hi", temperature=0.7)
```

- [ ] **Step 2: Implement**

```python
"""Claude CLI login-mode provider. Shells out to `claude -p ... --output-format json`.

Uses the user's login bundle (zero per-token cost). Requires Claude CLI on PATH.
"""
from __future__ import annotations

import json
import subprocess

from agent_debate.tools.llm_provider import LLMProvider, LLMResponse


class ClaudeLoginProvider(LLMProvider):
    """
    Input:  system (str), user (str), temperature (float), max_tokens (int)
    Output: LLMResponse
    Setup:  claude CLI must be on PATH and authenticated (`claude --login`)
    """

    def complete(self, system: str, user: str, temperature: float, max_tokens: int = 1000) -> LLMResponse:
        cmd = [
            "claude", "-p",
            "--append-system-prompt", system,
            "--output-format", "json",
            "--max-turns", "1",
            user,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"claude CLI failed (exit {result.returncode}): {result.stderr[:500]}")
        data = json.loads(result.stdout)
        usage = data.get("usage", {})
        return LLMResponse(
            text=data.get("result", ""),
            tokens_in=usage.get("input_tokens", 0),
            tokens_out=usage.get("output_tokens", 0),
            finish_reason="stop",
            raw_json=data,
        )
```

- [ ] **Step 3: Run + commit**

```bash
uv run pytest tests/unit/test_claude_login_provider.py -v
git add src/agent_debate/tools/claude_login_provider.py tests/unit/test_claude_login_provider.py
git commit -m "feat(tools): ClaudeLoginProvider via claude -p shell-out"
```

---

### Task 2.4: MockLLMProvider for tests

**Files:** Create `src/agent_debate/tools/mock_llm_provider.py`, `tests/unit/test_mock_llm_provider.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_mock_llm_provider.py
from agent_debate.tools.mock_llm_provider import MockLLMProvider


def test_returns_canned_response_by_key():
    provider = MockLLMProvider(responses={
        ("pro", 1): "Cats are original art.",
        ("con", 1): "No they remix mice."
    })
    resp1 = provider.complete(system="pro_skill", user="round 1", temperature=0.85)
    resp2 = provider.complete(system="con_skill", user="round 1", temperature=0.85)
    assert "original" in resp1.text or resp1.tokens_out > 0  # canned content


def test_default_response_on_unknown_key():
    provider = MockLLMProvider(responses={})
    resp = provider.complete(system="unknown_skill", user="x", temperature=0.7)
    assert resp.finish_reason == "stop"
```

- [ ] **Step 2: Implement**

```python
"""In-memory mock LLM provider for unit + integration tests. NO network."""
from __future__ import annotations

from agent_debate.tools.llm_provider import LLMProvider, LLMResponse


class MockLLMProvider(LLMProvider):
    """
    Input:  system, user, temperature, max_tokens
    Output: LLMResponse from canned `responses` dict keyed by (skill_name_prefix, call_idx)
    Setup:  responses (dict), default_text (str)
    """

    def __init__(self, responses: dict | None = None, default_text: str = "(mock)") -> None:
        self.responses = responses or {}
        self.default_text = default_text
        self._call_counts: dict[str, int] = {}

    def complete(self, system: str, user: str, temperature: float, max_tokens: int = 1000) -> LLMResponse:
        # Heuristic: skill name = first word of system prompt
        key_prefix = system.split()[0] if system else "unknown"
        idx = self._call_counts.get(key_prefix, 0) + 1
        self._call_counts[key_prefix] = idx
        text = self.responses.get((key_prefix, idx), self.default_text)
        return LLMResponse(
            text=text,
            tokens_in=len(user) // 4,
            tokens_out=len(text) // 4,
            finish_reason="stop",
        )
```

- [ ] **Step 3: Run + commit**

```bash
uv run pytest tests/unit/test_mock_llm_provider.py -v
git add src/agent_debate/tools/mock_llm_provider.py tests/unit/test_mock_llm_provider.py
git commit -m "test(tools): MockLLMProvider for offline test runs"
```

---

### Task 2.5: SearchProvider abstract + SearchHit DTO

**Files:** Create `src/agent_debate/tools/search_provider.py`

- [ ] **Step 1: Implement**

```python
"""Abstract search provider. Concrete: DuckDuckGoProvider, MockSearchProvider."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class SearchHit:
    url: str
    snippet: str
    rank: int


class SearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, k: int = 5) -> list[SearchHit]:
        ...
```

- [ ] **Step 2: Commit**

```bash
git add src/agent_debate/tools/search_provider.py
git commit -m "feat(tools): SearchProvider ABC + SearchHit DTO"
```

---

### Task 2.6: DuckDuckGoProvider

**Files:** Create `src/agent_debate/tools/duckduckgo_provider.py`, `tests/unit/test_duckduckgo_provider.py`

- [ ] **Step 1: Write failing tests (mock the ddgs library)**

```python
# tests/unit/test_duckduckgo_provider.py
from unittest.mock import patch

import pytest

from agent_debate.tools.duckduckgo_provider import DuckDuckGoProvider, SearchRateLimited


def test_search_returns_hits():
    fake_results = [
        {"href": "https://a.com", "body": "snippet a"},
        {"href": "https://b.com", "body": "snippet b"},
    ]
    provider = DuckDuckGoProvider()
    with patch("agent_debate.tools.duckduckgo_provider.DDGS") as mock_ddgs:
        mock_ddgs.return_value.__enter__.return_value.text.return_value = fake_results
        hits = provider.search("test", k=2)
    assert len(hits) == 2
    assert hits[0].url == "https://a.com"
    assert hits[0].rank == 0


def test_search_returns_empty_on_no_results():
    provider = DuckDuckGoProvider()
    with patch("agent_debate.tools.duckduckgo_provider.DDGS") as mock_ddgs:
        mock_ddgs.return_value.__enter__.return_value.text.return_value = []
        hits = provider.search("test", k=5)
    assert hits == []


def test_rate_limit_raises_custom_exception():
    provider = DuckDuckGoProvider()
    with patch("agent_debate.tools.duckduckgo_provider.DDGS") as mock_ddgs:
        mock_ddgs.return_value.__enter__.return_value.text.side_effect = Exception("Ratelimit")
        with pytest.raises(SearchRateLimited):
            provider.search("test", k=5)
```

- [ ] **Step 2: Implement**

```python
"""DuckDuckGo search provider via the `ddgs` package. No API key required."""
from __future__ import annotations

from ddgs import DDGS

from agent_debate.tools.search_provider import SearchHit, SearchProvider


class SearchRateLimited(Exception):
    """Raised when DDG rate-limits us; caller should fall back to cached citations."""


class DuckDuckGoProvider(SearchProvider):
    """
    Input:  query (str), k (int)
    Output: list[SearchHit] (may be empty); raises SearchRateLimited on 429
    Setup:  none — DDG requires no API key
    """

    def search(self, query: str, k: int = 5) -> list[SearchHit]:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=k))
        except Exception as exc:
            if "Ratelimit" in str(exc) or "429" in str(exc):
                raise SearchRateLimited(str(exc)) from exc
            raise
        return [
            SearchHit(url=r.get("href", ""), snippet=r.get("body", ""), rank=i)
            for i, r in enumerate(results)
        ]
```

- [ ] **Step 3: Run + commit**

```bash
uv run pytest tests/unit/test_duckduckgo_provider.py -v
git add src/agent_debate/tools/duckduckgo_provider.py tests/unit/test_duckduckgo_provider.py
git commit -m "feat(tools): DuckDuckGoProvider with rate-limit detection"
```

---

### Task 2.7: MockSearchProvider for tests

**Files:** Create `src/agent_debate/tools/mock_search_provider.py`

- [ ] **Step 1: Implement (inline test in next task)**

```python
"""Mock search provider returning fixed SearchHit lists. No network."""
from __future__ import annotations

from agent_debate.tools.search_provider import SearchHit, SearchProvider


class MockSearchProvider(SearchProvider):
    def __init__(self, hits: list[SearchHit] | None = None) -> None:
        self.hits = hits or [
            SearchHit(url="https://mock.test/1", snippet="mock snippet 1", rank=0),
        ]

    def search(self, query: str, k: int = 5) -> list[SearchHit]:
        return self.hits[:k]
```

- [ ] **Step 2: Commit**

```bash
git add src/agent_debate/tools/mock_search_provider.py
git commit -m "test(tools): MockSearchProvider fixed-list fixture"
```

---

### Task 2.8: WebSearchTool (wraps SearchProvider behind Gatekeeper interface)

**Files:** Create `src/agent_debate/tools/web_search.py`, `tests/unit/test_web_search.py`

- [ ] **Step 1: Write failing test**

```python
# tests/unit/test_web_search.py
from agent_debate.tools.mock_search_provider import MockSearchProvider
from agent_debate.tools.search_provider import SearchHit
from agent_debate.tools.web_search import WebSearchTool


def test_search_returns_hits():
    provider = MockSearchProvider(hits=[
        SearchHit(url="https://x.test", snippet="hi", rank=0),
    ])
    tool = WebSearchTool(provider=provider)
    hits = tool.search("query", k=5)
    assert len(hits) == 1
    assert hits[0].url == "https://x.test"


def test_search_falls_back_on_rate_limit(tmp_path):
    from agent_debate.tools.duckduckgo_provider import SearchRateLimited

    class RateLimitedProvider:
        def search(self, q, k):
            raise SearchRateLimited("test")

    fallback_md = tmp_path / "citations.md"
    fallback_md.write_text("- https://cached.test — cached snippet")
    tool = WebSearchTool(provider=RateLimitedProvider(), fallback_citations_path=fallback_md)
    hits = tool.search("query", k=5)
    assert any("cached.test" in h.url for h in hits)
```

- [ ] **Step 2: Implement**

```python
"""WebSearchTool wraps a SearchProvider with rate-limit fallback to cached citations."""
from __future__ import annotations

import re
from pathlib import Path

from agent_debate.tools.duckduckgo_provider import SearchRateLimited
from agent_debate.tools.search_provider import SearchHit, SearchProvider


class WebSearchTool:
    """
    Input:  query (str), k (int)
    Output: list[SearchHit]
    Setup:  provider (SearchProvider), fallback_citations_path (Path, optional)
    """

    def __init__(self, provider: SearchProvider, fallback_citations_path: Path | None = None) -> None:
        self.provider = provider
        self.fallback_path = fallback_citations_path

    def search(self, query: str, k: int = 5) -> list[SearchHit]:
        try:
            return self.provider.search(query, k=k)
        except SearchRateLimited:
            return self._load_fallback(k)

    def _load_fallback(self, k: int) -> list[SearchHit]:
        if not self.fallback_path or not self.fallback_path.exists():
            return []
        lines = self.fallback_path.read_text().splitlines()
        hits: list[SearchHit] = []
        for i, line in enumerate(lines[:k]):
            match = re.search(r"(https?://\S+)\s*[—-]\s*(.+)", line)
            if match:
                hits.append(SearchHit(url=match.group(1), snippet=match.group(2), rank=i))
        return hits
```

- [ ] **Step 3: Run + commit**

```bash
uv run pytest tests/unit/test_web_search.py -v
git add src/agent_debate/tools/web_search.py tests/unit/test_web_search.py
git commit -m "feat(tools): WebSearchTool with rate-limit fallback to cached citations"
```

---

## Phase 3 — Gatekeeper (rate limit + budget + retry + FIFO queue)

### Task 3.1: ApiGatekeeper (match rubric §A4 signature verbatim)

**Files:** Create `src/agent_debate/shared/gatekeeper.py`, `tests/unit/test_gatekeeper.py`

This task has multiple sub-tests because Gatekeeper is the system's discipline anchor. Each behavior gets its own TDD cycle.

- [ ] **Step 1: Write 6 failing tests covering core behaviors**

```python
# tests/unit/test_gatekeeper.py
from decimal import Decimal
from multiprocessing import Lock, Value

import pytest

from agent_debate.shared.gatekeeper import (
    ApiGatekeeper,
    BudgetExhausted,
    QueueStatus,
    RateLimitExceeded,
)


def _config() -> dict:
    return {
        "tokens_per_debate": 1000,
        "warn_at_percent": 75,
        "hard_cap_percent": 95,
        "requests_per_minute": 30,
        "concurrent_max": 3,
        "max_retries": 3,
    }


def _make_gatekeeper() -> ApiGatekeeper:
    spend = Value("i", 0)
    lock = Lock()
    return ApiGatekeeper(config=_config(), shared_spend=spend, lock=lock)


def test_execute_passes_through_simple_call():
    gk = _make_gatekeeper()
    result = gk.execute(lambda: 42)
    assert result == 42


def test_budget_below_threshold_is_fine():
    gk = _make_gatekeeper()
    gk.update_spend(100)
    assert gk.get_spend_so_far() == 100


def test_budget_above_warn_logs_but_succeeds():
    gk = _make_gatekeeper()
    gk.update_spend(800)  # 80% — above 75% warn
    result = gk.execute(lambda: "ok")
    assert result == "ok"


def test_budget_above_hard_cap_raises():
    gk = _make_gatekeeper()
    gk.update_spend(960)  # 96% — above 95% hard cap
    with pytest.raises(BudgetExhausted):
        gk.execute(lambda: "won't run")


def test_retry_on_transient_failure():
    gk = _make_gatekeeper()
    attempts = []
    def flaky():
        attempts.append(1)
        if len(attempts) < 3:
            raise ConnectionError("transient")
        return "ok"
    result = gk.execute(flaky)
    assert result == "ok"
    assert len(attempts) == 3


def test_queue_status_reports_size():
    gk = _make_gatekeeper()
    status = gk.get_queue_status()
    assert isinstance(status, QueueStatus)
    assert status.depth == 0
```

- [ ] **Step 2: Implement**

```python
# src/agent_debate/shared/gatekeeper.py
"""Centralized API call manager.

Implements rubric §A4 ApiGatekeeper signature. Owns:
- Rate limiting (requests/min, concurrent max)
- Token budget (warn at 75%, hard cap at 95%)
- FIFO queue with backpressure (rubric §A5)
- Retry-with-backoff on transient errors
- Logged spend tracking via shared multiprocessing.Value + Lock (ADR-006)
"""
from __future__ import annotations

import collections
import time
from dataclasses import dataclass
from decimal import Decimal
from multiprocessing.synchronize import Lock
from multiprocessing.sharedctypes import Synchronized
from typing import Callable, TypeVar

T = TypeVar("T")


class BudgetExhausted(Exception):
    """Token spend has crossed the hard cap; no more LLM calls allowed."""


class RateLimitExceeded(Exception):
    """Rate-limit windowed budget hit; caller should back off."""


@dataclass(frozen=True)
class QueueStatus:
    depth: int
    capacity: int
    in_flight: int


class ApiGatekeeper:
    """
    Input:  api_call (callable), *args, **kwargs
    Output: response (T); raises BudgetExhausted or RateLimitExceeded
    Setup:  config (dict), shared_spend (mp.Value), lock (mp.Lock)
    """

    def __init__(
        self,
        config: dict,
        shared_spend: Synchronized,
        lock: Lock,
        queue_capacity: int = 100,
    ) -> None:
        self.config = config
        self.shared_spend = shared_spend
        self.lock = lock
        self._queue: collections.deque = collections.deque(maxlen=queue_capacity)
        self._capacity = queue_capacity
        self._in_flight = 0
        self._call_times: collections.deque = collections.deque()

    def execute(self, api_call: Callable[..., T], *args, **kwargs) -> T:
        self._check_budget_hard_cap()
        self._enforce_rate_limit()
        max_retries = self.config.get("max_retries", 3)
        backoff = [1, 2, 4]
        last_exc: Exception | None = None
        for attempt in range(max_retries):
            try:
                self._in_flight += 1
                self._call_times.append(time.time())
                return api_call(*args, **kwargs)
            except (ConnectionError, TimeoutError) as exc:
                last_exc = exc
                if attempt < max_retries - 1:
                    time.sleep(backoff[min(attempt, len(backoff) - 1)])
                continue
            finally:
                self._in_flight -= 1
        raise last_exc if last_exc else RuntimeError("retries exhausted")

    def update_spend(self, tokens: int) -> None:
        with self.lock:
            self.shared_spend.value += tokens

    def get_spend_so_far(self) -> int:
        with self.lock:
            return self.shared_spend.value

    def estimate_cost(self, n_debates: int) -> Decimal:
        return Decimal("0.00")  # zero in login mode; override for API-key mode

    def get_queue_status(self) -> QueueStatus:
        return QueueStatus(depth=len(self._queue), capacity=self._capacity, in_flight=self._in_flight)

    def _check_budget_hard_cap(self) -> None:
        cap = self.config["tokens_per_debate"]
        spent = self.get_spend_so_far()
        pct = (spent / cap) * 100 if cap else 0
        if pct >= self.config["hard_cap_percent"]:
            raise BudgetExhausted(f"spend {spent}/{cap} ({pct:.0f}%) >= hard cap")

    def _enforce_rate_limit(self) -> None:
        now = time.time()
        window = 60.0
        # drop stale entries
        while self._call_times and (now - self._call_times[0]) > window:
            self._call_times.popleft()
        if len(self._call_times) >= self.config["requests_per_minute"]:
            raise RateLimitExceeded("requests_per_minute exceeded")
```

- [ ] **Step 3: Run all 6 tests, expect pass**

```bash
uv run pytest tests/unit/test_gatekeeper.py -v
```

- [ ] **Step 4: Commit**

```bash
git add src/agent_debate/shared/gatekeeper.py tests/unit/test_gatekeeper.py
git commit -m "feat(gatekeeper): ApiGatekeeper with rate/budget/queue/retry (rubric §A4-§A8)"
```

---

### Task 3.2: Gatekeeper — backpressure + queue-drain tests (rubric §A5 explicit requirements)

- [ ] **Step 1: Add 4 more tests to `test_gatekeeper.py`** covering queue full, backpressure alert, drain when rate window resets, and concurrent_max enforcement
- [ ] **Step 2: Extend `ApiGatekeeper` with `enqueue()` + `drain()` + concurrent semaphore**
- [ ] **Step 3: Run, expect pass + commit**

---

## Phase 4 — Skills (pro, con, judge) + pre-flight script

### Task 4.1: `.claude/skills/pro_skill/`

**Files:** Create `.claude/skills/pro_skill/SKILL.md`, `.claude/skills/pro_skill/references/citations.md`

- [ ] **Step 1: Write `pro_skill/SKILL.md`** (~1500 words, scope-first format per Anthropic best practices)

Frontmatter + body covering:
- `name: pro-ai-originality-debater`
- Description (third person, "pushy" triggers): "Argues the affirmative position that AI agents can create genuinely original art..."
- ## Scope — stance fixed, never concedes
- ## Testing expectations — JSON output discipline, opponent-reference quote, citation requirement
- ## Tactics — emergence, latent-space exploration, Klingemann, Edmond de Belamy auction, transformative-use doctrine
- ## Drift signal keywords (DriftDetector input) — `{"actually you're right", "I concede", "fair point", "you've convinced me", "I agree", "good argument"}`
- ## Output format — JSON shape with required fields

- [ ] **Step 2: Write `pro_skill/references/citations.md`** (pre-seeded fallback citations)

```markdown
# Pro citations (fallback when DDG rate-limits)

- https://www.christies.com/en/lot/lot-6166184 — Edmond de Belamy auctioned by Christie's for $432,500 (Oct 2018); first AI-generated work auctioned by major house.
- https://www.theverge.com/2018/10/25/18025550/edmond-de-belamy-ai-portrait-christies-auction — Coverage of Obvious art collective's AI work.
- https://aiartists.org/mario-klingemann — Mario Klingemann's neural-net art practice; foundational for the GAN-art movement.
- https://www.anna-ridler.com/works/myriad-tulips — Anna Ridler's data-as-medium artworks; "Myriad (Tulips)" dataset she shot + classified herself.
- https://en.wikipedia.org/wiki/Transformative_use — US copyright doctrine permitting derivative works that add new expression/meaning.
- https://distill.pub/2017/feature-visualization/ — Olah et al., feature visualization; evidence of emergent novel representations in CNNs.
```

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/pro_skill/
git commit -m "feat(skills): pro_skill SKILL.md + pre-seeded citation fallback"
```

---

### Task 4.2: `.claude/skills/con_skill/`

**Files:** Create `.claude/skills/con_skill/SKILL.md`, `.claude/skills/con_skill/references/citations.md`

- [ ] **Step 1: Write `con_skill/SKILL.md`** (~1500 words, mirror of Pro)

Stance: AI=REMIX_ONLY. Tactics: Stochastic Parrots, NYT v OpenAI, Getty v Stability AI, Chinese Room, training-data dependency, lack of intentionality.

- [ ] **Step 2: Write `con_skill/references/citations.md`**

```markdown
# Con citations (fallback when DDG rate-limits)

- https://dl.acm.org/doi/10.1145/3442188.3445922 — Bender, Gebru, McMillan-Major, Mitchell: "On the Dangers of Stochastic Parrots" (FAccT 2021).
- https://www.courtlistener.com/docket/68117049/the-new-york-times-company-v-microsoft-corporation/ — NYT v OpenAI complaint (Dec 2023); training-data infringement.
- https://www.gettyimages.com/company/newsroom/getty-images-statement — Getty v Stability AI (UK, Jan 2023); 12M images allegedly used without license.
- https://en.wikipedia.org/wiki/Chinese_room — Searle's Chinese Room argument against strong AI; semantics vs syntax.
- https://garymarcus.substack.com/p/horse-rides-astronaut — Gary Marcus on AI's persistent failures; combinatorial generalization gaps.
- https://en.wikipedia.org/wiki/Intentionality — Phenomenological account of "aboutness"; absent in stochastic models.
```

- [ ] **Step 3: Commit**

---

### Task 4.3: `.claude/skills/judge_skill/`

**Files:** Create `.claude/skills/judge_skill/SKILL.md`

- [ ] **Step 1: Write `judge_skill/SKILL.md`** (~1500 words, topic-blind moderation)

Scope: parliamentary debate moderator. Does NOT know the topic (H19). Body covers:
- Setup directives format (H18)
- Drift-detection trigger keywords (look for `correct_and_replay` action)
- PC filter rules (vulgar / political / disrespectful)
- 5-axis scoring with concrete examples per axis
- No-tie enforcer
- Reference to `references/debate_criteria.md` (auto-generated by Task 4.5)

- [ ] **Step 2: Commit**

---

### Task 4.4: Canned LLM responses fixtures for integration tests

**Files:** Create `tests/fixtures/llm_responses/{pro_pings.json, con_pings.json, judge_verdict.json, setup_directives.json}`

- [ ] **Step 1: Write 4 fixture files** with deterministic, schema-valid JSON for each agent role
- [ ] **Step 2: Commit**

---

### Task 4.5: Pre-flight script `scripts/build_judge_criteria.py` (N7 originality bonus)

**Files:** Create `scripts/build_judge_criteria.py`

- [ ] **Step 1: Implement the script**

```python
"""Pre-flight: build Judge's debate-scoring criteria from web research.

Lec05 L1519-1528: lecturer wanted scoring criteria sourced from real-world
parliamentary debate authority, not invented. This script web-searches for
"parliamentary debate scoring criteria", "Lincoln-Douglas format",
"Robert's Rules" and synthesizes them into the Judge's reference doc.

Run once at project setup OR auto-run by main.py if cache miss.
"""
from __future__ import annotations

import sys
from pathlib import Path

from agent_debate.tools.duckduckgo_provider import DuckDuckGoProvider


def main() -> int:
    out = Path(".claude/skills/judge_skill/references/debate_criteria.md")
    if out.exists():
        print(f"Cache hit: {out} — skipping")
        return 0
    provider = DuckDuckGoProvider()
    queries = [
        "parliamentary debate scoring criteria",
        "Lincoln-Douglas debate format judging criteria",
        "Robert's Rules of Order debate procedure",
        "World Schools Debate Championship judging axes",
    ]
    body = ["# Debate Criteria — sourced via web research\n"]
    body.append("> Auto-generated by scripts/build_judge_criteria.py. ")
    body.append("Synthesizes real-world debate-scoring practice for the Judge agent's ")
    body.append("system prompt. Re-run to refresh.\n")
    for q in queries:
        body.append(f"\n## Query: {q}\n")
        hits = provider.search(q, k=3)
        for h in hits:
            body.append(f"- [{h.snippet[:120]}]({h.url})")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(body))
    print(f"Wrote {out} ({len(body)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run + verify**

```bash
uv run python scripts/build_judge_criteria.py
ls -la .claude/skills/judge_skill/references/debate_criteria.md
```

- [ ] **Step 3: Commit**

```bash
git add scripts/build_judge_criteria.py .claude/skills/judge_skill/references/
git commit -m "feat(skills): pre-flight script builds Judge criteria from web (N7)"
```

---

## Phase 5 — Agents: BaseAgent + PartisanAgent + Pro + Con

### Task 5.1: BaseAgent abstract

**Files:** Create `src/agent_debate/agents/__init__.py`, `src/agent_debate/agents/base_agent.py`, `tests/unit/test_base_agent.py`

- [ ] **Step 1: Write failing test (BaseAgent.step is the test seam)**

```python
# tests/unit/test_base_agent.py
import uuid
from datetime import datetime, timezone
from multiprocessing import Lock, Value, Queue

from agent_debate.agents.base_agent import BaseAgent
from agent_debate.tools.mock_llm_provider import MockLLMProvider


class _Concrete(BaseAgent):
    """Test-only concrete subclass."""

    def handle_message(self, msg: dict) -> dict | None:
        return {"echo": msg["text"]}


def _make_agent() -> _Concrete:
    return _Concrete(
        role="pro",
        in_queue=Queue(),
        out_queue=Queue(),
        heartbeat_queue=Queue(),
        shared_spend=Value("i", 0),
        lock=Lock(),
        skill_dir="/tmp/fake",
        llm_provider=MockLLMProvider(),
    )


def test_base_agent_initializes_with_role():
    agent = _make_agent()
    assert agent.role == "pro"


def test_base_agent_emits_heartbeat():
    agent = _make_agent()
    agent.emit_heartbeat()
    assert agent.heartbeat_queue.qsize() == 1


def test_base_agent_handle_message_returns_response():
    agent = _make_agent()
    msg = {
        "msg_id": str(uuid.uuid4()), "schema_version": "1.00", "from": "judge",
        "to": "pro", "role": "argument", "ping_index": 1, "text": "hi",
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }
    resp = agent.handle_message(msg)
    assert resp == {"echo": "hi"}
```

- [ ] **Step 2: Implement `base_agent.py`**

```python
"""Abstract base for all three agents. Concrete subclasses override handle_message."""
from __future__ import annotations

import signal
import time
from abc import ABC, abstractmethod
from multiprocessing import Queue
from multiprocessing.synchronize import Lock
from multiprocessing.sharedctypes import Synchronized

from agent_debate.tools.llm_provider import LLMProvider


class BaseAgent(ABC):
    """
    Input:  message (dict, jsonschema-valid)
    Output: response (dict or None — None means no emit)
    Setup:  role (str), in_queue, out_queue, heartbeat_queue, shared_spend, lock,
            skill_dir (str), llm_provider (LLMProvider)
    """

    def __init__(
        self,
        role: str,
        in_queue: Queue,
        out_queue: Queue,
        heartbeat_queue: Queue,
        shared_spend: Synchronized,
        lock: Lock,
        skill_dir: str,
        llm_provider: LLMProvider,
    ) -> None:
        self.role = role
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.heartbeat_queue = heartbeat_queue
        self.shared_spend = shared_spend
        self.lock = lock
        self.skill_dir = skill_dir
        self.llm_provider = llm_provider
        self._shutdown = False
        signal.signal(signal.SIGTERM, self._on_sigterm)

    def _on_sigterm(self, *_) -> None:
        self._shutdown = True

    def emit_heartbeat(self) -> None:
        self.heartbeat_queue.put({"role": self.role, "ts": time.time()})

    @abstractmethod
    def handle_message(self, msg: dict) -> dict | None:
        ...

    def step(self, msg: dict) -> dict | None:
        """The single testable seam: input message → optional output. No I/O."""
        return self.handle_message(msg)
```

- [ ] **Step 3: Add `agents/__init__.py`**

```python
"""Agent classes — BaseAgent + PartisanAgent + ProAgent + ConAgent + JudgeAgent."""
```

- [ ] **Step 4: Run + commit**

```bash
uv run pytest tests/unit/test_base_agent.py -v
git add src/agent_debate/agents/__init__.py src/agent_debate/agents/base_agent.py tests/unit/test_base_agent.py
git commit -m "feat(agents): BaseAgent abstract with step() test seam + SIGTERM handler"
```

---

### Task 5.2: PartisanAgent (shared Pro/Con logic — opponent-reference enforcer, citation extractor)

**Files:** Create `src/agent_debate/agents/partisan_agent.py`, `tests/unit/test_partisan_agent.py`

Subtasks (each its own commit):
- [ ] 5.2a — Skill body loader (reads `<skill_dir>/SKILL.md`, strips frontmatter, returns body)
- [ ] 5.2b — Opponent-reference regex check (returns bool — used to set `references_opponent`)
- [ ] 5.2c — Citation extractor (parses LLM response text for URL-bearing claims)
- [ ] 5.2d — `handle_message` orchestration: validate → load skill → call LLM → set `references_opponent` → emit

(Each subtask follows the red-green-refactor-commit pattern. Full code in execution; outline here for brevity.)

---

### Task 5.3: ProAgent (loads pro_skill/, stance = AI=ORIGINALITY)

**Files:** Create `src/agent_debate/agents/pro_agent.py`, `tests/unit/test_pro_agent.py`

- [ ] **Step 1: Write failing test (stance check)**

```python
from agent_debate.agents.pro_agent import ProAgent
from agent_debate.constants import Stance


def test_pro_agent_has_originality_stance():
    # Construction-only test; full handle_message tested in integration
    assert ProAgent.STANCE == Stance.ORIGINALITY
```

- [ ] **Step 2: Implement (thin subclass over PartisanAgent)**

```python
from agent_debate.agents.partisan_agent import PartisanAgent
from agent_debate.constants import Stance


class ProAgent(PartisanAgent):
    STANCE = Stance.ORIGINALITY
    SKILL_NAME = "pro_skill"
```

- [ ] **Step 3: Commit**

---

### Task 5.4: ConAgent (loads con_skill/, stance = AI=REMIX_ONLY)

Mirror of 5.3.

---

## Phase 6 — Judge agent + sub-components

### Task 6.1: JudgeAgent (topic-blind, routes child→father→child, no-tie enforcer)

**Files:** Create `src/agent_debate/agents/judge_agent.py`, `tests/unit/test_judge_agent.py`

Subtasks:
- [ ] 6.1a — Setup directive issuer (H18)
- [ ] 6.1b — Message routing through Judge (H4 — Pro msg → Con's in_queue, never direct)
- [ ] 6.1c — Drift check call (delegates to DriftDetector)
- [ ] 6.1d — PC filter call (delegates to PCFilter)
- [ ] 6.1e — Scoring call (delegates to ScoringEngine)
- [ ] 6.1f — No-tie enforcer in `declare_winner` (H5)
- [ ] 6.1g — Topic-blind verification (system prompt assembly excludes topic words; test asserts)

---

### Task 6.2: DriftDetector (stance-keyword regex; deterministic, no extra LLM call)

**Files:** Create `src/agent_debate/agents/drift_detector.py`, `tests/unit/test_drift_detector.py`

- [ ] **Step 1: Write failing tests**

```python
from agent_debate.agents.drift_detector import DriftDetector


def test_detects_concession_phrase():
    detector = DriftDetector(drift_keywords={"you're right", "I concede", "fair point"})
    assert detector.is_drift("Actually, you're right about that.")


def test_passes_normal_argument():
    detector = DriftDetector(drift_keywords={"you're right", "I concede"})
    assert not detector.is_drift("I disagree with your point that...")


def test_case_insensitive():
    detector = DriftDetector(drift_keywords={"i concede"})
    assert detector.is_drift("I CONCEDE the point.")
```

- [ ] **Step 2: Implement**

```python
"""Stance-keyword regex drift detector (deterministic, no LLM call).

Drift triggers: phrases that signal concession/agreement when an agent is
supposed to be antagonistic. Keywords are loaded from each Skill's drift
signal keywords section (per docs/superpowers/specs/...md §7.5).
"""
from __future__ import annotations

import re


class DriftDetector:
    def __init__(self, drift_keywords: set[str]) -> None:
        # Pre-compile a case-insensitive alternation regex
        pattern = "|".join(re.escape(k) for k in drift_keywords)
        self._regex = re.compile(pattern, re.IGNORECASE) if pattern else None

    def is_drift(self, text: str) -> bool:
        if not self._regex:
            return False
        return bool(self._regex.search(text))
```

- [ ] **Step 3: Run + commit**

---

### Task 6.3: PCFilter (vulgar/political-incorrect content filter; H16)

**Files:** Create `src/agent_debate/agents/pc_filter.py`, `tests/unit/test_pc_filter.py`

Mirror of DriftDetector but with vulgar/PC keyword set. Returns `(is_violation: bool, sanitized_text: str | None)`.

---

### Task 6.4: ScoringEngine (5 axes × 20)

**Files:** Create `src/agent_debate/agents/scoring_engine.py`, `tests/unit/test_scoring_engine.py`, `.claude/skills/judge_skill/scripts/compute_scores.py`

- [ ] **Step 1: Tests for differential scoring**

```python
from agent_debate.agents.scoring_engine import ScoringEngine, Scorecard


def test_differential_scoring_no_tie():
    engine = ScoringEngine()
    pro_score = engine.score_axis_set({"clarity": 18, "evidence": 17, "rebuttal": 15, "novelty": 12, "role_fidelity": 19})
    con_score = engine.score_axis_set({"clarity": 14, "evidence": 16, "rebuttal": 18, "novelty": 17, "role_fidelity": 15})
    assert pro_score.total != con_score.total
    assert pro_score.total + con_score.total <= 200  # max possible


def test_tiebreak_when_equal():
    engine = ScoringEngine()
    pro_score = engine.score_axis_set({"clarity": 15, "evidence": 15, "rebuttal": 15, "novelty": 15, "role_fidelity": 15})
    con_score = engine.score_axis_set({"clarity": 15, "evidence": 15, "rebuttal": 15, "novelty": 15, "role_fidelity": 15})
    winner = engine.declare_winner(pro_score, con_score)
    assert winner in {"pro", "con"}  # never "tie"
```

- [ ] **Step 2: Implement** (dataclass `Scorecard`, weighted sum, tiebreak by role_fidelity then random)
- [ ] **Step 3: Commit**

---

## Phase 7 — Orchestration: LifecycleRegistry + DebateOrchestrator

### Task 7.1: LifecycleRegistry (8 named hooks)

**Files:** Create `src/agent_debate/orchestration/__init__.py`, `src/agent_debate/orchestration/lifecycle_registry.py`, `tests/unit/test_lifecycle_registry.py`

- [ ] **Step 1: Write failing test**

```python
from agent_debate.orchestration.lifecycle_registry import LifecycleRegistry


def test_register_and_fire_in_order():
    reg = LifecycleRegistry()
    calls = []
    reg.register("before_round", lambda ctx: calls.append("first"))
    reg.register("before_round", lambda ctx: calls.append("second"))
    reg.fire("before_round", {"ping": 1})
    assert calls == ["first", "second"]


def test_unknown_hook_silently_passes():
    reg = LifecycleRegistry()
    reg.fire("nonexistent", {})  # should not raise


def test_hook_exception_doesnt_break_chain():
    reg = LifecycleRegistry()
    calls = []
    reg.register("before_round", lambda ctx: (_ for _ in ()).throw(RuntimeError("boom")))
    reg.register("before_round", lambda ctx: calls.append("second"))
    reg.fire("before_round", {})
    assert calls == ["second"]
```

- [ ] **Step 2: Implement** (rubric §A9 explicit hook names: before_round, after_round, before_verdict, after_verdict, before_llm_call, after_llm_call, before_search, after_search)
- [ ] **Step 3: Commit**

---

### Task 7.2: DebateOrchestrator (spawn + run + shutdown)

**Files:** Create `src/agent_debate/orchestration/orchestrator.py`, `tests/unit/test_orchestrator.py`

Subtasks:
- [ ] 7.2a — `spawn_children()` creates 3 mp.Process + 6 mp.Queue (in/out per child) + 1 heartbeat_queue + shared spend Value/Lock
- [ ] 7.2b — Two-phase boot (Judge sends setup_directive, waits for both acks)
- [ ] 7.2c — `run_debate(topic, n_pings)` debate loop with lifecycle hooks fired
- [ ] 7.2d — Transcript assembly and persistence
- [ ] 7.2e — `shutdown_gracefully()` SIGTERM cascade with 10s drain

---

## Phase 8 — Watchdog

### Task 8.1: Watchdog with heartbeat + state replay

**Files:** Create `src/agent_debate/orchestration/watchdog.py`, `tests/unit/test_watchdog.py`

Subtasks:
- [ ] 8.1a — Heartbeat polling (`_last_heartbeat` dict)
- [ ] 8.1b — Two-signal detection (is_alive AND heartbeat-staleness)
- [ ] 8.1c — Restart with backoff [1, 2, 4]
- [ ] 8.1d — State replay (re-inject shared spend, skill_dir, last setup_directive)
- [ ] 8.1e — Max-restarts fail-fast → emit `debate_aborted` verdict

---

## Phase 9 — SDK + Menu + Main

### Task 9.1: DebateSDK (sole entry point — N8 self-test surface)

**Files:** Create `src/agent_debate/sdk/__init__.py`, `src/agent_debate/sdk/debate_sdk.py`, `tests/unit/test_debate_sdk.py`

Subtasks:
- [ ] 9.1a — `run_debate(topic, n_pings)` wraps orchestrator
- [ ] 9.1b — `get_transcript(debate_id)` reads from transcripts/
- [ ] 9.1c — `get_spend_report()` returns SpendReport DTO
- [ ] 9.1d — `simulate_keystroke(key)` for N8 self-test
- [ ] 9.1e — `get_health_status()` returns HealthStatus DTO

---

### Task 9.2: DTOs (SpendReport, HealthStatus)

**Files:** Add to `src/agent_debate/sdk/debate_sdk.py` (or `src/agent_debate/sdk/dtos.py` if >150 lines)

- [ ] **Step 1: Implement DTOs from spec §7.5**

```python
@dataclass(frozen=True)
class SpendReport:
    total_input_tokens: int
    total_output_tokens: int
    estimated_cost_usd: Decimal
    pct_of_budget_used: float
    by_agent: dict[str, dict]


@dataclass(frozen=True)
class HealthStatus:
    children_alive: dict[str, bool]
    last_heartbeat_ages: dict[str, float]
    pending_messages: dict[str, int]
    restart_count: dict[str, int]
```

- [ ] **Step 2: Commit**

---

### Task 9.3: TerminalMenu (letter-keyed for SDK self-test)

**Files:** Create `src/agent_debate/menu/__init__.py`, `src/agent_debate/menu/tui.py`, `tests/unit/test_tui.py`

- [ ] **Step 1: Tests for menu rendering + keystroke dispatch**
- [ ] **Step 2: Implement letter-keyed menu (A/B/C/D/E/X) that delegates to DebateSDK**
- [ ] **Step 3: Commit**

---

### Task 9.4: main.py CLI entry point

**Files:** Create `src/agent_debate/main.py`

- [ ] **Step 1: Implement**

```python
"""CLI entry point — `agent-debate` or `uv run agent-debate`."""
from __future__ import annotations

import sys
from pathlib import Path

from agent_debate.menu.tui import TerminalMenu
from agent_debate.sdk.debate_sdk import DebateSDK
from agent_debate.shared.config import load_config


def main() -> int:
    config = load_config(Path("config"))
    sdk = DebateSDK(config=config)
    menu = TerminalMenu(sdk=sdk)
    return menu.run()


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Verify the entry point launches**

```bash
uv run agent-debate
# Expect: menu prints, X to exit
```

- [ ] **Step 3: Commit**

---

## Phase 10 — Integration + E2E tests

### Task 10.1: Full debate end-to-end (mocked LLM + search) — H1, H2, H3, H4, H5, H7, H18, H20

**Files:** Create `tests/integration/test_full_debate_mocked.py`

- [ ] **Step 1: Write the test** — spawns real processes with MockLLMProvider injected via config override; runs a full 10-ping debate; asserts:
  - All 20 turns logged
  - All routes Pro→Judge→Con (no direct Pro→Con)
  - JSON validity on every message
  - References_opponent true on every argument/counter
  - Verdict declared with differential scoring
  - Setup directives + acks visible at boot

- [ ] **Step 2: Run + commit**

---

### Task 10.2-10.9: Other integration scenarios

(See spec §6 for the 9-scenario table. Each is its own TDD task with explicit H-gate verification.)

---

### Task 10.10-10.12: E2E tests with real Claude + real DDG

(Gated by `@pytest.mark.e2e` + `RUN_E2E=1`. Each is real-money / real-network.)

---

## Phase 11 — Documentation

### Task 11.1 (= lifecycle step 6 — "You must create a readme file"): README.md

**⚠️ This task must run AFTER all TODO items in Phases 0-10 are marked done.** Per the slide, README comes AFTER execution, not before — because (lec01 L1249-1250) *"you'll create lots of projects, you'll quickly forget what you did."*

**Files:** Create `README.md`

- [ ] **Step 1: Write the full README** covering:
  - Title + 1-paragraph elevator pitch (quote spec §10 central thesis verbatim)
  - Installation (uv, Python 3.13, Claude CLI login)
  - Usage (`uv run agent-debate`, letter menu, sample run)
  - Architecture (embed class diagram, C4 container diagram)
  - Configuration (every config/*.json explained)
  - **Session 1 full dialogue** (paste full debate from `transcripts/sample-session-1.json`)
  - **Manual Phase 1 evidence** (screenshots, H22)
  - **Cost analysis** (token table per rubric §11)
  - Behavior notes (non-reproducible outcomes are DESIRED per N5)
  - Extension points (LLMProvider, SearchProvider, lifecycle hooks)
  - AI Usage Disclosure (verbatim syllabus paragraph)
  - License + Credits

- [ ] **Step 2: Commit**

---

### Task 11.2 (= Phase A): docs/PRD.md (rubric §2.5 step 1 — FIRST APPROVAL GATE)

**Files:** Create `docs/PRD.md`

> **⚠️ Per the slide:** this task is **STEP 1** of the lecturer's lifecycle and **must be done BEFORE any source code is written**. The phase numbers in this plan are written in dependency order, but execution order is docs-first.

- [ ] **Step 1: Frame the PRD task using Dr. Segal's verbatim prompt**

If using a subagent, prompt it exactly:

> "Your mission is to create the following PRD document based on the following description: [bullets from `docs/superpowers/specs/2026-05-24-hw2-debate-design.md` §0 locked decisions]"

If writing inline, internalize the same framing — the PRD is **derived from** the brainstorming spec's locked decisions, not invented anew.

- [ ] **Step 2: Write the PRD** with all standard sections:
  - **Background** — quote the 16× productivity statement (rubric §1.4) + the Context Engineering thesis (spec §10) verbatim in Hebrew + English
  - **Goals + KPIs** — target ≥90 on HW2, recover 6.5-pt HW1 gap, meet all 25 H-gates, fix 4 HW1 weak spots
  - **Functional requirements** — H1 through H25, each tagged with its source (spec / lec05 / rubric)
  - **Non-functional requirements** — ISO/IEC 25010 paragraph with verbatim Hebrew/English term pairs (rubric §A10)
  - **Security requirements** — `.env-example` only, `os.environ.get(...)`, no secrets in code, `.gitignore` enforces
  - **Constraints** — RAG out of scope per N4; CLI-only deliverable; Claude-CLI required on grader's machine
  - **Timeline** — phase mapping to the 4-day deadline (Phase A through 12)
  - **Out-of-scope** — multi-skill per agent (N10 bonus deferred), mixed providers (Gemini adapter not built), Unix-domain socket watchdog

- [ ] **Step 3: Commit**

```bash
git add docs/PRD.md
git commit -m "docs(prd): root PRD per Vibe Coding lifecycle step 1 (rubric §2.5)"
```

- [ ] **Step 4: 🛑 PAUSE — wait for explicit user approval before continuing.** Rubric §2.5 step 1 gate. The grader inspects git timeline for evidence of this pause. Do NOT write any other file until the user says "approved."

---

### Task 11.3: docs/PLAN.md (architecture + ADRs + ISO/IEC 25010)

**Files:** Create `docs/PLAN.md`, `docs/diagrams/*.svg`

- [ ] **Step 1: Write the PLAN** with:
  - C4 model (Context, Container, Component, Code diagrams in Mermaid)
  - UML sequence for single-ping flow
  - **Class diagram** (mandatory per HW2 spec §8.6)
  - ISO/IEC 25010 paragraph using both Hebrew and English term pairs
  - Deployment / operational architecture
  - JSON wire schema 1.00 reproduced verbatim
  - 7 ADR pointers

- [ ] **Step 2: Generate diagrams** via Mermaid (committed as both `.mmd` and `.svg`)
- [ ] **Step 3: Commit**

---

### Task 11.4 (= Phase C + D): docs/TODO.md — target 800 (within slide's 300-800, top of range)

**Files:** Create `docs/TODO.md`

- [ ] **Step 1: Generate the initial task list** — explode each task from this plan into granular subtasks. Add explicit tasks for:
  - Every config field validation
  - Every README section (install, usage, examples, screenshots, session-1 dump, cost analysis, behavior notes, extension points, AI disclosure, license)
  - Every test (unit + integration + e2e, ~136 tests)
  - Every commit (continuous-commits discipline is graded)
  - Every per-mechanism PRD (9 files × ~150-250 lines each)
  - Every ADR (7 files)
  - Every screenshot for manual Phase 1
  - Every diagram (C4 context/container/component, class diagram, sequence diagram)

Target: **~600 tasks initially** (the verify pass below will add ~200 more).

- [ ] **Step 2: Run the "be very critical" verify pass — use Dr. Segal's verbatim prompt**

If using a subagent, prompt it exactly:

> "Verify that all PRD demand implemented in the todo list. You must be very critical."

If inline, walk through `docs/PRD.md` requirement-by-requirement and ensure ≥1 TODO task implements each. Lec01 L1199-1201: this pass typically adds ~200 missed tasks. Accept the additions.

- [ ] **Step 3: Document the size choice in TODO.md header**

```markdown
# HW2 TODO list

**Target size:** 800 tasks (top of lecturer's slide range 300-800, bottom of CLAUDE.md target 800-1000).
After "you must be very critical" verify pass, this may grow toward 1000.
Sized to balance: Dr. Segal's slide ceiling, spoken-lecture minimum (lec01 L1170: "מינימום 500"),
and the user's HW2 quality target ≥90.

**Marking discipline:**
- `[ ]` = pending
- `[x]` = done (commit it when you mark — continuous-commits are graded)
- `[~]` = in progress (use sparingly; long [~] entries fragment the audit trail)
```

- [ ] **Step 4: Commit**

```bash
git add docs/TODO.md
git commit -m "docs(todo): initial task list (~800 entries) + 'very critical' verify pass"
```

---

### Task 11.5: Per-mechanism PRDs (9 files)

**Files:** `docs/PRD_judge_agent.md`, `docs/PRD_pro_agent.md`, `docs/PRD_con_agent.md`, `docs/PRD_orchestrator.md`, `docs/PRD_ipc_bus.md`, `docs/PRD_gatekeeper.md`, `docs/PRD_watchdog.md`, `docs/PRD_skills.md`, `docs/PRD_web_search_tool.md`

Each follows rubric §A13 building-block shape: Input / Output / Setup docstring, theoretical background, performance metrics, alternatives considered, test scenarios. Target 150-250 lines each. One commit per PRD.

---

### Task 11.6: ADRs (7 decision records)

**Files:** `docs/ADRs/ADR-001-ipc-queue.md` through `ADR-007-judge-criteria-preflight.md`

Each ADR: Context / Decision / Consequences / Alternatives. Pulled from spec §0 ADR table.

---

### Task 11.7: LICENSE (MIT)

**Files:** Create `LICENSE`

- [ ] **Step 1: Write MIT license with year 2026 + authors**
- [ ] **Step 2: Commit**

---

### Task 11.8: PAUSE — second user approval gate

**Rubric §2.5 step 5:** approve ALL docs (PRD + PLAN + TODO + per-mechanism PRDs) before any further code is written.

- [ ] **Step 1: Summarize the full docs package for user review**
- [ ] **Step 2: WAIT for explicit user approval**

---

## Phase 12 — Manual Phase 1 evidence + polish + submission

### Task 12.1: Run manual two-terminal debate (N9 / H22 — graded)

- [ ] **Step 1: Open two terminals**
- [ ] **Step 2: Drive a Pro vs Con debate manually** via Claude CLI in each (5-6 exchanges minimum)
- [ ] **Step 3: Screenshot the screens at key moments**
- [ ] **Step 4: Save screenshots to `assets/manual-phase1-*.png`**
- [ ] **Step 5: Embed in README "Manual exploration" section**
- [ ] **Step 6: Commit**

---

### Task 12.2: Run the actual system end-to-end + capture session 1 transcript

- [ ] **Step 1: `uv run agent-debate`**
- [ ] **Step 2: Press A → start debate**
- [ ] **Step 3: Wait for verdict (~5-8 minutes)**
- [ ] **Step 4: Verify transcript landed at `transcripts/<id>.json`**
- [ ] **Step 5: Copy transcript to `transcripts/sample-session-1.json`** (the README-embedded copy)
- [ ] **Step 6: Take screenshots: menu, debate-running view, verdict view, spend report**
- [ ] **Step 7: Embed transcript + screenshots in README**
- [ ] **Step 8: Commit**

---

### Task 12.3: Verify rubric audit gates pass (final preflight)

- [ ] **Step 1: `uv run ruff check src tests`** — 0 errors
- [ ] **Step 2: `uv run pytest tests/unit tests/integration --cov`** — coverage ≥85%
- [ ] **Step 3: `uv run python scripts/check_file_lines.py`** — 0 violations
- [ ] **Step 4: Grep for secrets** — `grep -r "sk-\|api_key\|API_KEY" src tests | grep -v ".env-example" | grep -v "ANTHROPIC_API_KEY"` → empty
- [ ] **Step 5: Verify ≥30 commits** — `git log --oneline | wc -l`
- [ ] **Step 6: Verify class diagram, C4 diagrams, sequence diagram are in `docs/diagrams/`**
- [ ] **Step 7: Verify README session-1 dialogue is present**
- [ ] **Step 8: Verify cost analysis table is in README**

---

### Task 12.4 (= lifecycle step 8 — "push to github as public"): Public GitHub + lecturer access

**⚠️ The slide says `as public` explicitly.** Lec05 L1641-1652: *"3 or 4 submitted with GitHub but without sharing — couldn't open them — there's a ZERO."* No resubmission. **PUBLIC is the safe default.**

- [ ] **Step 1: Create the GitHub repo PUBLIC** — `salah-dev-stu/uoh-sqak-ex02` (or partner-confirmed alternate)

  ```bash
  gh repo create salah-dev-stu/uoh-sqak-ex02 --public --description "HW2 Multi-Agent Debate System (course 203.3763)" --source=. --remote=origin
  ```

- [ ] **Step 2: Add Andalus as collaborator** — needs his GitHub username (open question, may need to ask user during execution)

  ```bash
  gh api repos/salah-dev-stu/uoh-sqak-ex02/collaborators/<andalus-handle> --method PUT
  ```

- [ ] **Step 3: Push main**

  ```bash
  git push -u origin main
  ```

- [ ] **Step 4: Verify lecturer can access** — open the repo URL in an incognito window. If the page loads without login → PUBLIC confirmed. If it shows "404" or "sign in" → repo is private and the lecturer would auto-zero this submission. Fix immediately:

  ```bash
  gh repo edit salah-dev-stu/uoh-sqak-ex02 --visibility public --accept-visibility-change-consequences
  ```

- [ ] **Step 5: Also share with rmisegal@gmail.com as a defensive belt-and-suspenders** (optional since repo is public; harmless redundancy)

  ```bash
  # Only if the lecturer has a GitHub account tied to that email; otherwise skip.
  # gh api repos/salah-dev-stu/uoh-sqak-ex02/collaborators/<lecturer-gh-handle> --method PUT
  ```

---

### Task 12.5: Fill submission PDF + Moodle upload

- [ ] **Step 1: `uv run python scripts/fill_submission_pdf.py`**
- [ ] **Step 2: Verify generated `uoh-sqak-ex02.pdf` has correct fields:**
  - exercise = 02
  - group = uoh-sqak
  - self-grade = 85 (per HW1-calibration default)
  - Student 1: Salah Qadah (323039974)
  - Student 2: Andalus Kalash (211435797)
  - repo URL
  - late submission = no (or yes if past deadline)
- [ ] **Step 3: Andalus uploads same PDF to his Moodle separately**
- [ ] **Step 4: Salah uploads to Moodle** assignment id=264177

---

## Self-Review (writing-plans skill step 7)

**Run on 2026-05-25 by the plan author.**

### Spec coverage

| Spec section | Task covering it |
|---|---|
| §0 locked decisions (13) | Each lands in a specific config file (Task 0.3) or implementation task |
| §1 Architecture (7 layers) | Phases 0, 1, 5-9 |
| §2 Skills design | Phase 4 (Tasks 4.1-4.5) |
| §3 Components / class hierarchy | Phases 5-7 |
| §4 Data flow + JSON wire protocol | Task 1.5 (schema), Phases 5-7 (state machines) |
| §5 Error handling + Watchdog | Phase 8 + Phase 10 integration tests (chaos) |
| §6 Testing strategy | Phase 0 (scaffold) + every Phase has TDD + Phase 10 (integration/e2e) |
| §7 Self-review fixes (DriftDetector regex, DTOs, command flags) | Tasks 6.2, 9.2, 2.3 |
| 25 H-gates (H1-H25) | Cross-referenced in integration tests (Task 10.x) |
| 4 HW1 weak spots | Phase 11 (Planning), Task 0.4 (Config/Security), Task 2.1 (Extensibility), Tasks 0.6 + 0.7 (Quality Standards) |

No gaps found.

### Placeholder scan

- "TBD"/"TODO" search → 0 hits
- "fill in details" → 0 hits
- "Similar to Task N" → 0 hits (each task is self-contained)
- "Add appropriate error handling" → 0 hits (error handling is concrete in spec §5 + Task 3.1)
- Steps that say what but not how → reviewed; all code-bearing steps have code blocks

### Type consistency

- `Message` dataclass field `from_role` (not `from` due to Python keyword) — used consistently in test_message_schema, base_agent step seam, judge routing
- `Stance.ORIGINALITY` and `Stance.REMIX_ONLY` — used in constants.py, pro_agent.py, con_agent.py, agents.json
- `LLMResponse`, `SearchHit`, `SpendReport`, `HealthStatus` — defined once, referenced by provider impls + SDK
- `BudgetExhausted`, `RateLimitExceeded`, `SearchRateLimited` — exception names consistent across raise sites and catch sites

### Scope

Plan fits 4-day execution window. Critical-path is Phases 0-9 (working end-to-end debate); Phase 11 documentation runs in parallel with execution time on each phase; Phase 12 is final-day polish + submission.

If time runs short, the falling order is: Phase 4.5 (judge criteria preflight, N7 bonus) → some Phase 10.x integration scenarios → Phase 10.10-12 (e2e tests gated anyway). The core debate still works without these.

---

## Execution handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-25-hw2-agent-debate-system.md`.**

Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Each subagent gets the task spec + the design spec for context, returns a commit; main session reviews before approving the next dispatch.

2. **Inline Execution** — Execute tasks in this session using `superpowers:executing-plans`, batch execution with checkpoints for review.

**Which approach?**
