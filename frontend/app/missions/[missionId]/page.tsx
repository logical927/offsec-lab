import { notFound } from "next/navigation";
import { MissionBriefing } from "@/components/mission/MissionBriefing";

type MissionPageProps = {
  params: Promise<{ missionId: string }>;
};

export default async function MissionPage({ params }: MissionPageProps) {
  const { missionId } = await params;

  if (!/^[1-9]\d*$/.test(missionId) || !Number.isSafeInteger(Number(missionId))) notFound();
  return <MissionBriefing key={missionId} missionId={Number(missionId)} />;
}
