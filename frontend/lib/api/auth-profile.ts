import { apiFetchJson } from "./client";

export type MeResponse = {
  id: string | null;
  email: string | null;
  role: string | null;
  full_name: string | null;
  note?: string;
};

export async function getMe(): Promise<MeResponse> {
  return apiFetchJson("/auth/me");
}
