"use client";
import { Card, ProgressBar } from "@/components/ui";
import { api } from "@/lib/api/client";
import { useResource } from "@/lib/api/useResource";
import { ActionLink, ChallengeProgress, LoadState, PageHeader } from "@/components/mission/shared";
import { ActiveLabBanner } from "@/components/dashboard/ActiveLabBanner";
import { MissionRow } from "./MissionRow";
import styles from "@/components/mission/mission.module.css";
const load = async (signal: AbortSignal) => {
  const [missions, progress] = await Promise.all([api.missions(signal), api.progress(signal)]);
  return { missions: [...missions].sort((a, b) => a.sort_order - b.sort_order || a.id - b.id), progress };
};
export function LearningOverview({ view }: { view: "dashboard" | "path" | "progress" }) {
  const { data, error, retry } = useResource(load);
  const title = view === "dashboard" ? "Dashboard" : view === "path" ? "Learning Path" : "Progress";
  const current = data?.missions.find(m => data.progress.missions.find(p => p.mission_id === m.id)?.status === "IN_PROGRESS");
  const completed = data?.missions.filter(m => data.progress.missions.find(p => p.mission_id === m.id)?.status === "COMPLETED").length ?? 0;
  return <div className={styles.stack}>
    <PageHeader title={title}><p>Build practical security skills, one mission at a time.</p></PageHeader>
    {!data ? <LoadState error={error} retry={retry} /> : !data.missions.length ? <Card><h2>No missions available</h2><p>Mission content has not been added yet.</p></Card> : <>
      {view === "dashboard" && data.missions.map(mission => <ActiveLabBanner key={mission.id} mission={mission} />)}
      {view === "dashboard" && <Card><h2>Continue Training</h2>{current ? <><h3>{current.title}</h3><p>{current.description}</p><ChallengeProgress progress={data.progress.missions.find(p => p.mission_id === current.id)} /><ActionLink href={`/missions/${current.id}`}>Continue Mission</ActionLink></> : <><p>{completed === data.missions.length ? "You have completed all available missions. Review your learning path." : "Start your first mission from the Learning Path."}</p><ActionLink href="/learning-path">View Learning Path</ActionLink></>}</Card>}
      <Card><h2>Learning Progress</h2><ProgressBar label="Missions completed" value={completed} max={data.missions.length} /><p>{completed} of {data.missions.length} missions completed</p></Card>
      <ol className={styles.timeline} aria-label="Mission progression">{data.missions.map(mission => {
        const progress = data.progress.missions.find(p => p.mission_id === mission.id);
        return <li key={mission.id}><MissionRow mission={mission} progress={progress} showProgress={view === "progress"} /></li>;
      })}</ol>
    </>}
  </div>;
}
