import type { AgentStatus } from "./types";

type AgentNodeProps = {
  title: string;
  status: AgentStatus;
};

const statusColor: Record<AgentStatus, string> = {
  done: "text-emerald-700",
  running: "animate-pulse text-amber-600",
  pending: "text-slate-400",
  failed: "text-red-600",
};

export function AgentNode({ title, status }: AgentNodeProps) {
  return (
    <div className="h-24 w-44 shrink-0 rounded-2xl border border-slate-200 bg-white p-3 shadow-sm">
      <p className="text-sm font-medium text-slate-800">{title}</p>
      <span className={`text-xs capitalize ${statusColor[status]}`}>
        {status}
      </span>
    </div>
  );
}
