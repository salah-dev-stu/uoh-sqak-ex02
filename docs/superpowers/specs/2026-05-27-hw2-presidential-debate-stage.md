# Phase 14 — Presidential Debate Stage (Design Spec)

**Date:** 2026-05-27
**Branch:** `phase14-presidential-stage`
**Status:** Approved in conversation; ready to implement on branch
**Time-box:** 4 hours; if not converging, branch is dropped and `main` (commit `bc91e78`) ships as-is for HW2 Friday deadline

## 1. Vision

Replace the current "one fullscreen slide per turn" presentation with a single **persistent presidential debate stage** that stays on screen for the whole debate. Camera moves between the three positions (Pro podium left, Judge moderator desk centre-front, Con podium right) and the active speaker is spotlit. Arguments stream as a **TV-style chyron caption** at the bottom of the screen. Verdict reveal triggers a fireworks burst.

Inspired by US presidential debates — two podiums, dark navy backdrop, moderator desk in front, faint audience silhouettes in the rear, theatrical stage lighting.

## 2. Layout

```
                  ╔══════════════════════════════════╗
                  ║      "AGENT DEBATE — 2026"       ║
                  ║   [topic text on LED backdrop]    ║
                  ╚══════════════════════════════════╝
                  (dark navy gradient, faint stars)

    ┌─────┐                                       ┌─────┐
    │  P  │                                       │  C  │
    │ ╱│╲ │                                       │ ╱│╲ │
   ▕▏podium▕▏                                    ▕▏podium▕▏
   (magenta accent)                              (cyan accent)
                          ┌─────┐
                          │  ⚖  │
                          │ ╱│╲ │
                          └─────┘
                       moderator desk
                       (gold accent)
   ═════════════════════════════════════════════════════════
        ░░░░░░░░░░░░  audience silhouettes  ░░░░░░░░░░░░
        (very faint, blurred row of head outlines)

   ┌────────────────────────────────────────────────────────┐
   │ PRO · ARGUMENT · PING 1                                │
   │ "AI=ORIGINALITY ready. Generative systems reach beyond │
   │  the seed corpus by recombining latent patterns…"      │
   └────────────────────────────────────────────────────────┘
                          chyron caption
```

## 3. Components (file map)

```
frontend/components/stage14/
├── stage.tsx              # outer stage container (replaces components/stage.tsx wiring)
├── backdrop.tsx           # dark navy gradient + faint stars + topic banner
├── podium.tsx             # parametrised podium (speaker prop drives colour + glyph)
├── moderator-desk.tsx     # judge's central desk
├── audience.tsx           # row of blurred silhouettes in the rear
├── spotlight.tsx          # cone-of-light overlay following active speaker
├── chyron.tsx             # bottom caption strip with current speaker + text
├── camera.tsx             # wraps the stage; applies scale + translate per active speaker
└── fireworks.tsx          # tsParticles confetti + fireworks for verdict
```

The existing `components/stage.tsx` keeps its scroll-driven plumbing — only the rendered children change. SSE pipeline (`lib/sse.ts`), state store (`lib/state.ts`), and bottom strip stay untouched.

## 4. Behaviour

### 4.1 Idle (before debate starts)
- Empty stage rendered with all three positions visible
- Slight floor reflection beneath each podium
- "AGENT DEBATE" banner glows softly
- Audience silhouettes have a subtle drift animation

### 4.2 Per turn (Pro/Con/Judge speaks)
- Camera **scales 1.0 → 1.15** with a small `translateX` toward the active speaker (300ms ease-out)
- Active podium **brightens to full**; the other two dim to ~30%
- Active podium's spotlight cone appears overhead (CSS conic-gradient + blur)
- Chyron at the bottom **slides up from below**, animates the text in word-by-word for the first ~1.5s, then stays static
- 800ms total transition between speakers

### 4.3 Verdict
- Camera **pulls back to full wide shot** (1.0x, no translate)
- Judge avatar **"stands up"** — y-translate animation of 10-15px with a slight scale 1.0 → 1.05
- Centre-stage text reveal: `"PRO WINS"` or `"CON WINS"` in large display font, slow fade-in over 600ms
- Tally below: `67 · 73` in JetBrains Mono
- `tsParticles` fires confetti + fireworks bursts from the **winner's podium** for 3-4 seconds
- Winner's podium light brightens further; loser's fades

### 4.4 Reduced-motion fallback
- `prefers-reduced-motion: reduce` collapses all transitions to ≤80ms
- Fireworks become a single instant burst, not animated
- Camera does not move; only the spotlight indicates active speaker

## 5. Visual tokens (extend `globals.css`)

```css
--stage-bg-near:  #0a1024;        /* near-black navy */
--stage-bg-far:   #050818;        /* deeper navy at edges */
--stage-light:    #e7ecff;        /* spotlight near-white */
--stage-glow:     rgb(231 236 255 / 0.18);
--podium-pro:     var(--color-pro-accent);
--podium-con:     var(--color-con-accent);
--podium-judge:   var(--color-judge-accent);
--audience-tint:  rgb(255 255 255 / 0.04);
```

## 6. Tech

- Pure CSS + SVG + Framer Motion + `tsParticles/confetti` (~7KB)
- **No Three.js**, no 3D, no AI lip sync, no extra API keys
- SVG silhouettes drawn inline (~50 lines each) — head = circle, torso = simple path, arms = two paths
- Spotlight = CSS conic-gradient with `filter: blur(40px)` and `mix-blend-mode: screen`
- Camera = single transform on the stage container

## 7. Acceptance criteria

1. ☐ Stage renders the three positions visibly at 1280px, 1440px, and 1920px widths
2. ☐ At ≤768px viewport, layout collapses gracefully (positions stack vertically, or chyron expands to full)
3. ☐ Active-speaker spotlight + dimming of others is perceptible
4. ☐ Camera transition between Pro and Con turns is smooth (no layout shifts, no blur on text)
5. ☐ Chyron animates argument text in real time as SSE delivers it
6. ☐ Verdict triggers visible fireworks
7. ☐ `prefers-reduced-motion: reduce` collapses everything to ≤80ms
8. ☐ All 17 existing frontend tests still pass
9. ☐ `cd frontend && npx tsc --noEmit` clean
10. ☐ ≤150 effective lines per file (the existing pre-commit hook applies to TS too — we should respect it)

## 8. Time-box & exit criteria

| Hour | Goal |
|---|---|
| 0-1 | Backdrop + 2 podiums + judge desk rendered statically. Audience silhouettes in. |
| 1-2 | Spotlight overlay following active speaker; podium dimming. |
| 2-3 | Chyron caption pipeline wired to SSE; camera zoom transitions. |
| 3-4 | Verdict animation + fireworks; visual polish + regression test. |

**If at hour 4 the stage doesn't look right or there are layout regressions:** abandon the branch, switch back to `main`. HW2 submits with the current Phase 13g viewer. The stage becomes a portfolio project for after Friday.

## 9. Out of scope

- AI talking-head lip sync (Tier C in brainstorm — too expensive for the deadline)
- 3D models (Three.js, Ready Player Me)
- Real-time text-to-speech audio
- Camera rotations / orbits / parallax
- Animated audience reactions (clapping, head nods)

## 10. Brainstorm references kept for the next iteration

- Ready Player Me 2D PNG export for richer character portraits (after submission)
- Convai SDK for the future "actually talks" version
- TalkingHead.js for the future 3D version
- Wawa Sensei tutorial as the canonical walkthrough for the 3D upgrade path
