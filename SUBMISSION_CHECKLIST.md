# Submission Checklist — HW2

**Deadline: Friday, 29 May 2026, 23:59 (Asia/Jerusalem)** — Moodle assignment id=264177. Late penalty: −5 pts / 24h.

**Pair:** Salah Qadah (323039974) + Andalus Kalash (211435797). Group code: `uoh-sqak`. Each member uploads same-repo-link PDF separately on Moodle.

Tick every box before uploading the PDF to Moodle.

## Project structure
- [x] `docs/PRD.md` exists, ends with approved sign-off
- [x] `docs/PLAN.md` exists with C4 + 10 ADRs + ISO/IEC 25010
- [x] `docs/TODO.md` exists with ≥ 800 tasks (current: 1042)
- [x] `docs/PRD_<mechanism>.md` exists for dataset, fc, rnn, lstm, training, evaluation
- [x] `docs/PROMPTS.md` exists with prompt log + meta-reflections
- [x] `README.md` at repo root, manual-grade content
- [x] `LICENSE` (MIT) at root
- [x] `pyproject.toml` + `uv.lock` tracked
- [x] `.env-example` committed; `.env` git-ignored
- [x] `.gitignore` includes secrets, caches, generated artefacts
- [x] `config/setup.json`, `config/rate_limits.json`, `config/logging_config.json` (all v1.00)

## Code quality
- [ ] `uv run ruff check src tests` returns 0 errors
- [ ] `uv run pytest --cov` reports ≥ 85% (target ≥ 90%)
- [ ] `uv run python scripts/check_file_lines.py` reports 0 violations
- [ ] No hardcoded secrets (grep clean)
- [ ] No hardcoded URLs / paths (grep + manual review)
- [ ] All `.py` ≤ 150 logical lines (no whitespace games)

## Engineering process
- [ ] ≥ 50 git commits with meaningful messages (continuous, not one giant push)
- [ ] Every doc committed in its own commit (PRD, PLAN, TODO, each per-mechanism PRD)
- [ ] Significant TODO groups committed together (not per line item)
- [ ] Code authored via `uv` only (no `pip install`, `python -m`, `venv`)
- [ ] All commands documented in README run through `uv run`

## Experiments
- [ ] `results/experiment_matrix.csv` populated (3 archs × 4 alphas × 3 seeds = 36 rows)
- [ ] `results/sensitivity.csv` populated (OAT sweep)
- [ ] `results/runs/<run_id>/loss_history.json` for every run
- [ ] `results/runs/<run_id>/eval_report.json` for every run
- [ ] `results/runs/<run_id>/best_model.pt` for every run
- [ ] `results/figs/` contains the key plots (heatmaps, loss curves, OAT sensitivity)
- [ ] `results/hypothesis_test.json` written by the notebook

## Notebook
- [ ] `notebooks/analysis.ipynb` executes end-to-end with no errors
- [ ] All 8 sections present (Setup, Dataset, Architectures, Training, Evaluation, Sensitivity, Hypothesis, Conclusion)
- [ ] LaTeX equations rendered correctly
- [ ] AI-assistance acknowledgment paragraph present (§8)

## GitHub
- [ ] Repo is **public** at `https://github.com/salah-dev-stu/sinusoid-extractor`
- [ ] `rmisegal@gmail.com` added as collaborator (defensive)
- [ ] `v1.00` tag pushed
- [ ] Repo description filled
- [ ] Repo topics: `pytorch`, `lstm`, `rnn`, `university-of-haifa`

## Deferred items (TBDs from PRD/CLAUDE.md)
- [ ] **Group code confirmed** (placeholder `uoh-sk01`)
- [ ] **Solo/pair status confirmed**
- [ ] **If solo**: permission email sent to `rmisegal@gmail.com`
- [ ] **Self-grade calibrated** (placeholder 92 — recheck against actual deliverable quality)
- [ ] **Partner details** (English + Hebrew name + ID) — only if pair

## Submission PDF
- [ ] `uoh-rl07-ex01.docx` filled — exercise number 01
- [ ] Group ID code field filled (8 chars)
- [ ] Self-grade field filled
- [ ] Student 1: ID 323039974, En name "Salah Qadah", He name "סלאח קדח"
- [ ] Student 2: filled or marked N/A (solo)
- [ ] GitHub link filled with the public repo URL
- [ ] Late submission yes/no
- [ ] Save as PDF named `<group_code>-ex01.pdf`
- [ ] Upload PDF to Moodle: https://mw26.haifa.ac.il/mod/assign/view.php?id=255044

## Final pre-flight
- [ ] `make ci` passes (lint + tests + cov + file size + secret scan)
- [ ] `git status` clean
- [ ] `git log --oneline | wc -l ≥ 50`
- [ ] All TBDs in `docs/PRD.md` resolved or explicitly accepted as deferred
- [ ] `gh repo view salah-dev-stu/sinusoid-extractor` shows public visibility
