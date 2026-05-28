import { render, screen } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import { TitleBanner } from "@/components/stage14/title-banner";
import { resetState, setState } from "@/lib/state";

describe("TitleBanner", () => {
  beforeEach(() => resetState());

  it("renders the AGENT DEBATE title", () => {
    render(<TitleBanner />);
    expect(screen.getByText("AGENT DEBATE")).toBeInTheDocument();
  });

  it("shows STANDBY when status is idle", () => {
    render(<TitleBanner />);
    expect(screen.getByText(/Standby/i)).toBeInTheDocument();
  });

  it("shows ON AIR when status is live", () => {
    setState({ status: "live" });
    render(<TitleBanner />);
    expect(screen.getByText(/On Air/i)).toBeInTheDocument();
  });

  it("shows Recorded when status is done", () => {
    setState({ status: "done" });
    render(<TitleBanner />);
    expect(screen.getByText(/Recorded/i)).toBeInTheDocument();
  });

  it("renders the topic from state", () => {
    setState({ topic: "Test motion topic" });
    render(<TitleBanner />);
    expect(screen.getByText(/Test motion topic/)).toBeInTheDocument();
  });

  it("falls back to default topic when state.topic is unset", () => {
    render(<TitleBanner />);
    // Fallback constant should be visible
    expect(screen.getByText(/genuinely original art/i)).toBeInTheDocument();
  });
});
