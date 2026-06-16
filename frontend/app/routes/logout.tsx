import { signOut } from "firebase/auth";
import { redirect } from "react-router";
import { auth } from "~/lib/firebase.client";
import { backendFetch } from "~/lib/fetcher.server";
import type { Route } from "./+types/logout";


export async function action({ request }: Route.ActionArgs) {
    backendFetch(request, "/auth/session", {
        method: "DELETE",
    });
    return 
}

export async function clientAction({request, serverAction}: Route.ClientActionArgs) {
    console.log("clientAction");
    await serverAction();
    console.log("signOut");
    await signOut(auth);
    console.log("redirect");
    return redirect("/home");
}

export default function Logout() {
    return <div>error</div>
}