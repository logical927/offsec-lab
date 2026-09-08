import { render, screen } from "@testing-library/react";
import { MissionRow } from "@/components/learning-path/MissionRow";
import { ActiveLabBanner } from "@/components/dashboard/ActiveLabBanner";
import { api } from "@/lib/api/client";
vi.mock("@/lib/api/client", () => ({ api: { labStatus: vi.fn() } }));
const mission = { id: 1, title: "Fixture", slug: "fixture", description: null, sort_order: 1 };
it("labels a locked row and provides no navigation", () => {
  render(<MissionRow mission={mission} locked />);
  expect(screen.getByText("LOCKED")).toBeVisible();
  expect(screen.getByText(/prerequisite/)).toBeVisible();
  expect(screen.queryByRole("link")).not.toBeInTheDocument();
});
it("shows an active lab only from backend status", async () => {
  vi.mocked(api.labStatus).mockResolvedValue({ mission_id: 1, status: "RUNNING", target: { ip: "192.0.2.10", hostname: "fixture" } });
  render(<ActiveLabBanner mission={mission} />);
  expect(await screen.findByText("LAB RUNNING")).toBeVisible();
  expect(screen.getByRole("link", { name: "Open Lab" })).toHaveAttribute("href", "/missions/1/lab");
});
