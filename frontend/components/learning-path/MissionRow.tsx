import { Card } from "@/components/ui";
import type { Mission, MissionProgress } from "@/lib/api/client";
import { ActionLink, ChallengeProgress, MissionStatus } from "@/components/mission/shared";
import styles from "@/components/mission/mission.module.css";
export function MissionRow({ mission, progress, locked = false, showProgress = false }: { mission: Mission; progress?: MissionProgress; locked?: boolean; showProgress?: boolean }) {
  return <Card><div className={styles.row}><h2>{mission.title}</h2><MissionStatus status={locked ? "LOCKED" : progress?.status} /></div>
    <p className={styles.text}>{mission.description}</p>
    {showProgress && <ChallengeProgress progress={progress} />}
    {locked ? <p>Complete the prerequisite mission to unlock this mission.</p> : <ActionLink href={`/missions/${mission.id}`}>View Mission</ActionLink>}
  </Card>;
}
