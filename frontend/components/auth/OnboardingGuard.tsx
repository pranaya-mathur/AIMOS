"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { getOnboardingStatus } from "@/lib/api/brand";

export function OnboardingGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    // Skip check for onboarding page itself to avoid infinite loop
    if (pathname === "/onboarding") {
      setChecking(false);
      return;
    }

    getOnboardingStatus()
      .then((status) => {
        if (!status.is_onboarded) {
          router.push("/onboarding");
        } else {
          setChecking(false);
        }
      })
      .catch(() => {
        // On error, let them pass but log it
        setChecking(false);
      });
  }, [pathname, router]);

  if (checking) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-violet-600 border-t-transparent" />
          <p className="text-sm font-medium text-slate-500">Checking account status...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
