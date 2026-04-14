import { RequireAuth } from "@/components/auth/RequireAuth";
import { OnboardingGuard } from "@/components/auth/OnboardingGuard";
import { ControlTowerShell } from "@/components/layout/ControlTowerShell";

export default function ShellLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <RequireAuth>
      <OnboardingGuard>
        <ControlTowerShell>{children}</ControlTowerShell>
      </OnboardingGuard>
    </RequireAuth>
  );
}
