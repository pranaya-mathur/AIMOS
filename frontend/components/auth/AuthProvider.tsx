"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
} from "react";
import { readJwtExpMs } from "@/lib/auth/jwt";
import { refreshAccessToken } from "@/lib/auth/refresh-access";
import { getStoredToken } from "@/lib/api/token-store";

type AuthContextValue = {
  refreshSession: () => Promise<boolean>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function authDisabled(): boolean {
  return process.env.NEXT_PUBLIC_AUTH_DISABLED === "1";
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const refreshSession = useCallback(async () => {
    if (authDisabled()) return true;
    return refreshAccessToken();
  }, []);

  useEffect(() => {
    if (authDisabled()) return;

    const schedule = () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
      const token = getStoredToken();
      if (!token) return;
      const expMs = readJwtExpMs(token);
      if (!expMs) return;
      const skew = 120_000;
      const delay = Math.max(10_000, expMs - Date.now() - skew);
      timerRef.current = setTimeout(() => {
        void refreshAccessToken().finally(() => schedule());
      }, delay);
    };

    schedule();
    const pulse = setInterval(() => {
      const token = getStoredToken();
      if (!token) return;
      const expMs = readJwtExpMs(token);
      if (expMs && expMs - Date.now() < 180_000) void refreshAccessToken();
    }, 60_000);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
      clearInterval(pulse);
    };
  }, []);

  return (
    <AuthContext.Provider value={{ refreshSession }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    return { refreshSession: () => Promise.resolve(false) };
  }
  return ctx;
}
