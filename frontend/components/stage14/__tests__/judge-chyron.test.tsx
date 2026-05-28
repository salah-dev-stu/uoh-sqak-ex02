import { render, screen } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import { JudgeChyron } from "@/components/stage14/judge-chyron";
import { resetState, appendSlide, setState } from "@/lib/state";

describe("JudgeChyron", () => {
  beforeEach(() => resetState());

  it("renders nothing when no slides exist", () => {
    const { container } = render(<JudgeChyron />);
    expect(container.firstChild).toBeNull();
  });

  it("renders nothing when active slide is not Judge", () => {
    appendSlide({
      id: "p1", speaker: "pro", variant: "argument", pingIndex: 1,
      text: "Pro argument here.", timestamp: "2026-05-27T00:00:00Z",
    });
    const { container } = render(<JudgeChyron />);
    expect(container.firstChild).toBeNull();
  });

  it("renders Judge intro text", () => {
    appendSlide({
      id: "j1", speaker: "judge", variant: "intro", pingIndex: 0,
      text: "Welcome to the debate.", timestamp: "2026-05-27T00:00:00Z",
    });
    render(<JudgeChyron />);
    expect(screen.getByText(/Welcome to the debate/)).toBeInTheDocument();
  });

  it("renders verdict outcome + rationale", () => {
    appendSlide({
      id: "verdict", speaker: "judge", variant: "verdict", pingIndex: 99,
      text: "", timestamp: "2026-05-27T00:00:00Z",
      proScore: 68, conScore: 55, outcome: "pro_wins",
      rationale: "Pro took it 68-55. Pro's edge was clarity (+3).",
    });
    setState({ currentIndex: 0 });
    render(<JudgeChyron />);
    expect(screen.getByText(/PRO WINS/)).toBeInTheDocument();
    expect(screen.getByText(/Pro took it 68-55/)).toBeInTheDocument();
    expect(screen.getByText("68")).toBeInTheDocument();
    expect(screen.getByText("55")).toBeInTheDocument();
  });

  it("renders aborted state in distinct color", () => {
    appendSlide({
      id: "verdict", speaker: "judge", variant: "verdict", pingIndex: 1,
      text: "Debate aborted: setup phase timed out.",
      timestamp: "2026-05-27T00:00:00Z",
      proScore: 0, conScore: 0, outcome: "debate_aborted",
    });
    render(<JudgeChyron />);
    expect(screen.getByText(/DEBATE ABORTED/)).toBeInTheDocument();
    expect(screen.getByText(/setup phase timed out/)).toBeInTheDocument();
  });
});
