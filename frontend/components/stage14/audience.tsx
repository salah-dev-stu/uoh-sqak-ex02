"use client";
import * as React from "react";

const HEADS = Array.from({ length: 32 }, (_, i) => ({
  x: i * 3.1 + (i % 3) * 0.6,
  y: 88 + (i % 4) * 1.5,
  r: 1 + (i % 3) * 0.2,
}));

export function Audience(): React.JSX.Element {
  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none"
      style={{
        position: "absolute", bottom: 0, left: 0, right: 0,
        width: "100%", height: "20%", pointerEvents: "none",
        filter: "blur(1.2px)", opacity: 0.45,
      }}>
      <rect x="0" y="92" width="100" height="8" fill="rgba(255,255,255,0.025)" />
      {HEADS.map((h, i) => (
        <circle key={i} cx={h.x} cy={h.y} r={h.r}
          fill="rgba(231,236,255,0.18)" />
      ))}
    </svg>
  );
}
