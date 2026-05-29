import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { Avatar } from "@/components/avatar";

describe("Avatar", () => {
  it("renders P glyph for Pro speaker", () => {
    render(<Avatar speaker="pro" pulse={false} />);
    expect(screen.getByText("P")).toBeInTheDocument();
  });

  it("renders C glyph for Con speaker", () => {
    render(<Avatar speaker="con" pulse={false} />);
    expect(screen.getByText("C")).toBeInTheDocument();
  });

  it("renders ⚖ glyph for Judge speaker", () => {
    render(<Avatar speaker="judge" pulse={false} />);
    expect(screen.getByText("⚖")).toBeInTheDocument();
  });
});
