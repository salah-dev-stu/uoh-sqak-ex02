"use client";
import * as React from "react";
import { useEffect, useRef, useSyncExternalStore } from "react";
import { Stage14 } from "@/components/stage14/stage";
import { BottomStrip } from "@/components/bottom-strip";
import { getState, subscribe, setState } from "@/lib/state";
import { startDebate } from "@/lib/api";
import { openStream } from "@/lib/sse";
import { DEFAULT_N_PINGS } from "@/lib/config";

const DEFAULT_TOPIC = "Can AI agents create genuinely original art, or only remix human work?";

function useStoreState() {
  return useSyncExternalStore(subscribe, getState, getState);
}

export default function Page(): React.JSX.Element {
  const s = useStoreState();

  const firedRef = useRef(false);
  useEffect(() => {
    if (firedRef.current) return;
    firedRef.current = true;
    if (getState().status !== "idle") return;

    (async () => {
      try {
        const r = await startDebate({ nPings: DEFAULT_N_PINGS, live: true });
        openStream(r.debate_id, DEFAULT_TOPIC);
      } catch (e) {
        setState({
          status: "error",
          error: e instanceof Error ? e.message : "Failed to start debate",
        });
      }
    })();
  }, []);

  return (
    <main style={{ position: "relative" }}>
      <Stage14 />
      {s.slides.length > 0 && <BottomStrip />}
    </main>
  );
}
