import { render, screen } from "@testing-library/react";
import { MissionBriefing } from "@/components/mission/MissionBriefing";
import { api } from "@/lib/api/client";
vi.mock("@/lib/api/client", () => ({ api: { mission: vi.fn() } }));
it("maps briefing and challenges to a navigation-only lab CTA", async () => {
  vi.mocked(api.mission).mockResolvedValue({ id: 7, slug: "fixture", title: "Investigation", description: "Inspect the provided target.", sort_order: 1, challenges: [{ id: 8, slug: "observe", title: "Observe", description: "Record your findings.", sort_order: 1 }] });
  render(<MissionBriefing missionId={7} />);
  expect(screen.getByRole("status")).toBeVisible();
  expect(await screen.findByRole("heading", { name: "Investigation" })).toBeVisible();
  expect(screen.getByText("Record your findings.")).toBeVisible();
  expect(screen.getByRole("heading", { name: "Security Notice" })).toBeVisible();
  expect(screen.getByRole("link", { name: "Open Lab Workspace" })).toHaveAttribute("href", "/missions/7/lab");
  expect(api.mission).toHaveBeenCalledWith(7, expect.any(AbortSignal));
});
it("safely handles unavailable missions", async () => {
  vi.mocked(api.mission).mockRejectedValue(new Error("internal path"));
  render(<MissionBriefing missionId={999} />);
  expect(await screen.findByRole("alert")).not.toHaveTextContent("internal path");
  expect(screen.queryByRole("link", { name: "Open Lab Workspace" })).not.toBeInTheDocument();
});
