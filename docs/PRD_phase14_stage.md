# Per-Mechanism PRD — Presidential Debate Stage (Phase 14 Bonus)

**Component:** `frontend/components/stage14/` + content scorer + verdict rationale
**Version:** 1.00 (per R6)
**Companion design spec:** [`superpowers/specs/2026-05-27-hw2-presidential-debate-stage.md`](superpowers/specs/2026-05-27-hw2-presidential-debate-stage.md)
**Companion plan:** [`superpowers/plans/2026-05-27-hw2-presidential-debate-stage.md`](superpowers/plans/2026-05-27-hw2-presidential-debate-stage.md)
**Authored:** 2026-05-27
**Branch:** `phase14-presidential-stage`
**Phase:** 14 (bonus — cinematic 3D presentation layer over the Phase 13g viewer)

---

## Building-block docstring (rubric §A13)

```text
Input:  HTTP responses from the FastAPI backend at /api/debate/*
        Server-Sent Events stream of {started | message | before_round |
        after_round | verdict | after_verdict | done | error | stop_requested}
        Mouse/trackpad drag (PresentationControls cursor parallax),
        scroll-wheel events (±1 slide step, 220 ms throttle),
        click on bottom-strip pills (jump-to-turn).

Output: WebGL stage in the browser:
        - three illuminated 3D podiums (Pro left, Judge centre-forward, Con right)
        - per-podium volumetric spotlight beams; active speaker beam pulses
        - cinematic camera that lerps to a per-speaker target each frame
        - speech bubble anchored to the side of the speaking Pro/Con podium
        - DOM chyron at the bottom for all Judge text (intro + verdict)
        - broadcast title strip with status pill + designed Motion lower-third
        - fireworks particle bursts behind the winning podium at verdict time
        - bottom strip of grouped past-only pills + LIVE / Jump-to-Live badge
        Backend additions:
        - content_scorer.score_transcript(t) -> (Scorecard, Scorecard)
        - verdict_rationale.build_rationale(pro, con, winner) -> str
        - structured abort verdict when setup phase times out

Setup:  Same as Phase 13g (NEXT_PUBLIC_API_BASE, design-token CSS vars,
        Space Grotesk + Inter + JetBrains Mono fonts via next/font/google),
        PLUS:
        - three@0.184, @react-three/fiber@9.6, @react-three/drei@10.7
        - motion@11 via "motion/react"
        - CAMERA_TARGETS map (pro/con/judge/default)
        - POSITION map for speech bubble 3D anchors (pro/con)
        - DWELL presets STANDALONE (130 wpm, 800 ms entry, 14 s cap) and
          CHUNK (130 wpm, 700 ms entry, 11 s cap)
        - SENT_RE = /[\s\S]+?(?<!\d)[.!?]+(?!\d)(?=\s|$)/g
        - PARTICLES per firework burst = 64; CYCLE_S = 1.9; GRAVITY = 1.8
        - ACK_TIMEOUT_S in process_flow.py = 60.0 (was 30.0)
```

---

## 1. Theoretical background

### 1.1 Why a 3D stage on top of an HTML presentation

Phase 13g (committed on `main`) proves the SSE wire works and renders the
debate as a scroll-driven slide list. After seeing it the user's literal
reaction was *"It's good, but not wow."* That signal — a working-but-flat
presentation — is the same one product teams hit at the demo stage of a
shipped feature: the function is correct, the form does not yet match the
ambition. Phase 14 is the form pass.

A cinematic stage is appropriate here because the underlying content — a
structured Pro vs Con debate moderated by a Judge — already maps to a
real-world genre (a presidential debate). The translation cost is modest
when the user owns a single GPU machine; React Three Fiber lets the scene
be expressed declaratively, in the same file-size budget as a sufficiently-
ornate HTML alternative.

### 1.2 React Three Fiber is the right abstraction

R3F renders three.js scenes as a React component tree, which means:
- Each scene element (podium, beam, bubble) is one component file under
  the 150-LOC project cap.
- The scene reacts to state changes the same way DOM does — when
  `activeSpeaker` flips, the CameraDirector re-targets without an
  imperative `scene.update()` call.
- drei provides batteries: `<PresentationControls>` (cursor parallax),
  `<Stars>`, `<ContactShadows>`, `<Environment>`, `<Html>` (DOM inside
  3D), `<Text>` (true 3D text), `<Plane>`, `<RoundedBox>`. Each replaces
  custom shader / geometry code we would otherwise own.

The alternative — raw three.js + Canvas API — was rejected because:
1. Scene-graph management would explode the per-file line count.
2. We would re-implement what drei already ships, hand-rolled and untested.
3. Debugging is harder without React DevTools' component tree.

### 1.3 Reading-speed dwell is bounded by literature

Dwell timing is driven by the audience constraint (non-native English
readers — the lecturer and the grading agent). Brysbaert's 2019
meta-analysis (190 studies, 18,573 participants) reports a silent-reading
average of 238 wpm for native English non-fiction with explicit note that
*"reading rates are lower for ... readers with English as second
language."* The BBC subtitle guideline for general audiences is 160-180
wpm. Intermediate non-native readers fall in the 120-200 wpm band. We
chose **130 wpm + 700-800 ms reading-entry buffer**, well inside that
band, so a typical 28-word chunk lands at the ~11 s cap with comfortable
margin even for slower readers.

### 1.4 Content-derived scoring is information-theoretic

The Phase-10 placeholder emitted **Pro = 71, Con = 69** every debate
because four of five axes were hardcoded constants. That is no signal at
all. Phase 14's `content_scorer` re-derives all five axes from features
of the transcript text:

- **clarity** — avg words/sentence sweet-spot model
- **evidence** — citation cues, years, percentages, proper nouns
- **rebuttal** — opponent-referencing cue density
- **novelty** — type-token ratio (lexical variety)
- **role_fidelity** — own-stance keyword density vs opponent's

Each axis is bounded `[0, 20]`; totals bounded `[0, 100]`. The function
is pure, deterministic, and has no LLM round-trip — replaying the same
transcript replays the same score. That makes the scorer **auditable**:
the lecturer can read the same transcript, count the same features, and
verify the totals by hand.

---

## 2. Functional requirements

The Phase 14 functional requirements are F14-1 through F14-17 in root
`docs/PRD.md` §15. Restated here so this PRD is self-contained:

| #     | Requirement                                                                                              | Acceptance check                              |
|-------|----------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| F14-1 | Page auto-starts a fresh live debate on mount, no Start button required                                  | Open `localhost:3000`; debate visibly starts ≤ 5 s |
| F14-2 | Backend uses Claude CLI (`claude /login`), never an API key                                              | `ANTHROPIC_API_KEY` is unset; backend still produces real responses |
| F14-3 | Pro/Con responses split into ~28-word sentence-bundled chunks                                            | A 90-word turn renders as 3 bubbles, not one wall |
| F14-4 | Judge intro slide opens debate; Judge verdict closes; both in the bottom chyron                          | First and last slides have `speaker === 'judge'` |
| F14-5 | Auto-advance dwell scales with text length (130 wpm)                                                     | `computeDwellMs("Hello")` returns 3500; `computeDwellMs(80-word-text)` ≥ 7000 |
| F14-6 | Auto-advance does NOT reset when new chunks arrive mid-dwell                                             | Mid-stream append doesn't pause the current slide |
| F14-7 | When next slide arrives after current dwell elapsed, advance immediately                                  | A 30 s gap then arrival → advance within 100 ms |
| F14-8 | Title banner shows "ON AIR" while live, "Recorded" after verdict, "Standby" before, "Off Air" on error  | Inspect status pill in each state             |
| F14-9 | Title banner has a designed Motion pill below the title showing the topic                                | Visual: gold pill with "MOTION" tag + italic topic |
| F14-10| Camera lerps to a per-speaker target on every speaker change                                              | Pro turn: Pro reads larger in left foreground |
| F14-11| Bottom strip pill colours match speaker accent; consecutive same-speaker chunks group into ONE pill      | 3-chunk Pro turn → ONE Pro pill, not three    |
| F14-12| Bottom strip only renders past + active turns; future buffered chunks are hidden                          | Strip grows one pill at a time as dwell advances |
| F14-13| Verdict slide shows OUTCOME caps line + Judge's 1-2 sentence rationale                                    | Chyron renders both lines                     |
| F14-14| Fireworks particle bursts behind the winning podium during the verdict slide                             | Bursts visible behind Pro on `outcome === 'pro_wins'` |
| F14-15| Decimal points inside numbers (`0.002%`, `3.14`) survive through chunking                                 | Vitest regression case passes                 |
| F14-16| "OFF AIR" only fires on permanent stream closure, not on transient EventSource reconnects                | Title stays "ON AIR" through `readyState === CONNECTING` |
| F14-17| Setup-phase timeout renders a clear "Debate Aborted" chyron, not a 0 · 0 verdict                          | Trigger by rapid refreshes; orange caps + explanation visible |

---

## 3. Non-functional requirements

| ISO/IEC 25010 dimension      | How Phase 14 meets it                                                                                |
|------------------------------|------------------------------------------------------------------------------------------------------|
| Functional suitability       | 17 numbered F-reqs, each with an acceptance check; backend wire protocol unchanged.                  |
| Performance efficiency       | ≤ 12-mesh scene, 60 fps target on a recent MacBook with Chrome; bundle delta < 50 kB gzip vs Phase 13g. |
| Compatibility                | Reuses Phase 13g SSE consumer + state store; `main` still runs Phase 13g unchanged.                  |
| Usability                    | Auto-start (no click); ON AIR pulsing dot signals liveness; tooltip on every pill.                   |
| Reliability                  | EventSource onerror tightened to permanent-close + non-done; setup-timeout has its own verdict path. |
| Security                     | No API keys; `.env.local` git-ignored; CLI session-based auth (R11).                                  |
| Maintainability              | Every TS/Python file ≤ 150 lines; pure helpers (`chunks.ts`, `dwell.ts`, `content_scorer.py`, `verdict_rationale.py`) separately unit-tested. |
| Portability                  | Pure TypeScript + Python; WebGL works in any modern browser; no platform-specific bindings.          |

---

## 4. Alternatives considered

| Alternative                                              | Rejected because                                                                  |
|----------------------------------------------------------|-----------------------------------------------------------------------------------|
| Replace the Phase 13g viewer on `main`                   | Phase 13g is the proven safe submission. Phase 14 lives on a branch as bonus.    |
| Raw three.js without R3F                                 | Manual scene graph + disposal blows past the 150-LOC cap; loses React tree.       |
| `tsParticles` or `three.nebula` for fireworks            | 64-particle THREE.Points per burst is ~3 kB VRAM and fits in one 80-line file.   |
| LLM-generated rationale (extra Claude round-trip)         | Adds latency and per-debate cost; templated rationale is deterministic + free.   |
| Backend chunking (prompt Claude for pre-chunked JSON)     | Would change response quality and add per-turn LLM latency; transcript loses fidelity. |
| Audio / sound effects                                    | Deferred. "Without sound, for now." (User decision.)                              |
| Mobile / responsive layout                               | Demo-only artifact; desktop Chrome is the only target.                             |

---

## 5. Testing strategy

| Test target                                          | Where                                                  | Count |
|------------------------------------------------------|--------------------------------------------------------|-------|
| `splitIntoChunks` edge cases (incl. decimal regression) | `frontend/lib/__tests__/chunks.test.ts`                | 8     |
| `computeDwellMs` standalone + chunk presets          | `frontend/lib/__tests__/dwell.test.ts`                 | 9     |
| `score_transcript` deterministic on text features    | `tests/unit/test_content_scorer.py`                    | 6     |
| `build_rationale` length + shape + tiebreak path     | `tests/unit/test_verdict_rationale.py`                 | 5     |
| Visual: live debate runs end-to-end                  | Manual `/api/debate/start?live=1&n_pings=10`           | -     |
| Visual: fireworks at verdict                         | Manual; screenshot at verdict slide                    | -     |
| Visual: setup-timeout shows abort                    | Manual: rapid refreshes until CLI lags                 | -     |
| Type safety                                          | `npx tsc --noEmit`                                     | -     |
| Lint                                                 | `uv run ruff check src/` + `pre-commit run --all`      | -     |

---

## 6. Edge cases

| Case                                                | Handling                                                                                    |
|-----------------------------------------------------|---------------------------------------------------------------------------------------------|
| Claude CLI cold-start exceeds 60 s ack window       | Orchestrator writes structured abort verdict; chyron shows "DEBATE ABORTED" in orange.      |
| `0.002%`, `3.14`, `$1.50` mid-response              | Regex `(?<!\d)[.!?]+(?!\d)` — decimal points are not sentence boundaries; chunk preserves them. |
| Single sentence > 28 words                          | Becomes its own chunk; we don't mid-sentence chop.                                          |
| Empty response                                      | `splitIntoChunks("") → []`; no slide appended.                                              |
| EventSource transient reconnect                     | `onerror` only flips status to error on `readyState === CLOSED` && status !== "done".       |
| Page refresh during a debate                        | Fresh debate spawned; old SSE stream dies on tab close.                                     |
| User scrolls back during live debate                | `followLive` flips false; auto-advance halts until "Jump to live" pressed.                  |
| Active slide arrives after its dwell already passed | `setTimeout(max(0, dwell - elapsed))` → advance on next tick.                               |
| Tie on total + role_fidelity + evidence              | `declare_winner` returns "pro" (affirmative default); rationale emits the tiebreak sentence. |

---

## 7. Compliance with project-wide rules

| Rule | Status |
|------|--------|
| R7 (≤ 150 effective lines per file) | All new files under cap. `stage.tsx` 102, `r3f-scene.tsx` 115, `speech-bubble.tsx` 121, `judge-chyron.tsx` 114, `title-banner.tsx` 127, `fireworks.tsx` 80, `r3f-podium.tsx` ~95. `content_scorer.py` 131, `verdict_rationale.py` 59. |
| R11 (no secrets)                    | `.env.local` git-ignored; backend uses Claude `/login` session via `env -u ANTHROPIC_API_KEY`. |
| R12 (`uv` for Python)               | All Python commands run via `uv run`.                                                          |
| R13 (continuous commits)            | ~35 commits on `phase14-presidential-stage` branch, one per visible iteration.                 |
| TypeScript strict                   | `tsconfig.json` strict mode; no `any`; `React.JSX.Element` return types throughout.            |
| Real LLM calls only (H1)            | Backend `_make_provider_factory(live=True)` shells out to `claude -p`; no mocks.               |

---

## 8. Acceptance criteria

Mirror of `docs/PRD.md` §15.4 (copied here for grading-agent traceability):

1. Page loads, debate auto-starts within 5 s, no click required.
2. First Pro response visible within 30 s of page load.
3. Camera visibly swings between Pro / Judge / Con podiums.
4. Fireworks visible during verdict slide.
5. Verdict chyron shows score + outcome + rationale.
6. Different debates produce different scores.
7. All files ≤ 150 lines.
8. `npx tsc --noEmit` clean; `npx vitest run` green (34 tests).
9. `uv run pytest tests/unit/` green (151 tests).
10. Decimal preservation regression (`0.002%`) passes.
11. Setup-timeout case displays "Debate Aborted" cleanly.

---

## 9. Open questions

None blocking. The submission-time choice (does `main` ship Phase 13g
or Phase 14) is documented in root `docs/TODO.md` Phase 14.Y.8 and is
deferred until after the README screenshots are captured.
