"use client";

import { usePathname, useRouter } from "next/navigation";
import { startTransition, useEffect, useState } from "react";
import { getStoredToken } from "@/lib/api/token-store";

function authDisabled(): boolean {
  return process.env.NEXT_PUBLIC_AUTH_DISABLED === "1";
}

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [ok, setOk] = useState(() => authDisabled());

  useEffect(() => {
    if (authDisabled()) return;
    const token = getStoredToken();
    if (!token) {
      const next = encodeURIComponent(pathname || "/");
      router.replace(`/login?next=${next}`);
      return;
    }
    startTransition(() => setOk(true));
  }, [pathname, router]);

  if (!ok) {
    return (
      <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-[#0a0a12] text-slate-400">
        <div className="pointer-events-none absolute -right-24 top-[-10%] h-[420px] w-[420px] rounded-full bg-violet-600/10 blur-[100px]" />
        <div className="pointer-events-none absolute bottom-[-15%] left-[-10%] h-[360px] w-[360px] rounded-full bg-indigo-700/10 blur-[90px]" />
        <div className="relative flex flex-col items-center gap-3">
          <div className="h-9 w-9 animate-spin rounded-full border-2 border-violet-500/30 border-t-violet-500" />
          <p className="text-sm font-medium tracking-tight text-slate-500">
            Checking session…
          </p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
