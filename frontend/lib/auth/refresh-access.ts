import { getApiBaseUrl } from "@/lib/api/client-base";
import { getStoredToken, setStoredToken } from "@/lib/api/token-store";

type RefreshResponse = {
  access_token: string;
};

/** POST /auth/refresh — returns true if a new token was stored. */
export async function refreshAccessToken(): Promise<boolean> {
  const token = getStoredToken();
  if (!token) return false;
  try {
    const res = await fetch(`${getApiBaseUrl()}/auth/refresh`, {
      method: "POST",
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok) return false;
    const data = (await res.json()) as RefreshResponse;
    if (!data.access_token) return false;
    setStoredToken(data.access_token);
    return true;
  } catch {
    return false;
  }
}
