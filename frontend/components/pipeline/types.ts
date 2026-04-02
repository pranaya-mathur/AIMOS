export type AgentStatus = "done" | "running" | "pending" | "failed";

export type AgentStep = {
  title: string;
  status: AgentStatus;
};
