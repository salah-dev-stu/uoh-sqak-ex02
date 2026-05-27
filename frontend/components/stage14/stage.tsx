"use client";
import * as React from "react";
import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import { motion } from "motion/react";
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

function useCursorParallax(): { rx: number; ry: number } {
  const [p, setP] = useState({ rx: 0, ry: 0 });
  useEffect(() => {
    const onMove = (e: PointerEvent): void => {
      const dx = (e.clientX - window.innerWidth / 2) / window.innerWidth;
      const dy = (e.clientY - window.innerHeight / 2) / window.innerHeight;
      setP({ rx: -dy * 3, ry: dx * 3 });
    };
    window.addEventListener("pointermove", onMove);
    return () => window.removeEventListener("pointermove", onMove);
  }, []);
  return p;
}

export function Stage14(): React.JSX.Element {
  const state = useStoreState();
  const slide = activeSlide(state.slides, state.currentIndex);
  const activeSpeaker = slide?.speaker ?? null;
  const { rx, ry } = useCursorParallax();

  return (
    <div style={{
      position: "fixed", inset: 0,
      width: "100vw", height: "100dvh",
      overflow: "hidden",
      background: "#050818",
      perspective: "1600px",
      perspectiveOrigin: "50% 38%",
    }}>
      <motion.div
        animate={{ rotateX: rx, rotateY: ry }}
        transition={{ type: "spring", damping: 22, stiffness: 90 }}
        style={{
          position: "absolute", inset: 0,
          transformStyle: "preserve-3d",
        }}
      >
        <Backdrop topic={DEFAULT_TOPIC} />

        <div style={{
          position: "absolute", inset: 0,
          transform: "rotateX(28deg) translateZ(-200px) translateY(20%)",
          transformOrigin: "center bottom",
          transformStyle: "preserve-3d",
        }}>
          <Floor />
          <Audience />
        </div>

        <Lights active={activeSpeaker} />

        <div style={{
          position: "absolute", inset: 0,
          display: "grid",
          gridTemplateColumns: "1fr 1fr 1fr",
          alignItems: "end",
          padding: "0 2vw 6vh 2vw",
          gap: "1vw",
          transformStyle: "preserve-3d",
        }}>
          <div style={{
            display: "flex", justifyContent: "center", alignItems: "flex-end",
            transform: "translateZ(20px)",
          }}>
            <Podium speaker="pro" active={activeSpeaker === "pro"} />
          </div>
          <div style={{
            display: "flex", justifyContent: "center", alignItems: "flex-end",
            transform: "translateY(-4vh) translateZ(120px) scale(0.95)",
            transformOrigin: "bottom center",
          }}>
            <Podium speaker="judge" active={activeSpeaker === "judge"} />
          </div>
          <div style={{
            display: "flex", justifyContent: "center", alignItems: "flex-end",
            transform: "translateZ(20px)",
          }}>
            <Podium speaker="con" active={activeSpeaker === "con"} />
          </div>
        </div>

        <div style={{
          position: "absolute", inset: 0, pointerEvents: "none",
          background: "radial-gradient(ellipse at center 60%, transparent 38%, rgba(0,0,0,0.6) 100%)",
        }} />
      </motion.div>
    </div>
  );
}
