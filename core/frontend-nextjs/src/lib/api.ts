/**
 * API client — typed wrapper around the Infinity X One API.
 */
const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(err.message ?? "Request failed");
  }
  return res.json() as Promise<T>;
}

export const api = {
  auth: {
    register: (body: { email: string; password: string; name: string }) =>
      request<User>("/auth/register", { method: "POST", body: JSON.stringify(body) }),
    login: (body: { email: string; password: string }) =>
      request<TokenPair>("/auth/login", { method: "POST", body: JSON.stringify(body) }),
    me: (token: string) =>
      request<User>("/auth/me", { headers: { Authorization: `Bearer ${token}` } }),
  },
  health: {
    check: () => request<{ status: string; version: string; env: string }>("/health"),
  },
};
