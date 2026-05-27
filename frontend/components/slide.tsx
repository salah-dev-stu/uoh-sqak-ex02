"use client";
import * as React from "react";
import { Avatar } from "./avatar";
import { WordReveal } from "./word-reveal";
import type { Slide as SlideT, Speaker } from "@/lib/types";

const ANCHOR: Record<Speaker, "left" | "right" | "center"> = {
  pro: "left", con: "right", judge: "center",
};

const NAME: Record<Speaker, string> = { pro: "PRO", con: "CON", judge: "JUDGE" };

interface Props { slide: SlideT; index: number; isLatest: boolean; }

export function Slide({ slide, isLatest }: Props): React.JSX.Element {
  const anchor = ANCHOR[slide.speaker];
  const justify = anchor === "left" ? "flex-start" : anchor === "right" ? "flex-end" : "center";
  const align = anchor === "left" ? "items-start" : anchor === "right" ? "items-end" : "items-center";
  const textAlign = anchor === "right" ? "right" : "left";

  return (
    <div data-anchor={anchor} style={{
      width: "100%", height: "100dvh", display: "flex",
      justifyContent: justify, alignItems: "center",
      padding: "4vh 6vw 96px", overflow: "hidden",
    }}>
      <div className={`flex flex-col ${align}`} style={{
        maxWidth: "62ch", textAlign, gap: "0.9rem",
        maxHeight: "calc(100dvh - 8vh - 96px)",
        overflowY: "auto", overflowX: "hidden",
      }}>
        <Avatar speaker={slide.speaker} pulse={isLatest} />
        <div style={{
          fontFamily: "var(--font-display)", fontSize: "clamp(1.25rem, 1.4vw + 0.5rem, 1.75rem)",
          letterSpacing: "0.08em", fontWeight: 500,
          color: `var(--color-${slide.speaker}-accent)`,
        }}>{NAME[slide.speaker]}</div>
        <div style={{
          fontFamily: "var(--font-mono)", fontSize: "0.7rem", letterSpacing: "0.05em",
          color: "var(--color-fg-muted)", textTransform: "uppercase",
        }}>{slide.variant} · ping {slide.pingIndex} · {new Date(slide.timestamp).toLocaleTimeString()}</div>
        {slide.variant === "verdict" ? (
          <div className="flex flex-col gap-4">
            <div style={{ fontFamily: "var(--font-mono)", fontSize: "1.5rem" }}>
              <span style={{ color: "var(--color-pro-accent)" }}>{slide.proScore}</span>
              {" · "}
              <span style={{ color: "var(--color-con-accent)" }}>{slide.conScore}</span>
            </div>
            <div style={{
              fontFamily: "var(--font-display)", fontSize: "2rem", letterSpacing: "0.08em",
              color: "var(--color-fg-primary)",
            }}>{(slide.outcome ?? "").replace(/_/g, " ").toUpperCase()}</div>
          </div>
        ) : (
          <WordReveal text={slide.text} trigger={isLatest || slide.text.length > 0} />
        )}
      </div>
    </div>
  );
}
