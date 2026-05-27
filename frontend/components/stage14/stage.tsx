"use client";
import * as React from "react";
import { useEffect, useRef, useSyncExternalStore } from "react";
import { getState, subscribe, setState } from "@/lib/state";
import type { Slide } from "@/lib/types";
import { R3FScene } from "./r3f-scene";

const DEFAULT_TOPIC = "Can AI agents create genuinely original art, or only remix human work?";

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

  // Auto-advance: when a new slide arrives and followLive is true, jump to it.
  const lastCountRef = useRef(state.slides.length);
  useEffect(() => {
    if (state.slides.length > lastCountRef.current && state.followLive) {
      setState({ currentIndex: state.slides.length - 1 });
    }
    lastCountRef.current = state.slides.length;
  }, [state.slides.length, state.followLive]);

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

      <div style={{
        position: "absolute", top: "3vh", left: "50%",
        transform: "translateX(-50%)",
        textAlign: "center", maxWidth: "80vw",
        pointerEvents: "none", zIndex: 5,
      }}>
        <div style={{
          fontFamily: "var(--font-display)", letterSpacing: "0.22em", fontWeight: 600,
          color: "var(--color-judge-accent)",
          fontSize: "clamp(0.7rem, 0.4vw + 0.4rem, 0.95rem)",
          textTransform: "uppercase", marginBottom: "0.6rem",
          textShadow: "0 0 18px rgba(255,201,76,0.4)",
        }}>AGENT DEBATE · 2026</div>
        <div style={{
          fontFamily: "var(--font-body)", color: "var(--color-fg-primary)",
          fontWeight: 300, opacity: 0.75,
          fontSize: "clamp(0.85rem, 0.6vw + 0.5rem, 1.1rem)", lineHeight: 1.4,
        }}>{DEFAULT_TOPIC}</div>
      </div>

      <div style={{
        position: "absolute", inset: 0, pointerEvents: "none",
        background: "radial-gradient(ellipse at center 55%, transparent 35%, rgba(0,0,0,0.6) 100%)",
        zIndex: 4,
      }} />
    </div>
  );
}
