import { RequireAuth } from "@/components/auth/RequireAuth";
import { ControlTowerShell } from "@/components/layout/ControlTowerShell";

export default function ShellLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <RequireAuth>
      <ControlTowerShell>{children}</ControlTowerShell>
    </RequireAuth>
  );
}
