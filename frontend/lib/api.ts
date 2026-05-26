import { API_BASE } from "./config";
import type { StartDebateResponse } from "./types";

export async function startDebate(opts: { nPings: number; live: boolean }): Promise<StartDebateResponse> {
  const url = `${API_BASE}/api/debate/start?live=${opts.live ? 1 : 0}&n_pings=${opts.nPings}`;
  const r = await fetch(url, { method: "POST" });
  if (!r.ok) throw new Error(`startDebate failed: ${r.status}`);
  return r.json();
}

export async function stopDebate(id: string): Promise<void> {
  await fetch(`${API_BASE}/api/debate/${id}/stop`, { method: "POST" });
}

export function streamUrl(id: string): string {
  return `${API_BASE}/api/debate/${id}/stream`;
}
