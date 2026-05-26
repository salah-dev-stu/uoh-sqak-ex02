import type { Slide, SlideState } from "./types";

const initial: SlideState = {
  slides: [],
  currentIndex: 0,
  followLive: true,
  status: "idle",
  proTotal: 0,
  conTotal: 0,
  pingCounter: { current: 0, total: 22 },
};

let state: SlideState = { ...initial };
const listeners = new Set<() => void>();

export function getState(): SlideState { return state; }

export function setState(patch: Partial<SlideState>): void {
  state = { ...state, ...patch };
  listeners.forEach((l) => l());
}

export function appendSlide(slide: Slide): void {
  state = { ...state, slides: [...state.slides, slide] };
  listeners.forEach((l) => l());
}

export function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function resetState(): void {
  state = { ...initial };
  listeners.forEach((l) => l());
}
