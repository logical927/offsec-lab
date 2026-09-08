"use client";
import { useCallback } from "react";
import { Card } from "@/components/ui";
import { api } from "@/lib/api/client";
import { useResource } from "@/lib/api/useResource";
import { ActionLink, LoadState, PageHeader, SecurityNotice } from "./shared";
import styles from "./mission.module.css";

export function MissionBriefing({ missionId }: { missionId: number }) {
  const loader = useCallback((signal: AbortSignal) => api.mission(missionId, signal), [missionId]);
  const { data: mission, error, retry } = useResource(loader);
  if (!mission) return <LoadState error={error} retry={retry} />;
  return <div className={styles.stack}>
    <ActionLink href="/learning-path">Back to Learning Path</ActionLink>
    <PageHeader title={mission.title}><p>Mission Briefing · {mission.challenges.length} challenges</p></PageHeader>
    <Card><h2>Briefing</h2><p className={styles.text}>{mission.description ?? "A briefing has not been supplied for this mission."}</p></Card>
    <Card><h2>Challenges</h2>{mission.challenges.length ? <ol>{[...mission.challenges].sort((a, b) => a.sort_order - b.sort_order || a.id - b.id).map(challenge => <li key={challenge.id}><h3>{challenge.title}</h3><p className={styles.text}>{challenge.description}</p></li>)}</ol> : <p>No challenges are available yet.</p>}</Card>
    <Card><h2>Lab Environment</h2><p>Use the attacker environment in your external terminal to investigate the provided target on the isolated lab network. Target information appears in the Lab Workspace when available.</p></Card>
    <SecurityNotice />
    <ActionLink href={`/missions/${mission.id}/lab`}>Open Lab Workspace</ActionLink>
  </div>;
}
