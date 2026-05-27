"use client";
import * as React from "react";
import { useSyncExternalStore } from "react";
import { getState, subscribe, setState } from "@/lib/state";

function useStoreState() { return useSyncExternalStore(subscribe, getState, getState); }

export function BottomStrip(): React.JSX.Element {
  const s = useStoreState();
  if (s.slides.length === 0) return <></>;

  function jumpToLive(): void {
    setState({ currentIndex: s.slides.length - 1, followLive: true });
  }
  function jumpTo(i: number): void {
    setState({ currentIndex: i, followLive: false });
  }

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
      <div style={{ display: "flex", gap: 4 }}>
        {s.slides.map((slide, i) => {
          const color = `var(--color-${slide.speaker}-accent)`;
          const active = i === s.currentIndex;
          return (
            <button key={slide.id} onClick={() => jumpTo(i)} title={`${slide.speaker} · ${slide.variant} · ping ${slide.pingIndex}`}
              style={{
                width: active ? 12 : 8, height: active ? 12 : 8, borderRadius: "50%",
                background: color, border: "none", padding: 0, cursor: "pointer",
                opacity: active ? 1 : 0.55, transition: "all 0.2s",
              }} />
          );
        })}
      </div>
      <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
        <span>ping {s.currentIndex + 1}/{s.slides.length}</span>
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
