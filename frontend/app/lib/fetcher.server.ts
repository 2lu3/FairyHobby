import { env } from "~/lib/env.server";

export async function backendFetch(
  request: Request,
  path: string,
  init: RequestInit = {},
) {
  return fetch(`${env.BACKEND_URL}${path}`, {
    ...init,
    headers: {
      cookie: request.headers.get("cookie") ?? "",
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
  })
}
