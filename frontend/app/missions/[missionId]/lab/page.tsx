import { PlaceholderPage } from "@/components/layout/PlaceholderPage";

type LabPageProps = {
  params: Promise<{ missionId: string }>;
};

export default async function LabPage({ params }: LabPageProps) {
  const { missionId } = await params;

  return (
    <PlaceholderPage
      title="Lab Workspace"
      description="Frontend foundation ready."
      contextLabel="Mission ID"
      contextValue={missionId}
    />
  );
}
