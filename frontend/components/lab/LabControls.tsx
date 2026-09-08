"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { Badge, Button, Card, Spinner } from "@/components/ui";
import { Modal } from "@/components/ui/Modal";
import { api, type LabStatus } from "@/lib/api/client";
import styles from "@/components/mission/mission.module.css";

export function LabControls({ missionId }: { missionId: number }) {
  const [lab, setLab] = useState<LabStatus>();
  const [operation, setOperation] = useState<"start" | "stop" | "reset" | "status" | undefined>("status");
  const [error, setError] = useState("");
  const [confirm, setConfirm] = useState(false);
  const [pollLimit, setPollLimit] = useState(false);
  const inFlight = useRef(true);
  const lifetime = useRef<AbortController | null>(null);
  const refresh = useCallback(async (signal: AbortSignal) => {
    const status = await api.labStatus(missionId, signal);
    if (!signal.aborted) setLab(status);
    return status;
  }, [missionId]);

  useEffect(() => {
    const controller = new AbortController();
    lifetime.current = controller;
    api.labStatus(missionId, controller.signal).then(status => {
      if (!controller.signal.aborted) setLab(status);
    }).catch(() => {
      if (!controller.signal.aborted) setError("Unable to retrieve lab status. Check the local backend and refresh.");
    }).finally(() => {
      if (!controller.signal.aborted) {
        inFlight.current = false;
        setOperation(undefined);
      }
    });
    return () => controller.abort();
  }, [missionId]);

  const transitional = lab?.status === "STARTING" || lab?.status === "STOPPING";
  useEffect(() => {
    if (!transitional || operation || pollLimit) return;
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout>;
    let attempts = 0;
    const poll = async () => {
      try {
        const next = await refresh(controller.signal);
        if (controller.signal.aborted) return;
        if (next.status !== "STARTING" && next.status !== "STOPPING") return;
        if (++attempts >= 20) { setPollLimit(true); return; }
        timer = setTimeout(poll, 3000);
      } catch {
        if (!controller.signal.aborted) { setPollLimit(true); setError("Status refresh failed. Refresh status before another operation."); }
      }
    };
    timer = setTimeout(poll, 3000);
    return () => { controller.abort(); clearTimeout(timer); };
  }, [transitional, operation, pollLimit, refresh]);

  async function act(action: "start" | "stop" | "reset" | "status") {
    if (inFlight.current) return;
    const signal = lifetime.current?.signal;
    if (!signal || signal.aborted) return;
    inFlight.current = true;
    setOperation(action);
    setError("");
    setPollLimit(false);
    try {
      if (action !== "status") {
        const result = await api.labAction(missionId, action, signal);
        if (signal.aborted) return;
        setLab({ mission_id: missionId, status: result.status === "running" ? "RUNNING" : "STOPPED", target: null });
      }
      await refresh(signal);
    } catch {
      if (!signal.aborted) {
        setLab(undefined);
        setError("The lab request could not be confirmed. Check Docker and the local backend, then refresh status before trying again.");
      }
    } finally {
      inFlight.current = false;
      if (!signal.aborted) setOperation(undefined);
    }
  }
  const busy = Boolean(operation) || transitional;
  const status = operation === "start" ? "STARTING" : operation === "stop" ? "STOPPING" : operation === "reset" ? "RESETTING" : lab?.status;
  return <Card className={styles.stack}>
    <h2>Lab Status</h2>
    <div role="status">{status ? <Badge tone={status === "RUNNING" ? "success" : status === "ERROR" ? "error" : "neutral"}>{status}</Badge> : error ? "STATUS UNAVAILABLE" : <Spinner label="Loading lab status" />}</div>
    {operation && <p role="status">{operation === "status" ? "Refreshing status..." : "Processing lab operation..."}</p>}
    {error && <p role="alert">{error}</p>}
    {pollLimit && <p>Automatic status checks have paused. Refresh status to check again.</p>}
    <section aria-label="Target information"><h3>Target</h3>
      {!operation && lab?.status === "RUNNING" && lab.target ? <><p className="technical-value">{lab.target.ip}</p><p className="technical-value">{lab.target.hostname}</p></> : <p>Target information is unavailable until the lab is running.</p>}
    </section>
    <div className={styles.actions}>
      <Button disabled={busy || !lab || !["STOPPED", "ERROR"].includes(lab.status)} onClick={() => void act("start")}>Start Lab</Button>
      <Button variant="secondary" disabled={busy || !lab || !["RUNNING", "ERROR"].includes(lab.status)} onClick={() => void act("stop")}>Stop Lab</Button>
      <Button variant="destructive" disabled={busy || lab?.status !== "RUNNING"} onClick={() => setConfirm(true)}>Reset Lab</Button>
      <Button variant="secondary" disabled={Boolean(operation)} onClick={() => void act("status")}>Refresh Status</Button>
    </div>
    {confirm && <Modal title="Reset Lab?" onClose={() => setConfirm(false)}>
      <p>Current changes inside the attacker and target containers will be discarded. The environment will return to its initial state. Learning progress is preserved.</p>
      <div className={styles.actions}><Button variant="secondary" onClick={() => setConfirm(false)}>Cancel</Button><Button variant="destructive" onClick={() => { setConfirm(false); void act("reset"); }}>Confirm Reset</Button></div>
    </Modal>}
  </Card>;
}
