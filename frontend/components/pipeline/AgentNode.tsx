import type { AgentStatus } from "./types";

type AgentNodeProps = {
  title: React.ReactNode;
  status: AgentStatus;
};

const statusColor: Record<AgentStatus, string> = {
  done: "text-emerald-400",
  running: "animate-pulse text-amber-400",
  pending: "text-slate-500",
  failed: "text-rose-400",
};

export function AgentNode({ title, status }: AgentNodeProps) {
  return (
    <div className="h-24 w-44 shrink-0 rounded-2xl border border-white/[0.08] bg-white/[0.04] p-3 shadow-[0_4px_24px_-8px_rgba(0,0,0,0.4)] backdrop-blur-sm">
      <p className="text-sm font-medium text-slate-200">{title}</p>
      <span className={`text-xs capitalize ${statusColor[status]}`}>
        {status}
      </span>
    </div>
  );
}
