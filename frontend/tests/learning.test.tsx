import { render, screen, fireEvent } from "@testing-library/react";
import { LearningOverview } from "@/components/learning-path/LearningOverview";
import { api } from "@/lib/api/client";
vi.mock("@/lib/api/client", () => ({ api: { missions: vi.fn(), progress: vi.fn(), labStatus: vi.fn().mockResolvedValue({ status: "STOPPED", target: null }) } }));
const mission = { id: 1, slug: "m01", title: "Training mission", description: "Investigate the provided target.", sort_order: 1 };
beforeEach(() => { vi.mocked(api.missions).mockResolvedValue([mission]); vi.mocked(api.progress).mockResolvedValue({ missions: [{ mission_id: 1, status: "NOT_STARTED", challenges: [] }] }); });
it("loads the path with available mission navigation", async () => {
  render(<LearningOverview view="path" />);
  expect(screen.getByRole("status")).toHaveTextContent("Loading");
  expect(await screen.findByText("AVAILABLE")).toBeVisible();
  expect(screen.getByRole("link", { name: "View Mission" })).toHaveAttribute("href", "/missions/1");
});
it("guides a new learner to the path", async () => {
  render(<LearningOverview view="dashboard" />);
  expect(await screen.findByRole("link", { name: "View Learning Path" })).toHaveAttribute("href", "/learning-path");
});
it("resumes backend-confirmed progress", async () => {
  vi.mocked(api.progress).mockResolvedValue({ missions: [{ mission_id: 1, status: "IN_PROGRESS", challenges: [{ challenge_id: 1, status: "COMPLETED" }] }] });
  render(<LearningOverview view="dashboard" />);
  expect(await screen.findByRole("link", { name: "Continue Mission" })).toHaveAttribute("href", "/missions/1");
});
it("handles empty missions", async () => {
  vi.mocked(api.missions).mockResolvedValue([]);
  render(<LearningOverview view="path" />);
  expect(await screen.findByText("No missions available")).toBeVisible();
});
it("handles errors and retries", async () => {
  vi.mocked(api.missions).mockRejectedValueOnce(new Error("private failure"));
  render(<LearningOverview view="path" />);
  expect(await screen.findByRole("alert")).not.toHaveTextContent("private failure");
  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  expect(await screen.findByText("AVAILABLE")).toBeVisible();
});
