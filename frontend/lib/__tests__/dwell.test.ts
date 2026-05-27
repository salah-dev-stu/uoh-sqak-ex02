import { describe, it, expect } from "vitest";
import { computeDwellMs } from "@/lib/dwell";

describe("computeDwellMs", () => {
  it("returns the minimum dwell for empty text", () => {
    expect(computeDwellMs("")).toBe(3500);
    expect(computeDwellMs("   ")).toBe(3500);
  });

  it("returns the minimum dwell for very short text", () => {
    // 1 word @ 130 wpm = ~462 ms + 800 ms = 1262 ms → clamped to 3500 ms.
    expect(computeDwellMs("Hello")).toBe(3500);
  });

  it("scales with word count between the bounds", () => {
    // 20 words @ 130 wpm = ~9230 ms + 800 ms = ~10030 ms, inside [3500, 14000].
    const text = Array.from({ length: 20 }, () => "word").join(" ");
    const ms = computeDwellMs(text);
    expect(ms).toBeGreaterThan(3500);
    expect(ms).toBeLessThan(14_000);
    expect(ms).toBeCloseTo(10_030, -2); // within 50 ms
  });

  it("caps at the maximum dwell for long text", () => {
    const text = Array.from({ length: 500 }, () => "word").join(" ");
    expect(computeDwellMs(text)).toBe(14_000);
  });

  it("ignores extra whitespace when counting words", () => {
    expect(computeDwellMs("a  b\tc\n  d")).toBe(computeDwellMs("a b c d"));
  });
});
