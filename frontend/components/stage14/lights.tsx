"use client";
import * as React from "react";
import type { Speaker } from "@/lib/types";

interface Props {
  active: Speaker | null;
}

const POS: Record<Speaker, { x: number; tint: string }> = {
  pro:   { x: 18, tint: "rgba(255, 61, 168, 0.18)" },
  judge: { x: 50, tint: "rgba(255, 201, 76, 0.18)" },
  con:   { x: 82, tint: "rgba(61, 168, 255, 0.18)" },
};

export function Lights({ active }: Props): React.JSX.Element {
  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none"
      style={{
        position: "absolute", inset: 0, width: "100%", height: "100%",
        pointerEvents: "none", mixBlendMode: "screen",
      }}>
      <defs>
        {(["pro", "judge", "con"] as Speaker[]).map((s) => (
          <linearGradient key={s} id={`beam-${s}`} x1="0.5" y1="0" x2="0.5" y2="1">
            <stop offset="0" stopColor={POS[s].tint} stopOpacity={active === s ? 0.95 : 0.25} />
            <stop offset="0.5" stopColor={POS[s].tint} stopOpacity={active === s ? 0.45 : 0.12} />
            <stop offset="1" stopColor={POS[s].tint} stopOpacity="0" />
          </linearGradient>
        ))}
      </defs>
      {(["pro", "judge", "con"] as Speaker[]).map((s) => {
        const p = POS[s];
        const isActive = active === s;
        const wTop = isActive ? 4 : 3;
        const wBottom = isActive ? 28 : 22;
        return (
          <polygon key={s}
            points={`${p.x - wTop / 2},0 ${p.x + wTop / 2},0 ${p.x + wBottom / 2},75 ${p.x - wBottom / 2},75`}
            fill={`url(#beam-${s})`}
            style={{
              filter: isActive ? "blur(1.5px)" : "blur(2.5px)",
              transition: "all 600ms ease-out",
            }} />
        );
      })}
    </svg>
  );
}
