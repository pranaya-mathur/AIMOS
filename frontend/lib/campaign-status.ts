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
};

/** Light-theme badges (Bubble-style soft pills). */
export function statusBadgeClass(status: string): string {
  switch (status) {
    case "completed":
      return "bg-emerald-100 text-emerald-900 ring-1 ring-emerald-200/80";
    case "processing":
      return "bg-amber-100 text-amber-900 ring-1 ring-amber-200/80";
    case "failed":
    case "rejected":
      return "bg-red-100 text-red-900 ring-1 ring-red-200/80";
    case "active":
      return "bg-violet-100 text-violet-900 ring-1 ring-violet-200/80";
    case "paused":
      return "bg-slate-100 text-slate-700 ring-1 ring-slate-200";
    case "pending_payment":
    case "pending_approval":
      return "bg-orange-100 text-orange-900 ring-1 ring-orange-200/80";
    default:
      return "bg-slate-100 text-slate-700 ring-1 ring-slate-200";
  }
}
