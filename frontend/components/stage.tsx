"use client";
import * as React from "react";
import { useEffect, useRef, useSyncExternalStore } from "react";
import { motion } from "motion/react";
import { Slide } from "./slide";
import { getState, subscribe, setState } from "@/lib/state";
import type { Slide as SlideT } from "@/lib/types";

function useStoreState() {
  return useSyncExternalStore(subscribe, getState, getState);
}

interface ScrollSlideProps {
  slide: SlideT;
  index: number;
  currentIndex: number;
  isLatest: boolean;
}

function ScrollSlide({ slide, index, currentIndex, isLatest }: ScrollSlideProps): React.JSX.Element {
  const active = index === currentIndex;
  return (
    <motion.div
      animate={{ opacity: active ? 1 : 0, y: active ? 0 : 24 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      style={{
        position: "absolute", inset: 0,
        pointerEvents: active ? "auto" : "none",
      }}
    >
      <Slide slide={slide} index={index} isLatest={isLatest} />
    </motion.div>
  );
}

export function Stage(): React.JSX.Element {
  const state = useStoreState();
  const slidesCount = state.slides.length;

  const followLiveRef = useRef(state.followLive);
  const currentIndexRef = useRef(state.currentIndex);
  const slidesLenRef = useRef(slidesCount);
  followLiveRef.current = state.followLive;
  currentIndexRef.current = state.currentIndex;
  slidesLenRef.current = slidesCount;

  const debounceRef = useRef<number | null>(null);
  useEffect(() => {
    if (slidesCount === 0 || !state.followLive) return;
    if (debounceRef.current !== null) window.clearTimeout(debounceRef.current);
    debounceRef.current = window.setTimeout(() => {
      const target = (slidesCount - 1) * window.innerHeight;
      window.scrollTo({ top: target, behavior: "smooth" });
    }, 120);
    return () => {
      if (debounceRef.current !== null) window.clearTimeout(debounceRef.current);
    };
  }, [slidesCount, state.followLive]);

  useEffect(() => {
    let lastY = window.scrollY;
    const onScroll = (): void => {
      const scroll = window.scrollY;
      const userScrolledUp = scroll < lastY - 24;
      lastY = scroll;
      const idx = Math.min(
        slidesLenRef.current - 1,
        Math.max(0, Math.round(scroll / window.innerHeight)),
      );
      const latest = slidesLenRef.current - 1;
      if (userScrolledUp && idx < latest && followLiveRef.current) {
        setState({ followLive: false });
      }
      if (currentIndexRef.current !== idx) setState({ currentIndex: idx });
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  if (slidesCount === 0) {
    return (
      <div style={{
        height: "100vh", display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center", gap: "1.5rem",
      }}>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, ease: "linear", repeat: Infinity }}
          style={{
            width: 64, height: 64, borderRadius: "50%",
            border: "2px solid var(--color-fg-dim)",
            borderTopColor: "var(--color-judge-accent)",
          }}
        />
        <div style={{
          fontFamily: "var(--font-mono)", fontSize: "0.75rem",
          color: "var(--color-fg-muted)", textTransform: "uppercase",
          letterSpacing: "0.1em",
        }}>
          {state.status === "error"
            ? `Error: ${state.error ?? "unknown"}`
            : "Convening the debate — waiting for first response…"}
        </div>
      </div>
    );
  }

  // Clamp currentIndex (state may briefly lag behind slide arrival).
  const displayIndex = Math.min(slidesCount - 1, Math.max(0, state.currentIndex));

  return (
    <div style={{ height: `${slidesCount * 100}vh`, position: "relative" }}>
      <div style={{ position: "sticky", top: 0, height: "100vh", overflow: "hidden" }}>
        {state.slides.map((s, i) => (
          <ScrollSlide
            key={s.id}
            slide={s}
            index={i}
            currentIndex={displayIndex}
            isLatest={i === slidesCount - 1}
          />
        ))}
      </div>
    </div>
  );
}
