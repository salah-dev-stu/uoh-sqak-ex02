"use client";
import * as React from "react";
import { useSyncExternalStore } from "react";
import { StartScreen } from "@/components/start-screen";
import { Stage } from "@/components/stage";
import { BottomStrip } from "@/components/bottom-strip";
import { getState, subscribe } from "@/lib/state";

function useStoreState() { return useSyncExternalStore(subscribe, getState, getState); }

export default function Page(): React.JSX.Element {
  const s = useStoreState();
  return (
    <main style={{ position: "relative" }}>
      {s.status === "idle" ? <StartScreen /> : <Stage />}
      {s.slides.length > 0 && <BottomStrip />}
    </main>
  );
}
