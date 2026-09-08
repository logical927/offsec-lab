import { notFound } from "next/navigation";
import { LabWorkspace } from "@/components/lab/LabWorkspace";

type LabPageProps = {
  params: Promise<{ missionId: string }>;
};

export default async function LabPage({ params }: LabPageProps) {
  const { missionId } = await params;

  if (!/^[1-9]\d*$/.test(missionId) || !Number.isSafeInteger(Number(missionId))) notFound();
  return <LabWorkspace key={missionId} missionId={Number(missionId)} />;
}
