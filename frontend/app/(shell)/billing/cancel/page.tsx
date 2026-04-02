import Link from "next/link";

export default function BillingCancelPage() {
  return (
    <div className="mx-auto max-w-lg space-y-4 text-center">
      <h1 className="text-2xl font-semibold text-amber-400">Checkout cancelled</h1>
      <p className="text-sm text-slate-600">
        No charge was made. You can try again from the billing page when ready.
      </p>
      <Link
        href="/billing"
        className="inline-block rounded-xl bg-violet-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-violet-700"
      >
        Back to billing
      </Link>
    </div>
  );
}
