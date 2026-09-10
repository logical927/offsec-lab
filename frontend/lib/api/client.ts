export type Mission = { id: number; slug: string; title: string; description: string | null; sort_order: number };
export type Challenge = Mission & { hints?: { id: number; level: number; content: string }[] };
export type MissionDetail = Mission & { challenges: Challenge[]; learning_explanation?: string | null };
export type ChallengeStatus = "LOCKED" | "AVAILABLE" | "COMPLETED";
export type MissionProgress = { mission_id: number; status: "NOT_STARTED" | "IN_PROGRESS" | "COMPLETED"; challenges: { challenge_id: number; status: ChallengeStatus }[] };
export type Progress = { missions: MissionProgress[] };
export type LabStatus = { mission_id: number; status: "STOPPED" | "STARTING" | "RUNNING" | "STOPPING" | "ERROR"; target: { hostname: string; ip: string } | null };
export type AnswerResult = { correct: boolean; status: ChallengeStatus; next_challenge_id: number | null; mission_status: MissionProgress["status"] };
export class ApiError extends Error {
  constructor(public status: number) {
    super(status === 404 ? "The requested mission or lab is unavailable." : status === 409 ? "This challenge is not available yet. Refresh progress and try again." : "Unable to complete the request. Check the local backend and try again.");
  }
}
// Never display upstream error bodies: they may contain internal details.
async function request<T>(path: string, signal?: AbortSignal, body?: object): Promise<T> {
  const controller = new AbortController();
  const abort = () => controller.abort();
  signal?.addEventListener("abort", abort, { once: true });
  if (signal?.aborted) controller.abort();
  const timeout = setTimeout(abort, body && path.startsWith("/labs/") ? 300_000 : 30_000);
  try {
    const response = await fetch(`/api/v1${path}`, {
      method: body ? "POST" : "GET", cache: "no-store", signal: controller.signal,
      ...(body ? { headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {}),
    });
    if (!response.ok) throw new ApiError(response.status);
    return await response.json() as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(0);
  } finally {
    clearTimeout(timeout);
    signal?.removeEventListener("abort", abort);
  }
}
export const api = {
  missions: (signal?: AbortSignal) => request<Mission[]>("/missions", signal),
  mission: (id: number, signal?: AbortSignal) => request<MissionDetail>(`/missions/${id}`, signal),
  progress: (signal?: AbortSignal) => request<Progress>("/progress", signal),
  resetProgress: (id: number, signal?: AbortSignal) => request<MissionProgress>(`/progress/${id}/reset`, signal, {}),
  labStatus: (id: number, signal?: AbortSignal) => request<LabStatus>(`/labs/${id}/status`, signal),
  labAction: (id: number, action: "start" | "stop" | "reset", signal?: AbortSignal) => request<{ mission_id: number; status: "running" | "stopped" }>(`/labs/${id}/${action}`, signal, {}),
  answer: (id: number, answer: string, signal?: AbortSignal) => request<AnswerResult>(`/challenges/${id}/answers`, signal, { answer }),
};
