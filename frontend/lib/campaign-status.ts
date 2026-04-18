/** Labels and UI hints for campaign lifecycle (see backend `Campaign` model). */
export const STATUS_LABEL: Record<string, string> = {
  draft: "Draft",
  pending_approval: "Pending approval",
  pending_payment: "Pending payment",
  paid: "Paid",
  processing: "Processing",
  active: "Active",
  paused: "Paused",
  completed: "Completed",
  failed: "Failed",
  rejected: "Rejected",
  awaiting_feedback: "Feedback Required",
};

/** Dark-theme badges (glass / neon pills). */
export function statusBadgeClass(status: string): string {
  switch (status) {
    case "awaiting_feedback":
      return "bg-violet-600 text-white ring-2 ring-violet-400/60 shadow-lg shadow-violet-500/20 animate-pulse";
    case "completed":
      return "bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-500/30";
    case "processing":
      return "bg-amber-500/15 text-amber-300 ring-1 ring-amber-500/30";
    case "failed":
    case "rejected":
      return "bg-rose-500/15 text-rose-300 ring-1 ring-rose-500/30";
    case "active":
      return "bg-violet-500/15 text-violet-300 ring-1 ring-violet-500/30";
    case "paused":
      return "bg-white/[0.06] text-slate-300 ring-1 ring-white/10";
    case "pending_payment":
    case "pending_approval":
      return "bg-orange-500/15 text-orange-300 ring-1 ring-orange-500/30";
    default:
      return "bg-white/[0.06] text-slate-300 ring-1 ring-white/10";
  }
}
