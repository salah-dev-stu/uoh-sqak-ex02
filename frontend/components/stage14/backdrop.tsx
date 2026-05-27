"use client";
import * as React from "react";

const STARS = Array.from({ length: 40 }, (_, i) => ({
  cx: (i * 47) % 100,
  cy: (i * 31) % 100,
  r: 0.15 + ((i * 7) % 5) * 0.05,
  o: 0.25 + ((i * 11) % 5) * 0.12,
}));

export function Backdrop({ topic }: { topic: string }): React.JSX.Element {
  return (
    <div style={{
      position: "absolute", inset: 0,
      background: "radial-gradient(ellipse at center top, #0a1024 0%, #050818 70%)",
      overflow: "hidden",
    }}>
      <svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid slice"
        style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}>
        {STARS.map((s, i) => (
          <circle key={i} cx={s.cx} cy={s.cy} r={s.r} fill="white" fillOpacity={s.o} />
        ))}
      </svg>
      <div style={{
        position: "absolute", top: "4vh", left: "50%", transform: "translateX(-50%)",
        textAlign: "center", maxWidth: "80vw",
      }}>
        <div style={{
          fontFamily: "var(--font-display)", letterSpacing: "0.2em", fontWeight: 600,
          color: "var(--color-judge-accent)", fontSize: "clamp(0.7rem, 0.4vw + 0.4rem, 0.9rem)",
          textTransform: "uppercase", marginBottom: "0.6rem",
        }}>AGENT DEBATE · 2026</div>
        <div style={{
          fontFamily: "var(--font-body)", color: "var(--color-fg-primary)", fontWeight: 300,
          fontSize: "clamp(0.85rem, 0.6vw + 0.5rem, 1.1rem)", lineHeight: 1.4, opacity: 0.7,
        }}>{topic}</div>
      </div>
    </div>
  );
}
