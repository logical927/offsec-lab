import { api } from "@/lib/api/client";
afterEach(() => { vi.unstubAllGlobals(); vi.useRealTimers(); });
it("uses the actual API paths, methods and generic answer body", async () => {
  const fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({}) });
  vi.stubGlobal("fetch", fetch);
  await api.missions(); await api.mission(7); await api.progress(); await api.labStatus(7);
  await api.labAction(7, "start"); await api.labAction(7, "stop"); await api.labAction(7, "reset"); await api.answer(8, "fixture observation");
  expect(fetch.mock.calls.map(call => call[0])).toEqual(["/api/v1/missions", "/api/v1/missions/7", "/api/v1/progress", "/api/v1/labs/7/status", "/api/v1/labs/7/start", "/api/v1/labs/7/stop", "/api/v1/labs/7/reset", "/api/v1/challenges/8/answers"]);
  expect(fetch.mock.calls[7][1]).toMatchObject({ method: "POST", cache: "no-store", body: '{"answer":"fixture observation"}', headers: { "Content-Type": "application/json" } });
});
it.each([404, 409, 422, 500])("sanitizes HTTP %s without reading the response body", async status => {
  const json = vi.fn();
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status, json }));
  await expect(api.mission(1)).rejects.toMatchObject({ status });
  expect(json).not.toHaveBeenCalled();
});
it("aborts requests on unmount signal and times out stalled reads", async () => {
  vi.useFakeTimers();
  const signals: AbortSignal[] = [];
  vi.stubGlobal("fetch", vi.fn().mockImplementation((_url, options) => {
    signals.push(options.signal);
    return new Promise((_resolve, reject) => options.signal.addEventListener("abort", () => reject(new Error("private network failure"))));
  }));
  const controller = new AbortController();
  const aborted = expect(api.missions(controller.signal)).rejects.toMatchObject({ status: 0 });
  controller.abort(); await aborted;
  expect(signals[0].aborted).toBe(true);
  const timed = expect(api.progress()).rejects.toMatchObject({ status: 0 });
  await vi.advanceTimersByTimeAsync(30_000); await timed;
  expect(signals[1].aborted).toBe(true);
});
