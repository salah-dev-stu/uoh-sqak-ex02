# Phase 14 — Presidential Debate Stage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** On branch `phase14-presidential-stage`, build a cinematic 3D presentation layer over the existing FastAPI + SSE debate backend — three illuminated podiums, per-speaker volumetric spotlights, cinematic camera that swings to the active speaker, speech bubbles for Pro/Con, a Judge chyron, designed broadcast title strip, length-based per-slide dwell with sentence-bundled chunking, content-derived 5-axis scoring with a Judge rationale, and fireworks behind the winning podium.

**Architecture:** Same backend wire as Phase 13g (no protocol changes). A new `frontend/components/stage14/` directory hosts the React Three Fiber scene, R3F podiums + beams + camera director + fireworks, plus DOM overlays for the title banner and the Judge chyron. Backend gains a content-derived scorer and a templated rationale builder; the orchestrator's setup-phase timeout writes a structured abort verdict instead of a raw `{reason}` dict.

**Tech Stack:** Next.js 16.1.1, React 19, TypeScript 5 strict, three 0.184, @react-three/fiber 9.6, @react-three/drei 10.7, motion 11 (`motion/react`), native `EventSource`. Backend: Python 3.13, uv, FastAPI + uvicorn, Claude CLI via `/login` session.

**Spec reference:** [`../specs/2026-05-27-hw2-presidential-debate-stage.md`](../specs/2026-05-27-hw2-presidential-debate-stage.md)
**PRD reference:** root [`docs/PRD.md`](../../PRD.md) §15
**Global PLAN reference:** root [`docs/PLAN.md`](../../PLAN.md) §16

---

## File structure (additions / changes only)

```
frontend/
├── app/
│   └── page.tsx                  # MODIFIED: auto-start, no Start button
├── components/
│   ├── bottom-strip.tsx          # MODIFIED: grouped pills, future hidden
│   └── stage14/
│       ├── stage.tsx             # NEW: layout + auto-advance + wheel
│       ├── r3f-scene.tsx         # NEW: Canvas + CameraDirector + beams
│       ├── r3f-podium.tsx        # NEW: lectern + body + emblem
│       ├── speech-bubble.tsx     # NEW: Pro/Con side bubble (drei <Html>)
│       ├── judge-chyron.tsx      # NEW: Judge bottom strip + verdict
│       ├── title-banner.tsx      # NEW: top broadcast strip
│       └── fireworks.tsx         # NEW: winner particle bursts
└── lib/
    ├── chunks.ts                 # NEW: sentence-bundle splitter
    ├── __tests__/chunks.test.ts  # NEW: 8 vitest cases
    ├── dwell.ts                  # MODIFIED: two-mode preset
    ├── __tests__/dwell.test.ts   # MODIFIED: 9 cases covering both modes
    ├── sse.ts                    # MODIFIED: chunk fan-out, onerror tighten
    ├── state.ts                  # MODIFIED: topic field
    └── types.ts                  # MODIFIED: Slide.rationale + topic

src/agent_debate/
├── agents/
│   ├── content_scorer.py         # NEW: 5-axis text-feature scoring
│   └── verdict_rationale.py      # NEW: templated explanation
└── orchestration/
    ├── orchestrator.py           # MODIFIED: structured abort verdict
    ├── process_flow.py           # MODIFIED: ACK_TIMEOUT_S 30 → 60
    ├── process_verdict.py        # MODIFIED: delegate to new scorer
    └── debate_loop.py            # MODIFIED: delegate to finalize_verdict

tests/unit/
├── test_content_scorer.py        # NEW: 6 pytest cases
└── test_verdict_rationale.py     # NEW: 5 pytest cases
```

---

## Tasks

### Task 1 — Branch + foundation

- [x] **Step 1**: Cut `phase14-presidential-stage` from `main` and confirm `npx tsc --noEmit`, `npx vitest run`, `uv run pytest tests/unit/` all green.
- [x] **Step 2**: Save the brainstorm under `docs/superpowers/specs/2026-05-27-hw2-presidential-debate-stage.md`.
- [x] **Step 3**: Commit: `chore(phase14): branch foundation + brainstorm spec`.

### Task 2 — Install R3F + drei + motion

- [x] **Step 1**: `npm install three @react-three/fiber @react-three/drei motion` in `frontend/`.
- [x] **Step 2**: `npm install --save-dev @types/three`.
- [x] **Step 3**: Confirm Rolldown's native arm64 binding installs cleanly; if not, `rm -rf node_modules package-lock.json && npm install`.
- [x] **Step 4**: Verify the production build (`npm run build`) succeeds and the bundle delta < 50 kB gzip.
- [x] **Step 5**: Commit: `chore(phase14): install three + drei + motion`.

### Task 3 — Design tokens + accent flip

- [x] **Step 1**: In `frontend/app/globals.css`, confirm `--color-pro-accent`, `--color-con-accent`, `--color-judge-accent` are emerald / blue / amber. Flip Pro from magenta to emerald if necessary.
- [x] **Step 2**: Add `--color-{pro,con,judge}-glow` rgba tokens for box-shadow + filter usage.
- [x] **Step 3**: Commit: `style(phase14): accent + glow design tokens`.

### Task 4 — Scene scaffolding

- [x] **Step 1**: Create `frontend/components/stage14/` and stub `stage.tsx` rendering a fixed-viewport container that mounts an empty `<Canvas>`.
- [x] **Step 2**: Create `r3f-scene.tsx` with a `[0, 3.6, 10] fov 38` camera, ambient + directional lights, fog, a 40×40 floor, gridHelper, ContactShadows, Stars, and `Environment preset="night"`.
- [x] **Step 3**: Wire `Stage14` into `app/page.tsx` (still alongside the Phase 13g viewer at this point).
- [x] **Step 4**: Run dev server; verify the empty stage renders without console errors.
- [x] **Step 5**: Commit: `feat(phase14): R3F scene scaffold + base lighting`.

### Task 5 — Podiums

- [x] **Step 1**: Create `r3f-podium.tsx` accepting `{ speaker, position, rotationY, active }` props.
- [x] **Step 2**: Build the lectern as a RoundedBox + slanted top + emblem ring (drei `<Text>` glyph, not `<Html>` — needs to scale with camera).
- [x] **Step 3**: Add a Capsule body + Sphere head + per-podium pointLight that pulses (`useFrame`: `intensity = active ? 8 + sin(t*3)*0.6 : 0.8`).
- [x] **Step 4**: Mount three R3FPodiums in `r3f-scene.tsx`: Pro `(-3,0,0)` Y+0.22, Judge `(0,0,1.2)` Y0, Con `(3,0,0)` Y-0.22.
- [x] **Step 5**: Add lectern face labels (PRO / CON / JUDGE).
- [x] **Step 6**: Commit: `feat(phase14): three illuminated podiums with active-speaker pulse`.

### Task 6 — Volumetric beams

- [x] **Step 1**: In `r3f-scene.tsx`, add a `<VolumetricBeam>` cone (`coneGeometry(1.4, 6, 32, 1, true)`) per podium.
- [x] **Step 2**: Use MeshBasicMaterial with AdditiveBlending + DoubleSide + `depthWrite: false`.
- [x] **Step 3**: `useFrame` pulse: active `0.32 + sin(t*2)*0.04`, inactive `0.10`.
- [x] **Step 4**: Parametrize the beam's `z` so the Judge beam follows its podium (`z=1.2`).
- [x] **Step 5**: Commit: `feat(phase14): per-podium volumetric spotlights`.

### Task 7 — Cursor parallax

- [x] **Step 1**: Wrap all scene content in drei `<PresentationControls>` with `global`, `cursor`, `snap`, `polar={[-π/28, π/28]}`, `azimuth={[-π/8, π/8]}`.
- [x] **Step 2**: Remove any earlier manual cursor-camera shim; drop SpringConfig (incompatible with drei 10.7).
- [x] **Step 3**: Verify cursor drag rotates the scene group around the centre.
- [x] **Step 4**: Commit: `feat(phase14): PresentationControls cursor parallax`.

### Task 8 — Per-speaker camera framing

- [x] **Step 1**: Add `<CameraDirector>` inside `<Canvas>` (above `<PresentationControls>`) accepting `{ activeSpeaker }`.
- [x] **Step 2**: Define `CAMERA_TARGETS = { pro: [+3.6, 3.4, 8.6], con: [-3.6, 3.4, 8.6], judge: [0, 3.6, 9.4], default: [0, 3.6, 10] }` (Pro/Con flipped vs the obvious mapping — see PLAN §16 ADR 14-H.6).
- [x] **Step 3**: `useFrame` lerp `camera.position` toward the speaker's target at 0.035; `camera.lookAt(0, 2.0, 0)` so the swing is around centre.
- [x] **Step 4**: Manually verify the camera glides between Pro / Judge / Con as the active slide changes; confirm the scene-group rotation (from cursor parallax) composes cleanly.
- [x] **Step 5**: Commit: `feat(phase14): cinematic per-speaker camera swing`.

### Task 9 — Speech bubbles (Pro / Con)

- [x] **Step 1**: Create `speech-bubble.tsx`. Anchor each side at a 3D point: `pro: [-3.8, 3.4, 0.2]`, `con: [+3.8, 3.4, 0.2]`.
- [x] **Step 2**: Use drei `<Html>` with `transform: translate(-100%, 0)` (Pro grows LEFT) or `translate(0, 0)` (Con grows RIGHT) — no `center` prop.
- [x] **Step 3**: Drop the `maxHeight` clamp; the dwell is sized to the chunk so the bubble can grow to its content.
- [x] **Step 4**: Body font: `var(--font-display)` Space Grotesk 0.95 rem, line-height 1.55.
- [x] **Step 5**: `stripMarkdown` regex for `**`, `*`, backticks, `~~`, list bullets — Claude can emit these despite the prompt.
- [x] **Step 6**: SVG tail on right edge for Pro (rotate -90° toward Pro), left edge for Con (rotate +90° toward Con).
- [x] **Step 7**: Early-return when `slide.speaker` is not pro/con (Judge goes through the chyron).
- [x] **Step 8**: AnimatePresence cross-fade keyed on `slide.id`.
- [x] **Step 9**: Commit: `feat(phase14): side-anchored speech bubbles`.

### Task 10 — Judge chyron

- [x] **Step 1**: Create `judge-chyron.tsx` as a fixed bottom DOM overlay (`bottom: 4.5rem`) so it clears the bottom strip.
- [x] **Step 2**: 900 px max-width, gold border, glassy dark panel, blur backdrop.
- [x] **Step 3**: Header row: `JUDGE · variant · PING N` on the left; on verdict slides only, Pro/Con score pair on the right.
- [x] **Step 4**: Body: plain text for intro/abort; for verdict, OUTCOME caps line + italic rationale above a thin gold separator.
- [x] **Step 5**: Aborted outcome rendered in orange `#ff8a5c`.
- [x] **Step 6**: Commit: `feat(phase14): Judge chyron with verdict layout`.

### Task 11 — Title banner

- [x] **Step 1**: Create `title-banner.tsx` as a fixed top DOM overlay with a vertical dark-fade gradient background.
- [x] **Step 2**: "AGENT DEBATE" in Space Grotesk +0.35em tracking, gold glow, flanked by two horizontal gold gradient accent rails (max-width 220 px each).
- [x] **Step 3**: Status sub-line `2026 · ON AIR` with a pulsing red dot when `status === "live"`. Labels: On Air / Recorded / Standby / Off Air.
- [x] **Step 4**: Designed Motion pill below the status: gold capsule, inner "MOTION" mono tag, topic italic Space Grotesk single-line with `text-overflow: ellipsis`.
- [x] **Step 5**: `pointer-events: none` so the banner doesn't block PresentationControls drag.
- [x] **Step 6**: Commit: `feat(phase14): broadcast title banner with designed Motion pill`.

### Task 12 — Topic plumbing

- [x] **Step 1**: Add `topic?: string` to `SlideState` in `lib/types.ts`.
- [x] **Step 2**: In `lib/sse.ts`, `openStream(debate_id, topic)` sets `state.topic`.
- [x] **Step 3**: Banner reads `s.topic` with a hardcoded fallback constant.
- [x] **Step 4**: Same topic appears in the synthetic Judge intro slide.
- [x] **Step 5**: Commit: `feat(phase14): plumb topic into banner + intro slide`.

### Task 13 — Auto-start (no Start button)

- [x] **Step 1**: In `app/page.tsx`, call `startDebate({ nPings: 10, live: true })` inside a `useEffect` guarded by a `firedRef`.
- [x] **Step 2**: On success, `openStream(r.debate_id, DEFAULT_TOPIC)`.
- [x] **Step 3**: On error, `setState({ status: 'error', error: e.message })`.
- [x] **Step 4**: Remove the old StartScreen entirely.
- [x] **Step 5**: Commit: `feat(phase14): auto-start live debate on page mount`.

### Task 14 — SSE consumer hardening

- [x] **Step 1**: In `lib/sse.ts`, prepend a synthetic Judge intro slide on `openStream` so the stage opens on a Judge moment.
- [x] **Step 2**: On `verdict` event, detect abort via `verdict.reason === 'setup_phase_timeout'` OR `outcome === 'debate_aborted'`. Forward `verdict.rationale` onto the slide.
- [x] **Step 3**: Tighten `onerror` to fire only when `es.readyState === EventSource.CLOSED && getState().status !== 'done'` — otherwise leave status alone (transient reconnects, normal stream close after verdict).
- [x] **Step 4**: Commit: `feat(phase14): synthetic intro + tightened SSE error handling`.

### Task 15 — Sentence-bundle chunking

- [x] **Step 1**: Create `lib/chunks.ts` exposing `splitIntoChunks(text, maxWords = 28)`.
- [x] **Step 2**: Regex: `/[\s\S]+?(?<!\d)[.!?]+(?!\d)(?=\s|$)/g` — periods between digits do NOT split (preserves `0.002%`, `3.14`).
- [x] **Step 3**: Greedy bundler: pack consecutive sentences into chunks ≤ maxWords. Long single sentences become their own chunk.
- [x] **Step 4**: Empty input → `[]`. No sentence boundary found → whole text as one chunk.
- [x] **Step 5**: In `lib/sse.ts`, on `message` event for Pro/Con, fan out via `splitIntoChunks` → one Slide per chunk with id `msg_id-c<i>`.
- [x] **Step 6**: Judge text bypasses the splitter.
- [x] **Step 7**: Add `lib/__tests__/chunks.test.ts` covering empty, fallback, decimal preservation (regression), short-sentence bundling, single-long-sentence, terminal-punctuation preservation. 8 cases.
- [x] **Step 8**: Run `npx vitest run` → all green.
- [x] **Step 9**: Commit: `feat(phase14): sentence-bundle chunking with decimal-safe regex`.

### Task 16 — Two-mode dwell

- [x] **Step 1**: In `lib/dwell.ts`, define two presets: STANDALONE (130 wpm, 800 ms entry, 3.5-14 s clamp) and CHUNK (130 wpm, 700 ms entry, 4.5-11 s clamp). Same wpm, different caps.
- [x] **Step 2**: `computeDwellMs(text, opts?)` picks the preset based on `opts.isChunk`.
- [x] **Step 3**: Header comment cites Brysbaert 2019 + BBC subtitle guideline.
- [x] **Step 4**: `lib/__tests__/dwell.test.ts` covers both presets + edges (9 cases total).
- [x] **Step 5**: Commit: `feat(phase14): two-mode reading-speed dwell`.

### Task 17 — Auto-advance effect

- [x] **Step 1**: In `stage.tsx`, replace any `setInterval` ticker with a per-slide `setTimeout`.
- [x] **Step 2**: Track `slideStartRef = Date.now()` reset in a `useEffect` keyed on `slideId`.
- [x] **Step 3**: Detect chunk via `/-c\d+$/.test(slideId)`.
- [x] **Step 4**: Timeout = `Math.max(0, dwell - elapsed)` so a late slide arriving past its dwell advances immediately.
- [x] **Step 5**: Effect deps `[followLive, slideId, slideText, hasNext]` — NOT `state.slides` (would reset on every chunk append).
- [x] **Step 6**: Commit: `feat(phase14): elapsed-time-aware auto-advance`.

### Task 18 — Bottom strip (grouped, past-only)

- [x] **Step 1**: In `bottom-strip.tsx`, reduce `slides[]` to `groups[]` of consecutive same-speaker entries.
- [x] **Step 2**: Render `groups.slice(0, activeGroupIdx + 1)` — hide future buffered chunks entirely.
- [x] **Step 3**: Pill colour = `var(--color-${speaker}-accent)`; width scales with `count`.
- [x] **Step 4**: Active pill bigger + glow; past pills slightly dimmer.
- [x] **Step 5**: Right counter: `turn N/total` of groups.
- [x] **Step 6**: Commit: `feat(phase14): grouped pills, past-only rendering`.

### Task 19 — Content-derived scoring

- [x] **Step 1**: Create `src/agent_debate/agents/content_scorer.py`. Define `_clarity`, `_evidence`, `_rebuttal`, `_novelty`, `_role_fidelity` helpers each returning 0-20.
- [x] **Step 2**: Skip `ack` / `setup_directive` messages from the scoring corpus.
- [x] **Step 3**: `score_transcript(transcript) -> (pro_card, con_card)`.
- [x] **Step 4**: In `src/agent_debate/orchestration/process_verdict.py`, replace the Phase-10 placeholder body with a call to `score_transcript`.
- [x] **Step 5**: In `src/agent_debate/orchestration/debate_loop.py`, defer to `finalize_verdict` instead of inlining a verdict dict.
- [x] **Step 6**: Add `tests/unit/test_content_scorer.py` with 6 cases (empty, weak/strong, per-axis sensitivity, ack-leak guard).
- [x] **Step 7**: `uv run pytest tests/unit/` → all green.
- [x] **Step 8**: Commit: `feat(judge): real content-derived scoring (no more Pro 71 / Con 69)`.

### Task 20 — Verdict rationale

- [x] **Step 1**: Create `src/agent_debate/agents/verdict_rationale.py` exposing `build_rationale(pro, con, winner) -> str`.
- [x] **Step 2**: Find largest positive axis gap (winner's strength) and largest negative gap (loser's strength). Use `AXIS_LABELS` map for human-readable names.
- [x] **Step 3**: Margin classifier: ≤2 → "by a hair"; ≥15 → "in a decisive showing"; otherwise default.
- [x] **Step 4**: Tiebreak path: explicit "edged the tiebreak on role_fidelity" sentence when no positive gap exists.
- [x] **Step 5**: In `finalize_verdict`, set `transcript.verdict.rationale = build_rationale(...)`.
- [x] **Step 6**: Add optional `rationale?: string` on `frontend/lib/types.ts` `Slide`.
- [x] **Step 7**: In `lib/sse.ts`, copy `verdict.rationale` onto the verdict slide.
- [x] **Step 8**: In `judge-chyron.tsx`, render the rationale under the OUTCOME line as centered italic 0.92 rem above a thin gold separator.
- [x] **Step 9**: Add `tests/unit/test_verdict_rationale.py` with 5 cases (lopsided, hair-thin, loser-strength acknowledged, con-wins label, length cap).
- [x] **Step 10**: Commit: `feat(judge): verdict rationale templated from scorecards`.

### Task 21 — Setup-phase timeout handling

- [x] **Step 1**: In `process_flow.py`, bump `ACK_TIMEOUT_S` from 30 → 60 s to handle Claude CLI cold-start.
- [x] **Step 2**: In `orchestrator._run_with_processes`, on `run_setup_phase` failure write `transcript.verdict = {winner: None, pro_total: 0, con_total: 0, reason: 'setup_phase_timeout'}` (same shape as a finished verdict so the SSE consumer doesn't crash on missing fields).
- [x] **Step 3**: Frontend `sse.ts` detects abort via verdict.reason / outcome and writes a human-readable explanation onto the verdict slide.
- [x] **Step 4**: Chyron shows `DEBATE ABORTED` caps in orange `#ff8a5c` + the explanation text.
- [x] **Step 5**: `uv run pytest tests/unit/` still green.
- [x] **Step 6**: Commit: `fix(orch): structured abort verdict + 60s ack timeout`.

### Task 22 — Fireworks

- [x] **Step 1**: Create `components/stage14/fireworks.tsx` exporting `<Fireworks winner=... />`.
- [x] **Step 2**: Define `<FireworkBurst>` with a 64-particle `THREE.Points` buffer.
- [x] **Step 3**: Re-seed velocities on the unit sphere + small +y bias at every cycle start (1.9 s cycle).
- [x] **Step 4**: Per-frame parabolic: `position[i] = velocity[i] * dt - 0.5 * gravity * dt² * (i==y)`.
- [x] **Step 5**: PointsMaterial: AdditiveBlending + sizeAttenuation + `depthWrite: false`. Opacity fades 1 → 0 across cycle.
- [x] **Step 6**: Four bursts behind the winning podium with offsets `0 / 0.65 / 1.3 / 1.9` s. Two in winner accent, one gold, one white sparkle.
- [x] **Step 7**: Mount inside `<PresentationControls>` so cursor parallax pans the bursts too.
- [x] **Step 8**: In `stage.tsx`, derive `winner: 'pro' | 'con' | null` from the active slide — only non-null when `variant === 'verdict' && outcome ∈ {pro_wins, con_wins}`.
- [x] **Step 9**: Pass `winner` through to `<R3FScene>` → `<Fireworks>`.
- [x] **Step 10**: `args={[positions, 3]}` on `<bufferAttribute>` to satisfy R3F strict types.
- [x] **Step 11**: Commit: `feat(phase14): fireworks behind winning podium at verdict time`.

### Task 23 — Manual visual verification

- [x] **Step 1**: Refresh `localhost:3000` → debate auto-starts within 5 s, no click required.
- [x] **Step 2**: Judge intro slide visible before Pro's first turn.
- [x] **Step 3**: Pro turn → camera swings; Pro reads big in left foreground.
- [x] **Step 4**: Con turn → camera swings opposite; Con reads big in right foreground.
- [x] **Step 5**: Bottom strip grows one pill at a time as the dwell advances.
- [x] **Step 6**: Active pill glows + larger; past pills slightly dimmer.
- [x] **Step 7**: Title shows ON AIR with pulsing dot during live.
- [x] **Step 8**: Motion pill clearly shows the topic.
- [x] **Step 9**: Verdict slide shows OUTCOME caps + score pair + italic rationale.
- [x] **Step 10**: Fireworks pop behind winning podium for the duration of the verdict slide.
- [x] **Step 11**: Title flips to "Recorded" after verdict.
- [x] **Step 12**: Different debates produce different scores.
- [x] **Step 13**: Setup-timeout case displays "Debate Aborted" cleanly.
- [x] **Step 14**: No browser console errors after a full run-through.

### Task 24 — Automated regression

- [x] **Step 1**: `npx tsc --noEmit` → clean.
- [x] **Step 2**: `npx vitest run` → 34 / 34 passing.
- [x] **Step 3**: `uv run pytest tests/unit/` → 151 / 151 passing.
- [x] **Step 4**: `uv run ruff check src/` → clean.
- [x] **Step 5**: Pre-commit hook (`ruff` + `150-line check` + `pytest unit-only`) passes on every Phase 14 commit.

### Task 25 — Closure docs

- [x] **Step 1**: Append Phase 14 section to root `docs/PRD.md` (§15) with F14-1 through F14-17 functional requirements.
- [x] **Step 2**: Append Phase 14 section to root `docs/PLAN.md` (§16) with architecture diagram, 8 technical decisions, file structure, 7-row risk register.
- [x] **Step 3**: Append Phase 14 section to root `docs/TODO.md` with sub-phases 14.A through 14.Y.
- [x] **Step 4**: Mirror this plan at `docs/superpowers/plans/2026-05-27-hw2-presidential-debate-stage.md` (this file).
- [ ] **Step 5**: Capture README screenshots (per-speaker camera framing, verdict + fireworks).
- [ ] **Step 6**: Update root `README.md` Bonus section with Phase 14 branch + screenshots.
- [ ] **Step 7**: Decide whether `main` ships Phase 13g or Phase 14.
- [ ] **Step 8**: If Phase 14 ships: merge into `main`, bump version, tag `v1.00-phase14`.
- [ ] **Step 9**: Push branch to GitHub public OR add `rmisegal@gmail.com` as collaborator.
