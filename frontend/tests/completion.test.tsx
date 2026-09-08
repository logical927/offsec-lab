import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { LabWorkspace } from "@/components/lab/LabWorkspace";
import { api, type MissionDetail } from "@/lib/api/client";
vi.mock("@/lib/api/client", () => ({ api: { mission: vi.fn(), missions: vi.fn(), progress: vi.fn(), labStatus: vi.fn(), answer: vi.fn() } }));
const mission: MissionDetail = { id: 1, slug: "fixture", title: "Training", description: "Investigate.", sort_order: 1, challenges: [{ id: 10, slug: "observation", title: "Observation", description: "Record findings.", sort_order: 1 }] };
beforeEach(() => {
  vi.mocked(api.mission).mockResolvedValue(mission);
  vi.mocked(api.missions).mockResolvedValue([mission]);
  vi.mocked(api.labStatus).mockResolvedValue({ mission_id: 1, status: "STOPPED", target: null });
  vi.mocked(api.progress).mockReset().mockResolvedValue({ missions: [{ mission_id: 1, status: "NOT_STARTED", challenges: [{ challenge_id: 10, status: "AVAILABLE" }] }] });
  vi.mocked(api.answer).mockResolvedValue({ correct: true, status: "COMPLETED", next_challenge_id: null, mission_status: "COMPLETED" });
  HTMLDialogElement.prototype.showModal = function () { this.setAttribute("open", ""); };
  HTMLDialogElement.prototype.close = function () { this.removeAttribute("open"); };
});
it("waits for refreshed backend completion before showing the modal", async () => {
  render(<LabWorkspace missionId={1} />);
  fireEvent.change(await screen.findByRole("textbox"), { target: { value: "fixture finding" } });
  fireEvent.click(screen.getByRole("button", { name: "Submit Answer" }));
  await screen.findByText("✓ CORRECT");
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  vi.mocked(api.progress).mockResolvedValue({ missions: [{ mission_id: 1, status: "COMPLETED", challenges: [{ challenge_id: 10, status: "COMPLETED" }] }] });
  fireEvent.click(screen.getByRole("button", { name: "Refresh Progress" }));
  expect(await screen.findByRole("dialog", { name: "Mission Complete" })).toBeVisible();
  expect(screen.queryByRole("link", { name: "Next Mission" })).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Return to Workspace" }));
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Start Lab" })).toBeVisible();
});
it("restores recorded completion on reload and offers only a real available next mission", async () => {
  vi.mocked(api.progress).mockResolvedValue({ missions: [{ mission_id: 1, status: "COMPLETED", challenges: [{ challenge_id: 10, status: "COMPLETED" }] }, { mission_id: 2, status: "NOT_STARTED", challenges: [] }] });
  vi.mocked(api.missions).mockResolvedValue([mission, { ...mission, id: 2, title: "Next fixture", sort_order: 2 }]);
  render(<LabWorkspace missionId={1} />);
  await screen.findByRole("dialog", { name: "Mission Complete" });
  expect(await screen.findByRole("link", { name: "Next Mission" })).toHaveAttribute("href", "/missions/2");
  await waitFor(() => expect(api.answer).not.toHaveBeenCalled());
});
