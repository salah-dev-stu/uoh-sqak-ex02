import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { Slide } from "@/components/slide";
import type { Slide as SlideT } from "@/lib/types";

const baseSlide = (overrides: Partial<SlideT> = {}): SlideT => ({
  id: "m1", speaker: "pro", variant: "argument", pingIndex: 1,
  text: "Hello", timestamp: "2026-05-26T12:00:00Z", ...overrides,
});

describe("Slide", () => {
  it("renders Pro slide with left anchor class", () => {
    const { container } = render(<Slide slide={baseSlide()} index={0} isLatest={false} />);
    expect(container.querySelector('[data-anchor="left"]')).not.toBeNull();
  });

  it("renders Con slide with right anchor class", () => {
    const { container } = render(<Slide slide={baseSlide({ speaker: "con" })} index={0} isLatest={false} />);
    expect(container.querySelector('[data-anchor="right"]')).not.toBeNull();
  });

  it("renders Judge slide with center anchor class", () => {
    const { container } = render(<Slide slide={baseSlide({ speaker: "judge" })} index={0} isLatest={false} />);
    expect(container.querySelector('[data-anchor="center"]')).not.toBeNull();
  });

  it("renders verdict tally for verdict variant", () => {
    render(<Slide slide={baseSlide({
      speaker: "judge", variant: "verdict", proScore: 67, conScore: 73, outcome: "con_wins",
    })} index={0} isLatest={false} />);
    expect(screen.getByText("67")).toBeInTheDocument();
    expect(screen.getByText("73")).toBeInTheDocument();
    expect(screen.getByText(/CON WINS/i)).toBeInTheDocument();
  });
});
