import { useRouteLoaderData } from "react-router";

import Header from "~/component/Header";
import type { loader as authLoader } from "./_auth";

export default function Home() {
    const { user } = useRouteLoaderData("routes/_auth") as Exclude<
        Awaited<ReturnType<typeof authLoader>>,
        Response
    >;

    return (
        <div className="min-h-screen">
            <div className="mx-auto w-full max-w-5xl px-8">
                <Header userName={user.display_name} />
            </div>
        </div>
    );
}
