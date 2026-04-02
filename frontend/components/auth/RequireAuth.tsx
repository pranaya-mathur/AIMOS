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
      <div className="flex min-h-screen items-center justify-center bg-slate-50 text-slate-600">
        Checking session…
      </div>
    );
  }

  return <>{children}</>;
}
