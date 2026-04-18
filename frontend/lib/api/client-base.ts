export function getApiBaseUrl(): string {
  const base = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");
  if (!base) {
    return "http://localhost:8000";
  }
  return base;
}

/**
 * Same as `fetch`, but turns the browser's useless "Failed to fetch" into an actionable message.
 */
export async function apiFetch(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<Response> {
  const base = getApiBaseUrl();
  try {
    return await fetch(input, init);
  } catch (err) {
    if (err instanceof TypeError) {
      throw new Error(
        `Cannot reach the AIMOS API (${base}). ` +
          `From the repo root run: docker compose up -d api (or ./setup.sh). ` +
          `Open http://localhost:8000/health/ready — if it does not load, the API is not running. ` +
          `If your API is on another host/port, set NEXT_PUBLIC_API_URL in frontend/.env.local and restart npm run dev.`,
      );
    }
    throw err;
  }
}
