/** Mirrors `backend/services/orchestrator.py` AGENT_ORDER (graph node names). */
export const AGENT_PIPELINE_ORDER = [
  "business_analyzer",
  "brand_builder",
  "content_studio",
  "campaign_builder",
  "social_media_manager",
  "lead_capture",
  "sales_agent",
  "customer_engagement",
  "analytics_engine",
  "optimization_engine",
  "growth_planner",
  "business_dashboard",
] as const;

export type AgentGraphName = (typeof AGENT_PIPELINE_ORDER)[number];

/** Human labels for the control tower UI. */
export const AGENT_DISPLAY_NAMES: Record<string, string> = {
  business_analyzer: "Research",
  brand_builder: "Brand",
  content_studio: "Content",
  campaign_builder: "Campaign",
  social_media_manager: "Social",
  lead_capture: "Leads",
  sales_agent: "Sales",
  customer_engagement: "Engagement",
  analytics_engine: "Analytics",
  optimization_engine: "Optimize",
  growth_planner: "Growth",
  business_dashboard: "Dashboard",
};
