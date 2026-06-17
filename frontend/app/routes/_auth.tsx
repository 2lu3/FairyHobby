import { redirect, Outlet } from "react-router";
import type { Route } from "./+types/_auth";
import { backendFetch } from "~/lib/fetcher.server";
import { createSession } from "~/lib/auth.server";


export async function loader({ request }: Route.LoaderArgs) {
    const res = await backendFetch(request, "/users/me")
  
    if (res.status === 401) {
      return redirect("/home")
    }
  
    if (!res.ok) {
      return redirect("/home")
    }

    return { user: await res.json() }
  }


export default function Protected() {
    return <Outlet />
}