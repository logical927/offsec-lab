import Link from "next/link";
import type { ReactNode } from "react";
import { Badge, Button, Card, ProgressBar, Spinner } from "@/components/ui";
import type { MissionProgress } from "@/lib/api/client";
import styles from "./mission.module.css";
export function PageHeader({ title, children }: { title: string; children?: ReactNode }) {
  return <header className={styles.header}><h1>{title}</h1>{children}</header>;
}
export function ActionLink({ href, children }: { href: string; children: ReactNode }) {
  return <Link className={styles.link} href={href}>{children}</Link>;
}
export function LoadState({ error, retry }: { error?: string; retry: () => void }) {
  return error ? <Card><p role="alert">{error}</p><Button onClick={retry}>Try again</Button></Card> : <Spinner label="Loading mission data" />;
}
export function MissionStatus({ status }: { status?: MissionProgress["status"] | "LOCKED" }) {
  const text = status === "NOT_STARTED" ? "AVAILABLE" : status ?? "STATUS UNAVAILABLE";
  return <Badge tone={status === "COMPLETED" ? "success" : status === "IN_PROGRESS" ? "info" : "neutral"}>{text.replaceAll("_", " ")}</Badge>;
}
export function ChallengeProgress({ progress }: { progress?: MissionProgress }) {
  if (!progress) return <p>Progress unavailable.</p>;
  const complete = progress.challenges.filter(c => c.status === "COMPLETED").length;
  return <div><ProgressBar label="Challenge progress" value={complete} max={progress.challenges.length || 1} /><p>{complete} of {progress.challenges.length} challenges completed</p></div>;
}
export function SecurityNotice() {
  return <Card className={styles.notice}><h2>Security Notice</h2><p>Perform scanning and exploitation only against the target provided by OffSec Lab.</p></Card>;
}
