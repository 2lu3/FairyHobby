import { useRouteLoaderData } from "react-router";

import Header from "~/component/Header";
import type { loader as authLoader } from "./_auth";
import Container from "~/component/Container";

export default function Home() {
    const { user } = useRouteLoaderData("routes/_auth") as Exclude<
        Awaited<ReturnType<typeof authLoader>>,
        Response
    >;

    return (
        <div className="min-h-screen">
            <Container>
                <div className="mt-4">
                    <Header userName={user.display_name}/>
                </div>
                
            </Container>
        </div>
    );
}
