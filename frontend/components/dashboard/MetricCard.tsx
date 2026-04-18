import { ReactNode } from "react";

type MetricCardProps = {
  title: string;
  value: string | number;
  change: string;
  changeTone?: "positive" | "negative" | "neutral";
  icon?: ReactNode;
};

export function MetricCard({
  title,
  value,
  change,
  changeTone = "positive",
  icon,
}: MetricCardProps) {
  const toneBadge =
    changeTone === "positive"
      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
      : changeTone === "negative"
        ? "bg-rose-500/10 text-rose-400 border-rose-500/20"
        : "bg-white/[0.04] text-slate-400 border-white/[0.06]";

  return (
    <div className="glass-card group relative overflow-hidden p-5">
      {/* Hover glow orb */}
      <div className="absolute -right-6 -top-6 h-28 w-28 rounded-full bg-gradient-to-br from-violet-500/20 to-fuchsia-500/5 blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

      <div className="relative flex justify-between items-start mb-3">
        <p className="text-xs font-semibold tracking-widest text-slate-500 uppercase">{title}</p>
        {icon && (
          <div className="flex items-center justify-center h-9 w-9 rounded-lg bg-white/[0.04] border border-white/[0.06] text-slate-500 group-hover:text-violet-400 group-hover:border-violet-500/20 transition-all duration-300">
            {icon}
          </div>
        )}
      </div>

      <div className="relative">
        <h2 className="text-3xl font-bold tracking-tight text-white group-hover:text-violet-100 transition-colors duration-300">
          {value}
        </h2>
        <div className="mt-3">
          <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-semibold border ${toneBadge}`}>
            {change}
          </span>
        </div>
      </div>
    </div>
  );
}
