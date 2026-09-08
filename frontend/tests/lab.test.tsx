import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { LabControls } from "@/components/lab/LabControls";
import { api } from "@/lib/api/client";
vi.mock("@/lib/api/client", () => ({ api: { labStatus: vi.fn(), labAction: vi.fn() } }));
const stopped = { mission_id: 1, status: "STOPPED" as const, target: null };
const running = { mission_id: 1, status: "RUNNING" as const, target: { ip: "192.0.2.10", hostname: "training-target" } };
beforeEach(() => {
  vi.mocked(api.labStatus).mockReset().mockResolvedValue(stopped);
  vi.mocked(api.labAction).mockReset();
  HTMLDialogElement.prototype.showModal = function () { this.setAttribute("open", ""); };
  HTMLDialogElement.prototype.close = function () { this.removeAttribute("open"); };
});
it("starts once, disables conflicts, then displays status target", async () => {
  let resolve!: (value: { mission_id: number; status: "running" }) => void;
  vi.mocked(api.labAction).mockImplementation(() => new Promise(r => { resolve = r; }));
  render(<LabControls missionId={1} />);
  await screen.findByText("STOPPED");
  fireEvent.click(screen.getByRole("button", { name: "Start Lab" }));
  expect(screen.getByText("STARTING")).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: "Start Lab" }));
  expect(api.labAction).toHaveBeenCalledTimes(1);
  expect(screen.getByRole("button", { name: "Stop Lab" })).toBeDisabled();
  vi.mocked(api.labStatus).mockResolvedValue(running);
  resolve({ mission_id: 1, status: "running" });
  expect(await screen.findByText("192.0.2.10")).toBeVisible();
});
it("stops the lab and clears target", async () => {
  vi.mocked(api.labStatus).mockResolvedValueOnce(running).mockResolvedValue(stopped);
  vi.mocked(api.labAction).mockResolvedValue({ mission_id: 1, status: "stopped" });
  render(<LabControls missionId={1} />);
  await screen.findByText("RUNNING");
  fireEvent.click(screen.getByRole("button", { name: "Stop Lab" }));
  await screen.findByText("STOPPED");
  expect(api.labAction).toHaveBeenCalledWith(1, "stop", expect.any(AbortSignal));
  expect(screen.queryByText("192.0.2.10")).not.toBeInTheDocument();
});
it("requires confirmation, supports cancel and Escape, and resets", async () => {
  vi.mocked(api.labStatus).mockResolvedValue(running);
  vi.mocked(api.labAction).mockResolvedValue({ mission_id: 1, status: "running" });
  render(<LabControls missionId={1} />);
  await screen.findByText("RUNNING");
  const reset = screen.getByRole("button", { name: "Reset Lab" });
  reset.focus(); fireEvent.click(reset);
  expect(screen.getByRole("dialog", { name: "Reset Lab?" })).toHaveTextContent("discarded");
  expect(api.labAction).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
  expect(reset).toHaveFocus();
  fireEvent.click(reset);
  fireEvent(screen.getByRole("dialog"), new Event("cancel", { bubbles: true, cancelable: true }));
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  fireEvent.click(reset);
  fireEvent.click(screen.getByRole("button", { name: "Confirm Reset" }));
  await waitFor(() => expect(api.labAction).toHaveBeenCalledWith(1, "reset", expect.any(AbortSignal)));
  await screen.findByText("192.0.2.10");
});
it("sanitizes failures and requires a fresh status before retrying", async () => {
  vi.mocked(api.labAction).mockRejectedValue(new Error("/private/socket secret"));
  render(<LabControls missionId={1} />);
  await screen.findByText("STOPPED");
  fireEvent.click(screen.getByRole("button", { name: "Start Lab" }));
  expect(await screen.findByRole("alert")).not.toHaveTextContent("/private/socket");
  expect(screen.getByRole("button", { name: "Start Lab" })).toBeDisabled();
  fireEvent.click(screen.getByRole("button", { name: "Refresh Status" }));
  await screen.findByText("STOPPED");
});

it("bounds transitional polling and cleans it up on unmount", async () => {
  vi.useFakeTimers();
  try {
    vi.mocked(api.labStatus).mockResolvedValue({ ...stopped, status: "STARTING" });
    const { unmount } = render(<LabControls missionId={1} />);
    await act(async () => { await Promise.resolve(); });
    for (let count = 0; count < 20; count++) {
      await act(async () => { await vi.advanceTimersByTimeAsync(3000); });
    }
    expect(api.labStatus).toHaveBeenCalledTimes(21);
    expect(screen.getByText(/Automatic status checks have paused/)).toBeVisible();
    await act(async () => { await vi.advanceTimersByTimeAsync(30_000); });
    expect(api.labStatus).toHaveBeenCalledTimes(21);
    unmount();
    expect(vi.getTimerCount()).toBe(0);
  } finally { vi.useRealTimers(); }
});

it("stops polling at a terminal state and aborts initial reads on unmount", async () => {
  vi.useFakeTimers();
  try {
    vi.mocked(api.labStatus).mockResolvedValueOnce({ ...stopped, status: "STOPPING" }).mockResolvedValue(stopped);
    const { unmount } = render(<LabControls missionId={1} />);
    await act(async () => { await Promise.resolve(); });
    await act(async () => { await vi.advanceTimersByTimeAsync(3000); });
    expect(screen.getByText("STOPPED")).toBeVisible();
    await act(async () => { await vi.advanceTimersByTimeAsync(30_000); });
    expect(api.labStatus).toHaveBeenCalledTimes(2);
    const signal = vi.mocked(api.labStatus).mock.calls[0][1];
    unmount();
    expect(signal?.aborted).toBe(true);
  } finally { vi.useRealTimers(); }
});
