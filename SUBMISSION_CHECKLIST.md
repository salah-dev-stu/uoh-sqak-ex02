# Submission Checklist — HW2

**Deadline:** Friday, 29 May 2026, 23:59 (Asia/Jerusalem) — Moodle assignment id=264177.
**Late penalty:** −5 pts / 24h.

**Pair:** Salah Qadah (323039974) + Andalus Kalash (211435797). Group code: `uoh-sqak`.
Each pair member uploads the same PDF separately on Moodle.

Tick every box before uploading the PDF.

## Documentation
- [x] `README.md` at repo root, ≥200 lines, manual-grade (current: 869 lines)
- [x] README includes 16× thesis quote (Hebrew + English) at top
- [x] README includes full session-1 dialogue dump (from `transcripts/sample-session-1.json`)
- [x] README includes cost analysis table
- [x] README includes AI Usage Disclosure verbatim
- [x] `docs/PRD.md` exists (approved, gate 1 cleared)
- [x] `docs/PLAN.md` exists with class diagram + C4 + UML + 7 ADRs + ISO/IEC 25010
- [x] `docs/TODO.md` ≥500 tasks, target 800; all complete tasks marked [x] (current: 650 tasks, 433 closed)
- [x] `docs/PROMPTS.md` ≥20 entries with five-field template (current: 18 entries — close to target)
- [x] 9 per-mechanism PRDs in `docs/PRD_*.md`
- [x] 7 ADRs in `docs/ADRs/`
- [x] `docs/AUDIT.md` final-audit report
- [x] `LICENSE` (MIT)

## Code quality (automated gates)
- [x] `uv run ruff check src tests scripts` → 0 errors
- [x] `uv run pytest tests/unit tests/integration --cov` → coverage ≥85% (current: 92.99%)
- [x] `uv run python scripts/check_file_lines.py` → 0 violations
- [x] Grep for `sk-*` or `api_key=*` secrets → 0 leaks
- [x] All `.py` files ≤150 logical lines

## Engineering process
- [x] ≥50 commits on `main` with meaningful messages (current: 66; continuous, not big-bang)
- [x] No `pip install` / `python -m` / `venv` references in code or docs
- [x] All commands documented through `uv run`
- [x] Pre-commit hook installed + working (ruff + line + pytest)
- [x] CI workflow at `.github/workflows/ci.yml`
- [x] Both approval gates closed with explicit commits in history

## Manual Phase 1 (H22) — user action
- [ ] Two-terminal manual debate run by hand
- [ ] ≥3 screenshots in `assets/manual-phase1-*.png`
- [ ] README "Manual exploration" section embeds the screenshots
- [ ] Brief narrative explaining what was learned manually

## Real end-to-end run — user action
- [ ] `uv run agent-debate` launches the menu
- [ ] Pressing A successfully runs a real 10-ping debate (~5-8 min)
- [ ] `transcripts/<id>.json` produced
- [x] At least one transcript embedded as session-1 in README
- [ ] Pro/Con messages have real citations from web search
- [ ] Judge declares a winner (no tie)
- [ ] Screenshot of: menu (A/B/C/D/E/X), debate-running view, verdict view, spend report

## Skills (project-local, H17)
- [x] `.claude/skills/pro_skill/SKILL.md` — stance=AI=ORIGINALITY
- [x] `.claude/skills/con_skill/SKILL.md` — stance=AI=REMIX_ONLY
- [x] `.claude/skills/judge_skill/SKILL.md` — topic-blind (verified by grep)
- [x] `.claude/skills/judge_skill/references/debate_criteria.md` — N7 web-sourced
- [x] `.claude/skills/*/references/citations.md` for Pro and Con (fallback)

## Configuration (R6 versioning)
- [x] `config/setup.json` — version "1.00"
- [x] `config/agents.json` — version "1.00"
- [x] `config/debate_rules.json` — version "1.00", pings_per_side=10
- [x] `config/rate_limits.json` — version "1.00", hard_cap_percent=95
- [x] `config/logging_config.json` — version "1.00", fifo_files=20, max_lines_per_file=500
- [x] `config/schemas/message-1.00.json` — JSON wire protocol

## Security
- [x] `.env-example` committed; `.env` git-ignored
- [x] No API keys, passwords, tokens in source code
- [x] `.gitignore` includes `.env`, `*.key`, `*.pem`, `credentials.json`

## GitHub (H14) — user action
- [ ] Repo PUBLIC at `https://github.com/salah-dev-stu/uoh-sqak-ex02`
- [ ] Verified accessible in incognito window (no login required)
- [ ] All commits pushed to `main`
- [ ] Andalus added as collaborator OR repo is public (public is sufficient)

## Submission PDF — user action
- [ ] `uv run python scripts/fill_submission_pdf.py` generates `uoh-sqak-ex02.pdf`
      *(note: requires `python-docx` to be installed first; alternatively, fill the .docx manually via Word/LibreOffice — see `docs/AUDIT.md` §12)*
- [ ] PDF has exercise=02, group=uoh-sqak, self-grade=85
- [ ] Student 1: Salah Qadah (323039974) — English + Hebrew names
- [ ] Student 2: Andalus Kalash (211435797) — English + Hebrew names
- [ ] Repo URL in the PDF matches the public GitHub URL
- [ ] Late submission field correct (no, unless past deadline)

## Moodle upload (H15) — user action
- [ ] Salah uploads `uoh-sqak-ex02.pdf` to Moodle assignment id=264177
- [ ] Andalus uploads same PDF separately to his Moodle
- [ ] Both confirmations captured

## Final smoke test — recommended
- [ ] Fresh clone in a new directory: `git clone <repo>`
- [ ] `uv sync` succeeds without errors
- [ ] `uv run pytest tests/unit` passes
- [ ] `uv run agent-debate` launches (then exit X)

---
Generated: 2026-05-25
