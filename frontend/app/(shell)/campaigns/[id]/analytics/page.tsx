import { CampaignAnalyticsDetail } from "@/components/campaigns/CampaignAnalyticsDetail";

export default async function CampaignAnalyticsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <CampaignAnalyticsDetail campaignId={id} />;
}
