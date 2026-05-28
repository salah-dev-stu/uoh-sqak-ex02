"use client";
import * as React from "react";
import { useSyncExternalStore, useMemo } from "react";
import { getState, subscribe, setState } from "@/lib/state";
import type { Slide, Speaker } from "@/lib/types";

function useStoreState() { return useSyncExternalStore(subscribe, getState, getState); }

interface Group { startIdx: number; endIdx: number; speaker: Speaker; count: number }

function groupSlides(slides: Slide[]): Group[] {
  const out: Group[] = [];
  for (let i = 0; i < slides.length; i++) {
    const last = out[out.length - 1];
    if (last && last.speaker === slides[i].speaker) {
      last.endIdx = i;
      last.count += 1;
    } else {
      out.push({ startIdx: i, endIdx: i, speaker: slides[i].speaker, count: 1 });
    }
  }
  return out;
}

export function BottomStrip(): React.JSX.Element {
  const s = useStoreState();
  const groups = useMemo(() => groupSlides(s.slides), [s.slides]);
  if (s.slides.length === 0) return <></>;

  function jumpToLive(): void {
    setState({ currentIndex: s.slides.length - 1, followLive: true });
  }
  function jumpTo(i: number): void {
    setState({ currentIndex: i, followLive: false });
  }

  const activeGroupIdx = groups.findIndex(g => s.currentIndex >= g.startIdx && s.currentIndex <= g.endIdx);

  return (
    <div style={{
      position: "fixed", bottom: 0, left: 0, right: 0, padding: "1rem 1.5rem",
      display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem",
      fontFamily: "var(--font-mono)", fontSize: "0.7rem", letterSpacing: "0.05em",
      color: "var(--color-fg-muted)", background: "linear-gradient(to top, rgb(7 7 10 / 0.95), transparent)",
      pointerEvents: "auto", zIndex: 50,
    }}>
      <div>
        <span style={{ color: "var(--color-pro-accent)" }}>Pro {s.proTotal}</span>
        {" · "}
        <span style={{ color: "var(--color-con-accent)" }}>Con {s.conTotal}</span>
      </div>
      <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
        {groups.slice(0, Math.max(0, activeGroupIdx + 1)).map((g, gi) => {
          const color = `var(--color-${g.speaker}-accent)`;
          const glow = `var(--color-${g.speaker}-glow)`;
          const active = gi === activeGroupIdx;
          // Only render past + active turns. Future (already-received but
          // not-yet-displayed) chunks are intentionally hidden from the
          // strip so the dot count matches what the viewer has actually
          // seen on-stage — the LLM may be 1-2 turns ahead of the dwell.
          const dotH = active ? 11 : 9;
          const dotW = g.count === 1 ? dotH : dotH + (g.count - 1) * 7;
          return (
            <button
              key={`${g.startIdx}-${g.speaker}`}
              onClick={() => jumpTo(g.startIdx)}
              title={`${g.speaker} · ${g.count} ${g.count === 1 ? "bubble" : "bubbles"} · slides ${g.startIdx + 1}${g.count > 1 ? `–${g.endIdx + 1}` : ""} ${active ? "(now)" : "(seen)"}`}
              style={{
                width: dotW, height: dotH, borderRadius: dotH / 2,
                background: color, border: "none", padding: 0, cursor: "pointer",
                opacity: active ? 1 : 0.85, transition: "all 0.25s ease",
                boxShadow: active ? `0 0 10px ${glow}` : "none",
              }} />
          );
        })}
      </div>
      <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
        <span>turn {(activeGroupIdx < 0 ? 0 : activeGroupIdx) + 1}/{groups.length}</span>
        {s.status === "live" && (
          s.followLive ? (
            <span style={{ color: "var(--color-pro-accent)" }}>◉ LIVE</span>
          ) : (
            <button onClick={jumpToLive} style={{
              background: "transparent", border: "1px solid var(--color-pro-accent)",
              color: "var(--color-pro-accent)", padding: "0.25rem 0.5rem", borderRadius: 4,
              fontFamily: "var(--font-mono)", fontSize: "0.7rem", cursor: "pointer",
              letterSpacing: "0.05em", textTransform: "uppercase",
            }}>◉ Jump to live</button>
          )
        )}
      </div>
    </div>
  );
}
