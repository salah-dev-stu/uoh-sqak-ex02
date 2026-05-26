import { describe, it, expect } from "vitest";
import { shouldSkip } from "@/lib/sse";

describe("SSE dedup logic", () => {
  it("skips messages with no msg_id (boot directive)", () => {
    expect(shouldSkip({ phase: "boot", directive: "setup" }, new Set())).toBe(true);
  });

  it("skips duplicate msg_ids", () => {
    const seen = new Set(["m1"]);
    expect(shouldSkip({ msg_id: "m1", from: "judge", to: "pro" }, seen)).toBe(true);
  });

  it("skips forwarded pro/con messages routed to opponent", () => {
    expect(shouldSkip({ msg_id: "m1", from: "pro", to: "con" }, new Set())).toBe(true);
    expect(shouldSkip({ msg_id: "m2", from: "con", to: "pro" }, new Set())).toBe(true);
  });

  it("keeps judge-originated and judge-targeted messages", () => {
    expect(shouldSkip({ msg_id: "m3", from: "pro", to: "judge" }, new Set())).toBe(false);
    expect(shouldSkip({ msg_id: "m4", from: "judge", to: "pro" }, new Set())).toBe(false);
  });
});
