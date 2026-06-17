import { useRouteLoaderData } from "react-router";

import Header from "~/component/Header";
import type { loader as authLoader } from "./_auth";
import Container from "~/component/Container";
import  SettingsButton from "~/component/SettingsButton";
import Footer from "~/component/Footer";

export default function Home() {
    const { user } = useRouteLoaderData("routes/_auth") as Exclude<
        Awaited<ReturnType<typeof authLoader>>,
        Response
    >;

    return (
        <div className="flex flex-col">
            <Container className="flex-1 min-h-screen">
                <div className="mt-8">
                    <Header name={user.display_name} icon={user.icon} />
                </div>
                <main></main>
            </Container>
            <Footer />
            <div className="fixed bottom-8 left-8 z-50">
                <SettingsButton />
            </div>
        </div>
    );
}
