type MetricCardProps = {
  title: string;
  value: string;
  change: string;
  changeTone?: "positive" | "negative" | "neutral";
};

export function MetricCard({
  title,
  value,
  change,
  changeTone = "positive",
}: MetricCardProps) {
  const toneClass =
    changeTone === "positive"
      ? "text-emerald-600"
      : changeTone === "negative"
        ? "text-red-600"
        : "text-slate-500";

  return (
    <div className="w-full rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-slate-500">{title}</p>
      <h2 className="mt-1 text-2xl font-semibold tracking-tight text-slate-900">
        {value}
      </h2>
      <span className={`text-sm ${toneClass}`}>{change}</span>
    </div>
  );
}
