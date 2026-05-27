"use client";
import * as React from "react";
import { useSyncExternalStore } from "react";
import { getState, subscribe } from "@/lib/state";
import type { Slide } from "@/lib/types";
import { Backdrop } from "./backdrop";
import { Floor } from "./floor";
import { Lights } from "./lights";
import { Podium } from "./podium";
import { Audience } from "./audience";

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

  return (
    <div style={{
      position: "fixed", inset: 0,
      width: "100vw", height: "100dvh",
      overflow: "hidden",
      background: "#050818",
    }}>
      <Backdrop topic={DEFAULT_TOPIC} />
      <Floor />
      <Audience />
      <Lights active={activeSpeaker} />

      <div style={{
        position: "absolute", inset: 0,
        display: "grid",
        gridTemplateColumns: "1fr 1fr 1fr",
        alignItems: "end",
        padding: "0 3vw 10vh 3vw",
        gap: "2vw",
      }}>
        <div style={{ display: "flex", justifyContent: "center", alignItems: "flex-end" }}>
          <Podium speaker="pro" active={activeSpeaker === "pro"} />
        </div>
        <div style={{
          display: "flex", justifyContent: "center", alignItems: "flex-end",
          transform: "translateY(-3vh) scale(0.92)",
          transformOrigin: "bottom center",
        }}>
          <Podium speaker="judge" active={activeSpeaker === "judge"} />
        </div>
        <div style={{ display: "flex", justifyContent: "center", alignItems: "flex-end" }}>
          <Podium speaker="con" active={activeSpeaker === "con"} />
        </div>
      </div>

      <div style={{
        position: "absolute", inset: 0, pointerEvents: "none",
        background: "radial-gradient(ellipse at center 60%, transparent 40%, rgba(0,0,0,0.55) 100%)",
      }} />
    </div>
  );
}
