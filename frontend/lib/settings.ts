import { getApiBaseUrl } from "./api/client-base";

export type AppSettings = {
  apiBaseUrl: string;
};

/** Browser + API base URL for modules that use raw `fetch` (legacy pattern). */
export function getSettings(): AppSettings {
  return { apiBaseUrl: getApiBaseUrl() };
}
