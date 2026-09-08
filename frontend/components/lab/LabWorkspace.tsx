"use client";
import { useCallback, useState } from "react";
import { Card } from "@/components/ui";
import { api, type MissionProgress } from "@/lib/api/client";
import { useResource } from "@/lib/api/useResource";
import { ActionLink, LoadState, PageHeader, SecurityNotice } from "@/components/mission/shared";
import { LabControls } from "./LabControls";
import { ChallengePanel } from "./ChallengePanel";
import { HintPanel } from "./HintPanel";
import { MissionComplete } from "./MissionComplete";
import styles from "@/components/mission/mission.module.css";
export function LabWorkspace({ missionId }: { missionId: number }) {
  const [progress, setProgress] = useState<MissionProgress>();
  const [dismissed, setDismissed] = useState(false);
  const loader = useCallback((signal: AbortSignal) => api.mission(missionId, signal), [missionId]);
  const { data: mission, error, retry } = useResource(loader);
  if (!mission) return <LoadState error={error} retry={retry} />;
  return <div className={styles.stack}>
    <ActionLink href={`/missions/${mission.id}`}>Back to Mission Briefing</ActionLink>
    <PageHeader title={mission.title}><p>Lab Workspace</p></PageHeader>
    <div className={styles.workspace}>
      <div className={styles.stack}>
        <Card><h2>Mission Objective</h2><p className={styles.text}>{mission.description ?? "Review the challenges for this mission's objectives."}</p></Card>
        {progress?.status === "COMPLETED" && <Card className={styles.success}><h2>Mission completed</h2><p>Your completion is saved in backend progress.</p><ActionLink href="/learning-path">Back to Learning Path</ActionLink></Card>}
        <ChallengePanel key={missionId} mission={mission} onProgress={setProgress} />
        <Card><h2>Attacker Environment</h2><p>Open your external WSL2 terminal and connect to the attacker after starting the lab.</p>{mission.id === 1 && <code className="technical-value">docker exec -it offsec-m01-attacker bash</code>}<p>Desktop environment recommended for lab exercises.</p></Card>
        <SecurityNotice />
      </div>
      <aside className={`${styles.stack} ${styles.side}`} aria-label="Lab tools"><LabControls key={missionId} missionId={missionId} /><HintPanel hints={[]} /></aside>
    </div>
    {progress?.status === "COMPLETED" && !dismissed && <MissionComplete mission={mission} onClose={() => setDismissed(true)} />}
  </div>;
}
