import { ReactNode } from "react";

type AuthFlowShellProps = {
  children: ReactNode;
  /** `md` matches login; `lg` for wider forms (register). */
  maxWidthClass?: "max-w-md" | "max-w-lg";
};

/**
 * Shared dark canvas + glass card shell for login, register, and password reset.
 */
export function AuthFlowShell({
  children,
  maxWidthClass = "max-w-md",
}: AuthFlowShellProps) {
  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-[#0a0a12] px-4 py-10">
      <div className="ambient-orb h-[480px] w-[480px] bg-violet-600 top-[-140px] right-[-120px]" />
      <div
        className="ambient-orb h-[360px] w-[360px] bg-indigo-700 bottom-[-100px] left-[-80px]"
        style={{ animationDelay: "2.5s" }}
      />
      <div
        className={`relative z-10 w-full ${maxWidthClass} rounded-2xl border border-white/[0.08] bg-[rgba(15,15,25,0.75)] p-8 shadow-[0_24px_80px_-24px_rgba(0,0,0,0.6)] backdrop-blur-xl`}
      >
        {children}
      </div>
    </div>
  );
}
