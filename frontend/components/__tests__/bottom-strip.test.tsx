import { render, screen } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import { BottomStrip } from "@/components/bottom-strip";
import { setState, resetState, appendSlide } from "@/lib/state";

describe("BottomStrip", () => {
  beforeEach(() => resetState());

  it("shows running tally", () => {
    setState({ proTotal: 12, conTotal: 8, status: "live" });
    appendSlide({ id: "m1", speaker: "pro", variant: "argument", pingIndex: 1, text: "x", timestamp: "" });
    render(<BottomStrip />);
    expect(screen.getByText(/Pro 12/)).toBeInTheDocument();
    expect(screen.getByText(/Con 8/)).toBeInTheDocument();
  });

  it("renders LIVE badge when status is live and followLive", () => {
    setState({ status: "live", followLive: true });
    appendSlide({ id: "m1", speaker: "pro", variant: "argument", pingIndex: 1, text: "x", timestamp: "" });
    render(<BottomStrip />);
    expect(screen.getByText(/LIVE/i)).toBeInTheDocument();
  });

  it("renders JUMP TO LIVE when scrolled away from latest", () => {
    setState({ status: "live", followLive: false });
    appendSlide({ id: "m1", speaker: "pro", variant: "argument", pingIndex: 1, text: "x", timestamp: "" });
    render(<BottomStrip />);
    expect(screen.getByText(/JUMP TO LIVE/i)).toBeInTheDocument();
  });
});
