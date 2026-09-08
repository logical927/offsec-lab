import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { LabWorkspace } from "@/components/lab/LabWorkspace";
import { MissionBriefing } from "@/components/mission/MissionBriefing";
import type { MissionDetail } from "@/lib/api/client";

// Mock only the HTTP boundary: the real API client and response handling run.
const mission: MissionDetail = {
  id: 1, slug: "fixture", title: "Recon fixture", description: "Observe the target.", sort_order: 1,
  learning_explanation: "Interpret evidence before drawing conclusions.",
  challenges: [{ id: 10, slug: "finding", title: "Finding", description: "Record a finding.", sort_order: 1,
    hints: [1, 2, 3].map(level => ({ id: level, level, content: `Fixture hint ${level}` })) }],
};
let completed: boolean;
let running: boolean;
let failAnswer: boolean;
let requests: { path: string; method: string; body: unknown }[];
beforeEach(() => {
  completed = false; running = false; failAnswer = false; requests = [];
  HTMLDialogElement.prototype.showModal = function () { this.setAttribute("open", ""); };
  HTMLDialogElement.prototype.close = function () { this.removeAttribute("open"); };
  vi.stubGlobal("fetch", vi.fn(async (path: string, init: RequestInit) => {
    const body = init.body ? JSON.parse(String(init.body)) : undefined;
    requests.push({ path, method: init.method!, body });
    if (path === "/api/v1/missions/1") return Response.json(mission);
    if (path === "/api/v1/missions") return Response.json([mission]);
    if (path === "/api/v1/progress") return Response.json({ missions: [{ mission_id: 1,
      status: completed ? "COMPLETED" : "NOT_STARTED",
      challenges: [{ challenge_id: 10, status: completed ? "COMPLETED" : "AVAILABLE" }] }] });
    if (path === "/api/v1/labs/1/status") return Response.json({ mission_id: 1,
      status: running ? "RUNNING" : "STOPPED", target: running ? { hostname: "fixture-target", ip: "192.0.2.10" } : null });
    if (["start", "stop", "reset"].some(action => path === `/api/v1/labs/1/${action}`)) {
      running = !path.endsWith("/stop");
      return Response.json({ mission_id: 1, status: running ? "running" : "stopped" });
    }
    if (path === "/api/v1/challenges/10/answers") {
      if (failAnswer) return Response.json({ error: { message: "private host details" } }, { status: 503 });
      completed = body.answer === "fixture observation";
      return Response.json({ correct: completed, status: completed ? "COMPLETED" : "AVAILABLE",
        next_challenge_id: null, mission_status: completed ? "COMPLETED" : "NOT_STARTED" });
    }
    throw new Error(`Unexpected request: ${path}`);
  }));
});
afterEach(() => vi.unstubAllGlobals());

it("loads a briefing through the real API client and links to the workspace", async () => {
  render(<MissionBriefing missionId={1} />);
  expect(await screen.findByRole("heading", { name: mission.title })).toBeVisible();
  expect(screen.getByRole("link", { name: /Lab/ })).toHaveAttribute("href", "/missions/1/lab");
  expect(requests).toContainEqual({ path: "/api/v1/missions/1", method: "GET", body: undefined });
});

it("connects lab actions, hints, wrong/correct answers and completion through fetch", async () => {
  render(<LabWorkspace missionId={1} />);
  await screen.findByText("STOPPED");
  fireEvent.click(screen.getByRole("button", { name: "Start Lab" }));
  await screen.findByText("RUNNING");
  for (let level = 1; level <= 3; level++) {
    fireEvent.click(screen.getByRole("button", { name: `Hint ${level} — AVAILABLE` }));
    expect(screen.getByText(`Fixture hint ${level}`)).toBeVisible();
  }
  fireEvent.change(screen.getByRole("textbox"), { target: { value: "wrong" } });
  fireEvent.click(screen.getByRole("button", { name: "Submit Answer" }));
  await screen.findByText(/INCORRECT/);
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  fireEvent.change(screen.getByRole("textbox"), { target: { value: "fixture observation" } });
  fireEvent.click(screen.getByRole("button", { name: "Submit Answer" }));
  expect(await screen.findByRole("dialog", { name: "Mission Complete" })).toBeVisible();
  expect(screen.getByText(mission.learning_explanation!)).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: "Return to Workspace" }));
  fireEvent.click(screen.getByRole("button", { name: "Reset Lab" }));
  fireEvent.click(screen.getByRole("button", { name: "Confirm Reset" }));
  await waitFor(() => expect(screen.getByRole("button", { name: "Stop Lab" })).toBeEnabled());
  fireEvent.click(screen.getByRole("button", { name: "Stop Lab" }));
  await screen.findByText("STOPPED");
  expect(screen.getByRole("heading", { name: "Mission completed" })).toBeVisible();
  for (const action of ["start", "reset", "stop"]) {
    expect(requests).toContainEqual({ path: `/api/v1/labs/1/${action}`, method: "POST", body: {} });
  }
  expect(requests).toContainEqual({ path: "/api/v1/challenges/10/answers", method: "POST", body: { answer: "fixture observation" } });
});

it("handles an HTTP answer failure without leaking the body or completing the mission", async () => {
  failAnswer = true;
  render(<LabWorkspace missionId={1} />);
  fireEvent.change(await screen.findByRole("textbox"), { target: { value: "fixture observation" } });
  fireEvent.click(screen.getByRole("button", { name: "Submit Answer" }));
  expect(await screen.findByRole("alert")).not.toHaveTextContent("private host details");
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Submit Answer" })).toBeDisabled();
});
