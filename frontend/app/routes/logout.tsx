import { signOut } from "firebase/auth";
import { redirect } from "react-router";
import { auth } from "~/lib/firebase.client";
import { backendFetch } from "~/lib/fetcher.server";
import type { Route } from "./+types/logout";


export async function action({ request }: Route.ActionArgs) {
    await backendFetch(request, "/auth/session", {
        method: "DELETE",
    });
    return null;
}

export async function clientAction({ serverAction }: Route.ClientActionArgs) {
    await serverAction();
    await signOut(auth);
    return redirect("/home");
}

export default function Logout() {
    return <div>error</div>
}