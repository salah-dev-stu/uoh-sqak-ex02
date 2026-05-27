"use client";
import * as React from "react";
import { useEffect, useRef, useSyncExternalStore } from "react";
import { getState, subscribe, setState } from "@/lib/state";
import type { Slide } from "@/lib/types";
import { computeDwellMs } from "@/lib/dwell";
import { R3FScene } from "./r3f-scene";
import { TitleBanner } from "./title-banner";
import { JudgeChyron } from "./judge-chyron";

function useStoreState() {
  return useSyncExternalStore(subscribe, getState, getState);
}

function activeSlide(slides: Slide[], idx: number): Slide | null {
  if (slides.length === 0) return null;
  const clamped = Math.min(slides.length - 1, Math.max(0, idx));
  return slides[clamped];
}

export function Stage14(): React.JSX.Element {
  const state = useStoreState();
  const slide = activeSlide(state.slides, state.currentIndex);
  const activeSpeaker = slide?.speaker ?? null;

  // Auto-advance: while followLive is on, hold each slide for a dwell time
  // computed from its text length (see lib/dwell.ts — chunks read faster than
  // standalone slides). Effect deps are followLive + the CURRENT slide's id
  // + a hasNext boolean — NOT state.slides itself. If we depended on the
  // whole slides array, every new chunk append would clear the active timer
  // and restart it from zero, so the timer would never actually fire when
  // chunks arrive faster than the dwell duration. hasNext catches the
  // "we were stalled at the end, a new slide just arrived" transition.
  const currentSlide = state.slides[state.currentIndex];
  const slideId = currentSlide?.id;
  const slideText = currentSlide?.text ?? "";
  const hasNext = state.currentIndex < state.slides.length - 1;
  useEffect(() => {
    if (!state.followLive || !hasNext) return;
    const isChunk = /-c\d+$/.test(slideId ?? "");
    const dwell = computeDwellMs(slideText, { isChunk });
    const t = window.setTimeout(() => {
      const s = getState();
      if (!s.followLive) return;
      if (s.currentIndex < s.slides.length - 1) {
        setState({ currentIndex: s.currentIndex + 1 });
      }
    }, dwell);
    return () => window.clearTimeout(t);
  }, [state.followLive, slideId, slideText, hasNext]);

  // Wheel scroll = step between slides.
  const wheelLockRef = useRef(0);
  useEffect(() => {
    const onWheel = (e: WheelEvent): void => {
      if (state.slides.length === 0) return;
      const now = Date.now();
      if (now - wheelLockRef.current < 220) return;
      const dir = e.deltaY > 5 ? 1 : e.deltaY < -5 ? -1 : 0;
      if (dir === 0) return;
      e.preventDefault();
      wheelLockRef.current = now;
      const next = Math.min(state.slides.length - 1, Math.max(0, state.currentIndex + dir));
      if (next !== state.currentIndex) {
        const latest = state.slides.length - 1;
        setState({ currentIndex: next, followLive: next === latest });
      }
    };
    window.addEventListener("wheel", onWheel, { passive: false });
    return () => window.removeEventListener("wheel", onWheel);
  }, [state.slides.length, state.currentIndex]);

  return (
    <div style={{
      position: "fixed", inset: 0,
      width: "100vw", height: "100dvh",
      overflow: "hidden",
      background: "#050818",
    }}>
      <R3FScene activeSpeaker={activeSpeaker} />

      <TitleBanner />
      <JudgeChyron />

      <div style={{
        position: "absolute", inset: 0, pointerEvents: "none",
        background: "radial-gradient(ellipse at center 55%, transparent 35%, rgba(0,0,0,0.6) 100%)",
        zIndex: 4,
      }} />
    </div>
  );
}
