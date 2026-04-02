import type { AgentStatus, AgentStep } from "@/components/pipeline/types";
import {
  AGENT_DISPLAY_NAMES,
  AGENT_PIPELINE_ORDER,
} from "./agent-order";

type CampaignLike = {
  status: string;
  output: unknown;
};

function getAgentOutputs(output: unknown): Record<string, unknown> | null {
  if (!output || typeof output !== "object") return null;
  const o = output as Record<string, unknown>;
  const raw = o.agent_outputs;
  if (!raw || typeof raw !== "object") return null;
  return raw as Record<string, unknown>;
}

function titleFor(agentId: string): string {
  return AGENT_DISPLAY_NAMES[agentId] ?? agentId.replace(/_/g, " ");
}

/**
 * Maps persisted LangGraph state (`agent_outputs`, `last_agent`) + campaign status
 * into UI pipeline steps.
 */
export function mapAgentStepsFromCampaign(campaign: CampaignLike | null): {
  steps: AgentStep[];
  headline: string;
} {
  if (!campaign) {
    return {
      steps: AGENT_PIPELINE_ORDER.map((id) => ({
        title: titleFor(id),
        status: "pending" as const,
      })),
      headline: "No campaign loaded",
    };
  }

  const ao = getAgentOutputs(campaign.output);

  const steps: AgentStep[] = (() => {
    if (campaign.status === "completed" || campaign.status === "rejected") {
      return AGENT_PIPELINE_ORDER.map((id) => {
        const status: AgentStatus =
          ao && id in ao ? "done" : "pending";
        return { title: titleFor(id), status };
      });
    }

    if (campaign.status === "failed") {
      if (ao && Object.keys(ao).length > 0) {
        const firstMissing = AGENT_PIPELINE_ORDER.find((x) => !(x in ao));
        return AGENT_PIPELINE_ORDER.map((id) => {
          if (id in ao) return { title: titleFor(id), status: "done" as const };
          if (id === firstMissing)
            return { title: titleFor(id), status: "failed" as const };
          return { title: titleFor(id), status: "pending" as const };
        });
      }
      return AGENT_PIPELINE_ORDER.map((id, i) => ({
        title: titleFor(id),
        status: (i === 0 ? "failed" : "pending") as AgentStatus,
      }));
    }

    if (campaign.status === "processing") {
      return AGENT_PIPELINE_ORDER.map((id) => {
        if (ao && id in ao) return { title: titleFor(id), status: "done" as const };
        const firstPending = AGENT_PIPELINE_ORDER.find(
          (x) => !ao || !(x in ao),
        );
        const status: AgentStatus =
          id === firstPending ? "running" : "pending";
        return { title: titleFor(id), status };
      });
    }

    return AGENT_PIPELINE_ORDER.map((id) => ({
      title: titleFor(id),
      status: "pending" as const,
    }));
  })();

  const headline =
    campaign.status === "processing"
      ? "Pipeline running"
      : campaign.status === "completed"
        ? "Pipeline complete"
        : campaign.status === "rejected"
          ? "Rejected after review"
          : campaign.status === "failed"
            ? "Pipeline failed"
            : `Campaign: ${campaign.status}`;

  return { steps, headline };
}
