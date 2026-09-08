"use client";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui";
import { Modal } from "@/components/ui/Modal";
import { ActionLink } from "@/components/mission/shared";
import { api, type Mission, type MissionDetail } from "@/lib/api/client";
import styles from "@/components/mission/mission.module.css";
export function MissionComplete({ mission, onClose }: { mission: MissionDetail; onClose: () => void }) {
  const [next, setNext] = useState<Mission>();
  useEffect(() => {
    const controller = new AbortController();
    Promise.all([api.missions(controller.signal), api.progress(controller.signal)]).then(([missions, progress]) => {
      if (controller.signal.aborted) return;
      const ordered = [...missions].sort((a,b) => a.sort_order - b.sort_order || a.id - b.id);
      const index = ordered.findIndex(m => m.id === mission.id);
      const candidate = index < 0 ? undefined : ordered.slice(index + 1).find(m => {
        const status = progress.missions.find(p => p.mission_id === m.id)?.status;
        return status === "NOT_STARTED" || status === "IN_PROGRESS";
      });
      setNext(candidate);
    }).catch(() => { /* Back to Learning Path remains usable if next-mission discovery fails. */ });
    return () => controller.abort();
  }, [mission.id]);
  return <Modal title="Mission Complete" onClose={onClose}>
    <p>✓ All required challenges are complete.</p><h3>{mission.title}</h3>
    {mission.learning_explanation && <section><h4>Learning Review</h4><p className={styles.text}>{mission.learning_explanation}</p></section>}
    {mission.challenges.length > 0 && <><h4>Completed challenges</h4><ul>{mission.challenges.map(c => <li key={c.id}>{c.title}</li>)}</ul></>}
    <p>You can return to the learning path or return to the workspace to manage the lab.</p>
    <div className={styles.actions}><Button variant="secondary" onClick={onClose}>Return to Workspace</Button><ActionLink href="/learning-path">Back to Learning Path</ActionLink>{next && <ActionLink href={`/missions/${next.id}`}>Next Mission</ActionLink>}</div>
  </Modal>;
}
