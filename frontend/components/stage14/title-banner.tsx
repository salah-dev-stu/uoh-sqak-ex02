"use client";
import * as React from "react";
import { useSyncExternalStore } from "react";
import { motion } from "motion/react";
import { getState, subscribe } from "@/lib/state";

function useStoreState() {
  return useSyncExternalStore(subscribe, getState, getState);
}

export function TitleBanner(): React.JSX.Element {
  const s = useStoreState();
  const isLive = s.status === "live";

  return (
    <div style={{
      position: "fixed", top: 0, left: 0, right: 0,
      zIndex: 25, padding: "1.1rem 2rem 0.85rem",
      pointerEvents: "none",
      background: "linear-gradient(180deg, rgba(7,11,26,0.85) 0%, rgba(7,11,26,0.5) 60%, transparent 100%)",
    }}>
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "center",
        gap: "1.5rem", maxWidth: "900px", margin: "0 auto",
      }}>
        <div style={{
          flex: 1, height: "1px",
          background: "linear-gradient(90deg, transparent, var(--color-judge-accent) 75%)",
          maxWidth: "260px", opacity: 0.7,
        }} />

        <motion.div
          initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          style={{ textAlign: "center", minWidth: "10rem" }}>
          <div style={{
            fontFamily: "var(--font-display)",
            fontSize: "clamp(0.95rem, 0.75vw + 0.4rem, 1.45rem)",
            letterSpacing: "0.35em", fontWeight: 700,
            color: "var(--color-judge-accent)",
            textShadow: "0 0 22px rgba(255,201,76,0.45)",
          }}>AGENT DEBATE</div>
          <div style={{
            display: "flex", justifyContent: "center", alignItems: "center", gap: "0.6rem",
            fontFamily: "var(--font-mono)", fontSize: "0.6rem",
            letterSpacing: "0.45em", color: "var(--color-fg-muted)",
            marginTop: "0.3rem", textTransform: "uppercase",
          }}>
            <span>2026</span>
            <span style={{ opacity: 0.4 }}>·</span>
            <span style={{
              display: "inline-flex", alignItems: "center", gap: "0.3rem",
              color: isLive ? "var(--color-pro-accent)" : "var(--color-fg-muted)",
            }}>
              {isLive && (
                <motion.span
                  animate={{ opacity: [1, 0.3, 1] }}
                  transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut" }}
                  style={{
                    width: "6px", height: "6px", borderRadius: "50%",
                    background: "var(--color-pro-accent)",
                    boxShadow: "0 0 8px var(--color-pro-glow)",
                  }}
                />
              )}
              {isLive ? "On Air" : s.status === "done" ? "Recorded" : "Standby"}
            </span>
          </div>
        </motion.div>

        <div style={{
          flex: 1, height: "1px",
          background: "linear-gradient(90deg, var(--color-judge-accent) 25%, transparent)",
          maxWidth: "260px", opacity: 0.7,
        }} />
      </div>
    </div>
  );
}
