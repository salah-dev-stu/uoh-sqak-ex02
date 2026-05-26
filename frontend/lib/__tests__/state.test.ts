import { describe, it, expect, beforeEach } from "vitest";
import { getState, setState, subscribe, appendSlide, resetState } from "@/lib/state";

describe("state store", () => {
  beforeEach(() => resetState());

  it("starts with empty slides and idle status", () => {
    const s = getState();
    expect(s.slides).toEqual([]);
    expect(s.status).toBe("idle");
    expect(s.followLive).toBe(true);
  });

  it("appendSlide adds a slide and notifies subscribers", () => {
    let notified = 0;
    subscribe(() => notified++);
    appendSlide({
      id: "m1", speaker: "pro", variant: "argument", pingIndex: 1,
      text: "Hello world", timestamp: "2026-05-26T12:00:00Z",
    });
    expect(getState().slides).toHaveLength(1);
    expect(notified).toBe(1);
  });

  it("setState merges partial updates", () => {
    setState({ status: "live", proTotal: 5 });
    expect(getState().status).toBe("live");
    expect(getState().proTotal).toBe(5);
  });
});
