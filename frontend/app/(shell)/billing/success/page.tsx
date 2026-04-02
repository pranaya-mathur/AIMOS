import { Suspense } from "react";
import { BillingSuccess } from "@/components/billing/BillingSuccess";

export default function BillingSuccessPage() {
  return (
    <Suspense
      fallback={
        <p className="text-center text-sm text-slate-500">Loading…</p>
      }
    >
      <BillingSuccess />
    </Suspense>
  );
}
