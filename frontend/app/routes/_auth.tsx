import { redirect, Outlet } from "react-router";
import type { Route } from "./+types/_auth";
import { backendFetch } from "~/lib/fetcher.server";
import Header from "~/component/Header";
import Footer from "~/component/Footer";
import SettingsButton from "~/component/SettingsButton";

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


export default function Protected({ loaderData }: Route.ComponentProps) {
    const { user } = loaderData;

    return (
        <div className="flex min-h-screen flex-col">
            <Header name={user.display_name} icon={user.icon} />
            <main className="flex flex-1 flex-col">
                <Outlet />
            </main>
            <Footer />
            <div className="fixed bottom-8 left-8 z-50">
                <SettingsButton />
            </div>
        </div>
    );
}
