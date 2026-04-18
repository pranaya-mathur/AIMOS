export type AgentStatus = "done" | "running" | "pending" | "failed";

export type AgentStep = {
  title: React.ReactNode;
  status: AgentStatus;
};
