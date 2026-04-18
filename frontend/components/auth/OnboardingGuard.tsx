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
      <div className="relative flex h-screen items-center justify-center overflow-hidden bg-[#0a0a12]">
        <div className="pointer-events-none absolute right-[-20%] top-[15%] h-[380px] w-[380px] rounded-full bg-fuchsia-600/8 blur-[100px]" />
        <div className="pointer-events-none absolute bottom-[10%] left-[-15%] h-[320px] w-[320px] rounded-full bg-violet-600/10 blur-[90px]" />
        <div className="relative flex flex-col items-center gap-4">
          <div className="h-11 w-11 animate-spin rounded-full border-[3px] border-violet-500/25 border-t-violet-500" />
          <p className="text-sm font-medium text-slate-500">
            Checking account status…
          </p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
