"use client";
import { useCallback } from "react";
import { Badge, Card } from "@/components/ui";
import { api, type Mission } from "@/lib/api/client";
import { useResource } from "@/lib/api/useResource";
import { ActionLink } from "@/components/mission/shared";
export function ActiveLabBanner({ mission }: { mission: Mission }) {
  const loader = useCallback((signal: AbortSignal) => api.labStatus(mission.id, signal), [mission.id]);
  const { data } = useResource(loader);
  if (data?.status !== "RUNNING") return null;
  return <Card><Badge tone="success">LAB RUNNING</Badge><h2>{mission.title}</h2>{data.target && <p className="technical-value">{data.target.ip}</p>}<ActionLink href={`/missions/${mission.id}/lab`}>Open Lab</ActionLink></Card>;
}
