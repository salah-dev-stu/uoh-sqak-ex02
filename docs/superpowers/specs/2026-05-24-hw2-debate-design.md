# HW2 Multi-Agent Debate System — Design Spec

**Status**: In progress (brainstorming session, 2026-05-24). §1 + Skills locked; §2-§5 pending.
**Authoring agent**: Claude Opus 4.7 via brainstorming skill
**Audit trail**: see `docs/PROMPTS.md`

---

## 0. Locked decisions (one-line summary)

| Topic | Lock | Why |
|---|---|---|
| Debate topic | "Can AI agents create genuinely original art, or only remix human work?" | Meta — course-perfect; originality bonus |
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

## 3. Components (PENDING — to be designed in §2 of brainstorming)

Will cover:
- Full class hierarchy: `BaseAgent` → `PartisanAgent` → `ProAgent`/`ConAgent`; `BaseAgent` → `JudgeAgent`
- Mixins: `LoggingMixin`, `LifecycleMixin`, `HeartbeatMixin`
- Per-mechanism PRDs to be authored: `PRD_judge_agent.md`, `PRD_pro_agent.md`, `PRD_con_agent.md`, `PRD_orchestrator.md`, `PRD_ipc_bus.md`, `PRD_gatekeeper.md`, `PRD_watchdog.md`, `PRD_skills.md`, `PRD_web_search_tool.md`

## 4. Data flow + JSON wire protocol (PENDING — §3 of brainstorming)

## 5. Error handling + watchdog (PENDING — §4 of brainstorming)

## 6. Testing strategy (PENDING — §5 of brainstorming)

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
