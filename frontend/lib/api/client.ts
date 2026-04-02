import { getApiBaseUrl } from "./client-base";
import { refreshAccessToken } from "@/lib/auth/refresh-access";
import { getStoredToken } from "./token-store";

export { getApiBaseUrl } from "./client-base";
export {
  getStoredToken,
  setStoredToken,
} from "./token-store";

type FetchJsonOptions = RequestInit & {
  token?: string | null;
  /** @internal skip refresh loop */
  _skipRefreshRetry?: boolean;
};

async function doFetch(
  path: string,
  options: FetchJsonOptions,
): Promise<Response> {
  const { token, headers, _skipRefreshRetry, ...init } = options;
  void _skipRefreshRetry;
  const auth = token !== undefined ? token : getStoredToken();
  const h = new Headers(headers);
  h.set("Accept", "application/json");
  if (auth) {
    h.set("Authorization", `Bearer ${auth}`);
  }
  const url = path.startsWith("http") ? path : `${getApiBaseUrl()}${path}`;
  return fetch(url, { ...init, headers: h });
}

export async function apiFetch(
  path: string,
  init: FetchJsonOptions = {},
): Promise<Response> {
  const { _skipRefreshRetry, ...rest } = init;
  let res = await doFetch(path, rest);
  if (
    res.status === 401 &&
    !_skipRefreshRetry &&
    getStoredToken() &&
    !isAuthPath(path)
  ) {
    const ok = await refreshAccessToken();
    if (ok) {
      res = await doFetch(path, { ...rest, _skipRefreshRetry: true });
    }
  }
  return res;
}

function isAuthPath(path: string): boolean {
  return path.includes("/auth/login") || path.includes("/auth/register");
}

export async function apiFetchJson<T>(
  path: string,
  init?: FetchJsonOptions,
): Promise<T> {
  const res = await apiFetch(path, init);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}
