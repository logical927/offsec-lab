"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { Badge, Button, Card, Input } from "@/components/ui";
import { api, type AnswerResult, type MissionDetail, type MissionProgress } from "@/lib/api/client";
import { ChallengeProgress, LoadState } from "@/components/mission/shared";
import styles from "@/components/mission/mission.module.css";
import { HintPanel } from "./HintPanel";

export function ChallengePanel({ mission, onProgress }: { mission: MissionDetail; onProgress?: (progress: MissionProgress) => void }) {
  const [progress, setProgress] = useState<MissionProgress>();
  const [selected, setSelected] = useState<number>();
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState<AnswerResult>();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const lock = useRef(false);
  const heading = useRef<HTMLHeadingElement>(null);
  const focusNext = useRef(false);
  const lifetime = useRef<AbortController | null>(null);
  const callback = useRef(onProgress);
  useEffect(() => { callback.current = onProgress; }, [onProgress]);
  useEffect(() => {
    if (focusNext.current) {
      heading.current?.focus();
      focusNext.current = false;
    }
  }, [selected]);
  const challenges = [...mission.challenges].sort((a,b) => a.sort_order - b.sort_order || a.id - b.id);
  const refresh = useCallback(async (signal: AbortSignal) => {
    const data = await api.progress(signal);
    const snapshot = data.missions.find(p => p.mission_id === mission.id);
    if (!snapshot) throw new Error("Progress unavailable");
    if (!signal.aborted) {
      setProgress(snapshot);
      setConfirmed(true);
      callback.current?.(snapshot);
    }
    return snapshot;
  }, [mission.id]);
  useEffect(() => {
    const controller = new AbortController();
    lifetime.current = controller;
    api.progress(controller.signal).then(data => {
      const snapshot = data.missions.find(p => p.mission_id === mission.id);
      if (!snapshot) throw new Error("Progress unavailable");
      if (!controller.signal.aborted) {
        setProgress(snapshot);
        setConfirmed(true);
        callback.current?.(snapshot);
      }
    }).catch(() => { if (!controller.signal.aborted) setError("Progress is unavailable. Refresh progress to continue."); });
    return () => controller.abort();
  }, [mission.id]);

  async function refreshProgress() {
    if (lock.current) return;
    const signal = lifetime.current?.signal;
    if (!signal || signal.aborted) return;
    lock.current = true; setBusy(true); setError(""); setConfirmed(false);
    try { await refresh(signal); }
    catch { if (!signal.aborted) setError("Progress could not be confirmed. Refresh progress to continue."); }
    finally { lock.current = false; if (!signal.aborted) setBusy(false); }
  }
  const available = challenges.find(c => progress?.challenges.find(p => p.challenge_id === c.id)?.status === "AVAILABLE");
  const challenge = challenges.find(c => c.id === selected) ?? available ?? challenges[0];
  const status = progress?.challenges.find(p => p.challenge_id === challenge?.id)?.status;
  const index = challenges.findIndex(c => c.id === challenge?.id);
  async function submit() {
    if (lock.current || !challenge || status !== "AVAILABLE" || !answer.trim() || !confirmed) return;
    const signal = lifetime.current?.signal;
    if (!signal || signal.aborted) return;
    lock.current = true; setBusy(true); setError(""); setResult(undefined); setSelected(challenge.id);
    try {
      const response = await api.answer(challenge.id, answer, signal);
      if (signal.aborted) return;
      setResult(response);
      if (response.correct) {
        setAnswer("");
        setConfirmed(false);
        await refresh(signal);
      }
    } catch {
      if (!signal.aborted) { setConfirmed(false); setError("The answer or progress could not be confirmed. Refresh progress before continuing."); }
    } finally { lock.current = false; if (!signal.aborted) setBusy(false); }
  }
  if (!progress) return <LoadState error={error || undefined} retry={() => void refreshProgress()} />;
  return <Card className={styles.stack}>
    <h2>Challenges</h2>
    <ChallengeProgress progress={progress} />
    {error && <p role="alert">{error}</p>}
    <Button variant="secondary" disabled={busy} onClick={() => void refreshProgress()}>Refresh Progress</Button>
    {!challenge ? <p>No challenges available yet.</p> : <>
      <p>Challenge {index + 1} of {challenges.length}</p>
      <h3 ref={heading} tabIndex={-1}>{challenge.title}</h3>
      <p className={styles.text}>{challenge.description}</p>
      <Badge tone={status === "COMPLETED" ? "success" : "neutral"}>{status ?? "STATUS UNAVAILABLE"}</Badge>
      <form className={styles.stack} onSubmit={event => { event.preventDefault(); void submit(); }}>
        <Input label="Answer" value={answer} onChange={event => setAnswer(event.target.value)} maxLength={200} required disabled={busy || status !== "AVAILABLE" || !confirmed} helpText="Enter your findings (up to 200 characters)." />
        <Button type="submit" disabled={busy || status !== "AVAILABLE" || !answer.trim() || !confirmed}>Submit Answer</Button>
      </form>
      <div role="status" aria-live="polite">{busy ? "Checking answer or progress…" : result?.correct ? "✓ CORRECT" : result ? "✕ INCORRECT — Review your reconnaissance results and try again." : status === "COMPLETED" ? "Challenge completed." : ""}</div>
      {status === "LOCKED" && <p>Complete the preceding challenge to unlock this one.</p>}
      {status !== "LOCKED" && <HintPanel key={challenge.id} hints={[...(challenge.hints ?? [])].sort((a,b) => a.level - b.level).map(h => ({ id: String(h.id), content: h.content }))} />}
      {confirmed && !busy && status === "COMPLETED" && available && <Button onClick={() => { focusNext.current = true; setSelected(available.id); setAnswer(""); setResult(undefined); }}>Next Challenge</Button>}
    </>}
  </Card>;
}
