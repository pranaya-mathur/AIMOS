"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { setStoredToken } from "@/lib/api/token-store";

function authDisabled(): boolean {
  return process.env.NEXT_PUBLIC_AUTH_DISABLED === "1";
}

export function NavActions() {
  const router = useRouter();

  function signOut() {
    setStoredToken(null);
    router.push("/login");
    router.refresh();
  }

  return (
    <div className="flex items-center gap-2">
      {!authDisabled() && (
        <button
          type="button"
          onClick={signOut}
          className="rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 hover:text-slate-900"
        >
          Sign out
        </button>
      )}
      {authDisabled() && (
        <Link
          href="/login"
          className="hidden rounded-lg px-3 py-2 text-sm text-slate-600 hover:text-slate-900 sm:inline"
        >
          Sign in
        </Link>
      )}
      <Link
        href="/campaign"
        className="rounded-xl bg-violet-600 px-3 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-violet-700 md:px-4"
      >
        + Campaign
      </Link>
    </div>
  );
}
