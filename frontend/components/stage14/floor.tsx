"use client";
import * as React from "react";

export function Floor(): React.JSX.Element {
  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none"
      style={{
        position: "absolute", left: 0, right: 0, bottom: 0,
        width: "100%", height: "50%", pointerEvents: "none",
      }}>
      <defs>
        <linearGradient id="floorGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="rgba(15,22,48,0)" />
          <stop offset="0.5" stopColor="rgba(15,22,48,0.6)" />
          <stop offset="1" stopColor="rgba(8,12,30,1)" />
        </linearGradient>
      </defs>
      <rect x="0" y="0" width="100" height="100" fill="url(#floorGrad)" />
      {Array.from({ length: 10 }, (_, i) => {
        const t = (i + 1) / 11;
        const x1 = 50 - t * 80;
        const x2 = 50 + t * 80;
        const y = t * 100;
        return (
          <line key={i} x1={x1} y1={y} x2={x2} y2={y}
            stroke="rgba(231,236,255,0.04)" strokeWidth="0.1" />
        );
      })}
      {Array.from({ length: 9 }, (_, i) => {
        const x = 10 + i * 10;
        return (
          <line key={i} x1="50" y1="0" x2={x} y2="100"
            stroke="rgba(231,236,255,0.035)" strokeWidth="0.1" />
        );
      })}
    </svg>
  );
}
