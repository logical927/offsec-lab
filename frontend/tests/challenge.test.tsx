import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { ChallengePanel } from "@/components/lab/ChallengePanel";
import { api, type MissionDetail, type Progress } from "@/lib/api/client";
vi.mock("@/lib/api/client", () => ({ api: { progress: vi.fn(), answer: vi.fn() } }));
const mission: MissionDetail = { id: 1, slug: "fixture", title: "Training", description: "Investigate.", sort_order: 1, challenges: [
  { id: 10, slug: "one", title: "First observation", description: "Record one finding.", sort_order: 1 },
  { id: 20, slug: "two", title: "Second observation", description: "Record another finding.", sort_order: 2 },
] };
const initial: Progress = { missions: [{ mission_id: 1, status: "NOT_STARTED", challenges: [{ challenge_id: 10, status: "AVAILABLE" }, { challenge_id: 20, status: "LOCKED" }] }] };
beforeEach(() => {
  vi.mocked(api.progress).mockReset().mockResolvedValue(initial);
  vi.mocked(api.answer).mockReset();
});
async function enter() {
  const input = await screen.findByRole("textbox", { name: "Answer" });
  fireEvent.change(input, { target: { value: "fixture observation" } });
  await act(async () => {
    fireEvent.click(screen.getByRole("button", { name: "Submit Answer" }));
  });
}
it("submits a generic answer once and shows incorrect feedback without disclosure", async () => {
  let resolve!: (value: Awaited<ReturnType<typeof api.answer>>) => void;
  vi.mocked(api.answer).mockImplementation(() => new Promise(r => { resolve = r; }));
  render(<ChallengePanel mission={mission} />);
  await enter();
  expect(screen.getByRole("button", { name: "Submit Answer" })).toBeDisabled();
  fireEvent.click(screen.getByRole("button", { name: "Submit Answer" }));
  expect(api.answer).toHaveBeenCalledTimes(1);
  expect(api.answer).toHaveBeenCalledWith(10, "fixture observation", expect.any(AbortSignal));
  await act(async () => {
    resolve({ correct: false, status: "AVAILABLE", next_challenge_id: null, mission_status: "NOT_STARTED" });
  });
  expect(await screen.findByText(/INCORRECT/)).toBeVisible();
  expect(screen.getByRole("textbox")).toBeEnabled();
});
it("refreshes backend progress after correctness and moves to the unlocked challenge", async () => {
  vi.mocked(api.answer).mockResolvedValue({ correct: true, status: "COMPLETED", next_challenge_id: 20, mission_status: "IN_PROGRESS" });
  vi.mocked(api.progress).mockResolvedValueOnce(initial).mockResolvedValue({ missions: [{ mission_id: 1, status: "IN_PROGRESS", challenges: [{ challenge_id: 10, status: "COMPLETED" }, { challenge_id: 20, status: "AVAILABLE" }] }] });
  render(<ChallengePanel mission={mission} />);
  await enter();
  expect(await screen.findByText("✓ CORRECT")).toBeVisible();
  fireEvent.click(await screen.findByRole("button", { name: "Next Challenge" }));
  expect(screen.getByText("Challenge 2 of 2")).toBeVisible();
  expect(screen.getByRole("heading", { name: "Second observation" })).toHaveFocus();
  expect(screen.getByRole("textbox")).toHaveValue("");
  expect(api.progress).toHaveBeenCalledTimes(2);
});
it("does not unlock from answer response when progress refresh fails", async () => {
  vi.mocked(api.answer).mockResolvedValue({ correct: true, status: "COMPLETED", next_challenge_id: 20, mission_status: "COMPLETED" });
  vi.mocked(api.progress).mockResolvedValueOnce(initial).mockRejectedValue(new Error("private"));
  render(<ChallengePanel mission={mission} />);
  await enter();
  expect(await screen.findByRole("alert")).not.toHaveTextContent("private");
  expect(screen.queryByRole("button", { name: "Next Challenge" })).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Submit Answer" })).toBeDisabled();
});
it("resumes the available challenge and handles an empty mission", async () => {
  vi.mocked(api.progress).mockResolvedValue({ missions: [{ mission_id: 1, status: "IN_PROGRESS", challenges: [{ challenge_id: 10, status: "COMPLETED" }, { challenge_id: 20, status: "AVAILABLE" }] }] });
  const { unmount } = render(<ChallengePanel mission={mission} />);
  expect(await screen.findByText("Challenge 2 of 2")).toBeVisible();
  unmount();
  render(<ChallengePanel mission={{ ...mission, challenges: [] }} />);
  await waitFor(() => expect(screen.getByText("No challenges available yet.")).toBeVisible());
});
