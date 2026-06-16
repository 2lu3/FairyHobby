import { env } from "~/lib/env.server";


export async function registerUser(params: {
  displayName: string;
  token: string;
}) {
  const response = await fetch(`${env.BACKEND_URL}/users`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${params.token}`,
    },
    body: JSON.stringify({ display_name: params.displayName }),
  });

  const data = await response.json().catch(() => null);

  return { response, data, setCookie: response.headers.get("Set-Cookie") };
}

export async function createSession(token: string) {
  const response = await fetch(`${env.BACKEND_URL}/auth/session`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await response.json().catch(() => null);
  const needs_signup = data?.needs_signup as boolean;
  const user_id = data?.id as string | null;

  return { user_id, needs_signup, setCookie: response.headers.get("Set-Cookie") };
}