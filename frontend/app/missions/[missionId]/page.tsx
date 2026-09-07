import { PlaceholderPage } from "@/components/layout/PlaceholderPage";

type MissionPageProps = {
  params: Promise<{ missionId: string }>;
};

export default async function MissionPage({ params }: MissionPageProps) {
  const { missionId } = await params;

  return (
    <PlaceholderPage
      title="Mission Detail"
      description="Frontend foundation ready."
      contextLabel="Mission ID"
      contextValue={missionId}
    />
  );
}
