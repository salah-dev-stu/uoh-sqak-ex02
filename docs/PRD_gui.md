# Per-Mechanism PRD — Web GUI (Scroll-Driven Debate Presentation)

**Component:** `frontend/` (Next.js 16 App-Router SPA)
**Version:** 1.00 (per R6)
**Companion design spec:** [`superpowers/specs/2026-05-26-hw2-gui-scroll-presentation.md`](superpowers/specs/2026-05-26-hw2-gui-scroll-presentation.md)
**Authored:** 2026-05-26
**Phase:** 13g (presentation rebuild; supersedes 13a HTML and the wiped 13c–13f iterations)

---

## Building-block docstring (rubric §A13)

```text
Input:  HTTP responses from the FastAPI backend at /api/debate/*
        Server-Sent Events stream of {started | message | before_round |
        after_round | verdict | after_verdict | done | error | stop_requested}
        user inputs: topic (str), n_pings (1..20), live (bool),
        scroll wheel / trackpad / keyboard navigation events,
        click on dot-scrubber or JUMP-TO-LIVE badge

Output: rendered presentation in the browser:
        - landing screen with topic + pings + Live toggle + START
        - sequence of fullscreen slides (Judge intro · Pro · Con · ... · Judge verdict)
        - scroll-driven crossfade between slides via Framer Motion useScroll
        - bottom strip with running tally + dot scrubber + ping counter + live badge
        - real-time auto-follow during live debate with manual JUMP-TO-LIVE override
        - persistent scrubbable archive after debate completes

Setup:  NEXT_PUBLIC_API_BASE (str, default http://localhost:8000),
        FONTS: Space Grotesk (display) + Inter (body) + JetBrains Mono (meta)
              via next/font/google,
        COLOR TOKENS: --pro-accent #ff3da8, --con-accent #3da8ff,
                      --judge-accent #ffc94c, --bg-base #07070a,
        TRANSITIONS: per §6.5 of design spec (700ms easeOutCubic crossfade,
                     25ms word stagger, spring avatar entry),
        LENIS smooth-scroll provider mounted globally,
        N_SLIDES_DEFAULT = 22 (= 1 intro + 20 turns + 1 verdict for n_pings=10)
```

---

## 1. Theoretical background

The previous seven iterations (13c through 13f) all attempted multi-panel layouts: Pro/Con side-by-side, Judge dashboard panel, chat threads, comparison tables. The user rejected all seven for the same root cause — **"absolute chaos"** at the screen level, with no clear visual focus and broken responsiveness at non-default viewport sizes.

This redesign inverts the metaphor: **one speaker at a time, fullscreen, scroll-driven.** The pattern is well-established (Apple product pages, Linear landing pages, Stripe Sessions, awwwards-grade scrollytelling): the page DOM is a tall container, a sticky inner stage stays pinned to the viewport, and scroll position drives opacity + Y-transform animations on a single visible slide. Lenis (already on the existing Next.js template stack) provides the smooth scroll inertia; Framer Motion's `useScroll` + `useTransform` map scroll progress to visual state.

The debate-stage convention — **Pro left, Con right, Judge center** — matches parliamentary debate and most televised political debates. Pro is left because Western reading order goes left-first (so "for" precedes "against" as a default), and parliamentary debate seats the Government on the Speaker's right (audience's left).

Real-time SSE streaming with manual override is borrowed from Twitch's "follow live" pattern: scroll back to revisit anything, click `JUMP TO LIVE` to snap forward and resume auto-follow.

---

## 2. Functional requirements

| Req | Behavior | Implementation detail |
|---|---|---|
| **G1** | Landing screen renders before any backend call | `app/page.tsx` shows `<StartScreen />` until `status === "live"` |
| **G2** | START button issues `POST /api/debate/start?live=<0\|1>&n_pings=<n>` and opens SSE on the returned `debate_id` | `lib/api.ts` + `lib/sse.ts`; mock when `live=0`, real Claude when `live=1` |
| **G3** | Each SSE `message` event appends one slide, deduped by `msg_id` | `seenIds: Set<string>` in `lib/state.ts` |
| **G4** | The duplicate `message` event for forwarded messages (`from in {pro,con} && to !== judge`) is skipped to avoid double-rendering | Filter in `lib/sse.ts` before `appendSlide` |
| **G5** | Pro slides anchor visually to the left, Con to the right, Judge to center | `<Slide variant="pro" \| "con" \| "judge">` switches anchor utility class |
| **G6** | Each slide fades in over ~700ms with avatar spring + word-stagger body reveal | `components/slide.tsx` + `components/word-reveal.tsx` |
| **G7** | Scroll wheel / trackpad / arrow keys scrub the timeline; only one slide is fully visible at a time | Framer Motion `useScroll` on document; `useTransform` per slide |
| **G8** | While debate is streaming, each new slide triggers a smooth programmatic scroll if `followLive` is true | Lenis `scrollTo(latestSlideY, {duration: 0.7})` |
| **G9** | User scrolling back pauses `followLive`; `LIVE` badge becomes clickable `JUMP TO LIVE`; clicking it resumes auto-follow | `onUserScroll` handler in `<StatusStrip>` |
| **G10** | After `done` SSE event, the live badge hides and the full timeline becomes a scrubbable archive | `status` transitions `live → done` in `state.ts` |
| **G11** | Bottom dot-scrubber: one dot per slide, color-coded; hover = tooltip; click = jump | `components/dot-scrubber.tsx` |
| **G12** | Running Pro/Con tally updates from `after_round` SSE events | `state.proTotal` and `state.conTotal` |
| **G13** | Verdict slide displays `verdict.pro_total / verdict.con_total / outcome` from the nested verdict payload | `components/slide.tsx` `variant === "verdict"` branch |
| **G14** | All UI respects `prefers-reduced-motion: reduce` — transitions collapse to ≤80ms, no scale/translate | CSS media query + Framer Motion `useReducedMotion()` |
| **G15** | The page is viewable at any viewport ≥320px wide without horizontal scroll, broken text, or hidden content | Single-column slide; max-width 65ch; viewport-fluid font sizes |
| **G16** | All values that could vary (font, color, slide count, transition duration) come from `globals.css` custom properties — no magic numbers in TSX | CSS custom properties + Tailwind v4 theme tokens |
| **G17** | License key (React Bits Pro) is NOT used by this page — pure custom build — and `.env.local` is git-ignored regardless | `.gitignore` already includes `.env.local`; no `@reactbits-*` imports |
| **G18** | Backend code in `src/agent_debate/` is unchanged — frontend talks to existing endpoints only | No edits to `src/agent_debate/web/*.py` |

---

## 3. Non-functional requirements

| Req | Target | Measurement |
|---|---|---|
| First Contentful Paint | ≤ 1.2 s on M2 + cable broadband | Lighthouse production build |
| Lighthouse Performance | ≥ 85 | Lighthouse production build |
| Lighthouse Accessibility | ≥ 95 | Lighthouse production build |
| Cumulative Layout Shift | ≤ 0.05 | Lighthouse production build |
| Smooth-scroll frame rate | ≥ 55 fps during live debate | Chrome DevTools Performance recording |
| Initial JS bundle (gzip) | ≤ 300 kB | `next build` output |
| Re-renders per scroll tick | 0 (Framer Motion uses imperative style writes) | React DevTools Profiler |

---

## 4. Alternatives considered

| Alternative | Rejected because |
|---|---|
| Multi-panel layout (Pro left, Con right, Judge center, all visible at once) | Tried 7 times in phases 13c–13f. User rejected every variant — "chaos", "doesn't fit page", responsiveness broken at non-default viewports. Single-slide eliminates the layout problem entirely. |
| Chat-thread vertical scroll list (each message a card) | Phase 13a baseline. User asked for something "presentation-like" — a thread loses the dramatic per-turn focus the user wants. |
| React Bits Pro Minimal template fork + content swap | Phase 13f. User rejected — *"its not aapropriate, remove it again"*. The template's marketing-page composition (hero / features / pricing) doesn't fit a live debate viewer; the only reusable piece was Lenis, which we kept. |
| Slideshow with arrow-key advance only (no scroll-driven) | Less idiomatic for the web; scroll is the natural timeline scrubber. User explicitly said *"not with arrows, with scroll"*. |
| GSAP ScrollTrigger instead of Framer Motion `useScroll` | GSAP requires `@gsap/react`, adds ~50kB, and we already have Framer Motion in the dependency tree from prior iterations. Framer Motion's `useScroll` + Lenis combination is canonical in 2026. |
| Zustand or React Context for shared state | Module-level pub-sub is simpler, has zero deps, survives HMR cleanly, and we proved the pattern works in earlier iterations. Sticking with what's known to be reliable. |
| Aurora WebGL / glass / liquid-glass backgrounds | Rejected by user in phase 13c — *"absolute chaos"* — and the design intent here is "all focus on the speaker, no background distraction". |

---

## 5. Testing strategy

| Layer | What | Where |
|---|---|---|
| Unit | Pure helpers: dedup logic, slide-index math, color-from-speaker mapping | `frontend/lib/__tests__/*.test.ts` via Vitest |
| Component | `<Slide>`, `<Avatar>`, `<DotScrubber>` render correctness with mock state | `frontend/components/__tests__/*.test.tsx` via Vitest + Testing Library |
| Integration | Full debate replay against mock SSE stream — assert correct slide sequence, dedup, tally, verdict | `frontend/__tests__/e2e-mock.test.ts` |
| Visual | Playwright screenshots at 320 / 768 / 1280 / 1920 px wide of: landing, mid-debate, verdict, archive | `tests/web_visual/` (extends existing Python visual suite) |
| Accessibility | `prefers-reduced-motion` honored; keyboard navigation works; focus indicators visible | Playwright + axe-core |
| Backend regression | `uv run pytest` — 164 existing tests still pass (backend untouched) | CI |

Coverage threshold for the frontend Vitest suite: **≥ 85% lines** (matches the project-wide pytest threshold in pyproject.toml).

---

## 6. Edge cases

| Case | Handled by |
|---|---|
| SSE connection drops mid-debate | `EventSource.onerror` → `status = "error"`, show retry button (does NOT restart debate; user can resume scrubbing what's already loaded) |
| Backend returns 500 on `/api/debate/start` | Landing screen surfaces the error inline; START button re-enables |
| `n_pings = 1` (minimum) → 4 slides total | Slide-index math uses `slides.length`, no hardcoded 22 |
| Long body text (>800 chars) | `max-width: 65ch` + word-stagger; never overflows the slide |
| User scrolls past last slide before debate ends | Auto-follow re-engages on next message; otherwise scroll clamps at last slide |
| Two messages with same `msg_id` arrive (backend retry) | `seenIds` deduplicates; second one is dropped silently |
| `verdict` event arrives before all 20 message events (e.g. budget exhausted) | Verdict slide is appended regardless; the dot scrubber shrinks to match actual slide count |
| User opens two tabs to same debate ID | Each tab connects its own SSE; backend already broadcasts to all subscribers |
| Browser doesn't support `EventSource` (rare in 2026) | Detect at boot, show graceful fallback message ("Please use a modern browser") |

---

## 7. Compliance with project-wide rules

| Rule | Compliance |
|---|---|
| R1 SDK layer | N/A for frontend (backend untouched); the FastAPI endpoints in `src/agent_debate/web/` already wrap the Python SDK |
| R2 OOP / no duplication | TS classes / component composition; `<Slide>` factors out avatar + body for all 4 variants |
| R3 All external API via Gatekeeper | Frontend only calls our own `/api/debate/*` endpoints; backend's Gatekeeper class wraps the LLM and search calls |
| R4 Rate limits in JSON config | Backend already enforces; frontend has no LLM access |
| R5 Versioning | `frontend/package.json` `"version": "1.00"`; bump per change |
| R6 TDD | Vitest tests written alongside each component per the plan |
| R7 ≤150 lines per file | TS/TSX files capped at 150 effective lines; long components split into `slide.tsx`, `slide-pro.tsx`, etc. if needed |
| R8 ruff clean | ruff is Python-only; eslint + prettier handle TS |
| R9 ≥85% coverage | Vitest coverage threshold matches |
| R10 Zero hardcoded values | All tunables in `globals.css` custom properties or `frontend/lib/config.ts` |
| R11 Zero secrets | No secrets needed for this page; `.env.local` (containing only the unused React Bits Pro key) git-ignored |
| R12 uv only | Frontend uses npm — outside the uv scope (Python only). Documented in README. |
| R13 Continuous commits | Plan task-list has one commit per step |
| H-gates | H1-H11 are all backend properties; the frontend is purely a viewer for the backend's outputs |

---

## 8. Acceptance criteria (mirror of design spec §12, copied for grading-agent traceability)

1. ☐ Run `cd frontend && npm run dev`. Page loads at `localhost:3000` in <2s.
2. ☐ Landing screen visible — dark stage, futuristic fonts loaded, topic field + pings + Live toggle + START.
3. ☐ Click START → backend debate begins → Judge intro slide fades in within 1 second.
4. ☐ Each new SSE `message` produces a new slide that auto-scrolls into view smoothly (700ms).
5. ☐ Pro slides are anchored to the left 40%; Con slides to the right 40%; Judge slides centered.
6. ☐ Scroll wheel up / down moves through the timeline with smooth crossfades.
7. ☐ Mid-debate scroll-back triggers `JUMP TO LIVE` badge; clicking it resumes auto-follow.
8. ☐ After verdict + `done` event, the live badge hides; full timeline is scrubbable indefinitely.
9. ☐ Dot scrubber: hover shows tooltip with ping + role; click jumps to that slide.
10. ☐ Resize browser between 320px and 4K: layout remains coherent, no horizontal scroll, no broken text.
11. ☐ `prefers-reduced-motion: reduce`: all transitions ≤80ms, no scale or translate.
12. ☐ Lighthouse Performance ≥85 on the production build.
13. ☐ `uv run pytest` — all 164 backend tests still pass (backend untouched).
14. ☐ `cd frontend && npx vitest run` — all frontend tests pass with ≥85% line coverage.

---

## 9. Open questions (none blocking)

- Whether to add a "share replay" feature (URL with debate id → reloads the verdict + transcript). Out of scope for v1.00, easy follow-up.
- Whether to surface token-usage / spend in the bottom strip. Backend already emits `tokens_in/tokens_out` per message — could be a small `spend: 12k` chip. Deferred to v1.01 if reviewer wants it.

---

End of GUI PRD. Implementation plan: [`superpowers/plans/2026-05-26-hw2-gui-scroll-presentation.md`](superpowers/plans/2026-05-26-hw2-gui-scroll-presentation.md).
